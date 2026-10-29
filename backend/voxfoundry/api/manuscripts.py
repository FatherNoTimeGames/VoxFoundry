from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Query, Request, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from voxfoundry.domain.manuscripts import MAX_TEXT_BYTES, validate_text


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Label(Input):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not value or any(ord(c) < 32 for c in value):
            raise ValueError("Use a nonempty printable name")
        return value


Kind = Literal["part", "chapter", "episode", "manuscript", "research", "reference", "note"]


class NodeInput(Input):
    title: str = Field(min_length=1, max_length=200)
    kind: Kind = "manuscript"
    parent_id: UUID | None = None
    position: int = Field(default=0, ge=0, le=100000)
    references: list[UUID] = Field(default_factory=list, max_length=100)

    @field_validator("title")
    @classmethod
    def title_valid(cls, value):
        return Label(name=value).name


class NodeEdit(NodeInput):
    version: int = Field(ge=1)


class TextInput(Input):
    version: int = Field(ge=1)
    text: str = Field(max_length=MAX_TEXT_BYTES)

    @field_validator("text")
    @classmethod
    def valid_text(cls, value):
        return validate_text(value)


class Freeze(Label):
    version: int = Field(ge=1)


class RestoreRevision(Input):
    revision_id: UUID
    version: int = Field(ge=1)


class SnapshotRequest(Label):
    generation: int = Field(ge=0)
    project_version: int = Field(ge=1)


class RestoreSnapshot(Input):
    generation: int = Field(ge=0)
    project_version: int = Field(ge=1)


class Controls(Input):
    language: str | None = Field(default=None, min_length=2, max_length=40)
    pace: float | None = Field(default=None, ge=0.5, le=2, allow_inf_nan=False)


class Rule(Input):
    term: str = Field(min_length=1, max_length=120)
    replacement: str = Field(min_length=1, max_length=240)
    node_id: UUID | None = None

    @field_validator("term", "replacement")
    @classmethod
    def printable(cls, value):
        if value != value.strip() or any(ord(c) < 32 for c in value):
            raise ValueError(
                "Pronunciation entries must be printable without surrounding whitespace"
            )
        return value


class Configuration(Input):
    controls: Controls = Field(default_factory=Controls)
    rules: list[Rule] = Field(default_factory=list, max_length=300)

    @model_validator(mode="after")
    def unique_rules(self):
        keys = [(r.term, r.node_id) for r in self.rules]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate term in the same scope")
        return self

    def configuration(self):
        value = self.model_dump(mode="json", exclude_none=True)
        value["controls"] = {k: v for k, v in value["controls"].items() if v is not None}
        return value


class SettingsInput(Configuration):
    version: int = Field(ge=0)
    preset_id: UUID | None = None

    def configuration(self):
        return Configuration(controls=self.controls, rules=self.rules).configuration()


class PresetInput(Configuration):
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def name_valid(cls, value):
        return Label(name=value).name

    @model_validator(mode="after")
    def shared_scope(self):
        if any(r.node_id for r in self.rules):
            raise ValueError("Shared presets cannot contain project document IDs")
        return self

    def configuration(self):
        return Configuration(controls=self.controls, rules=self.rules).configuration()


router = APIRouter()


def service(request):
    return request.app.state.manuscripts


@router.get("/api/projects/{project_id}/workspace")
def workspace(project_id: UUID, request: Request):
    return service(request).workspace(str(project_id))


@router.post("/api/projects/{project_id}/documents", status_code=201)
def create_node(project_id: UUID, body: NodeInput, request: Request):
    return service(request).create_node(
        str(project_id),
        body.title,
        body.kind,
        str(body.parent_id) if body.parent_id else None,
        body.position,
        references=[str(r) for r in body.references],
    )


