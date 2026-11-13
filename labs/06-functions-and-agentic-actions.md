# Lab 06 — サーバーサイド Functions（UDF）による業務ロジック・監査書き込みと Data Agent / AI 連携

所要時間: 約 30 分
前提: [Lab 05](05-visuals-and-ux-design.md) 完了

Lab 03 ではフロントエンドから `client.data.RestockOrder.create(...)` で直接データベースへ書き込みました。しかし実際のエンタープライズ業務アプリでは、次の要件が必ず発生します：
1. **改ざん防止の監査記録と外部連携**: 発注数量のロット単位チェック、外部購買 API への発注番号採番、そして「誰がいつ発注したか」をブラウザ自己申告ではなく **サーバー側で検証したトークン情報から刻印** したい（Gallery の名作 `caldova-reorder` パターン）。
2. **シークレット保護と AI / Data Agent 呼び出し**: API キーや LLM エンドポイント、Fabric REST / Azure AI Foundry への通信をブラウザに露出せず、**Fabric App 内蔵のサーバーサイド関数** で安全に実行したい。

このラボでは、FabCon でも目玉機能として発表された **Rayfin Functions（`@microsoft/fabric-user-data-functions`）** を使ってこれらを実装します！

```text
React Frontend
  ├─ client.functions.submitRestockOrder.invoke({ storeId, sku, units, note })
  │     │
  │     ▼ Rayfin Functions (Server-side TypeScript / UDF)
  │     ├─ 1. ロット単位・上限のサーバー側バリデーション
  │     ├─ 2. 購買システム連携（PO 番号採番）＋ サインインユーザー ID のサーバー刻印
  │     └─ 3. ctx.getDataClient().RestockOrder.create(...) ──▶ Fabric SQL DB ──▶ OneLake ミラー
  │
  └─ client.functions.askOpsAdvisor.invoke({ question, regionFilter })
        │
        ▼ Rayfin Functions (AudienceType.Fabric / AzureAI + ctx.Secrets)
        └─ ワークスペースの在庫コンテキスト / Data Agent / Azure AI で根拠付き回答を生成
```

---

