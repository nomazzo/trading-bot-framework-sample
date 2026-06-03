from pathlib import Path
import contextlib
import io
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_bot_framework.cli import run_demo
from trading_bot_framework.config import BotConfig


class CliTests(unittest.TestCase):
    def test_demo_runs_offline(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result = run_demo(BotConfig(symbol="BTCUSD"), ticks=4)
        self.assertIn("position", result)
        self.assertIn("orders", result)


if __name__ == "__main__":
    unittest.main()
