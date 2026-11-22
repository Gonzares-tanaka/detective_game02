"""Verify exported payloads and reference hashes; render UI proof with real Pyxel."""
import ast
import base64
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import struct
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from novel import load_story


def check_archive(archive, prefix):
    sources = [ROOT / n for n in ("main.py", "novel.py", "story.json")] + [
        p for p in (ROOT / "assets").rglob("*") if p.is_file()]
    for path in sources:
        name = prefix + path.relative_to(ROOT).as_posix()
        assert archive.read(name) == path.read_bytes(), name
    return len(sources)


def verify():
    report = {}
    for name in ("main.py", "novel.py"):
        ast.parse((ROOT / name).read_text(encoding="utf-8"), feature_version=(3, 11))
    data = load_story(ROOT / "story.json")
    for name in data["backgrounds"].values():
        raw = (ROOT / name).read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", raw[16:24]) == (256, 100), name
    report["backgrounds_256x100"] = len(data["backgrounds"])
    with zipfile.ZipFile(ROOT / "dist/kent_case2.pyxapp") as archive:
        report["pyxapp_files_checked"] = check_archive(archive, "kent_case2/")
        assert archive.read("kent_case2/.pyxapp_startup_script") == b"main.py"
    with zipfile.ZipFile(ROOT / "dist/detective_kent2_gkd.zip") as archive:
        report["gkd_files_checked"] = check_archive(archive, "roms/ports/Detective_Kent2/")
        launcher = archive.read("roms/ports/Detective_Kent2.sh")
        assert b"\r" not in launcher and not launcher.startswith(b"\xef\xbb\xbf")
        assert archive.getinfo("roms/ports/Detective_Kent2.sh").external_attr >> 16 & 0o111
        assert b"Detective_Kent/" not in launcher
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.targets = []

        def handle_starttag(self, tag, attrs):
            self.targets.extend(value for key, value in attrs if key in ("src", "href") and value)

    for page in (ROOT / "index.html", ROOT / "web/index.html"):
        content = page.read_text(encoding="utf-8")
        assert all(f'id="{section}"' in content for section in ("play", "story", "controls", "characters"))
        assert "__GAME_" not in content and "__ROOT_" not in content and "__SITE_" not in content
        links = Links()
        links.feed(content)
        for target in links.targets:
            if target.startswith(("#", "https://", "http://", "data:")):
                continue
            assert (page.parent / target.split("#")[0]).is_file(), (page, target)
    game_html = (ROOT / "web/game.html").read_text(encoding="utf-8")
    match = re.search(r'base64: "([A-Za-z0-9+/=]+)"', game_html)
    assert match and 'gamepad: "disabled"' in game_html
    assert (ROOT / ".nojekyll").is_file()
    report["landing_pages_and_relative_links"] = True
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(match[1]))) as archive:
        report["embedded_web_files_checked"] = check_archive(archive, "kent_case2/")

    baseline = ROOT / "verification/reference_before.json"
    reference = ROOT.parent / "adventure_test"
    if baseline.exists() and reference.is_dir():
        hashes = json.loads(baseline.read_text(encoding="utf-8"))
        changed = [name for name, digest in hashes.items()
                   if not (reference / name).is_file() or hashlib.sha256((reference / name).read_bytes()).hexdigest() != digest]
        assert not changed, changed
        report["reference_files_unchanged"] = len(hashes)

    import main
    import pyxel
    app = main.App(gkd=True, headless=True, autorun=False)
    report["palette_colors"] = len(pyxel.colors)
    report["game_title"] = app.data["title"]
    report["subtitle"] = app.data["subtitle"]
    output = ROOT / "verification"
    output.mkdir(exist_ok=True)
    screenshots = [("title", "intro", "title"), ("story", "thief_brother", "story"),
                   ("choice", "love_confess", "choice"), ("game_over", "over_wine", "game_over"),
                   ("game_clear", "thief_clear", "game_clear")]
    for name, sid, mode in screenshots:
        app.change_scene(sid)
        app.mode = mode
        app.visible_chars = len(app.message)
        app.draw()
        pyxel.screenshot(str(output / f"{name}.png"), 2)
    app.choice_orders["love_confess"] = [1, 0]
    app.change_scene("love_confess")
    app.mode = "choice"
    app.draw()
    pyxel.screenshot(str(output / "choice_reversed.png"), 2)
    update_baseline = output / "interface_update_baseline.json"
    if update_baseline.is_file():
        baseline = json.loads(update_baseline.read_text(encoding="utf-8"))
        digest = hashlib.sha256(json.dumps(data["scenes"], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        assert digest == baseline["scenes_sha256"], "Scene content changed"
        for name, digest in baseline["png_sha256"].items():
            assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
        report["scene_content_and_artwork_unchanged"] = True
    import_manifest = output / "artwork_import.json"
    if import_manifest.is_file():
        imported = json.loads(import_manifest.read_text(encoding="utf-8"))
        for item in imported:
            assert hashlib.sha256((ROOT / item["file"]).read_bytes()).hexdigest() == item["sha256"]
        report["original_attached_pngs_unchanged"] = len(imported)
    report.update({"python_311_syntax": True, "scenes": len(data["scenes"]),
                   "rendered_pages": sum(map(len, app.pages.values())),
                   "endings": {sid: s["ending"] for sid, s in data["scenes"].items() if "ending" in s},
                   "pyxel_version": pyxel.VERSION,
                   "gkd_hardware_tested": False, "physical_smartphone_tested": False})
    (output / "release_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    verify()
