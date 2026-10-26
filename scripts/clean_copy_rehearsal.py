#!/usr/bin/env python3
"""Timed CLEAN-COPY setup rehearsal (not a fresh clone: no GitHub repository exists yet).

    python scripts/clean_copy_rehearsal.py [--port 8001]

1. Copies the files that would be committed (respecting .gitignore: no .venv, node_modules, local_data,
   .env, caches) into <tmp>/submissions/animal-volunteer.
2. Times: python -m venv, pip install -r requirements.txt, server start, page loads.
3. Credentials, with PORTKEY_API_KEY REMOVED from the server's environment:
   a) no .env at all (expect credentials_missing),
   b) .env in the project root, c) .env one folder above (submissions/.env).
   The key value is copied from the operator's environment into those temporary files without being
   printed, and the files are deleted at the end. Writing the file stands in for the grader's manual step.
4. One real assistant request (synthetic message) for b) and c).
Results: output/setup_rehearsal/clean_copy_rehearsal.json (+ .md written by hand from it).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".venv", "node_modules", "local_data", "__pycache__", ".pytest_cache", ".git"}
EXCLUDE_FILES = {".env", ".DS_Store"}

ROOT_DIV = b'<div id="root">'


def copy_tree(dst: Path) -> int:
    n = 0
    for p in SRC.rglob("*"):
        rel = p.relative_to(SRC)
        if any(part in EXCLUDE_DIRS for part in rel.parts) or p.name in EXCLUDE_FILES or p.is_dir():
            continue
        if p.name.startswith(".env") and p.name != ".env.example":
            continue
        (dst / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst / rel)
        n += 1
    return n


def get(url: str, timeout=10):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, r.headers.get("content-type", ""), r.read()


def post(url: str, body: dict, timeout=200):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read())


def start_server(proj: Path, port: int) -> tuple[subprocess.Popen, float]:
    env = {k: v for k, v in os.environ.items() if k != "PORTKEY_API_KEY"}  # no shell credential precedence
    t0 = time.perf_counter()
    proc = subprocess.Popen([str(proj / ".venv/bin/uvicorn"), "backend.api:app", "--host", "127.0.0.1", "--port", str(port)],
                            cwd=proj, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            get(f"http://127.0.0.1:{port}/api/health", timeout=1)
            return proc, round(time.perf_counter() - t0, 2)
        except Exception:
            time.sleep(0.25)
    proc.terminate()
    raise RuntimeError("server did not start")


def check(port: int, assistant: bool, stage: str = "") -> dict:
    base = f"http://127.0.0.1:{port}"
    _, _, body = get(base + "/api/health")
    health = json.loads(body)
    out = {"credentials_present": health["assistant"]["credentials_present"],
           "credential_source": health["assistant"]["credential_source"]}
    for path in ("/", "/explore", "/opportunities/gnhcp_grant_writing", "/find-my-fit"):
        st, ct, b = get(base + path)
        out[f"page {path}"] = f"{st} {ct.split(';')[0]} {'has app root' if ROOT_DIV in b else 'NO ROOT'}"
    st, _, b = get(base + "/api/opportunities")
    out["api /api/opportunities count"] = json.loads(b)["count"]
    if assistant:
        t0 = time.perf_counter()
        # each stage sends a different message so Portkey's gateway cache cannot replay an earlier answer
        st, r = post(base + "/api/assistant", {"message": f"SYNTHETIC SETUP CHECK ({stage}, {time.strftime('%H%M%S')}): "
                                                          "I'm 30, live in Hamden, and like cats. Any options?"})
        out["assistant"] = {"http": st, "ok": r["ok"], "error": r["error"], "returned_models": r["returned_models"],
                            "recommendations": [x["opportunity_id"] for x in r["recommendations"]],
                            "latency_s": round(time.perf_counter() - t0, 2),
                            "usage": r["usage"]}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8001)
    a = ap.parse_args()
    key = os.environ.get("PORTKEY_API_KEY")
    if not key:
        sys.exit("Set PORTKEY_API_KEY in your shell only so this script can write the temporary .env files.")
    root = Path(tempfile.mkdtemp(prefix="avf_clean_copy_"))
    subs = root / "submissions"
    proj = subs / "animal-volunteer"
    res = {"kind": "clean-copy rehearsal (NOT a fresh GitHub clone)", "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
           "host_python": sys.version.split()[0], "platform": platform.platform(), "port": a.port, "steps": {}}
    t_all = time.perf_counter()
    try:
        t = time.perf_counter(); res["files_copied"] = copy_tree(proj); res["steps"]["copy_s"] = round(time.perf_counter() - t, 2)
        res["dist_present"] = (proj / "frontend/dist/index.html").is_file()
        res["node_modules_present"] = (proj / "frontend/node_modules").exists()
        t = time.perf_counter()
        subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=proj, check=True)
        res["steps"]["venv_s"] = round(time.perf_counter() - t, 2)
        t = time.perf_counter()
        pip = subprocess.run([str(proj / ".venv/bin/pip"), "install", "-q", "-r", "requirements.txt"], cwd=proj,
                             capture_output=True, text=True)
        res["steps"]["pip_install_s"] = round(time.perf_counter() - t, 2)
        res["pip_ok"] = pip.returncode == 0
        res["venv_python"] = subprocess.run([str(proj / ".venv/bin/python"), "--version"], capture_output=True,
                                            text=True).stdout.strip()
        # a) no credentials anywhere supported
        proc, s = start_server(proj, a.port); res["steps"]["server_start_no_key_s"] = s
        res["no_key"] = check(a.port, assistant=False)
        st, r = post(f"http://127.0.0.1:{a.port}/api/assistant", {"message": "SYNTHETIC: hi"})
        res["no_key"]["assistant_error"] = r["error"]
        proc.terminate(); proc.wait()
        # b) project-root .env (key written without printing)
        (proj / ".env").write_text(f"PORTKEY_API_KEY={key}\n"); os.chmod(proj / ".env", 0o600)
        proc, s = start_server(proj, a.port); res["steps"]["server_start_project_env_s"] = s
        res["project_env"] = check(a.port, assistant=True, stage="project .env")
        proc.terminate(); proc.wait()
        # c) parent-folder .env only
        (proj / ".env").unlink()
        (subs / ".env").write_text(f"PORTKEY_API_KEY={key}\n"); os.chmod(subs / ".env", 0o600)
        proc, s = start_server(proj, a.port); res["steps"]["server_start_parent_env_s"] = s
        res["parent_env"] = check(a.port, assistant=True, stage="parent .env")
        proc.terminate(); proc.wait()
    finally:
        for f in (proj / ".env", subs / ".env"):
            if f.exists():
                f.unlink()
        res["temp_env_files_deleted"] = not (proj / ".env").exists() and not (subs / ".env").exists()
        res["total_automated_s"] = round(time.perf_counter() - t_all, 2)
        res["note"] = ("Automated time includes two real assistant requests. Manual credential placement (creating one "
                       ".env file) is not timed and was simulated by the script.")
        out = SRC / "output" / "setup_rehearsal"
        out.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(res, indent=2)
        assert key not in blob
        (out / "clean_copy_rehearsal.json").write_text(blob + "\n")
        print(blob)
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    main()
