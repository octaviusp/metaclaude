from typer.testing import CliRunner
from metaclaude.cli import app

runner = CliRunner()

def test_app():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage: metaclaude [OPTIONS] COMMAND [ARGS]" in result.stdout