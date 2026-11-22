# title: 探偵ケントの事件簿2 ～名探偵の家族～
# author: Kent Case 2
# desc: 二つの事件と、だいたい残念な名探偵。
# version: 1.0
from pathlib import Path
import json
import random
import sys
import time

import pyxel
from novel import SelectHold, load_story, paginate, wrap_text

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS = 320, 240, 30
INK, PANEL, MUTED, GOLD, PAPER, TEAL, RED = 0, 1, 2, 3, 4, 5, 6
# Keep the first 16 colors stable for the interface and missing-image fallback.
# An optional external palette adds up to 240 colors for the imported artwork.
PALETTE = [0x101822, 0x1B2836, 0x627783, 0xD4AE68, 0xF3E7CC,
           0x538D91, 0xBC5963, 0x344B59, 0x25323E, 0x766257,
           0xA48869, 0xDBCAA2, 0x273B46, 0x436274, 0x80A7AD, 0xFFFFFF]


def load_palette():
    file = ROOT / "assets/background_palette.json"
    if not file.is_file():
        return PALETTE
    colors = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(colors, list) or len(colors) > 240 or any(
            type(color) is not int or not 0 <= color <= 0xFFFFFF for color in colors):
        raise ValueError("background_palette.json は240色以内のRGB整数の配列にしてください")
    return PALETTE + colors


