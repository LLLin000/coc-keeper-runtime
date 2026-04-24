from pathlib import Path

from dm_bot.characters.sources import COCInvestigatorSource
from dm_bot.coc.assets import COCAssetLibrary, COCReference


def test_coc_asset_library_extracts_textual_rulebook_snippets(tmp_path: Path) -> None:
    rulebook = tmp_path / "基础规则.txt"
    rulebook.write_text("理智(SAN)会随着调查员目睹恐怖而下降。推动检定会在失败时带来更坏的后果。", encoding="utf-8")

    library = COCAssetLibrary.from_paths(rulebook_paths=[rulebook], investigator_paths=[], community_references=[])

    summary = library.summary()

    assert summary["rulebooks"][0]["name"] == "基础规则"
    assert "理智" in summary["rulebooks"][0]["preview"]


def test_coc_asset_library_tracks_dynamic_investigator_files_as_binary_assets(tmp_path: Path) -> None:
    investigator = tmp_path / "Jessie Williams.pdf"
    investigator.write_bytes(b"%PDF-1.7 fake dynamic form")

    library = COCAssetLibrary.from_paths(rulebook_paths=[], investigator_paths=[investigator], community_references=[])

    summary = library.summary()

    assert summary["investigators"][0]["name"] == "Jessie Williams"
    assert summary["investigators"][0]["text_available"] is False


def test_coc_investigator_source_loads_manifest_record() -> None:
    source = COCInvestigatorSource(
        fixtures={
            "jessie": {
                "id": "jessie",
                "name": "Jessie Williams",
                "occupation": "Dilettante",
                "age": 24,
                "san": 60,
                "hp": 11,
                "mp": 12,
                "luck": 40,
                "attributes": {"str": 45, "con": 55, "dex": 70, "app": 80, "pow": 60, "siz": 55, "int": 75, "edu": 65},
                "skills": {"图书馆使用": 60, "聆听": 50},
            }
        }
    )

    record = source.fetch("jessie")

    assert record.name == "Jessie Williams"
    assert record.coc is not None
    assert record.coc.san == 60
    assert record.coc.skills["图书馆使用"] == 60
