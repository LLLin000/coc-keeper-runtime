Feature: Combat Round Resolution
  COC-style combat round with initiative order, attack resolution,
  SAN checks, and pushed roll / fumble handling.

  Background:
    Given a rules engine with test dice roller

  Scenario: Attacker hits defender in combat round
    Given a combat encounter with Hero (AC 15, HP 20) vs Goblin (AC 13, HP 7)
    When Hero attacks Goblin with +5 bonus and "1d6+3" damage
    Then the attack hits Goblin
    And Goblin takes damage and HP becomes 4

  Scenario: Attacker misses defender in combat round
    Given a combat encounter for miss scenario
    When Hero attacks Goblin with -5 bonus (auto-miss)
    Then the attack misses Goblin
    And Goblin HP remains 7

  Scenario: Pushed roll grants second chance on failure
    Given an investigator with Skill 50 making a coc_skill_check
    When the check fails and is pushed
    Then the rules engine rolls again with same parameters
    And returns a second outcome

  Scenario: Fumble on natural 100 in percentile check
    Given an investigator with SAN 50 making a sanity check
    When the percentile roll is 100
    Then the result is a fumble
    And san_loss applies per the failure table

  Scenario: Combat encounter tracks initiative order
    Given combatants: Alice (init 85), Bob (init 72), Carol (init 90)
    When the encounter starts
    Then the initiative order is Carol, Alice, Bob
    And Carol is the active combatant
