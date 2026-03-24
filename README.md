<div align="center">

<img src="./static/image/modusoctopus-banner.svg" alt="ModusOctopus Logo" width="75%"/>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/ModusOctopus?style=flat-square&color=DAA520)](https://github.com/666ghj/ModusOctopus/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/ModusOctopus?style=flat-square)](https://github.com/666ghj/ModusOctopus/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/ModusOctopus?style=flat-square)](https://github.com/666ghj/ModusOctopus/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/ModusOctopus)

[![Discord](https://img.shields.io/badge/Discord-Join-5865F2?style=flat-square&logo=discord&logoColor=white)](http://discord.gg/ePf5aPaHnA)
[![X](https://img.shields.io/badge/X-Follow-000000?style=flat-square&logo=x&logoColor=white)](https://x.com/modusoctopus_ai)
[![Instagram](https://img.shields.io/badge/Instagram-Follow-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/modusoctopus_ai/)

[English](./README.md) | [Legacy English README](./README-EN.md)

</div>

# ModusOctopus

Open-source multi-agent simulation for testing business decisions before you make them.

> Fork/rebrand note: ModusOctopus is a rebranded fork of the original upstream codebase and remains distributed under `AGPL-3.0`. Keep the original license and attribution notices intact when redistributing modified versions.

ModusOctopus turns source material such as internal memos, policy drafts, customer research, press statements, meeting notes, and market context into:

- a scenario graph built from your documents
- a simulated multi-agent environment running on social platforms
- a report you can use to reason about likely reactions, risks, and next moves

The current product is best understood as a decision-simulation workflow:

1. Upload source documents
2. Describe the scenario you want to test
3. Build a graph of actors, relationships, and context
4. Prepare agent profiles and simulation settings
5. Run the simulation
6. Generate a report and inspect the result

## What ModusOctopus Is Good For

ModusOctopus is a good fit when you want to pressure-test a scenario before it goes live.

Examples:

- pricing changes
- product launches
- internal policy or org changes
- reputation or crisis scenarios
- public communications with multiple stakeholder groups

Typical inputs:

- internal memo or strategy draft
- customer feedback exports
- stakeholder notes
- press release draft
- regulatory or policy text
- research summary or briefing document

Typical outputs:

- likely stakeholder reactions
- dominant narratives
- escalation or backlash risks
- secondary effects worth monitoring
- a report you can use for planning or communication

## How It Works

ModusOctopus combines several layers:

- `LLM layer`: generates the ontology, agent profiles, simulation config, and report text
- `Zep layer`: stores graph memory, entities, edges, and retrieval context
- `OASIS layer`: runs the agent simulation on Twitter- and Reddit-style environments
- `Vue + Flask app`: provides the workflow UI and orchestration API

The current flow in the codebase is:

1. Upload `PDF`, `MD`, or `TXT` files and provide a simulation brief
2. Generate an ontology from the uploaded material
3. Build a graph in Zep from the extracted text
4. Read graph entities and generate agent profiles
5. Generate simulation parameters
6. Run the simulation
7. Generate a report and interact with the simulated world

## Run Locally

### Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Python | 3.11 - 3.12 |
| uv | latest |

### 1. Configure environment variables

```bash
cp .env.example .env
```

Required variables:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

ZEP_API_KEY=your_zep_api_key
```

Notes:

- Any OpenAI-compatible API should work if it supports the required chat-completions flow.
- The project currently recommends `qwen-plus` as a practical default.
- Simulation cost depends heavily on your selected model, number of entities, and number of rounds.

### 2. Install dependencies

```bash
npm run setup:all
```

Or install in parts:

```bash
npm run setup
npm run setup:backend
```

### 3. Start the app

```bash
npm run dev
```

Default local URLs:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

Run services individually:

```bash
npm run backend
npm run frontend
```

## Optional: Use With Codex Or Claude Code

ModusOctopus does not require Codex or Claude Code.

They are useful as optional helpers for:

- turning rough notes into a strong simulation brief
- identifying missing documents before you run a scenario
- interpreting the final report and deciding what to do next

Suggested workflow:

1. Collect your source documents
2. Draft a rough scenario question
3. Use Codex or Claude Code to refine the brief
4. Paste the final brief into ModusOctopus
5. Run the simulation
6. Use the resulting report for follow-up analysis

Prompt templates live in:

- [`docs/codex-prompt.md`](./docs/codex-prompt.md)
- [`docs/claude-code-prompt.md`](./docs/claude-code-prompt.md)

## Docker

```bash
cp .env.example .env
docker compose up -d
```

The compose file maps:

- `3000` for the frontend
- `5001` for the backend

## Current V1 Scope

The current English-first OSS v1 is focused on:

- clear GitHub positioning
- an understandable onboarding flow
- happy-path English UI copy
- optional Codex / Claude Code helper guidance

It does not yet fully translate every backend response, edge-case message, or internal system log.

## Acknowledgements

ModusOctopus is strategically supported by Shanda Group.

The simulation engine is powered by [OASIS](https://github.com/camel-ai/oasis). We appreciate the CAMEL-AI team's open-source work.