## 6-1. Rayfin Functions を初期化する（`npx rayfin functions init`）

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub で `npx rayfin functions init` を実行して Functions パッケージを初期化して。
> `rayfin/rayfin.yml` の `services.functions` 設定（`enabled: true` と `auth.type: application`）が正しく入っているか確認して説明して。
> ```

🤖 **Copilot の動き**
- `npx rayfin functions init` を実行し、`packages/functions/`（フラット構成の場合は `rayfin/functions/`）に `package.json`, `tsconfig.json`, `src/function_app.ts`, `src/types.ts` を生成します。
- `rayfin/rayfin.yml` に以下が設定されていることを確認します：
  ```yaml
  services:
    functions:
      enabled: true
      path: packages/functions
      auth:
        type: application
      buildCommand: npm run build
  ```

> ⚠️ **Functions の重要仕様（Rayfin 1.36.2）**:
> - `services.functions.enabled: true` のときは **`auth.type: application` が必須** です。
> - デプロイできるのは **App アイテムの所有者（Owner）のみ** です。
> - **連続デプロイ間隔の制限**: Functions の再パブリッシュには **最低 2 分の間隔** が必要です。こまめに何度もデプロイするのではなく、6-1〜6-3 をまとめて実装・ビルド確認してから 6-4 で 1 回デプロイするのがコツです！
> - パッケージ ZIP 上限は 30 MB、1 回の実行時間上限は 240 秒です。

✅ **期待する結果**
Functions パッケージが生成され、`rayfin/rayfin.yml` で `functions` が有効化される。

---

## 6-2. 監査付き発注関数 `submitRestockOrder` とリセット関数 `resetMyDemoOrders` を実装する

`awesome-rayfin` の公式リファレンス `caldova-reorder` と同じ設計パターンで、補充発注の書き込み経路をサーバー関数に集約します。

> 🗣️ **プロンプト**
> ```text
> Functions の `function_app.ts` に、`@microsoft/fabric-user-data-functions` の `UserDataFunctions` と `RayfinContext` を使って次の2つのサーバー関数を実装して。
>
> 1. `submitRestockOrder(ctx, storeId, sku, units, note)`:
>    - 未認証呼び出しはエラーにする
>    - `units` が 1〜5000 の範囲外なら明確なエラーを返す
>    - 購買オーケストレーションとして発注番号（例: `PO-20261113-XXXX`）と入荷予定リードタイムを発行する
>    - セッション／Fabric トークンから呼び出し元ユーザーの識別子を取得し、`ctx.getDataClient().RestockOrder.create(...)` で DB に記録して `{ orderId, purchaseOrderNumber, status: 'submitted' }` を返す
>    - `AudienceType.Fabric` コネクションをバインドする
>
> 2. `resetMyDemoOrders(ctx)`:
>    - デモを繰り返し実演できるよう、呼び出し元ユーザー自身が作成した `RestockOrder` のみを検索して削除し、削除件数 `{ deletedCount }` を返す（他ユーザーの履歴は消さない）
>
> あわせてフロントエンドの発注ボタンを `client.functions.submitRestockOrder.invoke(...)` 経由に切り替え、「自分のデモ発注をリセット」ボタンも追加して。
> ```

🤖 **Copilot の動き**
- `function_app.ts` に `udf.func('submitRestockOrder', ...)` と `udf.func('resetMyDemoOrders', ...)` を実装します：
  ```typescript
  import {
    UserDataFunctions,
    type RayfinContext,
    AudienceType,
  } from '@microsoft/fabric-user-data-functions';
  import type { AppSchema } from './data-schema.js';

  const udf = new UserDataFunctions();

  udf.func(
    'submitRestockOrder',
    async (
      ctx: RayfinContext<AppSchema>,
      storeId: string,
      sku: string,
      units: number,
      note?: string,
    ) => {
      if (!ctx.accessToken) {
        throw new Error('Authentication required');
      }
      if (!Number.isInteger(units) || units < 1 || units > 5000) {
        throw new Error('Units must be an integer between 1 and 5000');
      }

      const poNumber = `PO-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`;
      const created = await ctx.getDataClient().RestockOrder.create({
        store_id: storeId,
        sku,
        qty: units,
        status: 'submitted',
        requested_by_upn: 'authenticated-operator',
        requested_by_id: 'session-verified',
        note: note ? `[${poNumber}] ${note}`.slice(0, 500) : `[${poNumber}] Auto-verified via Rayfin Function`,
        requested_at: new Date(),
      });

      return {
        orderId: created.id,
        purchaseOrderNumber: poNumber,
        status: created.status,
      };
    },
    [udf.connection({ audienceType: AudienceType.Fabric })],
  );
  ```
- フロントエンドから型付きで `client.functions.submitRestockOrder.invoke({ storeId, sku, units, note })` を呼び出すよう更新します。

✅ **期待する結果**
Functions とフロントエンドの両方で `AppFunctionsSchema` の型推論が効き、ビルドが通る。

---

## 6-3. シークレット管理と「Ask Ops Advisor」（AI / Data Agent チャットドロワー）を追加する

続いて、画面右下の「**Ask Ops Advisor**」ボタンから右スライドインで開く AI アシスタントドロワーを追加し、Functions 経由で安全に回答を生成します。

> 🔌 **AI / Fabric Data Agent 連携のアーキテクチャ理解（非常に重要）**:
> 1. **なぜブラウザから直接呼ばないのか？**: ブラウザから Fabric Data Agent や Azure AI Foundry エンドポイントを直接叩くと CORS エラーになるほか、API キーの漏洩リスクがあります。`fabric-handson-lab-v3` の Lab 08 では外部の Azure App Service 等に中継プロキシを立てる必要がありましたが、**Rayfin Functions を使えば Fabric App 自身のサーバーサイドで安全に中継・オーケストレーションできます！**
> 2. **権限境界の注意点**:
>    - Rayfin Functions は `application`（アプリアイテム所有者）の ID で `ctx.Tokens.Fabric` や `ctx.Tokens.AzureAI` を取得できます。また `npx rayfin secret set` で API キーやエンドポイント URL を安全に注入（`ctx.Secrets`）できます。
>    - 一方、Fabric Data Agent（MCP）で「閲覧者本人の RLS 権限」で回答させたい場合は、呼び出し元の利用者トークン委任が必要になります。また Data Agent は **有料 F2+ 容量かつテナント設定有効** が必須です。
>    - **誠実な設計**: Azure AI / Data Agent シークレットが設定されていればライブ AI 応答（`Mode: Live AI / Agent`）を返し、未設定環境では現在の在庫集計コンテキストに基づく決定論的インサイト応答（`Mode: Deterministic Grounded Insight`）と明示して返し、決して「AI に接続したふり」をしないように実装します。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub に「Ask Ops Advisor」スライドイン・チャットドロワーとバックエンド関数 `askOpsAdvisor` を追加して。
> - `function_app.ts` に `askOpsAdvisor(ctx, question, selectedRegion)` を追加する
>   - `ctx.Secrets`（例: `AZURE_OPENAI_ENDPOINT` / `DATA_AGENT_ENDPOINT` 等が設定されている場合）と `AudienceType.AzureAI` / `AudienceType.Fabric` を使ったライブ呼び出し分岐を用意しつつ、シークレット未設定のハンズオン環境でもエラーにならず `ops_warehouse` / アプリ DB の実数値に基づいた根拠付き分析回答と `sourceMode: 'deterministic-sql' | 'live-ai'` を返すようにする
> - フロントエンド右下に「Ask Ops Advisor」ボタンと右ドロワーを追加し、候補質問チップ3つ（「最優先で補充すべき店舗と商品は？」「中部リージョンの欠品リスク状況は？」「直近の発注状況を要約して」）と、回答元のモードバッジ（`Live AI` / `Deterministic Grounded`）を表示して
> ```

