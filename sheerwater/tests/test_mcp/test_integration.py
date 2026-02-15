"""Integration tests using real Claude Code with the MCP server.

These tests spawn actual Claude Code sessions and verify the MCP tools work end-to-end.
Results are saved to tests/mcp/integration_results/ for review.

These tests are skipped by default. Run explicitly with:
    uv run pytest sheerwater/tests/mcp/test_integration.py -v -s -m integration

Or run all tests including integration:
    uv run pytest -v -s -m "integration or not integration"
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

# Output directory for test results
OUTPUT_DIR = Path(__file__).parent / "integration_results"


def run_claude(prompt: str, test_name: str, timeout: int = 120) -> str:
    """Run Claude Code with only sheerwater MCP tools allowed.

    Saves the prompt and response to a file for review.
    """
    # Use the sheerwater repo root as cwd
    repo_root = Path(__file__).parents[3]

    result = subprocess.run(
        [
            "claude",
            "-p",
            "--allowedTools",
            "mcp__sheerwater__*",
            "--",
            prompt,
        ],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(repo_root),
    )

    response = result.stdout if result.returncode == 0 else f"ERROR: {result.stderr}"

    # Save to file
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{test_name}.json"
    output_data = {
        "test_name": test_name,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "success": result.returncode == 0,
    }
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=2)

    # Also save markdown version for easy reading
    md_file = OUTPUT_DIR / f"{test_name}.md"
    with open(md_file, "w") as f:
        f.write(f"# {test_name}\n\n")
        f.write(f"**Timestamp:** {output_data['timestamp']}\n\n")
        f.write(f"## Prompt\n\n{prompt}\n\n")
        f.write(f"## Response\n\n{response}\n")

    if result.returncode != 0:
        raise Exception(f"Claude failed: {result.stderr}")

    return response


class TestClaudeCodeIntegration:
    """Integration tests using real Claude Code."""

    def test_list_forecasts(self):
        """Test that Claude can list forecast models via MCP."""
        response = run_claude(
            "List available forecast models using the sheerwater MCP tools",
            "test_list_forecasts",
        )

        assert "ecmwf_ifs_er" in response.lower() or "ecmwf" in response.lower()
        assert "fuxi" in response.lower()
        print(f"\n{response}")

    def test_list_metrics(self):
        """Test that Claude can list metrics via MCP."""
        response = run_claude(
            "List available evaluation metrics using sheerwater",
            "test_list_metrics",
        )

        assert "mae" in response.lower() or "mean absolute error" in response.lower()
        print(f"\n{response}")

    def test_get_metric_info(self):
        """Test that Claude can get metric info via MCP."""
        response = run_claude(
            "Tell me about the MAE metric using sheerwater tools",
            "test_get_metric_info",
        )

        assert "error" in response.lower() or "mae" in response.lower()
        print(f"\n{response}")

    def test_estimate_query_time(self):
        """Test query time estimation."""
        response = run_claude(
            "Using sheerwater, estimate how long it would take to compare ECMWF and FuXi for Kenya precipitation",
            "test_estimate_query_time",
        )

        assert "minute" in response.lower() or "time" in response.lower()
        print(f"\n{response}")

    def test_get_dashboard_link(self):
        """Test dashboard link generation."""
        response = run_claude(
            "Using sheerwater tools, get me a Grafana dashboard link for Kenya precipitation forecasts",
            "test_get_dashboard_link",
        )

        assert "grafana" in response.lower() or "http" in response.lower()
        print(f"\n{response}")

    def test_generate_comparison_chart(self):
        """Test chart generation with real Sheerwater data."""
        response = run_claude(
            "Using sheerwater tools, generate a bar chart comparing ECMWF and FuXi models "
            "on MAE metric for Kenya precipitation. Return the chart.",
            "test_generate_comparison_chart",
            timeout=300,  # Chart generation needs more time
        )

        # Should mention chart/image was generated or show data
        assert (
            "chart" in response.lower()
            or "image" in response.lower()
            or "bar" in response.lower()
            or "mae" in response.lower()
        )
        print(f"\n{response}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
