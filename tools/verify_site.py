"""Verify the introduction page and its embedded Pyxel player at a Pages subpath."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from verify_browser import state


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def translate_path(self, path):
        if path.startswith("/detective_game02/"):
            path = path[len("/detective_game02"):]
        return super().translate_path(path)


def game_frame(page):
    return page.locator("#game-frame").element_handle().content_frame()


def start_game(page, frame, touch=False):
    frame.locator("#start-button").click()
    frame.wait_for_selector("canvas", timeout=90000)
    frame.locator("#pyxel-prompt").wait_for(state="visible", timeout=60000)
    if touch:
        frame.locator("canvas").first.tap()
    else:
        frame.locator("canvas").first.click()
    frame.wait_for_function("""() => {
      try { return window.pyxelContext?.pyodide?.runPython('import pyxel; pyxel.frame_count > 5'); }
      catch (_) { return false; }
    }""", timeout=45000)
    assert state(frame)["mode"] == "title"


def tap(page, frame, x, y):
    box = frame.locator("canvas").first.bounding_box()
    page.touchscreen.tap(box["x"] + x / 320 * box["width"], box["y"] + y / 240 * box["height"])
    page.wait_for_timeout(100)


def check_page(page):
    assert page.title() == json.loads((ROOT / "story.json").read_text(encoding="utf-8"))["title"]
    assert page.locator(".character").count() == 9
    for section in ("#story", "#controls", "#characters", "#play"):
        assert page.locator(section).count() == 1
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Horizontal overflow"
    assert page.locator("a[download]").get_attribute("href").endswith("dist/detective_kent2_gkd.zip")


def verify():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    local_url = f"http://127.0.0.1:{server.server_port}/detective_game02/"
    target = ROOT / "verification"
    target.mkdir(exist_ok=True)
    errors, failures = [], []
    report = {"pages_subpath": "/detective_game02/"}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("response", lambda response: failures.append([response.status, response.url]) if response.status >= 400 else None)
            print("Checking desktop introduction and embedded player...", flush=True)
            page.goto(local_url)
            check_page(page)
            page.screenshot(path=str(target / "site_desktop.png"), full_page=True)
            frame = game_frame(page)
            start_game(page, frame)
            page.keyboard.press("Space", delay=80)
            page.wait_for_timeout(150)
            assert state(frame)["mode"] == "story"
            for _ in range(50):
                if state(frame)["mode"] == "choice":
                    break
                page.keyboard.press("Enter", delay=45)
                page.wait_for_timeout(45)
            current = state(frame)
            assert current["mode"] == "choice"
            expected = current["choice_targets"][1]
            page.keyboard.press("ArrowDown", delay=70)
            page.wait_for_timeout(80)
            assert state(frame)["choice"] == 1
            page.keyboard.press("Enter", delay=70)
            page.wait_for_timeout(100)
            assert state(frame)["scene"] == expected
            page.screenshot(path=str(target / "site_desktop_playing.png"))
            page.locator("#fullscreen-button").click()
            page.wait_for_function("document.fullscreenElement?.id === 'player-frame'")
            assert state(frame)["scene"] == expected
            page.evaluate("document.exitFullscreen()")
            page.wait_for_timeout(150)
            report["desktop"] = {"viewport": [1440, 1000], "nine_characters": True,
                                 "embedded_keyboard_play": True, "fullscreen": True, "no_horizontal_overflow": True}
            page.close()

            print("Checking mobile layout and embedded touch...", flush=True)
            mobile = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True)
            mobile.on("pageerror", lambda error: errors.append(str(error)))
            mobile.on("response", lambda response: failures.append([response.status, response.url]) if response.status >= 400 else None)
            mobile.goto(local_url)
            check_page(mobile)
            mobile.screenshot(path=str(target / "site_mobile.png"), full_page=True)
            mobile.locator("#play").scroll_into_view_if_needed()
            frame = game_frame(mobile)
            start_game(mobile, frame, touch=True)
            tap(mobile, frame, 150, 216)
            assert state(frame)["mode"] == "story"
            for _ in range(50):
                if state(frame)["mode"] == "choice":
                    break
                tap(mobile, frame, 150, 180)
            current = state(frame)
            assert current["mode"] == "choice"
            expected = current["choice_targets"][0]
            tap(mobile, frame, 150, 160)
            assert state(frame)["scene"] == expected
            mobile.screenshot(path=str(target / "site_mobile_playing.png"))
            check_page(mobile)
            # The independently served web/ folder uses different relative URLs.
            mobile.goto(local_url + "web/")
            check_page(mobile)
            assert game_frame(mobile).url.endswith("/web/game.html")
            report["mobile"] = {"viewport": [390, 844], "embedded_touch_play": True,
                                "no_horizontal_overflow": True, "web_folder_relative_links": True}
            assert not errors, errors
            assert not failures, failures
            report["javascript_errors"] = errors
            report["http_errors"] = failures
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        (target / "site_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    verify()
