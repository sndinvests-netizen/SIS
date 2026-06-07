"""
Standalone copywriter agent using the Anthropic SDK.
Mirrors the oJoy.ai workflow: Discovery → Strategy → Voice → Draft → Formats

Uses prompt caching on system prompts to reduce API costs on long sessions.
"""

import os
import json
import textwrap
from datetime import datetime
import anthropic

from .prompts import SYSTEM_PROMPT, STRATEGY_PROMPT, FORMAT_PROMPT
from .formats import AD_FORMATS


DISCOVERY_QUESTIONS = [
    (
        "product",
        "What is your product or service, and what does it actually DO for the "
        "customer? Describe it like you're explaining it to a close friend.",
    ),
    (
        "audience",
        "Who is your ideal customer? What keeps them up at night? What's the "
        "biggest frustration that your product solves?",
    ),
    (
        "transformation",
        "What is the #1 result or transformation your customer gets after buying "
        "or using your product? Be as specific as possible — numbers, timeframes, outcomes.",
    ),
    (
        "differentiator",
        "Why should someone choose YOU over every other option — including doing "
        "nothing? What makes your offer different or better?",
    ),
    (
        "cta",
        "What is the ONE action you want the reader to take right now? "
        "(e.g., click to buy, sign up for a free trial, book a call)",
    ),
]


def _hr(char: str = "=", width: int = 60) -> str:
    return char * width


def _wrap(text: str, width: int = 70) -> str:
    return "\n".join(
        textwrap.fill(line, width) if line.strip() else line
        for line in text.splitlines()
    )


