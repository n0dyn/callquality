import unittest
from pathlib import Path

from callquality.analyze import analyze_rtp, parse_sip, report
from callquality.__main__ import main

ROOT = Path(__file__).resolve().parents[1]
RTP = (ROOT / "fixtures" / "rtp.csv").read_text(encoding="utf-8")
SIP = (ROOT / "fixtures" / "sip.txt").read_text(encoding="utf-8")


class CallQualityTests(unittest.TestCase):
    def test_loss_and_jitter_from_sample(self):
        result = analyze_rtp(RTP)
        self.assertEqual(result.expected, 6)
        self.assertEqual(result.received, 5)
        self.assertEqual(result.loss_pct, 16.67)
        self.assertGreater(result.jitter_ms, 0)
        self.assertGreaterEqual(result.mos, 1)
        self.assertLessEqual(result.mos, 4.5)

    def test_ladder_contains_invite_and_bye(self):
        text = report(RTP, SIP)
        self.assertIn("INVITE", text)
        self.assertIn("BYE", text)
        self.assertEqual([event.message.split()[0] for event in parse_sip(SIP)][0], "INVITE")

    def test_cli_exits_clean(self):
        code = main([str(ROOT / "fixtures" / "rtp.csv"), str(ROOT / "fixtures" / "sip.txt")])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
