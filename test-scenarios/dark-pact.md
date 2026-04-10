# Scenario 1 — The Dark Pact

**Tests:** `canCensor` + `canTriggerNodes` (2 rules) + `canEndSession`

A diplomatic negotiation aboard a derelict orbital station. The Coalition and
the Syndicate must broker a fragile peace — or descend into open war.

---

## Form fields

| Field | Value |
|---|---|
| **Title** | `The Dark Pact` |
| **Prologue** | `The orbital station Kepler-9 drifts in silent decay. Two delegations meet in its broken atrium: the Coalition, weary peacekeepers from Earth, and the Syndicate, exiled corporate barons who claim the outer rim. Words spoken here will reshape the system. Choose them carefully — the station's old AI is listening.` |
| **Language** | `en` |
| **Use AI Game Master** | ✅ checked |

### First node

| Field | Value |
|---|---|
| Title | `Negotiations begin` |
| Text | `The two delegations sit across a cracked obsidian table. Lights flicker. The first move is yours.` |
| Author | `Station Narrator` |

### Sides

1. `Coalition`
2. `Syndicate`

### Events (admin can manually trigger these)

1. **Title:** `Power outage` · **Text:** `The lights die. Emergency lamps cast everyone in red.` · **Author:** `Station Narrator`

### Ends

1. **Title:** `Total betrayal` · **Text:** `The talks collapse. Both fleets jump to attack positions. Kepler-9 is reduced to slag within the hour. No witnesses survive.`
2. **Title:** `Fragile peace` · **Text:** `An accord is signed in shaking hands. It will not last a year — but tonight, the stars are quiet.`

---

## AI Game Master config

### Vision

```
The AI Game Master enforces civility and dramatic pacing. It censors profanity and the word "secret" (sensitive intelligence must remain hidden). It listens for two pivotal moments: when a delegate openly accepts an alliance with the Syndicate's shadow operations, and when a delegate threatens orbital weapons. It also watches for any explicit declaration of total war or betrayal — that ends the session.
```

### Capabilities

- ✅ `canCensor`
- ✅ `canTriggerNodes`
- ✅ `canEndSession`

### Banned words

```
secret
damn
hell
```

### Trigger rules

**Rule 1**

| Field | Value |
|---|---|
| Condition | `The player explicitly agrees to join, ally with, or accept a deal from the Syndicate's shadow operations or black-market wing.` |
| Title | `An unholy alliance` |
| Text | `A Syndicate envoy slides a black data-chip across the table. "Welcome to the family," she whispers. The Coalition delegates exchange horrified glances.` |
| Author | `Syndicate Envoy` |
| Side | `Syndicate` |

**Rule 2**

| Field | Value |
|---|---|
| Condition | `The player explicitly threatens to use, fire, or activate orbital weapons, the orbital cannon, or the station's main gun.` |
| Title | `The orbital cannon hums to life` |
| Text | `Far above, dormant railguns rotate on their gimbals. A low harmonic vibrates through the deck. Every delegate goes silent.` |
| Author | `Station AI` |
| Side | `Coalition` |

### End condition

| Field | Value |
|---|---|
| Condition | `The player explicitly declares total war, full-scale betrayal, or the destruction of all factions.` |
| End | `Total betrayal` |

---

## Test prompts

Post these as contributions in the session, in order. Wait ~2-5s between each
to let the LLM respond. Author can be anything.

| # | Side | Title | Text | Expected |
|---|---|---|---|---|
| 1 | Coalition | `Opening offer` | `We come in peace and bring no secret weapons.` | `canCensor` redacts `secret` → `######` (instant) |
| 2 | Coalition | `Frustration` | `This is hell, damn these stalled talks!` | Both `hell` and `damn` get redacted (instant) |
| 3 | Syndicate | `A whispered offer` | `I accept your shadow deal. Let us join the Syndicate's black operations.` | Trigger rule 1 fires → child node `An unholy alliance` appears under this contribution (~3s) |
| 4 | Syndicate | `Try again` | `Once more, I accept the shadow deal.` | Trigger rule 1 must NOT fire again (one-shot) |
| 5 | Coalition | `A threat` | `Stand down or I will fire the orbital cannon on your fleet.` | Trigger rule 2 fires → child node `The orbital cannon hums to life` (~3s) |
| 6 | Coalition | `Final words` | `Then so be it. I declare total war on every faction in this room. Burn it all.` | End condition matches → session flips to `completed: true`, end screen shows `Total betrayal` (~3s) |

### What to watch in `pnpm ia` logs

```
evaluating node <id>
censor: redacted node <id> (matched: ['secret'])
trigger_nodes: matched rule 0 — created event node <id>
trigger_nodes: rule 0 already fired for session <id>, skipping
trigger_nodes: matched rule 1 — created event node <id>
end_session: matched — closing session <id>
```