class App:
    def __init__(self, *, gkd=False, headless=False, autorun=True):
        self.gkd = gkd
        self.data = load_story(ROOT / "story.json")
        pyxel.init(WIDTH, HEIGHT, title=self.data["title"], fps=FPS,
                   quit_key=pyxel.KEY_NONE, headless=headless)
        pyxel.colors[:] = load_palette()
        if gkd and not headless:
            pyxel.integer_scale(True)
            pyxel.fullscreen(True)
        pyxel.mouse(not gkd)
        self.font = pyxel.Font(str(ROOT / "assets/PixelMplus12-Regular.ttf"), 12)
        self.large_font = pyxel.Font(str(ROOT / "assets/PixelMplus12-Regular.ttf"), 24)
        self.pages = {sid: paginate(s["pages"], self.font.text_width)
                      for sid, s in self.data["scenes"].items()}
        self.choice_lines = {}
        for sid, scene in self.data["scenes"].items():
            self.choice_lines[sid] = [wrap_text(c["label"], self.font.text_width, 252)
                                      for c in scene.get("choices", [])]
            if any(len(lines) > 2 for lines in self.choice_lines[sid]):
                raise ValueError(f"{sid}: 選択肢が長すぎます（252px×2行まで）")
            if self.font.text_width(scene["title"]) > 284:
                raise ValueError(f"{sid}: シーン名が長すぎます（284pxまで）")
        self.images = {key: self.load_background(name)
                       for key, name in self.data["backgrounds"].items()}
        self.choice_orders = {sid: list(range(len(scene.get("choices", []))))
                              for sid, scene in self.data["scenes"].items()}
        self.init_audio()
        self.quit_hold = SelectHold()
        self.bgm_kind = ""
        self.last_pointer = (pyxel.mouse_x, pyxel.mouse_y)
        self.return_to_title()
        if autorun:
            pyxel.run(self.update, self.draw)

    def load_background(self, name):
        try:
            picture = pyxel.Image.from_image(str(ROOT / name))
            if (picture.width, picture.height) != (256, 100):
                raise ValueError("背景は256×100ピクセルにしてください")
            return picture
        except Exception as error:
            # Pyxel 2.9.9's native image decoder raises plain Exception for
            # missing/corrupt files. Keep this catch local to optional artwork.
            print(f"仮背景を使用: {name}: {error}")
            picture = pyxel.Image(256, 100)
            picture.rect(0, 0, 256, 100, PANEL)
            picture.rectb(10, 10, 236, 80, MUTED)
            picture.line(10, 70, 245, 70, MUTED)
            return picture

    def init_audio(self):
        pyxel.sounds[0].mml("T240 Q25 @3 V12 O6 L32 C")
        tracks = {
            "title": ("T78 Q80 @1 V36 O4 L8 A4 E A B4 E4 C4 G E D2",
                      "T78 Q90 @0 V24 O2 L4 A E F C D A E E"),
            "common": ("T100 Q65 @1 V28 O4 L8 C E G R E G A R G E D R C4 R4",
                       "T100 Q70 @0 V20 O2 L4 C G A E F C G G"),
            "thief": ("T116 Q55 @1 V32 O4 L8 A C E R D C A R E G B R A4 R4",
                      "T116 Q75 @0 V22 O2 L4 A E A E F C E E"),
            "love": ("T108 Q70 @2 V30 O5 L8 C4 E G E4 D C4 D E G4 E C2",
                     "T108 Q80 @0 V20 O2 L4 C G F C A E G G"),
            "game_over": ("T164 Q42 @1 V40 O4 L8 G >C <B G E C D F E D C4 R4",
                          "T164 Q60 @0 V27 O2 L8 C R G R F R G R C4 R4 C4 R4"),
            "game_clear": ("T132 Q88 @1 V42 O4 L8 C E G >C4 <G8 >C E G4 E8 C4 R4",
                           "T132 Q80 @0 V28 O2 L8 C G C G A E G4 C G >C4 <G4 C2"),
        }
        self.music_ids = {}
        for index, (kind, voices) in enumerate(tracks.items()):
            sounds = [2 + index * 2, 3 + index * 2]
            for sound, mml in zip(sounds, voices):
                pyxel.sounds[sound].mml(mml)
            pyxel.musics[index].set([], [sounds[0]], [sounds[1]])
            self.music_ids[kind] = index

    def play_bgm(self, kind):
        if kind != self.bgm_kind:
            self.bgm_kind = kind
            pyxel.playm(self.music_ids[kind], loop=True)

    @property
    def scene(self):
        return self.data["scenes"][self.scene_id]

    @property
    def message(self):
        return self.pages[self.scene_id][self.page_index]

    @property
    def choices(self):
        """Display order and destinations must always use the same permutation."""
        source = self.scene.get("choices", [])
        return [source[index] for index in self.choice_orders[self.scene_id]]

    def start_game(self):
        # Shuffle once per play, never during drawing or while choosing.
        # Work on indices so the external scenario and its label/target pairs
        # remain unchanged, including when restarting after an ending.
        for sid, scene in self.data["scenes"].items():
            order = list(range(len(scene.get("choices", []))))
            random.shuffle(order)
            self.choice_orders[sid] = order
        self.change_scene(self.data["start"])

    def confirm(self):
        return any(pyxel.btnp(k) for k in
                   (pyxel.KEY_SPACE, pyxel.KEY_RETURN, pyxel.GAMEPAD1_BUTTON_A))

    def pointer(self):
        return not self.gkd and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

    def handle_quit_input(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
            return True
        select = pyxel.btn(pyxel.GAMEPAD1_BUTTON_BACK)
        # Chords must not exit even if the direction is released before SELECT.
        others = [pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
                  pyxel.KEY_SPACE, pyxel.KEY_RETURN]
        others += [getattr(pyxel, "GAMEPAD1_BUTTON_" + name) for name in
                   ("DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "A", "B", "X", "Y", "START",
                    "GUIDE", "LEFTSTICK", "RIGHTSTICK", "LEFTSHOULDER", "RIGHTSHOULDER")]
        if self.quit_hold.update(select, any(pyxel.btn(k) for k in others), time.monotonic()):
            pyxel.quit()
        return select

    def update(self):
        if self.handle_quit_input():
            return
        if self.mode == "title":
            if self.confirm() or self.pointer():
                self.start_game()
        elif self.mode == "story":
            if self.visible_chars < len(self.message):
                self.visible_chars += 1
                char = self.message[self.visible_chars - 1]
                if pyxel.frame_count % 3 == 0 and char not in "\n 、。！？「」…":
                    pyxel.play(0, 0)
            if self.confirm() or self.pointer():
                self.advance()
        elif self.mode == "choice":
            self.update_choice()
        elif self.mode in ("game_over", "game_clear"):
            if self.confirm() or self.pointer() or pyxel.btnp(pyxel.KEY_R):
                self.return_to_title()

    def advance(self):
        if self.visible_chars < len(self.message):
            self.visible_chars = len(self.message)
        elif self.page_index + 1 < len(self.pages[self.scene_id]):
            self.page_index += 1
            self.visible_chars = 0
        elif self.scene.get("choices"):
            self.mode = "choice"
            self.selected_choice = 0
            self.last_pointer = (pyxel.mouse_x, pyxel.mouse_y)
        elif "next" in self.scene:
            self.change_scene(self.scene["next"])
        else:
            self.mode = self.scene["ending"]
            self.play_bgm(self.mode)

    def choice_at(self, x, y):
        for index in range(2):
            top = 146 + index * 42
            if 12 <= x < 308 and top <= y < top + 36:
                return index
        return None

    def update_choice(self):
        previous = any(pyxel.btnp(k, 10, 3) for k in
                       (pyxel.KEY_UP, pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_UP, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
        following = any(pyxel.btnp(k, 10, 3) for k in
                        (pyxel.KEY_DOWN, pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT))
        self.selected_choice = (self.selected_choice + int(following) - int(previous)) % 2
        position = (pyxel.mouse_x, pyxel.mouse_y)
        hovered = self.choice_at(*position)
        if not self.gkd and position != self.last_pointer and hovered is not None:
            self.selected_choice = hovered
        self.last_pointer = position
        for index, key in enumerate((pyxel.KEY_1, pyxel.KEY_2)):
            if pyxel.btnp(key):
                self.choose(index)
                return
        if self.confirm():
            self.choose(self.selected_choice)
        elif self.pointer() and hovered is not None:
            self.choose(hovered)

    def choose(self, index):
        self.change_scene(self.choices[index]["to"])

    def change_scene(self, sid):
        self.scene_id = sid
        self.page_index = self.visible_chars = self.selected_choice = 0
        self.mode = "story"
        self.play_bgm(self.scene.get("music", "common"))

    def return_to_title(self):
        self.scene_id = self.data["start"]
        self.page_index = self.visible_chars = self.selected_choice = 0
        self.mode = "title"
        self.play_bgm("title")

    def centered(self, y, text, color=PAPER, font=None):
        font = font or self.font
        pyxel.text((WIDTH - font.text_width(text)) // 2, y, text, color, font)

    def draw(self):
        pyxel.cls(INK)
        if self.mode == "title":
            self.draw_title()
        else:
            pyxel.text(16, 12, self.scene["title"], PAPER, self.font)
            pyxel.line(16, 27, 304, 27, MUTED)
            pyxel.blt(32, 34, self.images[self.scene["background"]], 0, 0, 256, 100)
            pyxel.rectb(31, 33, 258, 102, MUTED)
            if self.mode == "choice":
                self.draw_choices()
            elif self.mode in ("game_over", "game_clear"):
                self.draw_ending()
            else:
                self.draw_story()

    def draw_title(self):
        pyxel.rectb(8, 8, 304, 224, MUTED)
        pyxel.rectb(11, 11, 298, 218, PANEL)
        pyxel.text(120, 37, "KENT CASE FILES / 02", GOLD)
        pyxel.line(42, 60, 278, 60, GOLD)
        self.centered(77, self.data["title_lines"][0], PAPER, self.large_font)
        self.centered(107, self.data["title_lines"][1], PAPER, self.large_font)
        self.centered(147, self.data["subtitle"], GOLD)
        self.centered(176, "二つの用事。ひとりの名探偵。", MUTED)
        pyxel.line(42, 199, 278, 199, GOLD)
        if pyxel.frame_count % 45 < 34:
            self.centered(216, "Aで開始" if self.gkd else "タッチ／SPACEで開始", GOLD)

    def draw_story(self):
        pyxel.rect(12, 144, 296, 80, PANEL)
        pyxel.rect(12, 144, 2, 80, GOLD)
        for index, line in enumerate(self.message[:self.visible_chars].split("\n")):
            pyxel.text(22, 151 + index * 16, line, PAPER, self.font)
        count = f"{self.page_index + 1:02}/{len(self.pages[self.scene_id]):02}"
        pyxel.text(23, 214, count, MUTED)
        if self.visible_chars >= len(self.message) and pyxel.frame_count % 30 < 22:
            pyxel.tri(288, 214, 296, 214, 292, 219, GOLD)
        pyxel.text(16, 230, "A: NEXT   SELECT HOLD: EXIT" if self.gkd else "TAP / SPACE / ENTER: NEXT", MUTED)

    def draw_choices(self):
        for index, source_index in enumerate(self.choice_orders[self.scene_id]):
            lines = self.choice_lines[self.scene_id][source_index]
            top = 146 + index * 42
            selected = index == self.selected_choice
            pyxel.rect(12, top, 296, 36, 7 if selected else PANEL)
            pyxel.rectb(12, top, 296, 36, GOLD if selected else MUTED)
            pyxel.text(21, top + 14, str(index + 1), GOLD)
            start = top + (36 - 14 * len(lines)) // 2
            for row, line in enumerate(lines):
                pyxel.text(40, start + row * 14, line, PAPER, self.font)
        pyxel.text(16, 230, "D-PAD: SELECT   A: OK" if self.gkd else "TAP / ARROWS + ENTER / 1,2", MUTED)

    def draw_ending(self):
        clear = self.mode == "game_clear"
        pyxel.rect(12, 144, 296, 80, PANEL)
        pyxel.line(24, 145, 296, 145, GOLD if clear else RED)
        self.centered(155, "GAME CLEAR" if clear else "GAME OVER", GOLD if clear else RED, self.large_font)
        self.centered(184, self.scene.get("end_caption", "名探偵の一日は、つづく。"), PAPER)
        self.centered(207, "Aでタイトルへ" if self.gkd else "タッチ／決定／Rでタイトルへ", MUTED)


if __name__ == "__main__":
    App(gkd="--gkd" in sys.argv[1:])
