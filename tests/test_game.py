"""Exercise both complete routes and every failure via the actual Pyxel App."""
import json
from itertools import product
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pyxel
import main
from novel import SelectHold, load_story, paginate

# All complete paths, including the initial route selection.
PATHS = [
    ([0, 1], "over_metro", "game_over"),
    ([0, 0, 1], "over_wine", "game_over"),
    ([0, 0, 0, 1], "over_guard", "game_over"),
    ([0, 0, 0, 0, 1], "over_degree", "game_over"),
    ([0, 0, 0, 0, 0], "thief_clear", "game_clear"),
    ([1, 1], "over_bath", "game_over"),
    ([1, 0, 1], "over_maid", "game_over"),
    ([1, 0, 0, 1], "over_bill", "game_over"),
    ([1, 0, 0, 0, 1], "over_sayori", "game_over"),
    ([1, 0, 0, 0, 0], "love_clear", "game_clear"),
]


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = main.App(headless=True, autorun=False)

    def setUp(self):
        self.app.gkd = True
        self.app.quit_hold = SelectHold()
        self.app.return_to_title()
        self.app.choice_orders = {sid: list(range(len(scene.get("choices", []))))
                                  for sid, scene in self.app.data["scenes"].items()}

    def tick(self, pressed=(), held=(), now=0, mouse=(0, 0)):
        with patch.object(pyxel, "btnp", side_effect=lambda key, *args: key in pressed), \
             patch.object(pyxel, "btn", side_effect=lambda key: key in held), \
             patch.object(main.time, "monotonic", return_value=now), \
             patch.object(pyxel, "mouse_x", mouse[0]), patch.object(pyxel, "mouse_y", mouse[1]), \
             patch.object(pyxel, "quit") as quit_game:
            self.app.update()
            return quit_game.called

    def test_all_ten_paths_from_title_back_to_title(self):
        visited = set()
        for reverse, (choices, target, ending) in product((False, True), PATHS):
            with self.subTest(target=target, reverse=reverse), patch.object(
                    main.random, "shuffle", side_effect=lambda order: order.reverse() if reverse else None):
                self.app.return_to_title()
                self.tick([pyxel.GAMEPAD1_BUTTON_A])
                pending = iter(choices)
                seen_choices = 0
                for _ in range(1000):
                    visited.add(self.app.scene_id)
                    self.app.draw()
                    if self.app.mode in ("game_over", "game_clear"):
                        break
                    if self.app.mode == "choice":
                        seen_choices += 1
                        desired = self.app.scene["choices"][next(pending)]["to"]
                        displayed = next(i for i, c in enumerate(self.app.choices) if c["to"] == desired)
                        if displayed:
                            self.tick([pyxel.GAMEPAD1_BUTTON_DPAD_DOWN])
                    self.tick([pyxel.GAMEPAD1_BUTTON_A])
                else:
                    self.fail("Story did not terminate")
                self.assertEqual(seen_choices, len(choices))
                self.assertEqual(self.app.scene_id, target)
                self.assertEqual(self.app.mode, ending)
                self.app.draw()
                self.tick([pyxel.GAMEPAD1_BUTTON_A])
                self.assertEqual(self.app.mode, "title")
                self.assertEqual(self.app.page_index, 0)
        self.assertEqual(visited, set(self.app.data["scenes"]))

    def test_every_page_and_choice_fits_without_truncation(self):
        for sid, scene in self.app.data["scenes"].items():
            self.app.change_scene(sid)
            self.assertEqual("".join(p.replace("\n", "") for p in self.app.pages[sid]),
                             "".join(p.replace("\n", "") for p in scene["pages"]))
            for index, page in enumerate(self.app.pages[sid]):
                lines = page.split("\n")
                self.assertLessEqual(len(lines), 4, (sid, index))
                for line in lines:
                    self.assertLessEqual(self.app.font.text_width(line), 276, (sid, line))
                self.app.page_index = index
                self.app.visible_chars = len(page)
                self.app.draw()
            for lines in self.app.choice_lines[sid]:
                self.assertLessEqual(len(lines), 2)
                for line in lines:
                    self.assertLessEqual(self.app.font.text_width(line), 252)
            if "ending" in scene:
                self.assertLessEqual(self.app.font.text_width(scene["end_caption"]), 280)
            self.assertEqual((self.app.images[scene["background"]].width,
                              self.app.images[scene["background"]].height), (256, 100))

    def test_long_external_text_is_split_into_pages(self):
        source = "長い文章も途中で消えずに次のページへ送られる。" * 50
        pages = paginate([source], self.app.font.text_width)
        self.assertGreater(len(pages), 2)
        self.assertEqual("".join(p.replace("\n", "") for p in pages), source)
        self.assertTrue(all(len(p.split("\n")) <= 4 for p in pages))

    def test_a_reveals_then_advances(self):
        self.tick([pyxel.GAMEPAD1_BUTTON_A])
        self.assertEqual(self.app.mode, "story")
        self.tick([pyxel.GAMEPAD1_BUTTON_A])
        self.assertEqual(self.app.page_index, 0)
        self.assertEqual(self.app.visible_chars, len(self.app.message))
        self.tick([pyxel.GAMEPAD1_BUTTON_A])
        self.assertEqual(self.app.page_index, 1)

    def test_all_four_directions_and_number_shortcuts(self):
        for key in (pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                    pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                    pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.app.change_scene("intro")
            self.app.mode = "choice"
            self.tick([key])
            self.assertEqual(self.app.selected_choice, 1)
            self.tick([pyxel.GAMEPAD1_BUTTON_A])
            self.assertEqual(self.app.scene_id, "love_intro")
        self.app.change_scene("intro")
        self.app.mode = "choice"
        self.tick([pyxel.KEY_1])
        self.assertEqual(self.app.scene_id, "thief_brief")

    def test_keyboard_and_direct_touch(self):
        for key in (pyxel.KEY_SPACE, pyxel.KEY_RETURN, pyxel.MOUSE_BUTTON_LEFT):
            self.app.gkd = False
            self.app.return_to_title()
            self.tick([key], mouse=(100, 100))
            self.assertEqual(self.app.mode, "story")
        self.app.mode = "choice"
        # Touch chooses the touched button even when another one is selected.
        expected = self.app.choices[1]["to"]
        self.tick([pyxel.MOUSE_BUTTON_LEFT], mouse=(140, 200))
        self.assertEqual(self.app.scene_id, expected)
        self.app.change_scene("intro")
        self.app.mode = "choice"
        self.tick([pyxel.MOUSE_BUTTON_LEFT], mouse=(10, 185))
        self.assertEqual(self.app.mode, "choice")
        self.assertIsNone(self.app.choice_at(12, 182))
        self.assertTrue(self.tick([pyxel.KEY_ESCAPE]))

    def test_select_only_long_hold_from_every_screen(self):
        back = pyxel.GAMEPAD1_BUTTON_BACK
        for mode in ("title", "story", "choice", "game_over", "game_clear"):
            self.app.mode = mode
            self.app.quit_hold = SelectHold()
            self.assertFalse(self.tick(held=[back], now=10))
            self.assertFalse(self.tick(held=[back], now=10.99))
            self.assertTrue(self.tick(held=[back], now=11))

    def test_select_chord_never_quits_until_select_released(self):
        back, a = pyxel.GAMEPAD1_BUTTON_BACK, pyxel.GAMEPAD1_BUTTON_A
        for direction in (pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN,
                          pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT,
                          pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                          pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER, pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER):
            self.app.return_to_title()
            self.app.quit_hold = SelectHold()
            self.assertFalse(self.tick(held=[back], now=0))
            self.assertFalse(self.tick([a, direction], [back, direction], now=0.8))
            self.assertFalse(self.tick([a], [back], now=100))
            self.assertEqual(self.app.mode, "title")
            self.tick(now=101)
            self.assertFalse(self.tick(held=[back], now=102))
            self.assertTrue(self.tick(held=[back], now=103))

    def test_title_has_no_background_or_sound_switch(self):
        self.app.gkd = False
        with patch.object(pyxel, "blt") as draw_image, patch.object(pyxel, "text") as draw_text:
            self.app.draw()
            draw_image.assert_not_called()
            text = [call.args[2] for call in draw_text.call_args_list]
            self.assertIn("～名探偵の家族～", text)
            self.assertNotIn("BGM", text)
            self.assertNotIn("OFF", text)
        with patch.object(pyxel, "stop") as stop:
            self.tick([pyxel.KEY_M])
            self.assertEqual(self.app.mode, "title")
            stop.assert_not_called()
        # The former sound button area is now an ordinary start tap.
        self.tick([pyxel.MOUSE_BUTTON_LEFT], mouse=(300, 12))
        self.assertEqual(self.app.mode, "story")

    def test_order_is_stable_during_play_and_rebuilt_on_restart(self):
        source = json.dumps(self.app.data, ensure_ascii=False, sort_keys=True)
        with patch.object(main.random, "shuffle", side_effect=lambda order: order.reverse()) as shuffle:
            self.tick([pyxel.GAMEPAD1_BUTTON_A])
            self.assertEqual(shuffle.call_count, len(self.app.data["scenes"]))
            first = {sid: list(order) for sid, order in self.app.choice_orders.items()}
            self.assertEqual(first["intro"], [1, 0])
            self.app.page_index = len(self.app.pages["intro"]) - 1
            self.app.visible_chars = len(self.app.message)
            self.tick([pyxel.GAMEPAD1_BUTTON_A])
            for _ in range(4):
                self.app.draw()
                self.tick()
            self.assertEqual(self.app.mode, "choice")
            self.assertEqual(self.app.choice_orders, first)
            self.assertEqual(shuffle.call_count, len(self.app.data["scenes"]))
        self.app.return_to_title()
        with patch.object(main.random, "shuffle"):
            self.tick([pyxel.GAMEPAD1_BUTTON_A])
        self.assertEqual(self.app.choice_orders["intro"], [0, 1])
        self.assertEqual(json.dumps(self.app.data, ensure_ascii=False, sort_keys=True), source)

    def test_shuffled_labels_and_touch_targets_match_in_every_scene(self):
        self.app.gkd = False
        with patch.object(main.random, "shuffle", side_effect=lambda order: order.reverse()):
            self.app.start_game()
        for sid, scene in self.app.data["scenes"].items():
            if not scene.get("choices"):
                continue
            for displayed in (0, 1):
                self.app.change_scene(sid)
                self.app.mode = "choice"
                expected = scene["choices"][1 - displayed]
                self.assertEqual(self.app.choices[displayed], expected)
                with patch.object(pyxel, "text") as draw_text:
                    self.app.draw()
                    rendered = [call.args[2] for call in draw_text.call_args_list]
                    for line in self.app.choice_lines[sid][1 - displayed]:
                        self.assertIn(line, rendered)
                self.tick([pyxel.MOUSE_BUTTON_LEFT], mouse=(140, 160 + 42 * displayed))
                self.assertEqual(self.app.scene_id, expected["to"])

    def test_external_scenario_rejects_broken_targets(self):
        data = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))
        data["scenes"]["intro"]["choices"][0]["to"] = "missing"
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            path = Path(temp) / "story.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing"):
                load_story(path)

    def test_missing_background_still_runs(self):
        image = self.app.load_background("assets/backgrounds/NOT_FOUND.png")
        self.assertEqual((image.width, image.height), (256, 100))


if __name__ == "__main__":
    unittest.main()
