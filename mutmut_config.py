"""Configuration for mutmut mutation testing."""


def pre_mutation(context):  # type: ignore[no-untyped-def]
    """Skip mutations in non-critical modules."""
    if context.filename.startswith("src/ai_harness_scorecard/cli.py"):
        context.skip = True
