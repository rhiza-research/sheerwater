"""GCS storage utility for chart files."""

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import timedelta

import google.auth
from google.cloud import storage

logger = logging.getLogger(__name__)


def get_chart_bucket_name() -> str:
    """Get the chart bucket name from environment variable."""
    return os.environ.get("CHART_BUCKET_NAME", "sheerwater-mcp-charts")


@dataclass
class ChartUrls:
    """URLs for both chart formats."""

    png_url: str
    html_url: str


def _generate_signed_url(blob: storage.Blob) -> str:
    """Generate a signed URL for a blob using IAM-based signing if needed."""
    credentials, project = google.auth.default()

    service_account_email = os.environ.get("SIGNING_SERVICE_ACCOUNT")
    if not service_account_email:
        service_account_email = getattr(credentials, "service_account_email", None)

    if service_account_email:
        from google.auth.transport import requests

        auth_request = requests.Request()
        credentials.refresh(auth_request)

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET",
            service_account_email=service_account_email,
            access_token=credentials.token,
        )
    else:
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET",
        )


def upload_chart(fig) -> ChartUrls:
    """Upload chart as both HTML and PNG, return signed URLs for both.

    Args:
        fig: A Plotly figure object.

    Returns:
        ChartUrls with signed URLs for PNG and HTML versions (expire in 7 days).
    """
    bucket_name = get_chart_bucket_name()
    chart_id = str(uuid.uuid4())

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Generate and upload PNG (fallback for non-interactive clients like Slack)
    png_bytes = fig.to_image(format="png", width=800, height=600, scale=2)
    png_blob = bucket.blob(f"charts/{chart_id}.png")
    png_blob.upload_from_string(png_bytes, content_type="image/png")

    # Generate and upload HTML (enhancement for interactive clients like sheerwater-chat)
    html_content = fig.to_html(full_html=True, include_plotlyjs="cdn")
    html_blob = bucket.blob(f"charts/{chart_id}.html")
    html_blob.upload_from_string(html_content, content_type="text/html")

    # Generate signed URLs for both
    return ChartUrls(
        png_url=_generate_signed_url(png_blob),
        html_url=_generate_signed_url(html_blob),
    )


def upload_chart_html(html_content: str) -> str:
    """Upload chart HTML to GCS and return a signed URL.

    DEPRECATED: Use upload_chart() instead for dual-format support.

    Args:
        html_content: The HTML string to upload.

    Returns:
        A signed URL for accessing the chart (expires in 7 days).
    """
    bucket_name = get_chart_bucket_name()
    blob_name = f"charts/{uuid.uuid4()}.html"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(html_content, content_type="text/html")

    return _generate_signed_url(blob)
