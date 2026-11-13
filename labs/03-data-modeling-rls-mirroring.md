# Lab 03 — 宣言的データモデル・リレーション・`@role` 行／列レベル認可・OneLake 自動ミラーリング

所要時間: 約 25 分
前提: [Lab 02](02-scaffold-and-auth.md) 完了（`smart-ops-hub` が作成・SSO 認証設定済み）

**Power BI レポートと Fabric Apps の最大の違いは「データのすぐ横で業務アクション（Write-back）を完結できること」です。**

このラボでは、TypeScript のデコレータだけで **Fabric SQL Database のスキーマ・GraphQL API（Data API Builder）・行／列レベル認可ポリシー・型安全なフロントエンドクライアント** を一括生成し、書き込んだ業務データが **手動 ETL ゼロで OneLake（`MirroredWarehouse`）へ自動ミラーリングされる** 一連の流れを体験します。

```text
TypeScript @entity() + @role() 定義
   │
   ▼ npx rayfin up (または rayfin up db apply)
[ Fabric SQL Database (MSSQL) ] ──▶ Data API Builder (GraphQL + Policy 強制)
   │                                       ▲
   │ 数秒で自動ミラー (Zero-ETL)           │ client.data.<Entity>.select / create / executePaginated
   ▼                                       │
[ OneLake: MirroredWarehouse ]      [ React Frontend + toStandardSchema バリデーション ]
```

---

## 3-1. エンティティ・リレーション・`@role` 認可ポリシーを定義する

`smart-ops-hub` に次の 3 つのエンティティを追加します：
1. **`RestockOrder`（補充発注レコード）**: どの店舗・どの SKU に何個発注したかを記録
2. **`StoreNote`（店舗点検メモ）**: 現場の気づき・異常報告を記録（作成者本人のみ更新・削除可能）
3. **`ChecklistItem`（点検チェック項目）**: `StoreNote` に 1 対多（`@many` / `@one`）で紐づく子明細

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub の data-modeling スキルに従って、`rayfin/rayfin.yml` の `services.data`（`dialect: mssql`）を有効化し、次の3つのエンティティを定義してスキーマに登録して。
>
> 1. `RestockOrder`:
>    - id: uuid
>    - store_id: text(max 20)
>    - sku: text(max 20)
>    - qty: int(min 1, max 10000)
>    - status: set('submitted', 'approved', 'shipped', 'cancelled')
>    - requested_by_upn: text(max 200)
>    - requested_by_id: text(max 100)
>    - note: text(max 500, optional)
>    - requested_at: date
>    - 権限: 認証済みユーザー（authenticated）に全操作を許可（Lab 06 で Functions 経由へ引き締めます）
>
> 2. `StoreNote`:
>    - id: uuid
>    - store_id: text(max 20)
>    - sku: text(max 20, optional)
>    - severity: set('info', 'warning', 'critical')
>    - body: text(max 1000, min 1)
>    - internal_audit_memo: text(max 500, optional)
>    - attachment_path: text(max 300, optional)
>    - resolved: boolean
>    - author_id: text(max 100)
>    - created_at: date
>    - checklists: ChecklistItem への @many リレーション
>    - 権限:
>      - authenticated に read と create を許可（ただし read 時は列レベル制御の例として `exclude: ['internal_audit_memo']` または明示的な列ポリシーを確認できるように説明を添えて）
>      - authenticated の update と delete は `policy: (claims, item) => claims.sub.eq(item.author_id)` で作成者本人のみに制限
>
> 3. `ChecklistItem`:
>    - id: uuid
>    - label: text(max 200)
>    - is_done: boolean
>    - store_note: StoreNote への @one リレーション
>    - 権限: authenticated に全操作を許可
> ```

🤖 **Copilot の動き**
- `@microsoft/rayfin-core` から `entity, role, authenticated, uuid, text, int, boolean, set, date, one, many` をインポートして実装します。
- 各ファイル間の相対インポートに `.js` 拡張子を付与し、`schema.ts`（または `packages/data/src/index.ts`）に 3 エンティティを登録します。

### 🔍 生成されるコードの重要ポイント（Rayfin 1.36.2 厳守ルール）

```typescript
import { entity, role, uuid, text, boolean, set, date, many } from '@microsoft/rayfin-core';
import { ChecklistItem } from './ChecklistItem.js';

