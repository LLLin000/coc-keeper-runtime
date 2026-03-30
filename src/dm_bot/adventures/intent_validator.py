from typing import Optional

from .action_intent import ActionIntent, ValidationResult, ClarificationReaction


class IntentValidator:
    """Validates ActionIntent against scene context.

    Full validation checks:
    1. Context existence - target exists in current scene/location
    2. Prerequisites - player has required skills/items
    3. Game state - current state allows this action
    4. Rules compliance - COC rules permit this action
    """

    def __init__(self, adventure_package: object, adventure_state: dict):
        """Initialize validator with adventure package and state.

        Args:
            adventure_package: AdventureModule with locations, entities, triggers
            adventure_state: Current game state dict with location_id, module_state, etc.
        """
        self.package = adventure_package
        self.state = adventure_state

    def validate(self, intent: ActionIntent) -> ValidationResult:
        """Validate a single ActionIntent.

        Returns ValidationResult with valid=True if all checks pass,
        or valid=False with errors and clarification_needed=True.
        """
        errors: list[str] = []

        # 1. Context validation
        context_ok, context_error = self.validate_context(intent)
        if not context_ok:
            errors.append(context_error)

        # 2. Prerequisites validation
        prereq_ok, prereq_error = self.validate_prerequisites(intent)
        if not prereq_ok:
            errors.append(prereq_error)

        # 3. State validation
        state_ok, state_error = self.validate_state(intent)
        if not state_ok:
            errors.append(state_error)

        # 4. Rules validation
        rules_ok, rules_error = self.validate_rules(intent)
        if not rules_ok:
            errors.append(rules_error)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            clarification_needed=len(errors) > 0,
        )

    def validate_context(self, intent: ActionIntent) -> tuple[bool, Optional[str]]:
        """Check if target exists in current scene/location.

        Returns (is_valid, error_message).
        """
        if not intent.target:
            # No target specified - could be valid for some actions
            return True, None

        target = intent.target
        current_location_id = self.state.get("location_id")
        current_scene_id = self.state.get("scene_id")

        # Try to resolve target against current scene entities
        if target.resolved_id:
            # Already resolved - verify it exists
            entity = self._find_entity(target.resolved_id)
            if not entity:
                return False, f"找不到目标「{target.reference}」"
            return True, None

        # Resolve target reference to entity ID
        resolved_id = self._resolve_target_reference(
            target.reference, target.entity_type, current_scene_id
        )

        if not resolved_id:
            return False, f"找不到目标「{target.reference}」"

        # Update intent with resolved ID
        target.resolved_id = resolved_id

        return True, None

    def validate_prerequisites(
        self, intent: ActionIntent
    ) -> tuple[bool, Optional[str]]:
        """Check if player has required skills/items for this action.

        Returns (is_valid, error_message).
        """
        action_type = intent.action_type

        # Define skill requirements per action type
        SKILL_REQUIREMENTS = {
            "lock_interaction": ["lockpicking"],
            "search": ["spot_hidden", "investigation"],
            "observe": ["perception", "spot_hidden"],
            "stealth": ["stealth"],
            "combat": ["fighting", "firearms"],
            "skill_use": [],  # Generic - prereq depends on specific skill
        }

        required_skills = SKILL_REQUIREMENTS.get(action_type, [])

        # Check character skills from adventure state
        character = self.state.get("character", {})
        character_skills = character.get("skills", {})

        for skill in required_skills:
            skill_value = character_skills.get(skill, 0)
            # COC skill check: if skill is 0 or missing, player doesn't have it
            if skill_value <= 0:
                return False, f"你需要「{skill}」技能才能执行此动作"

        # Check for required items
        required_items = self._get_required_items(action_type)
        character_items = character.get("inventory", [])

        for item in required_items:
            if item not in character_items:
                return False, f"你需要「{item}」才能执行此动作"

        return True, None

    def validate_state(self, intent: ActionIntent) -> tuple[bool, Optional[str]]:
        """Check if game state allows this action.

        Returns (is_valid, error_message).
        """
        # Check if already in combat (some actions not allowed)
        if self.state.get("in_combat", False):
            if intent.action_type in ["search", "observe"]:
                return False, "战斗中无法进行此动作"

        # Check if already performing another action
        if self.state.get("action_in_progress", False):
            return False, "你已经在进行另一个动作"

        # Check if location allows the action
        current_location_id = self.state.get("location_id")
        location = (
            self.package.location_by_id(current_location_id)
            if current_location_id
            else None
        )

        if location:
            # Location-specific restrictions
            location_type = location.get("location_type", "")
            if location_type == "combat" and intent.action_type == "search":
                return False, "战斗中无法搜索"

        return True, None

    def validate_rules(self, intent: ActionIntent) -> tuple[bool, Optional[str]]:
        """Check if COC rules permit this action.

        Returns (is_valid, error_message).
        """
        # COC-specific rule checks
        action_type = intent.action_type

        # Some actions are impossible in COC rules
        IMPOSSIBLE_ACTIONS = ["xray_vision", "telepathy", "mind_control"]

        if action_type in IMPOSSIBLE_ACTIONS:
            return False, f"「{action_type}」不是可行的COC动作"

        # Sanity check - some actions might cost SAN
        if intent.action_type == "observe":
            if "恐怖" in intent.intent or "尸体" in intent.intent:
                # Observing something disturbing might require SAN check
                pass  # SAN check handled by trigger, not validation

        return True, None

    def create_clarification(
        self, validation_result: ValidationResult
    ) -> ClarificationReaction:
        """Create clarification reaction from validation errors.

        Returns ClarificationReaction with user-friendly Chinese message.
        """
        if validation_result.valid:
            raise ValueError("Cannot create clarification for valid intent")

        # Primary error is usually the most relevant
        primary_error = (
            validation_result.errors[0] if validation_result.errors else "动作无效"
        )

        # Try to extract missing prerequisite
        missing_prereq = None
        suggested_correction = None

        for error in validation_result.errors:
            if "需要" in error and "技能" in error:
                # Extract skill name
                import re

                match = re.search(r"「(.+?)」", error)
                if match:
                    skill = match.group(1)
                    missing_prereq = f"学习{skill}"
                    suggested_correction = f"你想怎么用{skill}?"

        return ClarificationReaction(
            error_message=primary_error,
            missing_prereq=missing_prereq,
            suggested_correction=suggested_correction,
        )

    def _resolve_target_reference(
        self, reference: str, entity_type: str, scene_id: str
    ) -> Optional[str]:
        """Resolve player reference to actual entity ID in scene.

        This is a simple implementation - full resolution uses scene graph.
        """
        # Get current location
        location_id = self.state.get("location_id")
        if not location_id:
            return None

        # Get location data
        location = self.package.location_by_id(location_id)
        if not location:
            return None

        # Search entities in location
        entities = location.get("entities", [])
        reference_lower = reference.lower()

        for entity in entities:
            entity_id = entity.get("id", "")
            entity_name = entity.get("name", "").lower()
            entity_type_in_scene = entity.get("type", "").lower()

            # Match by name or type
            if (
                reference_lower in entity_name
                or entity_type.lower() in entity_type_in_scene
                or entity_name in reference_lower
            ):
                return entity_id

        return None

    def _find_entity(self, entity_id: str) -> Optional[dict]:
        """Find entity by ID in current scene/location."""
        location_id = self.state.get("location_id")
        if not location_id:
            return None

        location = self.package.location_by_id(location_id)
        if not location:
            return None

        entities = location.get("entities", [])
        for entity in entities:
            if entity.get("id") == entity_id:
                return entity

        return None

    def _get_required_items(self, action_type: str) -> list[str]:
        """Get required items for an action type.

        Override or extend this in subclasses for module-specific items.
        """
        # Base COC items
        ITEM_REQUIREMENTS = {
            "lock_interaction": ["lockpick", "tools"],
            "combat": ["weapon", "firearm"],
        }
        return ITEM_REQUIREMENTS.get(action_type, [])
