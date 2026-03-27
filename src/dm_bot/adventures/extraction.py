import json

from pydantic import BaseModel, Field


class AdventureExtractionLocationDraft(BaseModel):
    id: str
    title: str
    summary: str
    neighbors: list[str] = Field(default_factory=list)
    landmarks: list[str] = Field(default_factory=list)


class AdventureExtractionTriggerTreeDraft(BaseModel):
    location_id: str
    root_trigger: str
    outcomes: list[str] = Field(default_factory=list)


class AdventureExtractionTriggerDraft(BaseModel):
    id: str
    event_kind: str
    action_id: str = ""
    pending_roll_id: str = ""
    summary: str = ""


class AdventureExtractionDraft(BaseModel):
    source_name: str
    topology_summary: str
    locations: list[AdventureExtractionLocationDraft] = Field(default_factory=list)
    trigger_trees: list[AdventureExtractionTriggerTreeDraft] = Field(default_factory=list)
    trigger_drafts: list[AdventureExtractionTriggerDraft] = Field(default_factory=list)


async def extract_room_graph_draft(source_text: str, *, source_name: str, llm) -> AdventureExtractionDraft:
    prompt = (
        "Read the source script as a Keeper-facing module and extract a reviewable room graph draft. "
        "Return JSON with: source_name, topology_summary, locations[{id,title,summary,neighbors,landmarks}], "
        "trigger_trees[{location_id,root_trigger,outcomes}], "
        "trigger_drafts[{id,event_kind,action_id,pending_roll_id,summary}]. "
        "Preserve geographic layout, local trigger logic, and hidden information boundaries instead of summarizing the script linearly.\n\n"
        f"Source name: {source_name}\n"
        f"Source text:\n{source_text}"
    )
    payload = await llm.extract_json(prompt)
    return AdventureExtractionDraft.model_validate(json.loads(payload))
