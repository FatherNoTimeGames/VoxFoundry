"""Manual hosted access probe. Reads protected credentials, never logs values.

Run only against the approved disposable Site after enrolling the device. No job
is claimed or modified. No redirect is followed. This script has NOT been run on
a hosted Site in the current work.
"""
import argparse
import json
from pathlib import Path
import urllib.error
import urllib.request
from worker_client import Client


def main():
    parser = argparse.ArgumentParser(description="Read-only private Site access checks")
    parser.add_argument("--site", required=True)
    parser.add_argument("--credentials", required=True, type=Path)
    parser.add_argument("--job-id", help="Optional completed job UUID for owner-audio denial check")
    args = parser.parse_args()
    client = Client(args.site, args.credentials)

    def probe(path, *, service=False, device=False):
        headers = {}
        if service:
            headers["OAI-Sites-Authorization"] = "Bearer " + client.service_token
        if device:
            headers["Authorization"] = "Bearer " + client.token
        request = urllib.request.Request(client.base + path, headers=headers)
        try:
            response = client.opener.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            data = response.read(4096)
            try:
                value = json.loads(data)
            except (ValueError, UnicodeError):
                value = {}
            return response.code, value

    checks = []
    status, value = probe("/worker/ping", service=True, device=True)
    checks.append(("Both credentials reach authenticated app probe", status == 200 and value.get("authenticated") is True, status))
    status, value = probe("/worker/ping", service=True)
    checks.append(("Service credential alone reaches app but lacks worker identity", status == 401 and value.get("error") == "Worker credential required", status))
    status, _ = probe("/worker/ping", device=True)
    checks.append(("Worker identity alone cannot cross private boundary", status in (301, 302, 303, 307, 308, 401, 403), status))
    status, _ = probe("/api/jobs", service=True, device=True)
    checks.append(("Service plus device cannot impersonate owner", status == 401, status))
    if args.job_id:
        import uuid
        job_id = str(uuid.UUID(args.job_id))
        status, _ = probe("/api/jobs/" + job_id + "/audio", service=True, device=True)
        checks.append(("Service plus device cannot read owner audio", status == 401, status))
    for label, passed, status in checks:
        print(("PASS" if passed else "FAIL") + f": {label} (HTTP {status})")
    return 0 if all(item[1] for item in checks) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError):
        raise SystemExit("Access probe stopped; check protected configuration without logging values.") from None
