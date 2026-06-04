#!/usr/bin/env python3
"""
SIS Copywriter Agent — entry point.

Usage:
    python main.py
"""

import os
import sys


def main() -> None:
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
    CopywriterAgent().run()


if __name__ == "__main__":
    main()
