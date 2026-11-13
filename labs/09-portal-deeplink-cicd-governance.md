# Lab 09 — ポータル埋め込み・ディープリンク（App State）・マルチ環境昇格・CI/CD とガバナンス

所要時間: 約 20 分
前提: [Lab 08](08-spec-driven-development.md)（または [Lab 02](02-scaffold-and-auth.md) 以降）完了

このラボでは、開発した Fabric App を実際の組織・エンタープライズ環境で共有・継続運用するために不可欠な **4 つの本番運用機能** を学びます：
1. **Fabric ポータル埋め込みと URL ディープリンク状態同期（`@microsoft/rayfin-app-state-fabric`）**
2. **開発（Dev）→ 本番（Prod）ワークスペースのマルチ環境切り替え（`rayfin up switch` / `resolveRayfinConfig`）**
3. **サービスプリンシパルによる GitHub Actions 自動 CI/CD と破壊的スキーマ変更ゲート**
4. **権限モデル・App Metrics・Fabric Capacity（CU）課金の仕組み**

---

## 9-1. ポータル埋め込み姿勢とディープリンク（`@microsoft/rayfin-app-state-fabric`）を組み込む

たとえばリージョンマネージャーが「`Chubu` リージョンで絞り込み、`Regional Manager` ペルソナを開いた状態」のリンクを同僚にチャット共有したいとき、アプリが Fabric ポータルの iframe 内で動いていると通常の `window.location` だけではポータル側の URL に状態が乗りません。

Rayfin の **`@microsoft/rayfin-app-state-fabric`** を使うと、Fabric ポータル側の URL クエリ／状態とアプリ内の選択状態（リージョン・ペルソナ・タブ等）を安全に双方向同期（ディープリンク）できます！

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub のインストール済みドキュメント（`@microsoft/rayfin-app-state-fabric` または `npx rayfin docs search "app-state"` / `"deep link"`）を確認して、
> 選択中の `region`・`persona`・アクティブタブをポータルのディープリンク状態と同期できるように組み込んで。
>
> 厳守事項:
> - テナントごとに順次ロールアウトされる機能のため、必ず `isSupported()` を最初に判定し、非対応ホスト（`UNSUPPORTED_HOST_CAPABILITY`）やスタンドアロン実行時は通常の URL クエリパラメータ（`URLSearchParams`）に安全にフォールバックする
> - `targetOrigin` は固定指定しない（未設定のままにする）
> - 初回起動時に `getLaunchStateSync()` で起動状態を **1回だけ復元してから** 状態書き戻しを開始する（復元前の空状態で上書きしない）
> - 同期する state ペイロードは最小限（数キーの軽量オブジェクト）に保つ
> ```

🤖 **Copilot の動き**
- `@microsoft/rayfin-app-state-fabric` の `createFabricAppStateClient()` / `getLaunchStateSync()` を用いたフック（例: `usePortalDeepLinkState`）を作成します。
- ポータル外やロールアウト前のテナントでもエラーを出さず `?region=Chubu&persona=manager` で共有リンクが機能するハイブリッド実装にし、`npx rayfin up staticapp deploy` で反映します。

### 🔒 ポータル専用公開（`embedded.only`）とスタンドアロン公開の選び方

`rayfin/rayfin.yml` の `services.staticHosting` では、公開姿勢を用途に応じて選べます：

```yaml
services:
  staticHosting:
    enabled: true
    folder: dist
    buildCommand: npm run build
    indexDocument: index.html
    assetAccess: protected     # protected（既定・推奨）または public
    # ポータル埋め込み専用にする場合（caldova-reorder 等で採用）:
    # embedded:
    #   only: true