@router.post("/api/projects/{project_id}/documents/import", status_code=201)
def import_document(
    project_id: UUID,
    request: Request,
    file: UploadFile,
    title: str = Query(min_length=1, max_length=200),
    kind: Kind = "manuscript",
    parent_id: UUID | None = None,
    position: int = Query(default=0, ge=0, le=100000),
):
    from voxfoundry.domain.errors import DomainError

    if not title.strip() or any(ord(c) < 32 for c in title):
        raise DomainError("Use a nonempty printable title")
    try:
        return service(request).import_document(
            str(project_id),
            file.filename or "",
            file.file,
            title.strip(),
            kind,
            str(parent_id) if parent_id else None,
            position,
        )
    finally:
        file.file.close()


@router.get("/api/projects/{project_id}/documents/{node_id}")
def get_document(project_id: UUID, node_id: UUID, request: Request):
    return service(request).document(str(project_id), str(node_id))


@router.put("/api/projects/{project_id}/documents/{node_id}")
def edit_node(project_id: UUID, node_id: UUID, body: NodeEdit, request: Request):
    return service(request).edit_node(
        str(project_id),
        str(node_id),
        body.version,
        body.title,
        body.kind,
        str(body.parent_id) if body.parent_id else None,
        body.position,
        [str(r) for r in body.references],
    )


@router.put("/api/projects/{project_id}/documents/{node_id}/draft")
def save_draft(project_id: UUID, node_id: UUID, body: TextInput, request: Request):
    return service(request).save_draft(str(project_id), str(node_id), body.version, body.text)


@router.post("/api/projects/{project_id}/documents/{node_id}/revisions", status_code=201)
def freeze_document(project_id: UUID, node_id: UUID, body: Freeze, request: Request):
    return service(request).freeze_document(str(project_id), str(node_id), body.version, body.name)


@router.get("/api/projects/{project_id}/documents/{node_id}/revisions/{revision_id}")
def revision(project_id: UUID, node_id: UUID, revision_id: UUID, request: Request):
    return service(request).revision_detail(str(project_id), str(node_id), str(revision_id))


@router.post("/api/projects/{project_id}/documents/{node_id}/restore")
def restore_document(project_id: UUID, node_id: UUID, body: RestoreRevision, request: Request):
    return service(request).restore_document(
        str(project_id), str(node_id), str(body.revision_id), body.version
    )


@router.get("/api/projects/{project_id}/documents/{node_id}/script/{revision_id}")
def script(project_id: UUID, node_id: UUID, revision_id: UUID, request: Request):
    return service(request).script(str(project_id), str(node_id), str(revision_id))


@router.get("/api/presets")
def presets(request: Request):
    return service(request).list_presets()


@router.post("/api/presets", status_code=201)
def create_preset(body: PresetInput, request: Request):
    return service(request).create_preset(body.name, body.configuration())


@router.put("/api/projects/{project_id}/settings")
def save_settings(project_id: UUID, body: SettingsInput, request: Request):
    return service(request).update_settings(
        str(project_id),
        body.version,
        str(body.preset_id) if body.preset_id else None,
        body.configuration(),
    )


@router.get("/api/projects/{project_id}/snapshots")
def snapshots(project_id: UUID, request: Request):
    return service(request).list_snapshots(str(project_id))


@router.post("/api/projects/{project_id}/snapshots", status_code=201)
def create_snapshot(project_id: UUID, body: SnapshotRequest, request: Request):
    return service(request).create_snapshot(
        str(project_id), body.name, body.generation, body.project_version
    )


@router.get("/api/projects/{project_id}/snapshots/{snapshot_id}/preview")
def preview(project_id: UUID, snapshot_id: UUID, request: Request):
    return service(request).preview(str(project_id), str(snapshot_id))


@router.post("/api/projects/{project_id}/snapshots/{snapshot_id}/restore")
def restore_snapshot(project_id: UUID, snapshot_id: UUID, body: RestoreSnapshot, request: Request):
    return service(request).restore_snapshot(
        str(project_id), str(snapshot_id), body.generation, body.project_version
    )


@router.get("/api/projects/{project_id}/documents/{node_id}/revisions/{revision_id}/compare")
def compare_revision(project_id: UUID, node_id: UUID, revision_id: UUID, request: Request):
    return service(request).compare_revision(str(project_id), str(node_id), str(revision_id))
