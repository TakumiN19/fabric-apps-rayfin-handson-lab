# Implementation Tasks — Smart Ops Hub

各タスクは独立して検証可能な単位に分割されています。コーディングエージェントは各タスク完了時に型チェック（`tsc`）とビルド（`npm run build`）を確認してから次へ進みます。

- [ ] **T-01（Scaffold & Auth）**: Universal App スキャフォールドから `smart-ops-hub` を初期化し、Fabric Entra SSO 認証（`authentication` パック）を有効化して初回デプロイを確認する（Lab 02）
- [ ] **T-02（Data Model & RLS & Mirroring）**: `RestockOrder` と `StoreNote` エンティティを `@text({ max })`・`@boolean()`・`@role` ポリシー付きで実装し、OneLake `MirroredWarehouse` への自動ミラーを検証する（Lab 03）
- [ ] **T-03（Fabric Connectors）**: `sm_ops_inventory`（`fabric-semanticmodel`）と `ops_warehouse`（`fabric-warehouse`）コネクタを追加し、ライブ DAX 集計とマスタ参照を実装する（Lab 04）
- [ ] **T-04（UX & Visuals）**: `specs/constitution.md` の Linear スタイル × Z の法則に従い、結論 KPI・地域別チャート・クロスフィルタ付き要補充キューを実装する（Lab 05）
- [ ] **T-05（Server-Side Functions & Agent）**: `submitRestockOrder` および `askOpsAdvisor` を `UserDataFunctions` で実装し、サーバー側監査記録と AI アシスタントドロワーを統合する（Lab 06）
- [ ] **T-06（Managed Storage）**: OneLake ベースの `attachments` ストレージフォルダー（最大 10 MiB、画像・PDF 限定）を構成し、`StoreNote` への証憑添付・ダウンロードを実装する（Lab 07）
- [ ] **T-07（Spec v2 Convergence）**: `specs/spec-v2-iteration.md` の追加要件（3 ペルソナ切替・ホバーカード・補充スケジュール＆`.ics` 出力）へ収束させる（Lab 08）
- [ ] **T-08（Deep-link, CI/CD & Governance）**: `@microsoft/rayfin-app-state-fabric` による URL 状態同期と `--dry-run` デプロイ検証を完了する（Lab 09）
