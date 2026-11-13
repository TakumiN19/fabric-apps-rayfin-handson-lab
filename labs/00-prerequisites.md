# Lab 00 — 前提条件のセットアップと Rayfin / Fabric スキル導入

所要時間: 約 10 分

このラボでは、ハンズオンに必要な CLI ツールが揃っているかを確認し、GitHub Copilot CLI に **`skills-for-fabric`** と **`rayfin-skills`（公式 Rayfin スキル）** を導入したうえで、自分の参加者設定を一度だけ登録します。

> [!TIP]
> **GitHub Codespaces を使う場合**は、ルート README の [「GitHub Codespaces で開始」](../README.md#-github-codespaces-で開始推奨) から起動してください。
> CLI 一式と 3 つの Copilot プラグイン（`fabric-skills`、`powerbi-authoring`、`rayfin`）が自動導入済みのため、**0-2 と 0-4 と 0-6 のインストールは省略**できます。
> ターミナルで `bash .devcontainer/scripts/verify.sh` を実行し、すべて `[OK]` になることを確認したら **0-5** へ進んでください。

---

## 0-1. 事前準備チェックリスト

- **Web ブラウザ**: Microsoft Edge または Google Chrome 最新版（InPrivate / シークレットウィンドウ推奨）
- **Visual Studio Code**: ローカル PC で実施する場合（[ダウンロード](https://code.visualstudio.com/)）
- **GitHub アカウント ＆ GitHub Copilot ライセンス**: Copilot CLI が利用可能なアカウント（組織ポリシーで CLI が許可されていること）
- **Microsoft Fabric アカウント ＆ 容量付きワークスペース**: 講師から配布された `student<番号>` アカウント、または自身の検証テナントの `Contributor` 以上のワークスペース

---

## 0-2. 教材リポジトリを取得して VS Code で開く（ローカル PC の場合）

```bash
git clone https://github.com/TakumiN19/fabric-apps-rayfin-handson-lab.git
cd fabric-apps-rayfin-handson-lab
code .
```

> 💡 Git を使わない場合は GitHub ページの緑色 **「< > Code」→「Download ZIP」** から展開し、VS Code の **ファイル > フォルダーを開く…** でこのフォルダーを開いてください。

---

## 0-3. VS Code の組み込みターミナルを開く

メニュー **ターミナル > 新しいターミナル**（<kbd>Ctrl</kbd>+<kbd>`</kbd>）を開きます。以降の操作はすべてこのルートフォルダーで実行します。

---

## 0-4. CLI ツールのインストールとバージョン確認（ローカル PC の場合）

Rayfin CLI 1.36.2 と GitHub Copilot CLI の双方で安定動作する **Node.js 22.x または 24.x LTS** を使用します。

### Windows（PowerShell 7+）

```powershell
winget install OpenJS.NodeJS.LTS
winget install Microsoft.PowerShell
winget install GitHub.Copilot
winget install Microsoft.AzureCLI
winget install sqlcmd
```

VS Code を再起動し、グローバル npm ツールを導入します：

```powershell
npm install -g @microsoft/rayfin-cli@1.36.2 azure-functions-core-tools@4 @microsoft/powerbi-report-authoring-cli@0.5.0
```

### macOS / Linux / WSL（bash / zsh）

```bash
# Node.js 22 LTS または 24 LTS 導入後:
npm install -g @github/copilot @microsoft/rayfin-cli@1.36.2 azure-functions-core-tools@4 @microsoft/powerbi-report-authoring-cli@0.5.0
```

（macOS の場合は `brew install azure-cli sqlcmd python@3.12` で補助 CLI も導入できます。）

### バージョン確認

```bash
node --version
rayfin --version
func --version
copilot --version
az version
sqlcmd --version
python3 --version
```

---

## 0-5. GitHub Copilot CLI を起動してサインインする

1. ターミナルで Copilot CLI を起動します。

   ```bash
   copilot
   ```

2. フォルダーの信頼確認が出たら **「2. Yes, and remember this folder…」**（または「1. Yes, proceed」）を選択します。
3. 未サインインの場合はプロンプト内で `/login` を実行し、GitHub アカウントで認証します。
4. （推奨）`/model` で **Auto** を選択します。

---

## 0-6. Fabric スキル ＆ Rayfin 公式スキルを導入する

> [!IMPORTANT]
> **なぜ両方のスキルを入れるのか？**
> - `microsoft/skills-for-fabric`（`fabric-skills` / `powerbi-authoring`）は Lakehouse・Warehouse・セマンティックモデルの構築・検証を担います。ただし同梱の `FabricAppDev` エージェント単体は Python + ODBC アプリを既定で提案する性質があります。
> - そこに **`microsoft/rayfin`（`rayfin@rayfin-skills`）** を組み合わせることで、Copilot が **本物の TypeScript 製ネイティブ Fabric Apps（Rayfin）** の CLI 手順とバージョン固定スキルへ正確にルーティングします。

Copilot CLI のプロンプト内で以下を実行します（Codespaces では導入済みのため `/plugin list` の確認のみで OK です）：

```text
/plugin marketplace add microsoft/skills-for-fabric
/plugin install fabric-skills@fabric-collection
/plugin install powerbi-authoring@fabric-collection

/plugin marketplace add microsoft/rayfin
/plugin install rayfin@rayfin-skills

/plugin list
```

✅ **期待する結果**
`/plugin list` に以下の 3 プラグインが表示されること：
- `fabric-skills@fabric-collection`
- `powerbi-authoring@fabric-collection`
- `rayfin@rayfin-skills`

---

## 0-7. 参加者設定を一度だけ登録する（全 Lab 自動補完）

受講形態に合わせて **A（集合ハンズオン用）** または **B（自社／個人検証環境用）** の **どちらか一方** を Copilot CLI に貼り付けて送信してください。

### パターン A: 配布アカウント（`student` 番号）で受講する場合

`<番号>` だけを自分の番号（例: `3`）に書き換えて送ります：

> 🗣️ **プロンプト**
> ```text
> 私の student 番号は <番号> です。
> この番号を記憶して、以降の全 Lab で自分のアカウントとワークスペースに自動で反映してください。
> ```

### パターン B: 自分のテナント・ワークスペースで自習する場合

`<メールアドレス>`・`<テナントID>`・`<ワークスペース名>` を自分の環境に書き換えて送ります：

> 🗣️ **プロンプト**
> ```text
> 私のハンズオン環境を登録してください。
> - アカウント: <メールアドレス>
> - テナント ID: <テナントID>
> - ワークスペース名: <ワークスペース名>
> 以降の全 Lab でこの設定を自動で反映してください。
> ```

🤖 **Copilot の動き**
- `.github/copilot-instructions.md` に従い、`.github/student.local.md`（`.gitignore` 対象）へ設定を保存します。
- 保存直後にファイルを読み直し、アカウント・ワークスペース名・テナント ID を表示します。

✅ **期待する結果**
自分のアカウント名・ワークスペース名・テナント ID が正しく表示される。
**以降（Lab 01〜10）のプロンプトでは、ワークスペース名や ID を手で入力・置換する必要はありません。**

---

## ✅ チェックポイント

- [ ] `node`、`rayfin`（1.36.2）、`copilot`、`az`、`sqlcmd`、`python3` が利用できることを確認した
- [ ] `/plugin list` に `fabric-skills`、`powerbi-authoring`、`rayfin` の 3 つが表示された
- [ ] 0-7 で参加者設定を `.github/student.local.md` に保存し、内容を確認した

次は [受講者向け — Fabric ポータルへのサインイン](fabric-portal-login.md) を確認のうえ、[Lab 01 — サインインとデータ基盤のシード投入](01-seed-fabric-foundation.md) へ進みます 🚀
