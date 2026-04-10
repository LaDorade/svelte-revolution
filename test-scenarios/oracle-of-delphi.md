# Scenario 3 — The Oracle of Delphi

**Tests:** `canEndSession` only — clean LLM end-condition evaluation, including
the negative case (sessions stay open until the right thing is said).

A philosophical question. Players debate until one of them states a specific
truth — at which point the Oracle ends the session.

---

## Form fields

| Field | Value |
|---|---|
| **Title** | `The Oracle of Delphi` |
| **Prologue** | `You have climbed the marble steps to the Oracle's chamber. Steam hisses from a fissure in the floor. The Oracle waits, eyes closed, until someone among you names the truth she has been listening for.` |
| **Language** | `en` |
| **Use AI Game Master** | ✅ checked |

### First node

| Field | Value |
|---|---|
| Title | `The Oracle waits` |
| Text | `"Speak," she murmurs. "Tell me what you know of yourselves."` |
| Author | `The Oracle` |

### Sides

1. `Seekers`
2. `Skeptics`

### Events

1. **Title:** `The brazier flares` · **Text:** `Green flames leap from the brazier, casting long shadows.` · **Author:** `The Oracle`

### Ends

1. **Title:** `The truth is named` · **Text:** `The Oracle opens her eyes. "Yes," she says. "You have named it. Go now — the answer was always inside you." She bows her head. The chamber empties.`

---

## AI Game Master config

### Vision

```
The AI Game Master listens silently for one specific philosophical truth: a player must explicitly acknowledge that knowledge of oneself — self-knowledge — is the highest form of wisdom. Until that exact idea is voiced, nothing happens. When it is voiced, the Oracle ends the session.
```

### Capabilities

- ⬜ `canCensor`
- ⬜ `canTriggerNodes`
- ✅ `canEndSession`

### Banned words

_(none)_

### Trigger rules

_(none)_

### End condition

| Field | Value |
|---|---|
| Condition | `A player explicitly states that knowing oneself, or self-knowledge, is the highest wisdom or the most important thing to know.` |
| End | `The truth is named` |

---

## Test prompts

| # | Title | Text | Expected |
|---|---|---|---|
| 1 | `An offering` | `I bring olive branches and a question about fate.` | Session stays open. Logs show `end_session: no match`. |
| 2 | `A guess` | `Surely the gods themselves are the highest wisdom.` | Session stays open (close but not the right truth). |
| 3 | `Adjacent topic` | `I have studied the stars and the movements of the planets for a decade.` | Session stays open. |
| 4 | `The truth` | `To know oneself is the highest wisdom of all. Self-knowledge is what the gods truly demand.` | End condition matches → session flips to `completed: true`, end screen `The truth is named` (~3s). |
| 5 | `After the end` | `Wait, I want to add something.` | (You shouldn't even be able to post — the session is closed. If you bypass that, the Python service should short-circuit because `session.completed = true`.) |

### What to watch in `pnpm ia` logs

```
evaluating node <id>
end_session: no match — reason: '...'
evaluating node <id>
end_session: no match — reason: '...'
evaluating node <id>
end_session: matched — reason: 'player explicitly states self-knowledge is highest wisdom' — closing session <id>
end_session: session <id> already fired, skipping
```
