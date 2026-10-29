"""Immutable revision objects. Rollbacks can leave harmless unreferenced objects."""

import hashlib
import os
from uuid import uuid4

from sqlalchemy import select
from voxfoundry.domain.errors import DomainError
from voxfoundry.storage.assets import fingerprint, flush_directory
from voxfoundry.storage.schema import blobs


class TextObjects:
    def __init__(self, assets):
        self.assets = assets

    def put(self, conn, text: str) -> str:
        content = text.encode("utf-8")
        digest = hashlib.sha256(content).hexdigest()
        with self.assets.library.object_lock:
            path = self.assets.object_path(digest)
            if path.exists() or path.is_symlink():
                if fingerprint(path) != (digest, len(content)):
                    raise DomainError("Revision object corrupt; refusing overwrite", 409)
            else:
                stage = self.assets._stage(str(uuid4()))
                with stage.open("xb") as stream:
                    stream.write(content)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.rename(stage, path)
                flush_directory(path.parent)
            if not conn.execute(select(blobs.c.digest).where(blobs.c.digest == digest)).first():
                conn.execute(blobs.insert().values(digest=digest, size=len(content), state="valid"))
        return digest

    def read(self, digest: str) -> str:
        path = self.assets.object_path(digest)
        if fingerprint(path)[0] != digest:
            raise DomainError("Revision object corrupt; history retained", 409)
        return path.read_bytes().decode("utf-8")
