from pathlib import Path

from pydantic import BaseModel, Field

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - optional dependency in local runtime
    PdfReader = None


class COCReference(BaseModel):
    title: str
    url: str
    summary: str = ""


class COCTextAsset(BaseModel):
    name: str
    path: str
    preview: str = ""


class COCInvestigatorAsset(BaseModel):
    name: str
    path: str
    text_available: bool = False
    preview: str = ""


class COCAssetLibrary(BaseModel):
    rulebooks: list[COCTextAsset] = Field(default_factory=list)
    investigators: list[COCInvestigatorAsset] = Field(default_factory=list)
    community_references: list[COCReference] = Field(default_factory=list)

    @classmethod
    def from_paths(
        cls,
        *,
        rulebook_paths: list[Path],
        investigator_paths: list[Path],
        community_references: list[COCReference],
    ) -> "COCAssetLibrary":
        return cls(
            rulebooks=[_load_text_asset(path) for path in rulebook_paths],
            investigators=[_load_investigator_asset(path) for path in investigator_paths],
            community_references=community_references,
        )

    def summary(self) -> dict[str, object]:
        return self.model_dump()


def _load_text_asset(path: Path) -> COCTextAsset:
    preview = ""
    if path.suffix.lower() == ".pdf":
        preview = _extract_pdf_preview(path)
    else:
        try:
            preview = path.read_text(encoding="utf-8")[:240]
        except UnicodeDecodeError:
            preview = path.read_text(encoding="utf-8", errors="ignore")[:240]
    return COCTextAsset(name=path.stem, path=str(path), preview=preview)


def _load_investigator_asset(path: Path) -> COCInvestigatorAsset:
    text_available = path.suffix.lower() in {".txt", ".md", ".json"}
    preview = ""
    if text_available:
        preview = path.read_text(encoding="utf-8", errors="ignore")[:240]
    return COCInvestigatorAsset(name=path.stem, path=str(path), text_available=text_available, preview=preview)


def _extract_pdf_preview(path: Path) -> str:
    if PdfReader is None:
        return ""
    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""
    parts: list[str] = []
    for page in reader.pages[:4]:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)[:240]
