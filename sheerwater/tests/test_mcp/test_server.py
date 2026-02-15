"""Tests for the MCP server itself."""

import json

import pytest
from fastmcp import Client

from sheerwater.mcp.server import mcp
from sheerwater.mcp.tools.chart_storage import ChartUrls


@pytest.fixture
async def mcp_client():
    """Create an in-memory MCP client connected to the server."""
    async with Client(transport=mcp) as client:
        yield client


def parse_tool_result(result) -> dict:
    """Parse the CallToolResult content into a dict.

    FastMCP tool results are returned as CallToolResult objects.
    The content is a list of TextContent or ImageContent objects.
    """
    if not result.content:
        return {}
    # Find the first TextContent item and parse as JSON
    for content in result.content:
        if hasattr(content, "text"):
            return json.loads(content.text)
    return {}


class TestServerSetup:
    """Test server configuration and setup."""

    def test_server_name(self):
        """Test server has correct name."""
        assert mcp.name == "sheerwater"

    def test_server_has_instructions(self):
        """Test server has instructions configured."""
        assert mcp.instructions is not None
        assert "weather forecast" in mcp.instructions.lower()
        assert "benchmarking" in mcp.instructions.lower()


class TestToolRegistration:
    """Test that all tools are properly registered."""

    async def test_list_tools(self, mcp_client: Client):
        """Test that tools can be listed."""
        tools = await mcp_client.list_tools()
        assert len(tools) > 0

    async def test_expected_tools_registered(self, mcp_client: Client):
        """Test all expected tools are registered."""
        tools = await mcp_client.list_tools()
        tool_names = {tool.name for tool in tools}

        expected_tools = {
            "tool_list_forecasts",
            "tool_list_metrics",
            "tool_list_truth_datasets",
            "tool_get_metric_info",
            "tool_run_metric",
            "tool_compare_models",
            "tool_estimate_query_time",
            "tool_extract_truth_data",
            "tool_get_dashboard_link",
            "tool_generate_comparison_chart",
            "tool_render_plotly",
        }

        missing = expected_tools - tool_names
        extra = tool_names - expected_tools
        assert tool_names == expected_tools, f"Missing tools: {missing}, Extra tools: {extra}"

    async def test_tool_count(self, mcp_client: Client):
        """Test correct number of tools are registered."""
        tools = await mcp_client.list_tools()
        assert len(tools) == 11


class TestDiscoveryTools:
    """Test discovery tools through MCP interface."""

    async def test_list_forecasts_tool(self, mcp_client: Client):
        """Test list_forecasts tool can be called and returns forecasts."""
        result = await mcp_client.call_tool("tool_list_forecasts", {})
        data = parse_tool_result(result)

        assert "forecasts" in data
        assert len(data["forecasts"]) > 0

    async def test_list_metrics_tool(self, mcp_client: Client):
        """Test list_metrics tool can be called and returns metrics."""
        result = await mcp_client.call_tool("tool_list_metrics", {})
        data = parse_tool_result(result)

        assert "metrics" in data
        assert len(data["metrics"]) > 0
        # Check that common metrics are present
        metric_names = [m["name"] for m in data["metrics"]]
        assert "mae" in metric_names or "MAE" in metric_names

    async def test_list_truth_datasets_tool(self, mcp_client: Client):
        """Test list_truth_datasets tool can be called and returns datasets."""
        result = await mcp_client.call_tool("tool_list_truth_datasets", {})
        data = parse_tool_result(result)

        assert "datasets" in data
        assert len(data["datasets"]) > 0

    async def test_get_metric_info_tool(self, mcp_client: Client):
        """Test get_metric_info tool returns metric details."""
        result = await mcp_client.call_tool("tool_get_metric_info", {"metric_name": "mae"})
        data = parse_tool_result(result)

        assert "name" in data
        assert "description" in data


class TestEvaluationTools:
    """Test evaluation tools through MCP interface."""

    async def test_estimate_query_time_tool(self, mcp_client: Client):
        """Test estimate_query_time tool returns time estimate."""
        result = await mcp_client.call_tool(
            "tool_estimate_query_time",
            {
                "forecast": "ecmwf_ifs_er",
                "truth": "chirps_v3",
                "metric": "mae",
                "region": "Kenya",
            },
        )
        data = parse_tool_result(result)

        assert "estimated_time" in data
        assert "cached" in data or "cache_status" in data

    async def test_extract_truth_data_tool_has_parameters(self, mcp_client: Client):
        """Test extract_truth_data tool has expected parameters."""
        tools = await mcp_client.list_tools()
        tool = next((t for t in tools if t.name == "tool_extract_truth_data"), None)

        assert tool is not None
        properties = tool.inputSchema["properties"]
        assert "truth" in properties
        assert "variable" in properties
        assert "region" in properties
        assert "space_grouping" in properties
        assert "time_grouping" in properties
        assert "agg_fn" in properties