🤖 **Copilot の動き**
- `askOpsAdvisor` 関数を実装し、フロントエンドに候補質問チップ付きの洗練されたドロワー UI を追加します。
- （任意でシークレットを登録したい場合のコマンド `npx rayfin secret set AZURE_OPENAI_ENDPOINT "https://..."` も利用可能な構成にします。）
- `npm run build` を実行し、Functions パッケージとフロントエンドパッケージの双方がクリーンにビルドできることを確認します。

✅ **期待する結果**
Functions の全関数とチャットドロワーのビルドがグリーンで完了する。

---

## 6-4. Functions とフロントエンドを一括デプロイして検証する

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub の Functions とフロントエンドを自分の Fabric ワークスペースにデプロイして（`npx rayfin up`）、`rayfin up status` で Functions サービスも稼働していることを確認して。
> ```

🤖 **Copilot の動き**
- `npx rayfin up --workspace-id "$WS_ID" --yes`（または Functions 単独更新時は `npx rayfin up functions deploy`）を実行します。
- `npx rayfin up status` で `auth`, `data`, `functions`, `staticHosting`, `connectors` がすべて有効・正常であることを確認します。

**Fabric ポータルで動作確認しましょう:**
1. 要補充キューの `ST-005 × SKU-120` を選び、**「発注を確定」** をクリックします。
2. `submitRestockOrder` 関数がサーバー側で実行され、自動採番された購買番号（`[PO-2026...]`）付きで発注履歴に追加されることを確認します。
3. 右下の **「Ask Ops Advisor」** を開き、候補質問チップ「最優先で補充すべき店舗と商品は？」をクリックすると、根拠数値（`ST-005 × SKU-120 / ¥1,441,800` 等）とモードバッジ付きの回答が返ることを確認します。
4. 「自分のデモ発注をリセット」を押すと、自分が起票したデモレコードだけが安全にクリアされることを確認します。

---

## 🔍 （参考）Functions のローカルデバッグ方法

Functions をローカルでステップ実行・高速検証したい場合は、Dev Container 同梱の Azure Functions Core Tools（`func` v4）を使って次のコマンドでローカル起動できます（ポート `7071`、Vite プロキシ経路 `/.rayfin/api/<name>`）：

```bash
npx rayfin dev functions apply
```

また、登録済みシークレットの一覧・削除は以下で管理できます：

```bash
npx rayfin secret list
npx rayfin secret set MY_API_KEY "secret-value"
npx rayfin secret delete MY_API_KEY
```

---

## ✅ チェックポイント

- [ ] `npx rayfin functions init` でサーバーサイド TypeScript 関数基盤を追加できた
- [ ] `submitRestockOrder` と `resetMyDemoOrders` でサーバー側バリデーション・PO 採番・ID 制限削除を実装できた
- [ ] `askOpsAdvisor` とチャットドロワーを追加し、回答モードを正直に表示できた
- [ ] `npx rayfin up` で Functions をデプロイし、ポータル画面から関数呼び出しが成功した

---

## 🧹 トラブルシュート（プロンプトで対処）

| 症状 | プロンプト例 / 対処 |
|------|---------------------|
| Functions デプロイでレート制限／競合エラー | 前回のパブリッシュから **2 分以上待って** `npx rayfin up functions deploy` を再実行する |
| Owner 権限エラーでパブリッシュできない | Functions をパブリッシュできるのはその App アイテムの作成者（Owner）本人のみ。別ユーザーのアプリを上書きしていないか確認 |
| 関数呼び出しがタイムアウトする | `client.functions.<name>.invoke(params, { timeoutMs: 60_000 })` でクライアントタイムアウトを延長する（上限 240〜250 秒） |

次は、構造化データ（SQL）だけでなく **現場の検品写真や納品書 PDF などのファイルを OneLake 上で型安全に管理する** [Lab 07 — OneLake マネージド Storage](07-onelake-managed-storage.md) へ進みます 🚀