def _cached_system(prompt: str) -> list[dict]:
    """Wrap a system prompt string for prompt caching."""
    return [{"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]


class CopywriterAgent:
    def __init__(self, model: str = "claude-opus-4-8"):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set.\n"
                "Copy .env.example to .env and add your key.\n"
                "Get one at: https://console.anthropic.com/"
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.discovery: dict[str, str] = {}
        self.strategy: str = ""
        self.master_copy: str = ""
        self._strategy_history: list[dict] = []
        self._draft_history: list[dict] = []
        self._format_history: list[dict] = []

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _call(
        self,
        history: list[dict],
        user_message: str,
        system: str,
        max_tokens: int = 4096,
    ) -> str:
        history.append({"role": "user", "content": user_message})
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=_cached_system(system),
            messages=history,
        )
        reply = response.content[0].text
        history.append({"role": "assistant", "content": reply})
        return reply

    # ------------------------------------------------------------------ #
    # Session save / load
    # ------------------------------------------------------------------ #

    def save_session(self) -> str:
        """Save current progress to a JSON file so it can be resumed later."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.json"
        state = {
            "saved_at": datetime.now().isoformat(),
            "discovery": self.discovery,
            "strategy": self.strategy,
            "master_copy": self.master_copy,
        }
        with open(filename, "w") as f:
            json.dump(state, f, indent=2)
        print(f"\nSession saved to: {filename}")
        return filename

    def load_session(self, filename: str) -> None:
        """Restore a previously saved session."""
        with open(filename) as f:
            state = json.load(f)
        self.discovery = state.get("discovery", {})
        self.strategy = state.get("strategy", "")
        self.master_copy = state.get("master_copy", "")
        saved_at = state.get("saved_at", "unknown")
        print(f"\nSession restored from: {filename} (saved {saved_at})")

    # ------------------------------------------------------------------ #
    # Phase 1 — Discovery
    # ------------------------------------------------------------------ #

    def run_discovery(self) -> dict[str, str]:
        print(f"\n{_hr()}")
        print("PHASE 1: DISCOVERY")
        print(_hr())
        print(
            "\nI'm going to ask you 5 questions before writing a single word.\n"
            "Your answers are the raw material for great copy.\n"
        )

        for key, question in DISCOVERY_QUESTIONS:
            print(f"\n{_wrap(question)}")
            answer = input("> ").strip()
            while not answer:
                print("(Please provide an answer to continue)")
                answer = input("> ").strip()
            self.discovery[key] = answer

        return self.discovery

    # ------------------------------------------------------------------ #
    # Phase 2 — Strategy
    # ------------------------------------------------------------------ #

    def run_strategy(self) -> str:
        print(f"\n{_hr()}")
        print("PHASE 2: STRATEGY")
        print(_hr())

        discovery_block = "\n".join(
            f"{k.upper()}: {v}" for k, v in self.discovery.items()
        )

        prompt = (
            f"Here is everything I know about this offer:\n\n{discovery_block}\n\n"
            "Before writing any copy, define the strategy clearly:\n"
            "1. The single most emotionally compelling HOOK angle\n"
            "2. The best framework (AIDA, PAS, or Hook-Story-Offer) and why\n"
            "3. The TONE (urgent / conversational / authoritative / inspirational)\n"
            "4. The #1 benefit to lead with\n"
            "5. The top 2 objections to address in the copy\n\n"
            "Present this strategy, then ask if I want to adjust anything."
        )

        strategy = self._call(self._strategy_history, prompt, STRATEGY_PROMPT)
        print(f"\n{_wrap(strategy)}\n")

        feedback = input(
            "Feedback on the strategy (or press Enter to proceed): "
        ).strip()
        if feedback:
            refined = self._call(
                self._strategy_history,
                f"Adjust the strategy based on this feedback: {feedback}",
                STRATEGY_PROMPT,
            )
            print(f"\n{_wrap(refined)}\n")
            self.strategy = refined
        else:
            self.strategy = strategy

        return self.strategy

    # ------------------------------------------------------------------ #
    # Phase 3 — Voice training (optional)
    # ------------------------------------------------------------------ #

    def get_voice_samples(self) -> str | None:
        print(f"\n{_hr('-')}")
        print("VOICE TRAINING (Optional)")
        print(_hr("-"))
        print(
            "\nDo you want the copy to match a specific writing style or voice?\n"
            "If yes, paste 2-5 paragraphs of writing you like (your own or\n"
            "someone else's). Press Enter twice when done, or just press Enter\n"
            "now to skip.\n"
        )
        lines: list[str] = []
        while True:
            line = input()
            if line == "" and (not lines or lines[-1] == ""):
                break
            lines.append(line)

        samples = "\n".join(lines).strip()
        return samples if samples else None

    # ------------------------------------------------------------------ #
    # Phase 4 — Master copy draft
    # ------------------------------------------------------------------ #

    def run_draft(self, voice_samples: str | None = None) -> str:
        print(f"\n{_hr()}")
        print("PHASE 3: DRAFTING MASTER COPY")
        print(_hr())
        print("Writing your master copy...\n")

        self._draft_history.append(
            {"role": "assistant", "content": self.strategy}
        )

        instruction = (
            "Now write the master copy based on the strategy above.\n\n"
            "This is the complete message — written as if speaking directly to ONE\n"
            "specific person who has the exact problem your product solves.\n\n"
            "Rules:\n"
            "- No bullet-point lists of features\n"
            "- Lead with the hook immediately — no warm-up sentences\n"
            "- Build desire with specificity: numbers, results, time frames\n"
            "- Handle the top 2 objections naturally within the flow\n"
            "- Close with a single, unmistakable call to action\n"
            "- Write with rhythm — vary sentence length intentionally"
        )

        if voice_samples:
            instruction += (
                f"\n\nAdapt the writing to match this voice and style:\n\n{voice_samples}"
            )

        master = self._call(
            self._draft_history, instruction, SYSTEM_PROMPT, max_tokens=8096
        )
        print(_wrap(master))
        self.master_copy = master
        return master

    # ------------------------------------------------------------------ #
    # Phase 5 — All ad formats
    # ------------------------------------------------------------------ #

    def run_formats(self) -> str:
        print(f"\n{_hr()}")
        print("PHASE 4: GENERATING ALL AD FORMATS")
        print(_hr())
        print(
            "Generating Facebook, Instagram, Google, Email, Sales Page,\n"
            "VSL Script, and SMS formats...\n"
        )

        format_specs = "\n\n".join(
            f"### {fmt['name']}\n{fmt['spec']}" for fmt in AD_FORMATS
        )

        prompt = (
            f"Using this master copy as your source material:\n\n"
            f"{self.master_copy}\n\n"
            f"Generate ALL of the following ad formats. Label each section "
            f"clearly with its format name.\n\n"
            f"{format_specs}"
        )

        output = self._call(
            self._format_history, prompt, FORMAT_PROMPT, max_tokens=8096
        )
        print(output)
        return output

    # ------------------------------------------------------------------ #
    # Save final output
    # ------------------------------------------------------------------ #

    def save_output(self, formats_output: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"copy_output_{timestamp}.md"

        lines = [
            "# Generated Copy\n",
            f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n",
            "## Discovery Answers\n",
        ]
        for k, v in self.discovery.items():
            lines.append(f"**{k.capitalize()}**: {v}\n")

        lines += [
            "\n## Strategy\n",
            self.strategy,
            "\n## Master Copy\n",
            self.master_copy,
            "\n## All Ad Formats\n",
            formats_output,
        ]

        with open(filename, "w") as f:
            f.write("\n".join(lines))

        print(f"\nAll copy saved to: {filename}")
        return filename

    # ------------------------------------------------------------------ #
    # Main run loop
    # ------------------------------------------------------------------ #

    def run(self, resume_from: str | None = None, formats_only: bool = False) -> None:
        print(f"\n{_hr()}")
        print("  COPYWRITER AGENT — Direct Response AI")
        print("  Powered by Anthropic Claude")
        print(_hr())

        if resume_from:
            self.load_session(resume_from)
            if formats_only:
                # Skip straight to format generation
                formats_output = self.run_formats()
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == "y":
                    self.save_output(formats_output)
                return

            # Resume from whichever phase has missing data
            if not self.discovery:
                self.run_discovery()
            if not self.strategy:
                self.run_strategy()
            voice = self.get_voice_samples()
            if not self.master_copy:
                self.run_draft(voice)
        else:
            print(
                "\nThis agent will interview you, define a strategy, write master\n"
                "copy, then generate every ad format you need.\n"
            )
            self.run_discovery()
            self.run_strategy()
            voice = self.get_voice_samples()
            self.run_draft(voice)

        # Offer mid-run session save before the expensive formats call
        checkpoint = input(
            "\nSave session checkpoint before generating formats? (y/n): "
        ).strip().lower()
        if checkpoint == "y":
            self.save_session()

        formats_output = self.run_formats()

        save = input("\nSave all copy to a markdown file? (y/n): ").strip().lower()
        if save == "y":
            self.save_output(formats_output)

        print(f"\n{_hr()}")
        print("Done. Your copy is ready.")
        print(_hr())