class TestVisualizationTools:
    """Test visualization tools through MCP interface."""

    async def test_get_dashboard_link_tool(self, mcp_client: Client):
        """Test get_dashboard_link tool returns a URL."""
        result = await mcp_client.call_tool(
            "tool_get_dashboard_link",
            {
                "forecast": "ecmwf_ifs_er",
                "metric": "mae",
                "region": "Kenya",
            },
        )
        data = parse_tool_result(result)

        assert "url" in data
        assert data["url"].startswith("http")

    async def test_generate_comparison_chart_tool_has_parameters(self, mcp_client: Client):
        """Test generate_comparison_chart tool accepts required parameters."""
        tools = await mcp_client.list_tools()
        chart_tool = next((t for t in tools if t.name == "tool_generate_comparison_chart"), None)

        assert chart_tool is not None
        properties = chart_tool.inputSchema["properties"]
        assert "forecasts" in properties
        assert properties["forecasts"]["type"] == "array"
        assert "metric" in properties
        assert "truth" in properties
        assert "variable" in properties

    async def test_generate_comparison_chart_unsupported_type(self, mcp_client: Client, mocker):
        """Test generate_comparison_chart falls through to bar chart for unknown types."""
        mocker.patch(
            "sheerwater.mcp.tools.visualization.upload_chart",
            return_value=ChartUrls(
                png_url="https://storage.example.com/charts/test.png",
                html_url="https://storage.example.com/charts/test.html",
            ),
        )
        result = await mcp_client.call_tool(
            "tool_generate_comparison_chart",
            {
                "forecasts": ["ecmwf_ifs_er", "fuxi"],
                "metric": "mae",
                "region": "Kenya",
                "chart_type": "line",
            },
        )
        # Unknown chart types fall through to default bar chart — no error
        assert len(result.content) == 2
        assert not result.is_error

    async def test_generate_comparison_chart_bar(self, mcp_client: Client, mocker):
        """Test generate_comparison_chart creates a bar chart with cached data."""
        mock_upload = mocker.patch(
            "sheerwater.mcp.tools.visualization.upload_chart",
            return_value=ChartUrls(
                png_url="https://storage.example.com/charts/test.png",
                html_url="https://storage.example.com/charts/test.html",
            ),
        )
        result = await mcp_client.call_tool(
            "tool_generate_comparison_chart",
            {
                "forecasts": ["ecmwf_ifs_er", "fuxi"],
                "metric": "mae",
                "region": "Kenya",
                "chart_type": "bar",
                "truth": "chirps_v3",
                "variable": "precip",
            },
        )

        # Should return two text content blocks: chart URLs + summary
        assert len(result.content) == 2

        # First content is JSON with chart URLs
        urls_data = json.loads(result.content[0].text)
        assert "png_url" in urls_data
        assert "html_url" in urls_data

        # Second content is the text summary
        summary = result.content[1].text
        assert "ecmwf_ifs_er" in summary or "fuxi" in summary

        # Verify upload_chart was called
        mock_upload.assert_called_once()


class TestToolDescriptions:
    """Test that tools have proper descriptions."""

    async def test_tools_have_descriptions(self, mcp_client: Client):
        """Test all tools have non-empty descriptions."""
        tools = await mcp_client.list_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 10, f"Tool {tool.name} has too short description"

    async def test_run_metric_tool_has_parameters(self, mcp_client: Client):
        """Test run_metric tool has required parameters."""
        tools = await mcp_client.list_tools()
        run_metric_tool = next((t for t in tools if t.name == "tool_run_metric"), None)

        assert run_metric_tool is not None
        assert run_metric_tool.inputSchema is not None
        assert "properties" in run_metric_tool.inputSchema

        # Check required parameters are defined
        properties = run_metric_tool.inputSchema["properties"]
        required_params = ["forecast", "truth", "metric"]
        for param in required_params:
            assert param in properties, f"Missing required parameter: {param}"

    async def test_compare_models_tool_has_list_parameter(self, mcp_client: Client):
        """Test compare_models tool accepts a list of forecasts."""
        tools = await mcp_client.list_tools()
        compare_tool = next((t for t in tools if t.name == "tool_compare_models"), None)

        assert compare_tool is not None
        properties = compare_tool.inputSchema["properties"]
        assert "forecasts" in properties
        # The forecasts parameter should be an array
        assert properties["forecasts"]["type"] == "array"
