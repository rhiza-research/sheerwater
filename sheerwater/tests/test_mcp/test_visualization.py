"""Tests for visualization tools."""

from sheerwater.mcp.tools.chart_storage import ChartUrls
from sheerwater.mcp.tools.visualization import (
    DASHBOARDS,
    GRAFANA_BASE_URL,
    generate_comparison_chart,
    get_dashboard_link,
)


class TestGetDashboardLink:
    """Tests for get_dashboard_link function."""

    async def test_returns_url_with_no_filters(self):
        """Test that URL is returned with no filters."""
        result = await get_dashboard_link()

        assert "url" in result
        assert result["url"].startswith(GRAFANA_BASE_URL)
        assert DASHBOARDS["forecast-eval"] in result["url"]
        assert "?" not in result["url"]  # No query params

    async def test_returns_url_with_forecast_filter(self):
        """Test URL includes forecast parameter."""
        result = await get_dashboard_link(forecast="ecmwf_ifs_er")

        assert "var-forecast=ecmwf_ifs_er" in result["url"]
        assert "forecast=ecmwf_ifs_er" in result["description"]

    async def test_returns_url_with_metric_filter(self):
        """Test URL includes metric parameter."""
        result = await get_dashboard_link(metric="mae")

        assert "var-metric=mae" in result["url"]
        assert "metric=mae" in result["description"]

    async def test_returns_url_with_region_filter(self):
        """Test URL includes region parameter."""
        result = await get_dashboard_link(region="Kenya")

        assert "var-region=Kenya" in result["url"]
        assert "region=Kenya" in result["description"]

    async def test_returns_url_with_variable_filter(self):
        """Test URL includes variable parameter."""
        result = await get_dashboard_link(variable="precip")

        assert "var-variable=precip" in result["url"]
        assert "variable=precip" in result["description"]

    async def test_returns_url_with_multiple_filters(self):
        """Test URL includes multiple parameters."""
        result = await get_dashboard_link(
            forecast="ecmwf_ifs_er",
            metric="mae",
            region="Kenya",
        )

        assert "var-forecast=ecmwf_ifs_er" in result["url"]
        assert "var-metric=mae" in result["url"]
        assert "var-region=Kenya" in result["url"]
        assert "forecast=ecmwf_ifs_er" in result["description"]
        assert "metric=mae" in result["description"]
        assert "region=Kenya" in result["description"]

    async def test_returns_dashboard_name(self):
        """Test that dashboard name is included."""
        result = await get_dashboard_link()

        assert result["dashboard"] == "forecast-evaluation"

    async def test_returns_available_dashboards(self):
        """Test that available dashboards are listed."""
        result = await get_dashboard_link()

        assert "available_dashboards" in result
        assert "forecast-eval" in result["available_dashboards"]
        assert "forecast-eval-maps" in result["available_dashboards"]
        assert "ground-truth" in result["available_dashboards"]
        assert "reanalysis" in result["available_dashboards"]

    async def test_description_without_filters(self):
        """Test description text without filters."""
        result = await get_dashboard_link()

        assert result["description"] == "Forecast Evaluation Dashboard"
        assert "filtered by" not in result["description"]

    async def test_description_with_filters(self):
        """Test description text with filters."""
        result = await get_dashboard_link(forecast="fuxi", metric="rmse")

        assert "Forecast Evaluation Dashboard" in result["description"]
        assert "filtered by" in result["description"]


FAKE_COMPARISON_RESULT = {
    "status": "complete",
    "result": {
        "ranking": [
            {"model": "ecmwf_ifs_er", "score": 2.3},
            {"model": "fuxi", "score": 3.1},
        ],
    },
}


class TestGenerateComparisonChart:
    """Tests for generate_comparison_chart function."""

    async def test_unknown_chart_type_falls_through_to_bar(self, mocker):
        """Test that unknown chart types fall through to default bar chart."""
        mocker.patch(
            "sheerwater.mcp.tools.evaluation.compare_models",
            return_value=FAKE_COMPARISON_RESULT,
        )
        mocker.patch(
            "sheerwater.mcp.tools.visualization.upload_chart",
            return_value=ChartUrls(
                png_url="https://storage.example.com/charts/test.png",
                html_url="https://storage.example.com/charts/test.html",
            ),
        )
        from fastmcp.tools.tool import ToolResult

        result = await generate_comparison_chart(
            forecasts=["ecmwf_ifs_er", "fuxi"],
            metric="mae",
            chart_type="scatter",
        )

        # Falls through to bar chart, not an error
        assert isinstance(result, ToolResult)

    async def test_horizontal_bar_chart(self, mocker):
        """Test that horizontal_bar chart type works."""
        mocker.patch(
            "sheerwater.mcp.tools.evaluation.compare_models",
            return_value=FAKE_COMPARISON_RESULT,
        )
        mocker.patch(
            "sheerwater.mcp.tools.visualization.upload_chart",
            return_value=ChartUrls(
                png_url="https://storage.example.com/charts/test.png",
                html_url="https://storage.example.com/charts/test.html",
            ),
        )
        from fastmcp.tools.tool import ToolResult

        result = await generate_comparison_chart(
            forecasts=["ecmwf_ifs_er", "fuxi"],
            metric="mae",
            chart_type="horizontal_bar",
        )

        assert isinstance(result, ToolResult)
