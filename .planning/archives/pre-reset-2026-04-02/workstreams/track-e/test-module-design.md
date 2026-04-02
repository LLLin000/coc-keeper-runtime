# Test-Friendly Extraction: Fuzhe Mini (Vertical Slice)

## 1. Recommended Subset of Fuzhe
To achieve a 15-turn end-to-end scenario test that covers 80% of runtime patterns with 20% of the complexity, we will extract the **"Wetland Park Investigation"** arc.

### Included Nodes:
- **`car_crash_intersection` (Location/Scene)**: The entry point. Establishes the investigator/magical girl roles and the initial mystery.
- **`mystery_forum` (Location/Scene)**: A non-combat investigation node. Tests library use, clue collection, and information gathering.
- **`wetland_gate` (Location/Scene)**: The pivot point. Tests navigation and transition to combat.
- **`wetland_ambush` (Event)**: The core combat test. Tests initiative, turn-based combat, and enemy AI performance.

### Cut Nodes:
- `convenience_store`, `restaurant`, `cultural_street`: Side exploration nodes that don't drive the core "mystery -> combat" loop.
- `xinhai_school`, `chemical_factory`, `x_company`: Late-game complex nodes that would exceed the 15-turn limit.

## 2. Why This Subset is Ideal for Testing
- **Clear Trigger Points**: 
    - Intersection -> Forum (Action: Inspect crash/Search news).
    - Forum -> Wetland (Action: Find photo/Follow lead).
    - Wetland -> Ambush (Action: Enter/Listen).
- **Measurable Outcomes**: Clues collected (witnessing the girl, finding the photo), state changes (`san_pressure`, `danger_level`), and combat success (defeating Spring Shock).
- **Multiple Endings (Mini Version)**:
    - **Success**: Defeat Spring Shock and secure the clue about X-Company.
    - **Failure**: Investigation stalls or characters are defeated in combat.
    - **Retreat**: Characters decide the danger is too high after the first encounter.

## 3. Entry Point and Exit Conditions
- **Entry Point**: `car_crash_intersection`. Characters start in a "Normal" mode, witnessing the incident.
- **Exit Conditions**:
    - Completion of `wetland_ambush` event.
    - Reaching a "Failure" or "Retreat" state in the mini-trigger tree.
    - Reaching 15 turns (Timeout/Stall test).

## 4. Specific Test Scenarios
1. **The "Perfect Investigation" Run**: Players successfully investigate the crash, use the forum to find the photo, and prepare for the wetland ambush. Tests clue persistence and sequential scene transitions.
2. **The "Direct to Danger" Run**: Players skip the forum and head straight to the wetland park. Tests robust navigation and handling of missing information/clues.
3. **The "Combat Stress" Run**: Focuses on the `wetland_ambush`. Tests HP tracking, SAN checks during combat, and enemy action execution.
4. **The "Investigation Failure" Run**: Players fail the `LibraryUse` check at the forum. Tests "rescue hints" and fallback paths to keep the story moving.
5. **The "Mixed Role" Run**: One investigator and one magical girl. Tests asymmetric onboarding and role-specific dialogue/narrative hooks.

## 5. Module Structure as Standalone Test Fixture
- **File Location**: `src/dm_bot/adventures/fuzhe_mini.json`
- **Schema**: Adheres to the standard `Adventure` model defined in `src/dm_bot/adventures/models.py`.
- **Refinement**: Simplified triggers and fewer state fields to reduce "noise" in event logs during testing.

## 6. Track A Development Target
**Yes.** This extraction is an ideal target for Track A (Adventure Runtime) development. 
- It provides a "Gold Standard" for how a minimal module should be structured.
- It can be used to verify new trigger types or consequence kinds without the overhead of the full fuzhe module.
- It serves as a template for other "Micro-Modules" for rapid prototyping.
