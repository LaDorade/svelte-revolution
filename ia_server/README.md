# AI Game Master (Python)

FastAPI service that runs the per-scenario `aiConfig` capabilities for Babel Révolution.

It does **not** sit in the request path: it subscribes to the PocketBase `Node`
collection over real-time, evaluates each new contribution, and writes back
(censored text, AI-authored event nodes, session endings) using a dedicated
`ai-gamemaster` PocketBase user.

## Capabilities

Driven by `Scenario.aiConfig` (JSON, validated by `src/lib/zschemas/aiConfig.schema.ts`):

| Capability        | Engine             | Effect                                                          |
| ----------------- | ------------------ | --------------------------------------------------------------- |
| `canCensor`       | Rules (regex)      | Replaces banned words in node `title`/`text` with `####`        |
| `canTriggerNodes` | Mistral LLM (JSON) | Creates a pre-written `event`-type node when a condition matches |
| `canEndSession`   | Mistral LLM (JSON) | Sets `Session.completed = true` and `Session.end = <End.id>`    |

Trigger rules and the end condition fire **at most once per session**.

## Local development

Requires Python 3.12+ and either `uv` or plain `pip`/`venv`.

```sh
# from repo root
pnpm ia                                # uses uv
# or:
cd ia_server
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Required environment variables

| Variable          | Purpose                                                  |
| ----------------- | -------------------------------------------------------- |
| `DB_URL`          | PocketBase URL (e.g. `http://localhost:8090`)            |
| `PB_BOT_EMAIL`    | Email of the `ai-gamemaster` PocketBase user             |
| `PB_BOT_PASSWORD` | Password of the same user                                |
| `MISTRAL_API_KEY` | Mistral API key (also used by SvelteKit `analyzeVision`) |
| `MISTRAL_MODEL`   | Optional, defaults to `mistral-small-latest`             |

## PocketBase setup (one-off)

The bot needs `superAdmin` role because the `Node` collection's `updateRule`
restricts updates to superadmins (needed for censoring existing nodes).

1. Open `http://localhost:8090/_/`
2. In `Users`, create a user `ai-gamemaster@babel-revolution.local` with role `superAdmin`
3. Put the credentials in `.env.local`

## Tests

```sh
cd ia_server
uv run pytest
```
