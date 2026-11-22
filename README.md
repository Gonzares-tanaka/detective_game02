# 名探偵ケントの事件簿2 ～名探偵の家族～

Pyxel製の分岐型サウンドノベル。白いスクリーンしかない探偵事務所から、
ニヤ警部の「怪盗事件」とウテナの「恋物語」へ分岐します。
二つは独立した出来事です。それぞれ4回の2択、合計8種類のゲームオーバーと
2種類のゲームクリアを収録しています。クリアは恋の成就を意味しません。

ブラウザー版：[GitHub Pages](https://gonzares-tanaka.github.io/detective_game02/)

紹介ページには操作方法・あらすじ・登場人物紹介を掲載し、その場でゲームを遊べます。

作業場所は `C:\temp\mypyxel\adventure_2`。
前作 `C:\temp\mypyxel\adventure_test` の `main.py` を台詞の参考に、
`README.md` / `README_GKD.md` を構成・操作の参考にしました。
前作のファイルは編集せず、実行用ファイルも前作への参照を持ちません。
日本語フォントとそのライセンスのみ、前作から新作へコピーしています。

## PCで遊ぶ

Windowsでは **`run.cmd` をダブルクリック**。タイトル画面から始まります。
この作業環境には、新作フォルダ内に動作確認済みの `.venv` を用意しています。

別のPCで初めて使うときはPython 3.11以上をインストールし、`setup.cmd` → `run.cmd`。
Pythonの自動選択が合わなければ、PowerShellで次のように指定できます。

```powershell
.\setup.ps1 -Python "C:\path\to\python.exe"
```

macOS / Linuxでは次のとおりです。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python main.py
```

実行時の依存は **Pyxel 2.9.9のみ**。シナリオ・日本語フォント・背景・BGMが同梱されています。
Pillowは背景の再生成にだけ必要です。通常の起動・パッケージ生成・ゲーム検証には不要です。

## 操作

| 操作 | PC | Web／スマートフォン | GKD Pixel 2 |
|---|---|---|---|
| 開始／文章を全表示／次へ | Space、Enter、クリック | 画面タッチ | A |
| 選択 | 矢印キー（上下左右） | 選択肢を直接タッチ | 十字キー（上下左右） |
| 決定 | Space、Enter、1／2、クリック | 選択肢を直接タッチ | A |
| エンディングからタイトルへ | 決定、クリック、R | 画面タッチ | A |
| 終了 | Esc | タブを閉じる | SELECT単独を約1秒長押し |

文章送りの最初の入力は、そのページの文字を全表示します。次の入力で次ページへ進みます。
選択画面ではボタン以外をタッチしても決定しません。
タイトルは画像を使わない文字中心の画面です。BGMとタイプ音は自動再生し、音量は端末側で調整します。
ゲーム内の音声ON/OFFボタンやMキーによる切替はありません。
タイトルから開始するたびに、最初のルート選択を含む各2択の上下をランダムに並べ替えます。
表示中の順番は固定され、選択肢の文章と遷移先は必ず対になります。ランダムなので同じ順になる場合もあります。
進行の保存・既読スキップはありません。

GKDではSELECTを押している間は文章・選択入力を止めます。
SELECTと十字キーを同時に押した場合、**SELECTを離すまで終了を無効化**します。
十字キーだけ先に離しても終了しません。SELECT＋A等でも単独長押しになりません。
OS側の音量・明るさショートカットをゲームが取得・変更する処理はありません。

## Web版

生成済みの **`index.html`** がGitHub Pages用の紹介・プレイページです。
ローカル配信用にも同じ紹介内容の **`web/index.html`** を用意しています。
`serve_web.cmd` を実行してPCから <http://localhost:8000/> を開いてください。
スマートフォンでは同じWi-Fiから `http://PCのLAN内IP:8000/` へアクセスします。
OSから通信の確認が出る場合は、使うネットワークでPythonへの接続を許可してください。

ページ内のゲーム画面で「タッチしてゲームを読み込む」を押し、Pyxelの読み込み後にもう一度画面をタッチして開始します。
「全画面で遊ぶ」で拡大できます。「ゲーム画面だけで開く」から `web/game.html` を直接開くこともできます。
音声は実際のタッチで有効になります。音量は端末やブラウザー側で調整してください。
縦向き・横向きとも4:3を保って収まり、仮想ゲームパッドは出しません。

シナリオ、画像、フォントはゲーム用の `web/game.html` の中へ埋め込み済みです。
紹介ページの `index.html` からiframeで読み込みます。紹介文とゲーム画面を行き来せずに遊べます。
**Pyxel本体（WASM等）の取得にインターネット接続が必要**で、完全オフライン版ではありません。
CDNは前作と同じPyxel 2.9.9に固定しています。HTMLを直接開くよりHTTPサーバーでの実行を推奨します。
GitHub Pagesはリポジトリ `Gonzares-tanaka/detective_game02` の `main` ブランチ・ルートを公開元にします。
ルートの `.nojekyll` により、生成済みHTMLをそのまま配信する構成です。
今後の更新は、再生成後の `index.html` と `web/`、必要な素材・配布物をコミットしてPushします。

シナリオや背景を変更したら **`build_web.cmd`** を実行してください。
同じ処理で以下を更新します。

- `index.html`（GitHub Pages用の紹介ページ）、`web/index.html`（ローカル配信用の紹介ページ）
- `web/game.html`（画面単独でも遊べるゲーム）、`web/site-assets/`（紹介ページ用背景画像）
- `dist/kent_case2.pyxapp`（Pyxelアプリ）
- `dist/detective_kent2_gkd.zip` と `gkd-release/`（GKD用）

コマンドなら `python tools/build_release.py`。Python標準ライブラリだけで生成できます。

## GKD版

詳しくは [README_GKD.md](README_GKD.md)。
`dist/detective_kent2_gkd.zip` を展開し、`roms/ports/` の中身を本体へコピーします。
第2作用の `Detective_Kent2` という名前なので、前作と並べて置けます。

## 台詞・選択肢・遷移先を編集する

**`story.json`** をUTF-8のテキストとして編集します。Pythonコードの編集は不要です。
Windowsメモ帳、VS Code等で開けます。JSONは末尾の余分なカンマやコメントを許可しません。

```json
"love_clothes": {
  "title": "恋物語／名探偵の服選び",
  "background": "boutique",
  "music": "love",
  "pages": ["サーヤ「私に似合いそうな服、どれだと思います？」"],
  "choices": [
    {"label": "ウテナの意見を聞く", "to": "love_lunch"},
    {"label": "ケントが選ぶ", "to": "over_maid"}
  ]
}
```

| 項目 | 意味 |
|---|---|
| `start` | タイトルから開始するシーンID |
| `title`、`title_lines`、`subtitle` | ウィンドウ名とタイトル画面の文章 |
| `backgrounds` | 背景IDとPNGファイルの相対パスの対応表 |
| `scenes`のキー | 重複しないシーンID |
| シーンの`title` | 画面上部の場所・章名（284pxまで） |
| `pages` | 文章の配列。要素ごとにページを改める |
| `background` | このシーンで使う背景ID |
| `music` | `common`、`love`、`thief`のいずれか |
| `choices` | `label`（表示文）と`to`（遷移先ID）を持つ2択 |
| `next` | 選択肢なしで最後の文章の後に移動する先 |
| `ending` | `game_over` または `game_clear` |
| `end_caption` | エンディング画面の短い一言（280px以内） |

各シーンは`choices` / `next` / `ending`の**いずれか一つ**を持たせます。
遷移先の誤記、到達不能なシーン、循環、空の本文は起動時にエラーとして検出します。
本文は実際の日本語フォント幅で自動折り返しし、**4行を超えたら自動的に次ページへ分割**します。
`\n`で任意の改行もできます。句読点・括弧の簡易禁則処理があります。
選択肢は252px×2行（全角約42字）まで。長すぎる選択肢は切り捨てず、起動時にエラーにします。
シーン名と短い一言は長くしすぎないでください。

PC版は保存後に再起動すれば反映されます。
Web版とGKD用の配布物には **`build_web.cmd` で再生成してから**反映してください。
GKD上の `story.json` を直接編集した場合は再起動で反映されます。

## 背景を差し替える

`assets/backgrounds/` に**人物のいない256×100ピクセルのPNG**を13枚同梱しています。
ユーザー提供の本画像へ差し替え済みです。添付された元のPNGをリサイズ・切り抜きせず保存しています。
事務所・風呂・街・洋服店・飲食店・公園・地下鉄・タクシー車内・ホテル・ケーキ・展示室・
署名の拡大・表彰式の舞台を用意しました。以前の仮背景はローカルの `backups/backgrounds_before_artwork/` に退避しています（Git管理・配布の対象外）。
同じ場所の背景は使い回します。彫像は人型ではなく抽象的な幾何学造形です。

一番簡単な変更方法は**同じ名前のPNGを上書きすること**です。
別名を使う場合は `story.json` の `backgrounds` のパスを変更します。
表示にはUI用16色と本画像用240色を合わせた、最大256色の共通パレットを使います。
`assets/background_palette.json` が本画像用の色定義です。PNGの原本はそのまま保持し、Pyxelへの読み込み時に近い色へ変換します。
そのためフルカラーの原本とゲーム画面には多少の色差があります。
人物なし、解像度256×100、PNGの条件を守ってください。ゲーム内では縮小せずそのまま描画します。
画像の欠損・破損・サイズ不一致があっても、人物のいない枠だけの背景に置き換えて進行できます。
その場合コンソールへ対象ファイルを表示します。配布検証では欠損やサイズ違いをエラーにします。

画像を差し替えた後、色定義と一覧を更新する場合は、次を実行してください。
この処理はPNG原本を変更しません。その後 `build_web.cmd` でWeb・GKD配布版を更新します。

```sh
python -m pip install -r requirements-dev.txt
python tools/prepare_backgrounds.py
```

一覧は `verification/backgrounds.png`。各ファイルと使用シーンの対応は `story.json` で確認できます。
実際の256色表示の一覧は `verification/backgrounds_in_game.png` です。
`tools/make_backgrounds.py` は旧仮背景の生成器です。本画像を上書きするため、通常は実行しないでください。
フォントのライセンスは `assets/FONT_LICENSE.txt`。
BGMはタイトル・共通・怪盗・恋物語・ゲームオーバー・クリアの6曲をMMLで内蔵しています。
タイプ音はチャンネル0、BGMは別チャンネルです。

## 確認方法と確認範囲

`verify.cmd` で自動検証できます。先に配布物を再生成してください。

```sh
python -m unittest discover -s tests -v
python tools/verify_release.py
```

- タイトルから両成功経路と8失敗経路を、選択肢が元の順・逆順の両方で通り、エンディングからタイトルへ戻ること。
- 全26シーンの本文が残り、各ページが4行以内・276px以内に収まること。全選択肢も2行以内。
- PCキー／GKDのA・十字キー／ポインター入力、SELECT長押しと同時押し解除順。
- プレイ開始ごとの選択肢の並べ替え、プレイ中の順序固定、表示文と遷移先の一致。
- タイトルの新しいサブタイトル、背景画像を描画しないこと、音声切替UIがないこと。
- Pyxel 2.9.9による全ページ描画。Python 3.11の構文互換性。
- 全背景サイズ、Web埋め込み・Pyxelアプリ・GKD ZIP内のソース／素材の一致。
- 添付された本画像13枚が元のPNGと同じSHA-256で保持され、256色で描画できること。
- 前作の参照対象62ファイルのSHA-256が作業開始時と同じこと。

`verification/` に描画見本、配布検証結果、ブラウザー検証結果を保存しています。
制作時はEdgeの実ブラウザーで全10経路とタイトル復帰を確認しました。
スマホ相当の390×844／844×390表示では、タッチによる開始・文章送り・ランダムな上下両方の選択肢と
4:3表示を別途確認しています。結果は `verification/browser_report.json` です。
本画像への差し替え後のWeb表示・タッチ再確認は `verification/browser_touch_report.json` に記録しています。
ブラウザー確認を再実行するときは `python -m pip install playwright` 後、
Microsoft EdgeのあるWindowsで `python tools/verify_browser.py`。
ブラウザー側のPython状態を読みながら、実際のキー・タッチイベントで両ルート・全失敗経路を進行させます。
このツールは配布には不要です。
紹介ページと埋め込みプレイヤーの確認は `python tools/verify_site.py`。
PC・スマホ相当の表示、9人の紹介、キー・タッチ・全画面操作、GitHub Pagesと同じサブパスでのリンクを確認します。
`verification/` はローカルの確認用で、Git管理の対象外です。

**GKD Pixel 2実機、物理スマートフォン、macOS／Linuxデスクトップは未確認です。**
PCのヘッドレス描画やブラウザーのタッチエミュレーションは実機の画面・音声・ボタンの確認ではありません。
GKDでは初回に倍率表示、AとSELECTの割り当て、音声、本体の音量・明るさ操作を確認してください。

## ファイル構成

```text
adventure_2/
  main.py                 Pyxel画面・入力・音声
  novel.py                JSON検証・ページ分割・終了入力判定
  story.json              全台詞・2択・遷移・背景割り当て
  assets/                 フォントと256×100のPNG背景
  run.cmd / setup.cmd     PC起動・初回セットアップ
  build_web.cmd           Web／GKD／Pyxelアプリを再生成
  serve_web.cmd           web/ だけを配信
  verify.cmd              経路・入力・表示・配布物の検証
  tools/                  生成・検証用スクリプト
  tests/                  両ルート全経路の回帰検証
  index.html              GitHub Pagesの紹介・プレイページ
  web/index.html          ローカル配信用の紹介ページ
  web/game.html           iframeで埋め込むゲーム本体
  web/site-assets/        紹介ページ用の画像
  dist/                   .pyxappとGKD ZIP
  gkd-release/            展開済みGKD配布構成
  verification/           確認結果と画面見本
```
