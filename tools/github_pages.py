"""Inspect or enable this repository's GitHub Pages using existing Git credentials.

Tokens stay in process memory and are never printed, written to files, or put
in command-line arguments. This helper only addresses the requested repository.
"""
import argparse
import json
import os
import subprocess
import urllib.error
import urllib.request

REPOSITORY = "Gonzares-tanaka/detective_game02"


def credential():
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run(
        ["git", "credential", "fill"],
        input=f"protocol=https\nhost=github.com\nusername=Gonzares-tanaka\npath={REPOSITORY}.git\n\n",
        text=True, capture_output=True, env=env, timeout=30)
    if result.returncode:
        raise RuntimeError("No existing GitHub credential is available through Git Credential Manager.")
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    token = fields.get("password")
    if not token:
        raise RuntimeError("Git Credential Manager did not return an access token.")
    return token


def request(token, suffix, method="GET", body=None):
    url = f"https://api.github.com/repos/{REPOSITORY}/{suffix}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2026-03-10", "User-Agent": "Kent-Case2-Pages"}
    raw = None if body is None else json.dumps(body).encode("utf-8")
    if raw is not None:
        headers["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, raw, headers, method=method), timeout=30) as response:
            content = response.read()
            return response.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as error:
        try:
            data = json.loads(error.read())
        except ValueError:
            data = {"message": "GitHub returned a non-JSON error."}
        return error.code, {"message": data.get("message"), "documentation_url": data.get("documentation_url")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "enable", "build"), nargs="?", default="status")
    args = parser.parse_args()
    token = credential()
    code, data = request(token, "pages")
    if args.action == "enable":
        source = {"branch": "main", "path": "/"}
        if code == 404:
            code, data = request(token, "pages", "POST", {"source": source, "build_type": "legacy"})
        elif code == 200 and (data.get("source") != source or data.get("build_type") != "legacy"):
            code, data = request(token, "pages", "PUT", {"source": source, "build_type": "legacy"})
    elif args.action == "build" and code == 200:
        build_code, build = request(token, "pages/builds/latest")
        print(json.dumps({"http_status": build_code, "build_status": build.get("status"),
                          "commit": build.get("commit"), "error": build.get("error"),
                          "message": build.get("message")}, ensure_ascii=False))
        return
    print(json.dumps({"http_status": code, "url": data.get("html_url"), "status": data.get("status"),
                      "source": data.get("source"), "build_type": data.get("build_type"),
                      "message": data.get("message")}, ensure_ascii=False))
    if code not in (200, 201, 204, 404) or (args.action == "enable" and code == 404):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
