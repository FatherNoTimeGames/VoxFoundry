import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def test_documented_headless_launcher_and_health(tmp_path):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    command = [
        sys.executable,
        "-m",
        "voxfoundry.cli",
        "--library",
        str(tmp_path / "library"),
        "--port",
        str(port),
        "--no-browser",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Local request only; never change runtime proxy settings for external destinations.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        deadline = time.monotonic() + 10
        while True:
            try:
                with opener.open(f"http://127.0.0.1:{port}/api/health", timeout=1) as response:
                    assert json.load(response)["status"] == "ok"
                    break
            except urllib.error.URLError:
                assert process.poll() is None, "Launcher exited before becoming ready"
                assert time.monotonic() < deadline, "Launcher readiness timeout"
                time.sleep(0.05)
        with opener.open(f"http://127.0.0.1:{port}/", timeout=1) as response:
            assert b"VoxFoundry" in response.read()
    finally:
        process.terminate()
        output, errors = process.communicate(timeout=10)
        assert b"token=" not in output + errors
