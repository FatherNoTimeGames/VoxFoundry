"""Run on the worker machine. Never paste secrets into chat or command arguments."""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import secrets
from worker_client import private_path


def main():
    parser = argparse.ArgumentParser(description="Create an owner-only worker credential file locally")
    parser.add_argument("--site", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--device-id", default="windows-tone-1")
    args = parser.parse_args()
    output = private_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    token = secrets.token_urlsafe(32)
    # Local terminal input only; not a tool/chat prompt and never echoed/logged.
    service_token = getpass.getpass("Site service credential (hidden local input): ")
    if not service_token:
        raise ValueError("Service credential required")
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump({"site": args.site.rstrip("/"), "token": token,
                   "service_token": service_token}, stream)
    # Only the public verifier and non-secret device ID are displayed.
    print("Public device ID:", args.device_id)
    print("Public token SHA-256 verifier:", hashlib.sha256(token.encode()).hexdigest())
    if os.name == "nt":
        print("Before use, restrict this directory and file to your Windows account with NTFS ACLs.")


if __name__ == "__main__":
    main()
