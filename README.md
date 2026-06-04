# SIS — Marketing

AI-powered direct-response copywriter agent.

## Copywriter Agent

Walks through the full oJoy.ai-style workflow:
1. Discovery (5 questions)
2. Strategy (hook, framework, tone, objections)
3. Voice training (optional — paste samples to match your style)
4. Master copy draft
5. All ad formats (Facebook, Instagram, Google, Email, Sales Page, VSL, SMS)

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### Run (CLI)

```bash
python main.py
```

### Run (Claude Code skill)

Inside a Claude Code session, type:

```
/copywriter
```

The agent will walk you through the full workflow interactively.

### Output formats generated

| Format | Details |
|---|---|
| Facebook / Instagram Feed | Primary text + headline + CTA |
| Facebook / Instagram Story | 5-word hook + 3-line body + overlay CTA |
| Google Search Ad | 3 headlines + 2 descriptions (char limits enforced) |
| Email Campaign | Subject + preview text + full body |
| Sales Page Above-the-Fold | Headline + subheadline + opening para + CTA |
| Video Script (VSL / Reel) | Hook → Problem → Solution → Proof → Offer/CTA |
| SMS / Push Notification | Under 160 chars with [LINK] placeholder |