@entity()
@role('authenticated', ['read', 'create'])
@role('authenticated', ['update', 'delete'], {
  policy: (claims, item) => claims.sub.eq(item.author_id),
})
export class StoreNote {
  @uuid() id!: string;
  @text({ max: 20 }) store_id!: string;
  @text({ max: 20, optional: true }) sku?: string;
  @set('info', 'warning', 'critical') severity!: 'info' | 'warning' | 'critical';
  @text({ min: 1, max: 1000 }) body!: string;
  @text({ max: 300, optional: true }) attachment_path?: string;
  @boolean() resolved!: boolean;
  @text({ max: 100 }) author_id!: string;
  @date() created_at!: Date;

  @many(() => ChecklistItem)
  checklists!: ChecklistItem[];
}
```

> ⚠️ **絶対に押さえるべき 5 つのアンチパターン防止策**:
> 1. **`@text()` には必ず `max` を付ける**: 省略すると MSSQL 上で `NVARCHAR(MAX)` が生成され、デプロイは通るのに実行時の GraphQL クエリが **Internal Server Error** で失敗します。
> 2. **`@boolean()` を使う**: 一部古い資料にある `@bool()` はパッケージに存在しません。
> 3. **`@optional()` デコレータは存在しない**: `{ optional: true }` をオプション引数で渡します。
> 4. **多対多（Many-to-Many）や複合主キーは非対応**: 多対多が必要な場合は中間エンティティ（Join Entity）を定義します。外部キー列を明示宣言する場合は `{property}_id`（例: `store_note_id`）の命名規約に従います。
> 5. **`@role` を省略しない**: 省略するとサインイン済み全ユーザーに無制限の CRUD が開くか、セキュリティレビューで NG になります。

✅ **期待する結果**
3 エンティティがスキーマに登録され、`npm run build` が型エラーなく成功する。

---

## 3-2. Standard Schema バリデーションとページネーション対応 UI を実装する

Rayfin は定義したエンティティから **Standard Schema v1 準拠のバリデータ（`toStandardSchema`）** を取り出せるため、フロントエンドとバックエンドで制約（文字数上限・最小値など）を二重管理する必要がありません。また、100 件超のレコードを扱うための `executePaginated()` ヘルパーも実装します。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub に「補充発注（RestockOrder）」と「店舗点検メモ＋チェックリスト（StoreNote / ChecklistItem）」の登録・一覧・完了切替パネルを実装して。
> - 入力フォームのクライアント側検証には `@microsoft/rayfin-core`（または `./schema` サブパス）の `toStandardSchema` / `getFieldConstraints` を活用する
> - 一覧取得サービスでは、`.execute()` の1ページ上限（約100件）で無言の切り捨てが起きないよう、`executePaginated()` で全ページ取得できるヘルパー関数を用意する
> - また、ステータス別の発注件数・合計数量を `groupBy(['status']).aggregate(...)` で集計してミニサマリーに表示して
> - ローカル未接続時（`npm run preview`）でも試せるよう、メモリ内フォールバックと `Sample: ※サンプル値` バッジを付けて
> ```

🤖 **Copilot の動き**
- `src/services/opsData.ts` に `RayfinClient` を使った型付き CRUD、カーソルページング（`while (hasNextPage)` で `after(endCursor)` を辿る `fetchAllPages`）、および `groupBy` 集計を実装します。
- 作成時に現在のサインインセッションからユーザー識別子を取得して `author_id` / `requested_by_id` にセットします。

✅ **期待する結果**
フォームバリデーション（例: `qty` に `0` や負数を入れると送信前にエラー表示）と CRUD サービスが実装され、`npm run build` が通る。

---

