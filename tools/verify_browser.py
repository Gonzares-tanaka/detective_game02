"""Run the exported game in Edge with real keyboard and emulated touch events.

Requires optional playwright package and an installed Microsoft Edge. Tests do
not alter game state through Python; the runtime is read only for assertions.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
from pathlib import Path
import sys
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_game import PATHS


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


STATE_JS = """() => window.pyxelContext.pyodide.runPython(`
import gc, json
_kent_test_app = next(obj for obj in gc.get_objects() if type(obj).__name__ == 'App' and hasattr(obj, 'scene_id'))
json.dumps({'mode': _kent_test_app.mode, 'scene': _kent_test_app.scene_id,
  'choice': _kent_test_app.selected_choice, 'visible': _kent_test_app.visible_chars,
  'length': len(_kent_test_app.message), 'page': _kent_test_app.page_index,
  'frame': __import__('pyxel').frame_count,
  'choice_targets': [c['to'] for c in _kent_test_app.choices],
  'source_targets': [c['to'] for c in _kent_test_app.scene.get('choices', [])],
  'subtitle': _kent_test_app.data['subtitle'],
  'palette_colors': len(__import__('pyxel').colors),
  'mouse': [__import__('pyxel').mouse_x, __import__('pyxel').mouse_y]})
`)"""


def state(page):
    return json.loads(page.evaluate(STATE_JS))


def start(page, url, touch=False):
    # Detailed input tests run the same standalone game embedded by index.html.
    page.goto(url.rstrip("/") + "/game.html")
    page.locator("#start-button").click()
    print("Loading Pyxel WASM...", flush=True)
    try:
        page.wait_for_selector("canvas", timeout=60000)
    except Exception:
        page.screenshot(path=str(ROOT / "verification/web_load_failure.png"))
        print("Page text:", page.locator("body").inner_text(), flush=True)
        raise
    page.locator("#pyxel-prompt").wait_for(state="visible", timeout=60000)
    if touch:
        page.locator("canvas").first.tap()
    else:
        page.locator("canvas").first.click()
    page.wait_for_function("""() => {
      try { return window.pyxelContext?.pyodide?.runPython('import pyxel; pyxel.frame_count > 5'); }
      catch (e) { return false; }
    }""", timeout=45000)
    assert state(page)["mode"] == "title", state(page)


def key(page, name="Enter"):
    page.keyboard.press(name, delay=45)
    page.wait_for_timeout(38)


def touch_at(page, x, y):
    canvas = page.locator("canvas").first
    box = canvas.bounding_box()
    page.touchscreen.tap(box["x"] + x / 320 * box["width"], box["y"] + y / 240 * box["height"])
    page.wait_for_timeout(85)


def verify():
    output = ROOT / "verification"
    output.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "web")))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    report = {"browser": "Microsoft Edge headless", "keyboard_paths": [], "touch_emulation": {}}
    started = time.monotonic()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 960, "height": 720})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda msg: print("Browser:", msg.text[:300], flush=True) if msg.type == "error" else None)
            page.on("requestfailed", lambda request: print("Request failed:", request.url, request.failure, flush=True))
            start(page, f"http://127.0.0.1:{server.server_port}/")
            report["palette_colors"] = state(page)["palette_colors"]
            report["runtime_pyxapp_sha256"] = hashlib.sha256((ROOT / "dist/kent_case2.pyxapp").read_bytes()).hexdigest()
            page.screenshot(path=str(output / "web_desktop_title.png"))
            assert state(page)["subtitle"] == "～名探偵の家族～"
            report["subtitle"] = state(page)["subtitle"]
            report["initial_choice_orders"] = []
            for choices, target, ending in ([] if "--touch-only" in sys.argv else PATHS):
                print(f"Keyboard route: {target}", flush=True)
                assert state(page)["mode"] == "title"
                key(page)
                pending = iter(choices)
                count = 0
                for _ in range(1000):
                    current = state(page)
                    if current["mode"] in ("game_over", "game_clear"):
                        break
                    if current["mode"] == "choice":
                        desired = current["source_targets"][next(pending)]
                        selected = current["choice_targets"].index(desired)
                        count += 1
                        if count == 1:
                            report["initial_choice_orders"].append(current["choice_targets"])
                        if selected:
                            key(page, "ArrowDown")
                            assert state(page)["choice"] == 1
                    key(page)
                else:
                    raise AssertionError("Web route did not terminate")
                assert current["scene"] == target and current["mode"] == ending, current
                assert count == len(choices)
                if ending == "game_clear":
                    page.screenshot(path=str(output / f"web_{target}.png"))
                key(page)
                assert state(page)["mode"] == "title"
                report["keyboard_paths"].append(target)
            page.close()

            mobile = browser.new_page(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True,
                                      device_scale_factor=1)
            mobile.on("pageerror", lambda error: errors.append(str(error)))
            start(mobile, f"http://127.0.0.1:{server.server_port}/", touch=True)
            touch_at(mobile, 150, 216)
            assert state(mobile)["mode"] == "story"
            for _ in range(50):
                if state(mobile)["mode"] == "choice":
                    break
                touch_at(mobile, 150, 180)
            assert state(mobile)["mode"] == "choice"
            mobile.screenshot(path=str(output / "web_mobile_portrait.png"))
            portrait_box = mobile.locator("canvas").first.bounding_box()
            assert abs(portrait_box["width"] / portrait_box["height"] - 4 / 3) < 0.02
            expected = state(mobile)["choice_targets"][0]
            touch_at(mobile, 150, 160)
            assert state(mobile)["scene"] == expected, state(mobile)
            for _ in range(100):
                if state(mobile)["mode"] == "choice":
                    break
                touch_at(mobile, 150, 180)
            assert state(mobile)["mode"] == "choice"
            # Exercise both rows and follow their actual, shuffled targets.
            expected = state(mobile)["choice_targets"][1]
            touch_at(mobile, 150, 200)
            assert state(mobile)["scene"] == expected
            before = state(mobile)
            touch_at(mobile, 150, 180)
            after = state(mobile)
            assert before != after
            mobile.set_viewport_size({"width": 844, "height": 390})
            mobile.wait_for_timeout(250)
            box = mobile.locator("canvas").first.bounding_box()
            assert box["x"] >= -1 and box["y"] >= -1
            assert box["width"] <= 845 and box["height"] <= 391
            assert abs(box["width"] / box["height"] - 4 / 3) < 0.02
            mobile.screenshot(path=str(output / "web_mobile_landscape.png"))
            report["touch_emulation"] = {"title_start": True, "text_advance": True,
                "second_choice": True, "first_choice": True, "shuffled_targets_match": True,
                "portrait": [390, 844], "landscape": [844, 390], "canvas_fits_4_3": True}
            report["javascript_errors"] = errors
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        report["elapsed_seconds"] = round(time.monotonic() - started, 1)
        report_file = "browser_touch_report.json" if "--touch-only" in sys.argv else "browser_report.json"
        (output / report_file).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    verify()