```

> ⚠️ **重要なセキュリティ知識**:
> - `assetAccess: public` にしても公開されるのは HTML/JS/CSS の静的アセットのみであり、**バックエンドの Data / Functions / Storage API が匿名公開されるわけではありません**（匿名データアクセスはテナント管理設定 `Enable anonymous data access for Fabric Apps` が既定オフでブロックしています）。
> - `assetAccess` を変更した場合は、`rayfin up staticapp deploy` だけでは反映されないため、フルデプロイの **`npx rayfin up`** を実行してください。
> - 社内ポータル（SharePoint や独自 Web ポータル等）の親ウィンドウに Rayfin アプリを埋め込む場合は、`@microsoft/rayfin-embed-host` の `createEmbedHost()` を親サイト側で利用できます。

---

## 9-2. マルチ環境管理（Dev ワークスペース ⇄ Prod ワークスペース）

実運用では、開発用ワークスペース（例: `ops-app-dev`）と本番用ワークスペース（例: `ops-app-prod`）を分離します。Rayfin CLI は複数デプロイターゲットの記録と切り替えを標準サポートしています。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub の現在のデプロイターゲット一覧を `npx rayfin up list` で確認して、
> 開発ワークスペースと本番ワークスペースを切り替えて運用する手順（`rayfin up switch` と `resolveRayfinConfig`、および Fabric Deployment Pipelines 利用時の注意点）を整理して教えて。
> ```

🤖 **Copilot の動き**
- `npx rayfin up list` と `npx rayfin up status` を実行し、`rayfin/.deployments.json` に記録されている現在のデプロイプロファイルを確認します。
- 環境切り替え手順と `resolveRayfinConfig`（`@microsoft/rayfin-client`）の使い方を案内します。

### 📋 マルチ環境運用のベストプラクティス早見表

```bash
# 登録済みデプロイターゲットの一覧確認
npx rayfin up list

# 別ワークスペース（ステージング／本番）へのデプロイ
npx rayfin up --workspace "ops-app-prod" --item-name "smart-ops-hub"

# アクティブなデプロイターゲットの切り替え
npx rayfin up switch <deployment-name>
```

- **環境別クライアント設定**: Fabric Deployment Pipelines 等でアイテム定義を昇格させる場合、ビルド時固定の `.env` だけでなく `@microsoft/rayfin-client` の `resolveRayfinConfig({ apiUrl, publishableKey })` を使うことで環境横断の設定解決に対応できます。
- **複製時のワナ**: 既存アプリフォルダを `cp -r` でコピーして別アプリを作る際は、**必ず `rayfin/.deployments.json` を削除** してから `rayfin up` してください（残っていると元のアプリアイテムを上書きします）。

---

## 9-3. GitHub Actions による自動 CI/CD パイプライン（Service Principal 連携）

本番ワークスペースへのデプロイを個人の手元 PC から行うのではなく、GitHub Actions から **サービスプリンシパル（Service Principal）** と環境承認ゲート付きで自動化する構成例です。

- **Pull Request 時**: `tsc`・`npm test`・`npm run build`・`rayfin up --dry-run` のみを実行
- **Main マージ／手動実行時**: GitHub Environment（`dev` / `prod`）の承認ゲート通過後に `rayfin up --yes` を実行
- **破壊的 DB スキーマ変更（列削除・型変更）**: 自動で `--force` を付けず、バックアップ計画確認後の明示入力フラグでのみ許可する

```yaml
# 参考: .github/workflows/deploy-fabric-app.yml 構成例
name: Deploy Fabric App

on:
  workflow_dispatch:
    inputs:
      environment:
        description: "Target Fabric environment (dev / prod)"
        required: true
        default: "dev"
        type: choice
        options: [dev, prod]
      allow_destructive_schema:
        description: "Allow --force schema changes"
        required: false
        default: false
        type: boolean

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    defaults:
      run:
        working-directory: smart-ops-hub
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22.22.0"
      - name: Install dependencies & pinned Rayfin CLI
        run: |
          npm ci
          npm install -g @microsoft/rayfin-cli@1.36.2
      - name: Build & Test
        run: |
          npm test --if-present
          npm run build
      - name: Login with Service Principal & Deploy
        env:
          FABRIC_TENANT_ID: ${{ secrets.FABRIC_TENANT_ID }}
          FABRIC_CLIENT_ID: ${{ secrets.FABRIC_CLIENT_ID }}
          FABRIC_CLIENT_SECRET: ${{ secrets.FABRIC_CLIENT_SECRET }}
        run: |
          rayfin login --service-principal \
            --client-id "$FABRIC_CLIENT_ID" \
            --client-secret "$FABRIC_CLIENT_SECRET" \
            -t "$FABRIC_TENANT_ID"
          rayfin up --workspace-id "${{ vars.FABRIC_WORKSPACE_ID }}" --dry-run
          FORCE_FLAG=""
          if [ "${{ inputs.allow_destructive_schema }}" = "true" ]; then
            FORCE_FLAG="--force"
          fi
          rayfin up --workspace-id "${{ vars.FABRIC_WORKSPACE_ID }}" --yes $FORCE_FLAG
          rayfin up status
```

