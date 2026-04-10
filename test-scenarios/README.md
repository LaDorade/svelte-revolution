# AI Game Master test scenarios

Mock scenarios to exercise the Python AI Game Master (`canCensor`,
`canTriggerNodes`, `canEndSession`).

## Two ways to load a scenario

### Option A — fastest: localStorage seed (recommended)

The scenario create form auto-restores from `localStorage.scenario` on every
mount. Each scenario in this directory ships with a `*.localStorage.json` file
that mirrors the form state exactly.

1. Open `http://localhost:5173/admin/scenario/create` once (needed so the
   localStorage origin exists).
2. Open DevTools → Console and paste:
   ```js
   localStorage.setItem('scenario', JSON.stringify(/* paste the JSON contents here */))
   ```
3. Refresh the page. Every field — including AI capabilities, banned words,
   trigger rules and the end condition — is now populated.
4. Submit the form.

### Option B — manual copy-paste

Each `*.md` file lists every field in the order they appear in the form. Just
copy each value into the matching input.

## After creation

1. From the scenario page, **create a session** for the scenario.
2. Open `/sessions/<slug>` in a normal (non-admin) browser tab.
3. Use the test prompts at the bottom of each scenario file.
4. Watch `pnpm ia` logs in parallel — every evaluation, censor, trigger and end
   decision is logged there.

## Scenarios

| File | What it tests |
|---|---|
| `dark-pact.md` / `dark-pact.localStorage.json` | All three capabilities together (censor + 2 triggers + end) |
| `word-warden.md` / `word-warden.localStorage.json` | `canCensor` only — banned words with edge cases (case, accents, word boundaries) |
| `oracle-of-delphi.md` / `oracle-of-delphi.localStorage.json` | `canEndSession` only — clean end-condition LLM evaluation |
