from uuid import uuid4

from sqlalchemy import select
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.library import timestamp
from voxfoundry.storage.schema import projects, series


class Projects:
    def __init__(self, library):
        self.library = library

    def list(self, trashed=False):
        with self.library.engine.connect() as conn:
            rows = conn.execute(
                select(projects)
                .where(
                    projects.c.trashed_at.is_not(None)
                    if trashed
                    else projects.c.trashed_at.is_(None)
                )
                .order_by(projects.c.created_at, projects.c.id)
            ).mappings()
            return [dict(r) for r in rows]

    def get(self, project_id, *, active=False):
        with self.library.engine.connect() as conn:
            row = (
                conn.execute(select(projects).where(projects.c.id == project_id)).mappings().first()
            )
        if row is None or (active and row["trashed_at"]):
            raise DomainError("Project not found", 404)
        return dict(row)

    def create(self, name, description, series_id):
        now = timestamp()
        data = dict(
            id=str(uuid4()),
            name=name,
            description=description,
            series_id=series_id,
            version=1,
            created_at=now,
            updated_at=now,
            trashed_at=None,
        )
        with self.library.engine.begin() as conn:
            self._series_exists(conn, series_id)
            conn.execute(projects.insert().values(**data))
        return data

    def update(self, project_id, version, **changes):
        with self.library.engine.begin() as conn:
            if "series_id" in changes:
                self._series_exists(conn, changes["series_id"])
            result = conn.execute(
                projects.update()
                .where(projects.c.id == project_id, projects.c.version == version)
                .values(**changes, updated_at=timestamp(), version=version + 1)
            )
            if result.rowcount != 1:
                raise DomainError("Project changed or no longer exists; reload before saving", 409)
            row = conn.execute(select(projects).where(projects.c.id == project_id)).mappings().one()
            return dict(row)

    def list_series(self):
        with self.library.engine.connect() as conn:
            return [
                dict(r) for r in conn.execute(select(series).order_by(series.c.name)).mappings()
            ]

    def create_series(self, name):
        data = dict(id=str(uuid4()), name=name, created_at=timestamp())
        with self.library.engine.begin() as conn:
            conn.execute(series.insert().values(**data))
        return data

    @staticmethod
    def _series_exists(conn, series_id):
        if (
            series_id
            and not conn.execute(select(series.c.id).where(series.c.id == series_id)).first()
        ):
            raise DomainError("Series not found", 404)
