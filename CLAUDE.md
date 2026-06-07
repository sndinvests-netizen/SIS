# SIS — Marketing

Direct-response AI copywriter agent for generating high-converting ad copy
across all major formats.

## What This Project Does

Runs a structured 4-phase copywriting workflow modeled on the oJoy.ai
methodology (Frank Kern / Anthropic-based direct-response AI):

1. **Discovery** — 5-question interview to extract product, audience,
   transformation, differentiator, and desired action
2. **Strategy** — Defines hook, framework (AIDA / PAS / Hook-Story-Offer),
   tone, and top objections before any copy is written
3. **Voice training** — Optional: user pastes writing samples; agent adapts
   style to match
4. **Master copy + All ad formats** — Drafts master copy, then outputs 7
   platform-specific formats in one pass

## Tech Stack

- **Language**: Python 3.11+
- **AI**: Anthropic SDK (`anthropic` package) — uses `claude-opus-4-8`
- **Prompt caching**: Enabled on all system prompts via `cache_control`
- **Config**: `.env` file for `ANTHROPIC_API_KEY`

## Key Files

| File | Purpose |
|---|---|
| `main.py` | CLI entry point — `python main.py` |
| `copywriter/agent.py` | Core agent: phases, session save/load, API calls |
| `copywriter/prompts.py` | System prompts for each phase |
| `copywriter/formats.py` | Ad format specs (name + character constraints) |
| `.claude/commands/copywriter.md` | `/copywriter` skill for Claude Code sessions |

## How to Run

```bash
pip install -r requirements.txt
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

python main.py                         # Fresh session
python main.py --resume session.json   # Resume saved session
python main.py --formats session.json  # Regenerate formats only
```

Or inside a Claude Code session:
```
/copywriter
```

## Output Formats Generated

- Facebook / Instagram Feed Ad
- Facebook / Instagram Story Ad
- Google Search Ad (char limits enforced)
- Email (subject + preview + full body)
- Sales Page above-the-fold
- Video Script / VSL / Reel
- SMS / Push Notification

## Sessions

Sessions save to `session_YYYYMMDD_HHMMSS.json` — contains discovery
answers, strategy, and master copy. Final copy output saves to
`copy_output_YYYYMMDD_HHMMSS.md`.

Both file types are gitignored.

## Adding New Ad Formats

Edit `copywriter/formats.py` — add a dict with `name` and `spec` to the
`AD_FORMATS` list. The agent picks them up automatically.

## Changing the AI Model

Pass a different model name to `CopywriterAgent(model="...")` in `main.py`,
or change the default in `agent.py`. Requires an Anthropic-supported model.
