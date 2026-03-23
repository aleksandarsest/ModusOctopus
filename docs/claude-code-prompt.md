# Claude Code Prompt

Use this prompt when you want Claude Code to tighten your scenario framing before you run MiroFish.

```text
I am preparing a simulation brief for MiroFish.

Scenario type:
[pricing change / product launch / policy or org change / reputation or crisis / custom]

Draft brief:
[paste your current brief here]

Source material available:
- [list the documents you have]

I want you to:
1. Identify gaps, ambiguity, or weak assumptions in this brief.
2. Suggest the most important missing inputs that would improve the simulation.
3. Rewrite the brief so it is explicit, business-focused, and ready to paste into MiroFish.

Return the final version in this format:

Scenario:
[text]

Timing:
[text]

Key stakeholders:
[text]

Main question:
[text]

Success or risk to evaluate:
[text]
```

Tips:

- Ask Claude Code to be strict about missing stakeholders and vague wording.
- Keep the final output structured instead of narrative.
