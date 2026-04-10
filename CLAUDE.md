# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
pnpm dev              # Start SvelteKit dev server
pnpm build            # Production build
pnpm preview          # Preview production build locally
pnpm start:remote     # Run production server with remote config
pnpm check            # TypeScript + Svelte type checking
pnpm check:watch      # Continuous type checking
pnpm lint             # ESLint validation
pnpm lint:fix         # Auto-fix ESLint issues
pnpm test:unit        # Run Vitest unit tests
pnpm ia               # Launch Python AI Game Master (FastAPI in ia_server/)
```

## Local Development Setup

1. Install dependencies: `pnpm install`
2. Create `.env.local` at project root:
   ```env
   PUBLIC_DB_URL=http://localhost:8090
   DB_URL=http://localhost:8090
   # AI Game Master (only needed if running pnpm ia)
   PB_BOT_EMAIL=ai-gamemaster@babel-revolution.local
   PB_BOT_PASSWORD=<the password you set in PocketBase>
   MISTRAL_API_KEY=<your Mistral key>
   ```
3. Start PocketBase: `docker compose up pocketbase`
4. Import DB schema: go to `http://localhost:8090/_/` → Settings → Import collections → paste `db/schema.json`
5. Create the AI bot user (only if you want to run the AI Game Master):
   in `http://localhost:8090/_/`, create a user `ai-gamemaster@babel-revolution.local`
   in the `Users` collection with role `superAdmin` (required so the bot can update
   existing nodes for censoring).
6. Start frontend: `pnpm dev`
7. (Optional) Start AI Game Master: `pnpm ia` (requires Python 3.12+)

## Architecture

This is a collaborative storytelling platform ("Babel Révolution") with three services:

- **SvelteKit frontend/backend** (`src/`) — handles UI and API routes
- **PocketBase** (`db/`) — self-hosted database + auto-generated REST API + auth + real-time subscriptions
- **Python AI Game Master** (`ia_server/`) — FastAPI service that polls the `Node`
  collection and runs each scenario's `aiConfig` capabilities (`canCensor`,
  `canTriggerNodes`, `canEndSession`) using rules + Mistral. It is **not** in the
  request path; it writes back to PocketBase as a dedicated `ai-gamemaster` user.

All three are orchestrated via `docker-compose.yml` for production.

### Data Flow

1. Frontend calls PocketBase REST API directly for CRUD (users, scenarios, sessions, nodes)
2. The `addNode` action persists contributions straight to PocketBase — no AI in the request path.
3. The Python AI Game Master observes the `Node` collection and writes back asynchronously.
4. The only synchronous AI call from the frontend is `POST /api/ai/analyzeVision`,
   which forwards to Mistral during scenario creation to suggest capabilities from a vision text.

### PocketBase Collections (defined in `db/schema.json`)

Core types in `src/types/TableType.d.ts`:
- **Scenario** — narrative scenario with prologue, language, first node
- **Session** — active session linked to a scenario (has slug, visibility, audio flag)
- **Node** — story graph node (type: `contribution` | `event` | `startNode`)
- **End**, **Event**, **Side** — supporting narrative structures
- **Users** — auth collection

### Frontend Structure

- `src/routes/` — SvelteKit routes; `(auth)/` and `(home)/` are route groups
- `src/components/` — UI components (form inputs, graph visualization, nav)
- `src/stores/` — Svelte runes-based state (session, graph, ui, admin)
- `src/lib/` — utilities: `pocketbase.ts` (client init), `sessions.ts` (session CRUD), `i18n.ts`, `taskProgress.ts`
- `src/types/` — TypeScript type definitions
- `src/lang/` — i18n translation files (fr, en, jp, es)

### Key Technical Details

- **Svelte 5** with runes (`$state`, `$derived`, etc.) — not legacy Svelte 4 reactivity
- **Tailwind CSS 4** for styling — use utility classes directly in markup
- **svelte-i18n** for internationalization — primary language is French
- ESLint is configured for **tabs** and **single quotes**
- Path alias `$lib` maps to `src/lib/`
