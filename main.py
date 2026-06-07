#!/usr/bin/env python3
"""
SIS Copywriter Agent — entry point.

Usage:
    python main.py                          # Start a fresh session
    python main.py --resume session.json    # Resume a saved session
    python main.py --formats session.json   # Regenerate formats from saved session
"""

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Direct-response AI copywriter agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--resume",
        metavar="SESSION_FILE",
        help="Resume from a saved session JSON file",
    )
    parser.add_argument(
        "--formats",
        metavar="SESSION_FILE",
        help="Regenerate all ad formats from a saved session (skips discovery/draft)",
    )
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "\nError: ANTHROPIC_API_KEY is not set.\n"
            "Copy .env.example to .env and add your Anthropic API key.\n"
            "Get one at: https://console.anthropic.com/\n"
        )
        sys.exit(1)

    from copywriter import CopywriterAgent
    agent = CopywriterAgent()

    if args.formats:
        agent.run(resume_from=args.formats, formats_only=True)
    elif args.resume:
        agent.run(resume_from=args.resume)
    else:
        agent.run()


if __name__ == "__main__":
    main()