> ⚠️ **CI/CD と権限の注意点**:
> - サービスプリンシパルがワークスペースへデプロイするには、管理ポータルで「サービスプリンシパルによる Fabric API 利用」が許可され、対象ワークスペースの `Contributor` 以上のロールが必要です。
> - なお、Lab 06 の **Functions の初回所有権（Owner）** や Lab 04 の **`delegated` セマンティックモデル権限** はユーザー／アイテム所有者の ID 境界に関わるため、[specs/fit-gates/identity-fit-assessment.md](../specs/fit-gates/identity-fit-assessment.md) に沿って設計してください。

---

## 9-4. エンタープライズ・ガバナンス、権限モデル、CU 課金の仕組み

顧客や情報システム部門への説明で必ず聞かれる **権限・監視・課金** の公式仕様（Rayfin 1.36.2 時点）を整理しておきます。

### 1. アプリ利用者に必要な権限（Workspace 全員を Contributor にする必要はない！）
- **アプリ開発者・デプロイ担当者**: ワークスペースの `Contributor` / `Member` / `Admin`（Functions 発行はアイテム `Owner`）
- **一般の業務利用者（エンドユーザー）**:
  - ワークスペースの編集権限は不要。アプリアイテムの共有で **`Run and interact`（既定の実行権限）** を付与するだけで利用できます。
  - ただしアプリが **`delegated` コネクタ（例: `fabric-semanticmodel`）** を使う場合のみ、その接続先セマンティックモデルに対する `Read + Build` 権限（および RLS ロール割り当て）が各利用者に必要です。
- **テナント管理者による緊急停止**: 管理者は問題のあるアプリを管理ポータルからブロック／ブロック解除でき、App Metrics で利用状況を把握できます。

### 2. Fabric Capacity（CU）課金モデル
Fabric Apps 固有の追加ライセンス課金はなく、ワークスペースが紐づく **Fabric 容量の Capacity Units（CU）** を消費します：
- **Fabric SQL Database**: コンピュート（1 CU = 0.383 vCores 換算）＋ ストレージ
- **GraphQL（Data API）処理**: クエリ処理時間に応じた CU 消費（目安: 処理 1 時間あたり 10 CU-hours）
- **OneLake ストレージ＆トランザクション**: 静的アセット・ミラーデータ・Rayfin Storage の OneLake 消費分
- **Functions（UDF）**: User Data Functions の実行 CU
- *(プレビュー時点では WebService ホスティング制御・認証ブローカー・デプロイ処理自体の追加課金はなし)*

---

## ✅ チェックポイント

- [ ] `@microsoft/rayfin-app-state-fabric`（`isSupported()` 判定付き）によるポータル URL 状態共有を理解・組み込めた
- [ ] `npx rayfin up list` / `switch` と `rayfin/.deployments.json` の扱いを理解した
- [ ] サービスプリンシパルによる CI/CD フローと `--dry-run` / `--force` ゲートを把握した
- [ ] エンドユーザー権限（`Run and interact` vs `delegated` Build 権限）と CU 課金モデルを説明できるようになった

最後に、**Fabric Apps Gallery と `microsoft/awesome-rayfin` の全 20+ 公式・コミュニティ事例** を俯瞰し、自分の案件に最適なアーキテクチャを即座に選べるようにする [Lab 10 — Fabric Apps Gallery ＆ `awesome-rayfin` 全テンプレートカタログ](10-gallery-and-architecture-catalog.md) を見に行きましょう 🚀
