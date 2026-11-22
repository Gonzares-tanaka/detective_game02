# 探偵ケントの事件簿2 — GKD Pixel 2版

前作のREADME_GKD.mdに記載された環境（aarch64、Python 3.11.7、Pyxel 2.9.9、plumOS）を
基準にした構成です。**第2作のGKD実機動作は未確認**です。PC上の入力シミュレーションと区別してください。

## 配置と起動

`dist/detective_kent2_gkd.zip` を展開し、`roms/ports/` の中身を
本体の `/storage/roms/ports/` にコピーします。前作とは別名で共存できます。

```text
/storage/roms/ports/
  Detective_Kent2.sh
  Detective_Kent2/
    main.py
    novel.py
    story.json
    assets/
      PixelMplus12-Regular.ttf
      FONT_LICENSE.txt
      backgrounds/ (13枚)
```

Portsから `Detective_Kent2` を選びます。スクリプトとゲームフォルダを隣に配置してください。
標準Pythonは `/storage/pyxel_Python/bin/python3`。
別の場所にある場合は起動スクリプト内の既定値を変更するか、
環境変数 `DETECTIVE_KENT2_PYTHON` で指定できます。
ゲーム内の台詞や背景の差し替えにスクリプト編集は不要です。

起動ログは `roms/ports/detective_kent2_launch.log` に出力します。
ランチャーはLF・UTF-8 BOMなし、ZIP内で実行権限付きです。
必要なら `chmod +x /storage/roms/ports/Detective_Kent2.sh` を実行します。
Python環境自体は同梱せず、前作同様に本体のPyxel環境を使います。

## 操作

| 操作 | ボタン |
|---|---|
| 開始・文字の全表示・次ページ・決定 | A |
| 2択の切替 | 十字キー上下（左右も可） |
| ゲームオーバー／クリアからタイトルへ | A |
| 終了してPortsへ戻る | SELECT単独を約1秒長押し |

各2択の表示順はタイトルから開始するたびにランダムに決まり、プレイ中は固定されます。
BGMは自動再生です。ゲーム内のON/OFFボタンはなく、音量は本体側で調整します。

SELECT＋十字キーは本体の音量・明るさ操作用に残します。
同時押し中はゲーム進行を止め、いったん同時押しになったらSELECTを離すまで終了しません。
そのため十字キーを先に離しても誤終了しません。終了したい場合はSELECTをいったん離し、
改めてSELECTだけを1秒押してください。終了時のセーブはありません。

PyxelではAを `GAMEPAD1_BUTTON_A`、SELECTを `GAMEPAD1_BUTTON_BACK` として扱っています。
本体環境で割り当てが異なる場合は、OS側のゲームパッド設定を確認してください。

## 表示と初回の実機確認

320×240の4:3画面。背景は256×100をそのまま表示し、下部に日本語12pxの文章・選択肢を置きます。
`--gkd` 指定時のみ整数拡大・全画面表示を有効にします。
640×480表示環境では2倍で画面に収まる設計です。実際の液晶での可読性は未確認です。

初回に以下を実機で確認してください。

1. Portsから起動し、日本語・背景・BGMが表示／再生される。
2. Aで開始し、十字キーで上下両方の選択肢へ動き、Aで決定できる。
3. SELECT＋各方向で本体の音量・明るさを調整でき、ゲームは進行・終了しない。
4. 十字キーを先に離してSELECTを保持しても終了せず、離してからSELECT単独1秒なら終了する。
5. 両ルートのクリア／ゲームオーバーからAでタイトルへ戻れる。

## 編集・再生成

台詞・選択肢・行き先は `story.json`、背景は `assets/backgrounds/*.png` を差し替えます。
背景は人物なし256×100のPNG。詳しい形式と例は [README.md](README.md) を参照してください。
同梱の本画像は `assets/background_palette.json` の240色とUI用16色を合わせて表示します。
PNGを差し替えた場合はPCで `python tools/prepare_backgrounds.py` を実行して色定義を更新できます。
本体上で編集した場合はゲームを再起動してください。
PC側で編集後 `build_web.cmd` または `python tools/build_release.py` を実行し、
新しいZIPの中身をコピーしても更新できます。

Web版とPC版も同じ `main.py` / `novel.py` / `story.json` / 素材を使用します。
PCの `python main.py --gkd` は表示設定の予行確認用で、実機確認の代わりにはなりません。
