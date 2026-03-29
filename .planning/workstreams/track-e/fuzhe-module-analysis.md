# Fuzhe (覆辙) Module Analysis

## Overview
- **Slug**: `fuzhe`
- **Title**: 覆辙 (Fuzhe)
- **Premise**: A car crash, a forum, and a group of magical girls and investigators are pulled into the truth by the same abnormal trajectory.
- **Starting Scene**: `car_crash_scene`
- **Starting Location**: `car_crash_intersection`
- **Starting Story Node**: `investigator_intro`

## File List
- `src/dm_bot/adventures/fuzhe.json`: Main module definition (rooms, scenes, triggers, endings).
- `src/dm_bot/adventures/trigger_engine.py`: Logic for processing triggers and effects.
- `src/dm_bot/adventures/models.py`: Data models for adventures.

## Rooms, Scenes, and Events

| ID | Title | Type | Description |
|---|---|---|---|
| `car_crash_intersection` | 车祸路口 | Location | Entry point for investigators. Gasoline and blood smell. |
| `mystery_forum` | 神秘论坛 | Location | Urban legend forum with magical girl photos and X-Company clues. |
| `wetland_gate` | 湿地公园入口 | Location | Quiet park where the first major combat encounter occurs. |
| `convenience_store` | 便利店 | Location | Routine scene for supplies and encountering Blood Angel. |
| `restaurant` | 梅华饭店 | Location | Social scene for rest and Blood Angel interaction. |
| `cultural_street` | 文化街 | Location | Flavor scene with stalls and mini-games. |
| `xinhai_school` | 新海中学 | Location | Concert venue where truth about "Spring Shock" is revealed. |
| `chemical_factory` | 信材化工厂 | Location | Investigation site for X-Potion production and company secrets. |
| `x_company` | X公司总部 | Location | Final dungeon, an extradimensional space. |

## Triggers and Conditions

| Trigger ID | Event Kind | Condition | Key Effects |
|---|---|---|---|
| `fuzhe_inspect_crash` | action | `inspect_crash` | Move to `forum_investigation`, set `car_crash_witnessed=true`, SAN +1. |
| `forum_search_success` | roll | `LibraryUse` >= 10 | Set `forum_researched=true`, stage to `wetland`. |
| `wetland_listen_success`| roll | `Listen` >= 10 | Move to `wetland_ambush`, stage to `battle`. |
| `spring_shock_defeated`| action | `spring_shock_battle` | Set `spring_shock_defeated=true`, add clue. |
| `blood_angel_joins` | action | `blood_angel_encounter`| Set `blood_angel_joined=true`, increment `magical_girl_count`. |
| `school_concert_visit` | action | `watch_concert` | Stage to `concert`. |
| `chemical_factory_search`| action | `search_reactor` | Stage to `factory`. |
| `x_company_enter` | action | `sritika_encounter` | Stage to `final`, SAN +1 (SC 1/1d3). |
| `sritika_killed` | action | `final_battle` | Set `sritika_killed=true`. |

## Reveal Policies and Gates

- **Investigator Intro**: Witnessing the girl reveals "Magical girls exist".
- **Forum**: Researching reveals "X-Company exists".
- **Wetland**: Combat reveals "Spring Shock is a former magical girl" and "Magical girls turn into monsters".
- **School**: Concert reveals "The magical girl dream is a lie".
- **Factory**: Investigation reveals "X-Potion causes monster transformation".
- **X-Company**: Final encounter reveals "Magical girls are stepping stones for executives".

## Consequence Chains (Action → Trigger → Effect → State Change)

1. **Investigation Start**: `inspect_crash` → `fuzhe_inspect_crash` → Move Story Node (`forum_investigation`) + State Change (`car_crash_witnessed: true`).
2. **Combat Escalation**: `wetland_listen_check` (Roll) → `wetland_listen_success/fail` → Move Story Node (`wetland_ambush`) + Stage Change (`battle`).
3. **Recruitment**: `blood_angel_encounter` → `blood_angel_joins` → State Change (`blood_angel_joined: true`, `magical_girl_count: +1`).
4. **Final Stage**: `sritika_encounter` → `x_company_enter` → State Change (`x_company_visited: true`, `current_investigation_stage: final`).

## Endings and Requirements

| Ending ID | Title | How to Reach |
|---|---|---|
| `nothing_happens` | 无事发生 | Abandon investigation early. |
| `dream_broken` | 梦破 | All investigators/magical girls fall in battle. |
| `fuzhe` | 覆辙 | Defeat Sritika and leave X-Company. |

## Entry/Exit Conditions

- **Entry Point**: 
    - Investigators start at `car_crash_intersection`.
    - Magical Girls start at `wetland_gate` via `magical_girl_intro`.
- **Exit Conditions**: No explicit exit keyword found in JSON, but typical flow ends at `final_battle` or `nothing_happens`.

## Key Decision Points

1. **Forum vs. Direct Movement**: Choosing to investigate the forum opens the Factory early vs. going straight to the Park.
2. **Engaging Blood Angel**: Choosing to interact in the Convenience Store/Restaurant determines if you have a powerful ally.
3. **Confronting Sritika**: The final decision to fight vs. potentially missing the truth (though the JSON implies battle is the primary path).

## Testing Complexity Analysis

### Hardest to Test (High Complexity)
- **Multi-role Onboarding**: Testing the convergence of the Investigator and Magical Girl tracks at `wetland_ambush`. Requires two distinct state setups.
- **Combat-State Transitions**: Triggers like `spring_shock_defeated` that depend on health thresholds (not fully defined in the JSON but implied).
- **Global Stage Progression**: The `current_investigation_stage` field acts as a global state gate that many narrations likely depend on.

### Easiest to Test (Linear Flow)
- **Initial Interactions**: `inspect_crash` and `witness_girl` are simple action-triggers.
- **Location Navigation**: The `connections` list provides a straightforward graph for navigation testing.
- **Static Reveals**: Auto-judgement interactables like `find_photo` or `blood_angel_encounter`.
