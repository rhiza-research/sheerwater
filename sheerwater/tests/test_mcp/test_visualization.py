"""Tests for visualization tools."""

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


class TestGenerateComparisonChart:
    """Tests for generate_comparison_chart function."""

    async def test_unsupported_chart_type_returns_error(self):
        """Test that unknown chart type returns error."""
        result = await generate_comparison_chart(
            forecasts=["ecmwf_ifs_er", "fuxi"],
            metric="mae",
            chart_type="scatter",  # Not supported
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert "unknown chart type" in result["error"].lower()
        assert "supported_types" in result

    async def test_line_chart_not_implemented(self):
        """Test that line chart returns helpful error."""
        result = await generate_comparison_chart(
            forecasts=["ecmwf_ifs_er", "fuxi"],
            metric="mae",
            chart_type="line",
        )

        assert isinstance(result, dict)
        assert "error" in result
        assert "not yet implemented" in result["error"].lower()
        assert "suggestion" in result

    async def test_supported_types_includes_bar(self):
        """Test that bar is in supported types."""
        result = await generate_comparison_chart(
            forecasts=["ecmwf_ifs_er"],
            metric="mae",
            chart_type="heatmap",  # Not supported
        )

        assert "supported_types" in result
        assert "bar" in result["supported_types"]
