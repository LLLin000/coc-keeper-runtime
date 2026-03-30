"""Module extraction contracts and validation.

Provides:
- ModuleExtractionContract: Schema definition for required vs optional fields
- ModuleAdapter: Legacy module transformation and adaptation
- Validation functions: Trigger referential integrity, ending validity
"""

from dataclasses import dataclass, field
from typing import Any


# Core required fields - missing these = load failure
REQUIRED_FIELDS: set[str] = {
    "slug",
    "title",
    "start_scene_id",
}

# Optional fields with defaults - missing these = warning + default
OPTIONAL_FIELDS: set[str] = {
    "premise",
    "objectives",
    "state_fields",
    "scenes",
    "locations",
    "onboarding_tracks",
    "story_nodes",
    "endings",
    "start_story_node_id",
    "start_location_id",
}

# Default values for optional fields
FIELD_DEFAULTS: dict[str, Any] = {
    "objectives": [],
    "state_fields": [],
    "scenes": [],
    "locations": [],
    "onboarding_tracks": [],
    "story_nodes": [],
    "endings": [],
}

# Valid trigger event kinds
VALID_TRIGGER_EVENT_KINDS: set[str] = {
    "action",
    "roll",
    "chain",
    "ending",
}

# Valid effect kinds
VALID_EFFECT_KINDS: set[str] = {
    "set_module_state",
    "increment_module_state",
    "set_location_state",
    "add_clue",
    "record_knowledge",
    "move_location",
    "move_story_node",
    "set_pending_roll",
    "clear_pending_roll",
    "trigger_ending",
}


@dataclass
class ValidationWarning:
    """A warning from module validation (non-fatal)."""

    code: str
    message: str
    field: str | None = None
    trigger_id: str | None = None


@dataclass
class ValidationResult:
    """Result of module validation."""

    valid: bool  # Core fields present
    warnings: list[ValidationWarning] = field(default_factory=list)
    adapted_module: dict | None = None

    @property
    def error_count(self) -> int:
        return sum(1 for w in self.warnings if w.code.startswith("ERR_"))

    @property
    def warning_count(self) -> int:
        return sum(1 for w in self.warnings if w.code.startswith("WRN_"))


class ModuleAdapter:
    """Transforms legacy module format to current schema.

    Provides:
    - Field normalization
    - Default value injection
    - Validation with warnings (not errors)
    """

    def adapt(self, raw_module: dict) -> ValidationResult:
        """Adapt a raw module dict to current schema.

        Returns ValidationResult with adapted_module and any warnings.
        Core field validation happens here - missing required = valid=False.
        """
        warnings: list[ValidationWarning] = []

        # Check required fields first
        for field in REQUIRED_FIELDS:
            if field not in raw_module:
                warnings.append(
                    ValidationWarning(
                        code="ERR_MISSING_REQUIRED",
                        message=f"Missing required field: {field}",
                        field=field,
                    )
                )

        # If core fields missing, return early (can't adapt)
        if any(w.code == "ERR_MISSING_REQUIRED" for w in warnings):
            return ValidationResult(valid=False, warnings=warnings)

        # Copy and inject defaults for optional fields
        adapted = dict(raw_module)
        for field in OPTIONAL_FIELDS:
            if field not in adapted:
                if field in FIELD_DEFAULTS:
                    adapted[field] = FIELD_DEFAULTS[field]
                    warnings.append(
                        ValidationWarning(
                            code="WRN_INJECTED_DEFAULT",
                            message=f"Injected default for optional field: {field}",
                            field=field,
                        )
                    )

        # Inject start_location_id from start_scene_id if missing
        if "start_location_id" not in adapted and "start_scene_id" in adapted:
            adapted["start_location_id"] = adapted["start_scene_id"]

        return ValidationResult(
            valid=True,
            warnings=warnings,
            adapted_module=adapted,
        )


def validate_triggers(module: dict) -> list[ValidationWarning]:
    """Validate trigger referential integrity.

    Checks:
    - All next_trigger_ids reference existing triggers
    - Ending triggers have valid event_kind and ending_id
    """
    warnings: list[ValidationWarning] = []
    triggers = module.get("triggers", [])
    trigger_ids = {t.get("id") for t in triggers if t.get("id")}

    for trigger in triggers:
        trigger_id = trigger.get("id", "UNKNOWN")

        # Check next_trigger_ids references
        for next_id in trigger.get("next_trigger_ids", []):
            if next_id not in trigger_ids:
                warnings.append(
                    ValidationWarning(
                        code="WRN_ORPHAN_TRIGGER_REF",
                        message=f"Trigger '{trigger_id}' references non-existent trigger '{next_id}'",
                        trigger_id=trigger_id,
                    )
                )

        # Check ending triggers
        if trigger.get("event_kind") == "ending":
            # Must have at least one trigger_ending effect with ending_id
            has_ending_effect = any(
                e.get("kind") == "trigger_ending" and e.get("ending_id")
                for e in trigger.get("effects", [])
            )
            if not has_ending_effect:
                warnings.append(
                    ValidationWarning(
                        code="WRN_MISSING_ENDING_ID",
                        message=f"Ending trigger '{trigger_id}' missing ending_id in effects",
                        trigger_id=trigger_id,
                    )
                )

    return warnings


def validate_schema(module: dict) -> list[ValidationWarning]:
    """Validate field types and basic schema compliance."""
    warnings: list[ValidationWarning] = []

    # slug must be string
    if "slug" in module and not isinstance(module["slug"], str):
        warnings.append(
            ValidationWarning(
                code="ERR_INVALID_SLUG",
                message="slug must be a string",
                field="slug",
            )
        )

    # title must be string
    if "title" in module and not isinstance(module["title"], str):
        warnings.append(
            ValidationWarning(
                code="ERR_INVALID_TITLE",
                message="title must be a string",
                field="title",
            )
        )

    # start_scene_id must be string
    if "start_scene_id" in module and not isinstance(module["start_scene_id"], str):
        warnings.append(
            ValidationWarning(
                code="ERR_INVALID_START_SCENE",
                message="start_scene_id must be a string",
                field="start_scene_id",
            )
        )

    return warnings


def validate_module(raw_module: dict) -> ValidationResult:
    """Full module validation pipeline.

    1. Core field check (fail-fast if missing)
    2. Schema validation
    3. Trigger validation
    4. Adapter with defaults injection

    Returns ValidationResult with all warnings accumulated.
    """
    # Schema validation first (catches type errors)
    all_warnings = validate_schema(raw_module)

    # Core field check
    for field in REQUIRED_FIELDS:
        if field not in raw_module:
            all_warnings.append(
                ValidationWarning(
                    code="ERR_MISSING_REQUIRED",
                    message=f"Missing required field: {field}",
                    field=field,
                )
            )

    # If core fields missing, can't proceed
    if any(w.code == "ERR_MISSING_REQUIRED" for w in all_warnings):
        return ValidationResult(
            valid=False,
            warnings=all_warnings,
        )

    # Trigger validation
    all_warnings.extend(validate_triggers(raw_module))

    # Adapter (injects defaults, returns adapted module)
    adapter = ModuleAdapter()
    result = adapter.adapt(raw_module)
    all_warnings.extend(result.warnings)

    return ValidationResult(
        valid=True,
        warnings=all_warnings,
        adapted_module=result.adapted_module,
    )
