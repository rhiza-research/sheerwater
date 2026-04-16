"""`sheerwater list` — discovery commands for datasets, forecasts, and metrics."""
from __future__ import annotations

import click


def _emit(names, as_json: bool) -> None:
    if as_json:
        import json

        click.echo(json.dumps(sorted(names)))
    else:
        for n in sorted(names):
            click.echo(n)


@click.group("list")
def list_():
    """Discovery: list registered datasets, forecasts, and metrics."""


@list_.command("datasets")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON array.")
def list_datasets(as_json: bool) -> None:
    """List all registered data source names."""
    from sheerwater.interfaces import list_data

    _emit(list_data(), as_json)


@list_.command("forecasts")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON array.")
def list_forecasts_cmd(as_json: bool) -> None:
    """List all registered forecast model names."""
    from sheerwater.interfaces import list_forecasts

    _emit(list_forecasts(), as_json)


@list_.command("metrics")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON array.")
def list_metrics(as_json: bool) -> None:
    """List all registered verification metric names."""
    # Import metrics_library to populate the metric registry.
    import sheerwater.metrics_library  # noqa: F401
    from sheerwater.metrics_library import SHEERWATER_METRIC_REGISTRY

    _emit(SHEERWATER_METRIC_REGISTRY.keys(), as_json)
