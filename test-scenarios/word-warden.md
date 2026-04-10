# Scenario 2 — The Word Warden

**Tests:** `canCensor` only — banned-word edge cases (case, accents, word
boundaries, multiple matches per node).

A minimal scenario whose only job is to validate the rule-based censor. No LLM
calls, instant feedback (~1 poll cycle = 2s).

---

## Form fields

| Field | Value |
|---|---|
| **Title** | `The Word Warden` |
| **Prologue** | `In the silent monastery of Saint Lexicon, every word spoken aloud is weighed by the Warden. Forbidden syllables are erased from the parchment before they can echo.` |
| **Language** | `en` |
| **Use AI Game Master** | ✅ checked |

### First node

| Field | Value |
|---|---|
| Title | `Speak, novice` |
| Text | `The Warden waits. Place your first word upon the parchment.` |
| Author | `The Warden` |

### Sides

1. `Novices`
2. `Elders`

### Events

1. **Title:** `Bell tolls` · **Text:** `The cloister bell rings once.` · **Author:** `The Warden`

### Ends

1. **Title:** `Vow of silence` · **Text:** `The novice has spoken the unspeakable too many times. The monastery imposes eternal silence.`

---

## AI Game Master config

### Vision

```
The AI Game Master only censors. It removes a list of forbidden words and their accented variants from any contribution before they corrupt the parchment. It does not trigger any narrative events and never ends the session.
```

### Capabilities

- ✅ `canCensor`
- ⬜ `canTriggerNodes`
- ⬜ `canEndSession`

### Banned words

```
forbidden
heresy
blasphème
schism
```

(`blasphème` includes a French accent — tests Unicode normalization.)

### Trigger rules

_(none — leave empty)_

### End condition

_(none — leave empty)_

---

## Test prompts

| # | Title | Text | Expected |
|---|---|---|---|
| 1 | `Lowercase` | `This forbidden truth must not be spoken.` | `forbidden` → `#########` |
| 2 | `Mixed case` | `That is HERESY of the highest order.` | `HERESY` → `######` |
| 3 | `Accented` | `Quel blasphème! Un véritable scandale.` | `blasphème` → `#########` |
| 4 | `Multiple in one` | `A heresy and a schism — pure forbidden doctrine!` | three words redacted in the same node |
| 5 | `Substring guard` | `He was forbiddenly clever.` | NOTHING redacted (`forbiddenly` is not the word `forbidden` — word boundaries) |
| 6 | `Clean message` | `All is well and the parchment is pure.` | NOTHING redacted, no PB write |

### What to watch in `pnpm ia` logs

```
evaluating node <id>
censor: redacted node <id> (matched: ['forbidden'])
censor: redacted node <id> (matched: ['heresy'])
censor: redacted node <id> (matched: ['blasphème'])
censor: redacted node <id> (matched: ['heresy', 'schism', 'forbidden'])
evaluating node <id>   # prompts 5 and 6 — no censor line follows
```

If prompt 5 redacts anything, the regex word-boundary logic in
`ia_server/app/capabilities/censor.py` is broken.
