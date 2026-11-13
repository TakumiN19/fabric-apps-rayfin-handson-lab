# Lab 07 — OneLake ベースのマネージド Storage（証憑・現場写真アップロードと権限制御）

所要時間: 約 20 分
前提: [Lab 06](06-functions-and-agentic-actions.md) 完了

店舗点検や補充業務では、テキストメモだけでなく **「棚の欠品状況の写真（PNG/JPEG）」や「納品書・検品票（PDF）」** を添付したい場面が多々あります。バイナリデータを無理に SQL Database の列に詰め込むのはアンチパターンです。

Fabric Apps by Rayfin の **Storage サービス（Experimental）** を使うと、**OneLake 上に型定義・サイズ制限・MIME タイプ制限・`@role` アクセス制御付きのストレージフォルダー** を宣言的に作成し、数行のクライアントコードでアップロード・一覧・ダウンロード・削除を行えます！

```text
rayfin/storage/Attachments.ts (@blob + StorageObject + @role('authenticated', ...))
   │
   ▼ npx rayfin up (または rayfin up storage apply)
[ OneLake Managed App Storage ]
   ▲
   │ client.storage.attachments.upload / list / download / delete
[ React Frontend: StoreNote 証憑添付 UI ] ──(相対パスのみ保存)──▶ [ SQL DB: StoreNotes.attachment_path ]
```

---

## 🚦 7-0. 機能ゲート（Feature Gate）の事前確認

Rayfin Storage は Experimental 機能であり、以下の前提条件が必要です（満たさない環境では無理にモック成功させず、ゲート判定を記録して Lab 08 へ進むことができます）：

1. Fabric 管理ポータル > OneLake 設定で **`Users can access data stored in OneLake with apps external to Fabric`** が有効であること（多くのテナントで既定オン）。
2. ワークスペースが **Fabric 容量** に割り当てられていること（Power BI Pro ワークスペースは非対応）。
3. アプリの `services.data`（`dialect: mssql`）および Fabric 認証が有効であること。
4. **ローカル Docker エミュレータは非対応**: `npx rayfin dev` 実行時もファイル操作はリモートの Fabric OneLake ストレージに対して行われます。

---

## 7-1. 型付き Storage フォルダー `attachments` を定義する

`StoreNote`（店舗点検メモ）に添付する画像・PDF 用の `attachments` フォルダーを定義します。

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub のインストール済み Rayfin Storage ドキュメント（`@microsoft/rayfin-storage` / `npx rayfin docs search storage`）を参照して、
> OneLake ベースの `attachments` ストレージフォルダーを追加して。
>
> 要件:
> - `rayfin/rayfin.yml` で `services.storage.enabled: true` を有効化する（既存の auth / data / functions / connectors はそのまま保持）
> - `rayfin/storage/` 配下に `@blob` と `StorageObject`、`mb(10)`、`ContentTypes` を使って `attachments` フォルダーを定義する
> - 最大ファイルサイズ: 10 MiB、許可する Content-Type: PDF・PNG・JPEG・WebP
> - 権限: `@role('authenticated', '*')` を必ず設定する（匿名アクセス不可）
> - 既存の認証済みクライアントと同一セッションを共有する形で `ExtendableRayfinClient` / `createStorageClient` を統合して
> ```

🤖 **Copilot の動き**
- `@microsoft/rayfin-storage`（未導入の場合は CLI バージョンと一致する `1.36.2`）を確認・導入します。
- `@microsoft/rayfin-core/experimental` の `@blob`, `StorageObject`, `mb`, `ContentTypes` を用いてフォルダー定義と `schema` エクスポートを作成します。
- **重要**: サインイン処理を行う `client.auth` と Storage 呼び出しを行う `client.storage` が **必ず同一のクライアントセッション** を共有するようにクライアントシングルトンを構成します。

### 🔍 パス指定の厳守ルール（Rayfin Storage）
オブジェクトパスはフォルダーからの相対パス（例: `ST-005/20261113-shelf-check.png`）で指定します：
- 区切り文字は `/` を使用する（`\` は不可）
- **先頭または末尾に `/` を付けない**
- 空セグメント、`.`、`..` を含めない

✅ **期待する結果**
Storage スキーマとクライアント統合が完了し、`npm run build` が成功する。

---

## 7-2. `StoreNote` へのファイル添付・一覧・ダウンロード・削除 UI を追加する

> 🗣️ **プロンプト**
> ```text
> 店舗点検メモ（`StoreNote`）パネルに証憑ファイル添付機能を統合して。
> - ファイル選択欄（PDF / PNG / JPEG / WebP、10 MiB 以下）を追加する
> - メモ登録時にファイルが選択されていれば `client.storage.attachments.upload('<store_id>/<timestamp>-<filename>', file, { contentType: file.type })` でアップロードし、その相対パスを `StoreNote.attachment_path` に保存する
> - メモ一覧で `attachment_path` がある行には「📎 添付ファイルを開く／ダウンロード」ボタンと削除連動を付け、`StorageError`（`isStorageError`）発生時はユーザーに分かりやすいメッセージを表示して
> ```

🤖 **Copilot の動き**
- 構造化メタデータ（誰が・どの店舗に・どんなメモを残したか）は SQL Database の `StoreNote` に置き、実体バイナリだけを OneLake Storage の `attachments` フォルダーに置くクリーンな責務分離で実装します。

✅ **期待する結果**
添付 UI とエラーハンドリングが実装され、`npm run build` が成功する。

---

## 7-3. Storage 設定をデプロイして動作確認する

> 🗣️ **プロンプト**
> ```text
> smart-ops-hub を Fabric にデプロイして Storage フォルダー構成を反映して（`npx rayfin up`、必要に応じて `npx rayfin up storage apply`）。
> デプロイ出力に storage の警告がないか確認して教えて。
> ```

🤖 **Copilot の動き**
- `npx rayfin up --workspace-id "$WS_ID" --yes` を実行し、デプロイログに Storage 構成の警告が出ていないことを確認します（フォルダー変更のみ再適用したい場合は `npx rayfin up storage apply` が使えます）。

**Fabric ポータルで動作確認しましょう:**
1. `smart-ops-hub` を開き、店舗点検メモ作成欄で任意の PNG 画像または PDF（10 MiB 以下）を選択して登録します。
2. メモ一覧に `📎 添付ファイルを開く／ダウンロード` が表示され、クリックすると OneLake からファイルが取得できることを確認します。
3. 10 MiB 超または許可外の拡張子（例: `.exe` や `.zip`）を選んだ場合、アップロードが拒否されることを確認します。

---

## ✅ チェックポイント

- [ ] 機能ゲート（OneLake 外部アクセス設定・Fabric 容量 WS）を確認した
- [ ] `@blob`・`StorageObject`・`@role('authenticated', '*')` で型付き Storage フォルダーを定義できた
- [ ] SQL（パス保持）と OneLake Storage（バイナリ実体）を分離してアップロード・取得・削除できた

次は、FabCon セッションで **Sujata Narayana 氏** が紹介した **Spec-Driven 開発（仕様駆動開発）** の背景思想を学び、実際に Markdown 仕様書を更新してアプリを一気に v2 へ進化させる [Lab 08 — Spec-Driven 開発（FabCon セッション解説＆実践）](08-spec-driven-development.md) へ進みます 🚀
