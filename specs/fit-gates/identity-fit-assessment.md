# Identity & Security Fit Assessment Gate（認証・認可境界確認票）

| レイヤー | 認証主体（Identity） | 認可境界（Authorization） | 注意点 |
|---|---|---|---|
| アプリ画面・静的資産 | Microsoft Entra ID（Fabric SSO） | Workspace / App の `Run and interact` 権限 ＋ `assetAccess: protected` | `public` にしてもバックエンド Data API は匿名公開されない |
| Rayfin Data（`@entity`） | サインイン中のアプリ利用者 | `@role('authenticated', ...)` および `claims.sub.eq(...)` による行所有者制限 | `@role` 省略は禁止。複雑な業務ルール（発注検証・監査刻印）は Functions へ委譲 |
| Semantic Model Connector | `delegated`（サインイン中の利用者本人） | セマンティックモデルの `Read + Build` 権限およびモデルの RLS / OLS | サービスプリンシパルや `application` モードは使用不可 |
| Warehouse / SQL Connector | 既定 `application`（アプリ所有者）、必要に応じて `delegated` | 共有マスタ参照は `application`、ユーザー別行制限が必要なら `delegated` | CLI 1.36.2 では `rayfin.yml` の `auth.type` を明示確認する |
| Rayfin Functions | 実行基盤は `application`（アイテム所有者）、呼び出し元情報は `RayfinContext` から取得 | `udf.connection({ audienceType: AudienceType.Fabric })` 等で必要な Audience のみバインド | シークレットはコードや `.env` に書かず `npx rayfin secret set` で管理する |