## 3-3. Fabric SQL Database へスキーマを反映し、データ登録を試す

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub を Fabric にデプロイして、新しい3テーブル（RestockOrders / StoreNotes / ChecklistItems）をプロビジョニングして。
> デプロイ完了後、公開 URL を教えて。
> ```

🤖 **Copilot の動き**
- `npx rayfin up --workspace-id "$WS_ID" --yes` を実行し、管理対象の Fabric SQL Database に複数形テーブル（`dbo.RestockOrders`, `dbo.StoreNotes`, `dbo.ChecklistItems`）と DAB GraphQL エンドポイントを自動構成します。

**ブラウザで動作確認しましょう:**
1. デプロイされた `smart-ops-hub` をブラウザ（InPrivate）で開き、サインインします。
2. **補充発注フォーム**から `store_id: ST-005`、`sku: SKU-120`、`qty: 360` で 1 件登録します。
3. **店舗点検メモフォーム**から `store_id: ST-005`、`severity: critical`、`body: ネブライザーの安全在庫割れを確認、緊急手配済み` とチェックリスト項目を登録します。

✅ **期待する結果**
画面の一覧とステータス別集計に即座に反映され、自分が作成した `StoreNote` の完了チェック更新・削除が動作する。

> 💡 **スキーマ変更時の注意**:
> 列の追加（非破壊的変更）はそのまま `npx rayfin up` で通りますが、列の削除・型変更・リネームはデータ消失を伴うため `npx rayfin up db apply --force` が必要になります。また **Fabric ポータルから管理対象 SQL Database のスキーマを手動で ALTER TABLE することは厳禁** です（`rayfin.yml` / TypeScript との整合が壊れます）。

---

## 3-4. OneLake 自動ミラーリング（`MirroredWarehouse`）を検証する

Fabric Apps の `data` サービスが裏側で作成する **Fabric SQL Database** は、書き込まれたトランザクションを **数秒〜数十秒以内に OneLake の Delta テーブルへ自動ミラーリング** します。これを確認しましょう！

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub の管理対象 SQL Database に入れた `RestockOrders` と `StoreNotes` のデータが、
> OneLake の自動ミラー先（MirroredWarehouse / SQL 分析エンドポイント）からも参照できるかクエリして確認して。
> ```

🤖 **Copilot の動き**
- 自分のワークスペース内のアイテム一覧から、`smart-ops-hub` に紐づく SQL Database およびミラーされた分析エンドポイント（`MirroredWarehouse` / SQL analytics endpoint）の接続先を取得します。
- `sqlcmd`（`--authentication-method=ActiveDirectoryDefault`）または Fabric SQL MCP で `SELECT store_id, sku, qty, status FROM dbo.RestockOrders ORDER BY requested_at DESC` を実行し、先ほど画面から入力した `ST-005 / SKU-120 / 360` が OneLake 側にも現れていることを実証します。

✅ **期待する結果**
アプリ画面から書き込んだレコードが、**ETL パイプラインを 1 本も作ることなく** OneLake 上の Delta テーブルとして SQL 分析エンドポイントから参照できる！

> 📌 **なぜこれが業務アプリ革命なのか？**
> 従来の業務 Web アプリでは、アプリの RDB（Azure SQL や PostgreSQL）に入った業務アクションを分析基盤に戻すために夜間バッチや CDC パイプラインの構築・保守が必要でした。
> Fabric Apps（Rayfin）では **`アプリ入力 → Fabric SQL DB → OneLake 自動ミラー → Lakehouse ショートカット / Direct Lake セマンティックモデル`** が最初から繋がっているため、現場がアプリで入力した発注や承認結果がそのまま BI や AI エージェントの根拠データになります。

---

## ✅ チェックポイント

- [ ] `@text({ max })`・`@boolean()`・`@one`/`@many`・`@role` ポリシーを使って 3 エンティティを定義できた
- [ ] `toStandardSchema` によるバリデーションと `executePaginated()` によるページング取得を組み込めた
- [ ] アプリ画面から `RestockOrder` と `StoreNote` を登録・更新できた
- [ ] 登録したデータが OneLake（ミラー分析エンドポイント）に自動反映されることを確認できた

---

## 🧹 トラブルシュート（プロンプトで対処）

| 症状 | プロンプト例 / 対処 |
|------|---------------------|
| GraphQL が `Internal server error` を返す | `@text()` に `max` が抜けている列がないか確認し、`@text({ max: 200 })` 等に修正して `npx rayfin up db apply --force` |
| 100 件を超えた行が一覧に出ない | `.execute()` ではなく `executePaginated()` ループで全ページ取得するよう修正 |
| ミラー側にまだ行が見えない | 初回ミラー確立には 30〜60 秒ほどかかる場合があるため、少し待ってから再クエリする |

次は Lab 01 で構築した `sm_ops_inventory`（セマンティックモデル）と `ops_warehouse` に **ネイティブ Fabric Data Connectors** で直結する [Lab 04 — ネイティブ Fabric Data Connectors 連携](04-fabric-data-connectors.md) へ進みます 🚀
