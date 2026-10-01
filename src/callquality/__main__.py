import argparse
from pathlib import Path

from callquality.analyze import report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="callquality", description="Score a sample SIP/RTP call")
    parser.add_argument("rtp", help="RTP stats CSV")
    parser.add_argument("sip", help="SIP text trace")
    args = parser.parse_args(argv)
    print(
        report(
            Path(args.rtp).read_text(encoding="utf-8"),
            Path(args.sip).read_text(encoding="utf-8"),
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
