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


class AdventureExtractionDraft(BaseModel):
    source_name: str
    topology_summary: str
    locations: list[AdventureExtractionLocationDraft] = Field(default_factory=list)
    trigger_trees: list[AdventureExtractionTriggerTreeDraft] = Field(default_factory=list)


async def extract_room_graph_draft(source_text: str, *, source_name: str, llm) -> AdventureExtractionDraft:
    prompt = (
        "Read the source script and extract a reviewable room graph draft. "
        "Return JSON with: source_name, topology_summary, locations[{id,title,summary,neighbors,landmarks}], "
        "trigger_trees[{location_id,root_trigger,outcomes}]. "
        "Preserve geographic layout and local trigger logic instead of summarizing the script linearly.\n\n"
        f"Source name: {source_name}\n"
        f"Source text:\n{source_text}"
    )
    payload = await llm.extract_json(prompt)
    return AdventureExtractionDraft.model_validate(json.loads(payload))
