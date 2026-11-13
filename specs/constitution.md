# Project Constitution — Smart Ops Hub (Fabric Apps by Rayfin)

この文書は、AI コーディングエージェント（GitHub Copilot CLI）および開発チームが、どの機能追加・反復変更においても **絶対に逸脱してはならない原則（Constitution）** を定義します。

## 1. アーキテクチャおよびプラットフォーム原則

1. **ネイティブ Fabric Apps（Rayfin 1.36.2）準拠**:
   - バックエンド・ホスティングはすべて `@microsoft/rayfin-*`（1.36.2）で構成し、Fabric ワークスペース上の `AppBackend` アイテムへデプロイする。ローカル専用の Python / FastAPI / Streamlit 等で代替しない。
2. **二層の仕様（Dual-Layer Spec）の整合**:
   - プロダクト要件は `specs/spec.md` を単一の真実（Source of Truth）とし、バックエンド仕様は `rayfin/rayfin.yml` および TypeScript デコレータ（`@entity`, `@role`, `@blob`）で宣言的に表現する。手書きの DDL やポータルからの直接テーブル変更は禁止する。
3. **データの粒度と出所に対する誠実さ**:
   - 分析数値は `sm_ops_inventory`（セマンティックモデル）または `ops_warehouse` コネクタから取得し、異なる粒度のテーブル間で根拠のないドリルダウンや架空の数値を表示しない。
   - ライブデータ取得時（`Live: Fabric`）とローカル開発／オフライン時のサンプルフォールバック（`Sample: ※サンプル値`）をヘッダーバッジで必ず明示する。

## 2. セキュリティ・ガバナンス原則（Vibe Coding との決定的な境界）

1. **認証必須（Entra SSO）**:
   - デプロイ環境では Microsoft Entra ID（Fabric SSO）のみを使用し、カスタム認証やハードコードされた資格情報を持ち込まない。
2. **明示的認可ポリシー（`@role` 必須）**:
   - すべての `@entity()` および Storage フォルダーに `@role('authenticated', ...)` を明示する。権限デコレータ無しのエンティティ作成を禁止する。
   - 業務上改ざんを防ぎたい書き込み（補充発注の送信者記録など）はクライアント直接書き込みではなく Rayfin Functions（`UserDataFunctions`）経由で実行し、サーバー側で呼び出し元 ID を記録する。
3. **最小権限のコネクタ設定**:
   - `fabric-semanticmodel` は `delegated` 認証を使用し、モデル側の RLS（行レベルセキュリティ）を尊重する。

## 3. Rayfin 1.36.2 実装ガードレール

- `@text({ max: N })` に必ず上限文字数 `max` を指定する（`NVARCHAR(MAX)` による GraphQL エラー防止）。
- 真偽値は `@boolean()`、省略可能列は `{ optional: true }`、ESM 相対 import は `.js` 拡張子を使用する。
- 100 件超になり得るエンティティ一覧取得は `executePaginated()` を使用する。
- ビルドゲートとして `tsc`（型チェック）、`npm test`、`npm run build` がすべて成功してからデプロイする。

## 4. UI / UX デザイン原則（Linear スタイル × Z の法則）

- **配色**: アプリ全体のブランドアクセントは 1 色（`#2563EB` またはダーク時 `#4C8DFF`）のみ。赤・琥珀・緑は安全在庫割れ・要注意・正常のステータス表現に限定する。グラデーション・過度な影・発光装飾を禁止する。
- **情報配置（Z の法則）**:
  - 上段左に最重要結論 KPI（要補充 SKU 数・欠品リスク金額）、上段右に地域別・カテゴリ別根拠チャート、下段左に優先度順の要補充キュー、下段右に詳細・発注／証憑添付ドロワーを配置する。
- **アクセシビリティ**: コントラスト比 WCAG AA（4.5:1 以上）、数値は等幅または `tabular-nums` で桁揃えする。
