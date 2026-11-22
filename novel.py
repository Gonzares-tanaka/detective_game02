"""Scenario loading and pagination. No Pyxel dependency; content lives in story.json."""
import json
from pathlib import Path


def load_story(path):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    scenes = data["scenes"]
    if data["start"] not in scenes:
        raise ValueError("start: 存在しないシーンです")
    for sid, scene in scenes.items():
        if not scene.get("pages") or not all(isinstance(p, str) and p.strip() for p in scene["pages"]):
            raise ValueError(f"{sid}: pages は空でない文字列の配列にしてください")
        if not scene.get("title") or scene.get("background") not in data["backgrounds"]:
            raise ValueError(f"{sid}: title/background を確認してください")
        if sum(bool(scene.get(k)) for k in ("choices", "next", "ending")) != 1:
            raise ValueError(f"{sid}: choices / next / ending のどれか一つが必要です")
        if scene.get("ending") not in (None, "game_over", "game_clear"):
            raise ValueError(f"{sid}: ending が不正です")
        choices = scene.get("choices", [])
        if choices and (len(choices) != 2 or any(not c.get("label") for c in choices)):
            raise ValueError(f"{sid}: 選択肢は label/to を持つ2択にしてください")
        for target in [c["to"] for c in choices] + ([scene["next"]] if "next" in scene else []):
            if target not in scenes:
                raise ValueError(f"{sid}: 遷移先 {target} がありません")
    for key, name in data["backgrounds"].items():
        file = Path(name)
        if file.is_absolute() or ".." in file.parts:
            raise ValueError(f"背景 {key}: プロジェクト内の相対パスを指定してください")
    # A typo must not silently strand a scene or create an endless story loop.
    visited, active = set(), set()

    def visit(sid):
        if sid in active:
            raise ValueError(f"シナリオに循環があります: {sid}")
        if sid in visited:
            return
        active.add(sid)
        scene = scenes[sid]
        for target in [c["to"] for c in scene.get("choices", [])] + ([scene["next"]] if "next" in scene else []):
            visit(target)
        active.remove(sid)
        visited.add(sid)

    visit(data["start"])
    if visited != set(scenes):
        raise ValueError(f"到達できないシーン: {set(scenes) - visited}")
    return data


def wrap_text(text, measure, width):
    """Wrap using the actual font metrics, with basic Japanese kinsoku rules."""
    lines = []
    forbidden_start = "、。，．！？!?ーゃゅょぁぃぅぇぉっャュョァィゥェォッ）」』】〉》…"
    forbidden_end = "（「『【〈《"
    for paragraph in text.split("\n"):
        current = ""
        for char in paragraph:
            if current and measure(current + char) > width:
                carry = ""
                if char in forbidden_start or current[-1] in forbidden_end:
                    carry, current = current[-1], current[:-1]
                if current:
                    lines.append(current)
                current = carry
            current += char
        lines.append(current)
    return lines


def paginate(paragraphs, measure, width=276, rows=4):
    pages = []
    for paragraph in paragraphs:
        lines = wrap_text(paragraph, measure, width)
        pages.extend("\n".join(lines[i:i + rows]) for i in range(0, len(lines), rows))
    return pages


class SelectHold:
    """Any SELECT chord cancels quitting until SELECT has been released."""
    def __init__(self):
        self.started = None
        self.cancelled = False

    def update(self, select, other_button, now):
        if not select:
            self.started = None
            self.cancelled = False
            return False
        if other_button:
            self.cancelled = True
            self.started = None
        if self.cancelled:
            return False
        if self.started is None:
            self.started = now
        return now - self.started >= 1.0
