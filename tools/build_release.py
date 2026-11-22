"""Build self-contained Web payload and copy-ready GKD release, using stdlib."""
import base64
import html
import json
from pathlib import Path
import shutil
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def runtime_files():
    return [ROOT / n for n in ("main.py", "novel.py", "story.json")] + sorted(
        p for p in (ROOT / "assets").rglob("*") if p.is_file())


def put(archive, name, data, executable=False):
    info = zipfile.ZipInfo(name)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    archive.writestr(info, data)


def build():
    files = runtime_files()
    story = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    app = dist / "kent_case2.pyxapp"
    with zipfile.ZipFile(app, "w") as archive:
        archive.comment = f"title: {story['title']}\nauthor: Kent Case 2\nversion: 1.0".encode("utf-8")
        put(archive, "kent_case2/.pyxapp_startup_script", b"main.py")
        for file in files:
            put(archive, "kent_case2/" + file.relative_to(ROOT).as_posix(), file.read_bytes())
    shell = (ROOT / "tools/web_shell.html").read_text(encoding="utf-8")
    content = shell.replace("__PYXAPP_BASE64__", base64.b64encode(app.read_bytes()).decode("ascii"))
    for marker, value in (("__GAME_TITLE__", story["title"]),
                          ("__GAME_MAIN_TITLE__", "".join(story["title_lines"])),
                          ("__GAME_SUBTITLE__", story["subtitle"])):
        content = content.replace(marker, html.escape(value))
    web = ROOT / "web"
    web.mkdir(exist_ok=True)
    (web / "game.html").write_text(content, encoding="utf-8", newline="\n")
    landing = (ROOT / "tools/site_shell.html").read_text(encoding="utf-8")
    for marker, value in (("__GAME_TITLE__", story["title"]),
                          ("__GAME_MAIN_TITLE__", "".join(story["title_lines"])),
                          ("__GAME_SUBTITLE__", story["subtitle"])):
        landing = landing.replace(marker, html.escape(value))
    for target, game_url, site_assets, root_prefix in (
            (ROOT / "index.html", "web/game.html", "web/site-assets/", ""),
            (web / "index.html", "game.html", "site-assets/", "../")):
        page = landing.replace("__GAME_URL__", game_url).replace("__SITE_ASSETS__", site_assets)
        page = page.replace("__ROOT_PREFIX__", root_prefix)
        target.write_text(page, encoding="utf-8", newline="\n")
    (web / "site-assets").mkdir(exist_ok=True)
    for name in ("hotel.png", "park.png"):
        shutil.copyfile(ROOT / "assets/backgrounds" / name, web / "site-assets" / name)
    (ROOT / ".nojekyll").write_bytes(b"")
    (web / ".nojekyll").write_bytes(b"")

    release = ROOT / "gkd-release"
    ports = release / "roms/ports"
    game = ports / "Detective_Kent2"
    package = dist / "detective_kent2_gkd.zip"
    with zipfile.ZipFile(package, "w") as archive:
        for file in files:
            relative = file.relative_to(ROOT)
            target = game / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file.read_bytes())
            put(archive, "roms/ports/Detective_Kent2/" + relative.as_posix(), file.read_bytes())
        launcher = (ROOT / "tools/run_gkd.sh").read_bytes().replace(b"\r\n", b"\n")
        (ports / "Detective_Kent2.sh").write_bytes(launcher)
        put(archive, "roms/ports/Detective_Kent2.sh", launcher, executable=True)
        readme = (ROOT / "README_GKD.md").read_bytes()
        (release / "README_GKD.md").write_bytes(readme)
        put(archive, "README_GKD.md", readme)
    print(f"Web: {ROOT / 'web/index.html'}")
    print(f"Standalone game: {web / 'game.html'}")
    print(f"Pyxel: {app}")
    print(f"GKD: {package} ({len(files)} runtime files)")


if __name__ == "__main__":
    build()
