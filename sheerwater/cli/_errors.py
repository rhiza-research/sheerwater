"""Translate sheerwater/nuthatch/GCS errors into clean CLI messages.

Sheerwater fetches go through nuthatch → fsspec/gcsfs → GCS. When auth is
missing or insufficient the underlying exception is opaque (DefaultCredentialsError,
Forbidden, RefreshError, OSError chained off a 401/403). The CLI wraps each
verb invocation in `cli_run` so the user gets a one-line "you need
GOOGLE_APPLICATION_CREDENTIALS for this dataset" instead of a stack trace.
"""
from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from typing import Any

import click


_AUTH_HINT = (
    "Authentication required for this dataset.\n"
    "Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON path, or run "
    "`gcloud auth application-default login`. Public-bucket datasets work without auth."
)


def _is_gcs_auth_error(exc: BaseException) -> bool:
    """Detect GCS auth/permission failures across the layers we go through."""
    # Walk the chain; gcsfs/google-cloud-storage often wrap underlying errors.
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        cls_name = type(current).__name__
        module = type(current).__module__
        if module.startswith("google.auth.exceptions") and cls_name in {
            "DefaultCredentialsError",
            "RefreshError",
            "GoogleAuthError",
        }:
            return True
        if module.startswith("google.api_core.exceptions") and cls_name in {
            "Forbidden",
            "Unauthorized",
            "PermissionDenied",
        }:
            return True
        if module.startswith("google.cloud.exceptions") and cls_name in {
            "Forbidden",
            "Unauthorized",
        }:
            return True
        # gcsfs / aiohttp tend to surface 401/403 as messages on plain Exceptions.
        msg = str(current)
        if "401" in msg or "403" in msg or "Anonymous caller" in msg or "credentials" in msg.lower():
            if any(token in msg for token in ("gs://", "googleapis", "storage.googleapis", "oauth2")):
                return True
        current = current.__cause__ or current.__context__
    return False


def cli_run(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: translate auth errors into a clean ClickException.

    Other exceptions are re-raised unchanged so click prints its normal traceback
    in --debug mode and a short summary otherwise.
    """

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except click.ClickException:
            raise
        except Exception as exc:  # noqa: BLE001 — translation layer
            if _is_gcs_auth_error(exc):
                click.echo(f"sheerwater: {_AUTH_HINT}", err=True)
                click.echo(f"  underlying error: {type(exc).__name__}: {exc}", err=True)
                sys.exit(2)
            raise

    return wrapper
