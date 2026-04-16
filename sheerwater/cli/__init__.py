"""Top-level Sheerwater CLI.

Exposes sheerwater's data, forecast, ops, eval, and list verbs as a kubectl-style
click group. Skills in `sheerwater/skills/` document the per-verb invocations the
agent should use.

Cache management is provided by the `nuthatch` CLI directly; sheerwater does not
re-export it here.
"""
import click

from . import data, eval, forecast, list_, ops


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """Sheerwater: weather data, forecasts, ops, and benchmarking.

    Authentication: public datasets work anonymously against sheerwater's
    public GCS bucket. Private datasets require GCS credentials via
    GOOGLE_APPLICATION_CREDENTIALS or `gcloud auth application-default login`.

    Cache management uses the `nuthatch` CLI directly (sheerwater's caches are
    backed by nuthatch).
    """


cli.add_command(data.data, name="data")
cli.add_command(forecast.forecast, name="forecast")
cli.add_command(ops.ops, name="ops")
cli.add_command(eval.eval_, name="eval")
cli.add_command(list_.list_, name="list")


def main():
    """Entry point for the `sheerwater` console script."""
    cli()


if __name__ == "__main__":
    main()
