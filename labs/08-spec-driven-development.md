# Lab 08 — 【補足＆実践】Spec-Driven 開発（FabCon — Sujata Narayana 氏セッション解説＆実践）

所要時間: 約 25 分
前提: [Lab 05](05-visuals-and-ux-design.md) 以降（[Lab 06](06-functions-and-agentic-actions.md)・[Lab 07](07-onelake-managed-storage.md) 完了後を推奨）

このラボでは、**FabCon（Microsoft Fabric Community Conference）および Microsoft Build** のセッションで **Sujata Narayana 氏**（Principal Group Product Manager, Power BI / Microsoft Fabric）らが提示した **Fabric Apps における Spec-Driven Development（仕様駆動開発 / SDD）** の考え方と実践ワークフローを深掘りし、実際にリポジトリ同梱の `specs/` を使ってアプリを v2 へ進化させます。

---

## 🧠 1. なぜ「Vibe Coding」ではなく「Spec-Driven 開発」なのか？（FabCon セッションの核心）

Sujata Narayana 氏はセッションの中で、AI 時代のカスタム Web アプリ開発が抱える最大の課題を次のように指摘しています：

> 💬 **Sujata Narayana 氏のメッセージ要旨**:
> *「AI によって誰もがデータからカスタム Web アプリを作れるようになりました。しかし現実には、Lovable や Streamlit などで作られた **“Vibe-coded（思いつきの対話だけで作った）アプリ” の大半は本番運用（Production）に到達しません**。AI が最初の **80%** を一瞬で作ってくれても、エンタープライズに必要な **残り 20%（認証・ガバナンス・RLS・信頼性・運用統制・継続保守性）** が欠けていれば、顧客や現場ユーザーには届けられないのです。」*

### Vibe Coding と Spec-Driven × Rayfin の決定的な違い

| 観点 | Vibe Coding（場当たり的なチャット開発） | Spec-Driven Development × Fabric Apps (Rayfin) |
|---|---|---|
| **真実の源泉（Source of Truth）** | 消えていくチャット履歴と生成された場当たりコード | Git 管理された **Markdown 仕様書（`specs/*.md`）** と **宣言的バックエンド（`rayfin.yml` + `@entity`）** |
| **変更・機能追加の方法** | 「ここも直して」「やっぱりタブ足して」とチャットを重ね、徐々に前の要件やデザインが壊れる（Context Drift） | **`spec.md` を更新し、「最新仕様にアプリを収束（Converge）させて」と指示する** |
| **本番に必要な残り 20%** | 認証・DB・API・権限・CORS 対策を手組みして破綻しやすい | **Rayfin + Microsoft Fabric** が Entra SSO・SQL DB・DAB・OneLake ガバナンス・モデル RLS を標準提供 |
| **チーム引き継ぎ・監査** | プロンプトを書いた本人しか意図が分からない | PR レビューで `spec.md` と `plan.md` の差分を合意・監査できる |

---

## 🏗️ 2. Fabric Apps における「二層の仕様（Dual-Layer Spec）」と GitHub Spec Kit

Fabric Apps by Rayfin と GitHub Copilot を組み合わせると、**プロダクト仕様** と **インフラ／バックエンド仕様** の二層がきれいに噛み合います。

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ Layer 1: 人間と AI が合意するプロダクト仕様（Markdown / GitHub Spec Kit）   │
│   0. specs/constitution.md  … 組織の不変ルール・セキュリティ・UX 原則      │
│   1. specs/spec.md          … 何を・誰のために作るか（What & Why）         │
│   2. specs/plan.md          … どの Rayfin サービスで実現するか（How）      │
│   3. specs/tasks.md         … 検証可能な実装ステップ分解                   │
│   +  specs/fit-gates/*.md   … テナント機能・データ粒度・ID 境界の事前確認  │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │ コーディングエージェント（Copilot CLI）が実装・収束
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ Layer 2: Rayfin コンパイラが実行保証するバックエンド仕様（TypeScript/YAML） │
│   ・rayfin/rayfin.yml       … Auth / Data / Connectors / Functions / Storage│
│   ・@entity() / @role()     … SQL スキーマ・GraphQL API・行／列認可を自動生成│
│   ・Source / executeQuery   … Fabric Semantic Model・Warehouse への型安全接続│
└────────────────────────────────────────────────────────────────────────────┘
```

### Sujata 氏が実演した「2 つの入力 ＋ 仕様更新ループ」
Sujata 氏のデモでは、次の極めてシンプルな反復サイクルで複雑な業務アプリ（複数ペルソナ・ホバーカード・カレンダータブ・Outlook 連携）を構築しています：
1. **初回構築**: コーディングエージェントに **① Markdown 仕様書（`spec.md`）** と **② セマンティックモデルの接続情報** の 2 つだけを渡し、アプリ構築からデプロイまでを実行させる。
2. **反復進化（Iteration）**: 新機能（ランディング切替、ペルソナ別画面、ホバーカード、カレンダー連携など）が欲しくなったら、**コードを直接いじるのではなく `spec.md` に要件を追記** し、Copilot に **「最新の `spec.md` を使ってアプリを更新して」** と伝える。

---

## 8-1. 同梱の Spec アーティファクト一式（`specs/`）を確認する

本リポジトリには、すでにここまでの Lab 02〜07 の設計意図を体系化した `specs/` が用意されています。まず中身を確認させましょう。

> 🗣️ **プロンプト**
> ```text
> リポジトリの `specs/` 配下にある `constitution.md`、`spec.md`、`plan.md`、`tasks.md`、および `fit-gates/` の3ファイルを読んで、
> 現在の `smart-ops-hub` の実装が `constitution.md` と `spec.md` の受入基準をすべて満たしているかギャップ診断（Converge チェック）をして。
> ```

🤖 **Copilot の動き**
- `specs/` 内の各 Markdown 文書と `smart-ops-hub/` の現在のソースコードを突き合わせ、原則違反（例: `@role` 漏れ、`@text` の `max` 漏れ、グラデーション混入など）がないか監査レポートを出力します。

✅ **期待する結果**
現在の実装と v1 仕様（`specs/spec.md`）の整合性が確認される（軽微な差分があればその場で解消できます）。

---

## 8-2. 仕様書を v2 へ更新する（Sujata 氏セッションと同型の機能拡張）

次に、Sujata 氏のセッションデモでも登場した代表的な 3 つの業務アプリ拡張を定義した **`specs/spec-v2-iteration.md`** を確認し、仕様書を更新します：
1. **ペルソナ別ビュー切替（Persona Switcher）**: `Executive（経営サマリー）` / `Regional Manager（リージョン運用）` / `Store Staff（店舗現場メモ＆証憑集中）` の 3 モード切替
2. **リッチ・ホバーカード（Hover Card Tooltip）**: 要補充キューの商品／店舗にフォーカスすると、単価・リードタイム・ロット単位・店舗ティア・担当連絡先をポップオーバー表示
3. **補充入荷スケジュールタブ（Replenishment Schedule ＋ Outlook 用 `.ics` 出力）**: 起票済み発注に商品のリードタイム日数を加算して入荷予定タイムラインを表示し、ワンクリックで `.ics` カレンダー予定をダウンロード

> 🗣️ **プロンプト**
> ```text
> `specs/spec-v2-iteration.md` の追加要件3点（ペルソナ別ビュー切替・リッチホバーカード・補充入荷スケジュールタブと .ics 出力）を `specs/spec.md` に統合し、
> それに合わせて `specs/plan.md` と `specs/tasks.md` も最新化して。まだアプリコードは変更せず、更新した仕様と実装計画を要約して見せて。
> ```

🤖 **Copilot の動き**
- いきなりコードを書くのではなく、まず **Specify → Plan → Tasks** の Markdown アーティファクトを更新し、設計上の影響範囲（既存バックエンド変更は不要でフロントエンドのビュー層と `.ics` 生成ユーティリティ追加で完結すること等）を整理して提示します。

✅ **期待する結果**
`specs/spec.md`、`specs/plan.md`、`specs/tasks.md` が v2 仕様に更新される。

---

## 8-3. 更新された仕様書からアプリを収束（Implement & Converge）させる

仕様と計画が固まったら、Sujata 氏のデモと同じ一言でエージェントに実装・検証を任せます！

> 🗣️ **プロンプト**
> ```text
> 最新の `specs/constitution.md`、`specs/spec.md`、`specs/plan.md`、`specs/tasks.md` に従って、`smart-ops-hub` を v2 仕様へ実装・収束（Converge）させて。
> 実装後、型チェック・テスト・ビルドを通し、`specs/tasks.md` の完了チェックを更新してから Fabric へ再デプロイして。
> ```

🤖 **Copilot の動き**
- `specs/constitution.md` のガードレール（単一アクセント色・グラデーション禁止・`tabular-nums`・WCAG AA・既存認証／コネクタ維持）を守ったまま、3 つの新機能を実装します。
- `npm test` / `npm run build` が成功することを確認し、`specs/tasks.md` のチェックボックスを更新します。
- バックエンド変更がないため `npx rayfin up staticapp deploy`（または `npx rayfin up --workspace-id "$WS_ID" --yes`）で Fabric へ反映します。

✅ **期待する結果（v2 受入基準の達成）**
Fabric ポータルで `smart-ops-hub` を再読み込みし、次の 3 点がすべて動作することを確認します：
1. **ペルソナ切替**: ヘッダーで `Executive` / `Regional Manager` / `Store Staff` を切り替えると、それぞれの役割に最適化された画面構成へ切り替わる。
2. **ホバーカード**: `ST-005 × SKU-120` 行にホバー／フォーカスすると、`Devices / 単価 ¥8,900 / リードタイム 8 日 / ロット 8 個 / Flagship` が即座に表示される。
3. **補充スケジュール＆カレンダー連携**: 「補充スケジュール」タブに起票済み発注の入荷予定日が表示され、`.ics` ボタンから Outlook 等に取り込める予定ファイルがダウンロードできる 🎉

---

## 💡 実案件でさらに本格運用する場合（GitHub Spec Kit 連携）

チーム開発や顧客向け SI／内製開発で Spec-Driven 開発を標準化する場合は、[GitHub Spec Kit](https://github.com/github/spec-kit) CLI をリポジトリに導入することで、Copilot 内のスラッシュコマンド（`/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`）として定型運用することもできます。

また、提案・要件定義フェーズでは必ず `specs/fit-gates/` の 3 シート（**Capability / Data / Identity Fit Gate**）を最初に埋めることで、「プレビュー未対応機能を見積もりに入れてしまう」手戻りをゼロにできます。

---

## ✅ チェックポイント

- [ ] Vibe Coding が本番の「残り 20%」でつまずく理由と、Spec-Driven × Rayfin の役割分担を理解した
- [ ] `specs/constitution.md` / `spec.md` / `plan.md` / `tasks.md` の 4 文書フローを体験した
- [ ] 仕様書の更新だけで 3 ペルソナ切替・ホバーカード・補充スケジュール（`.ics` 出力）を一貫したデザインで追加・デプロイできた

次は、完成したアプリを本番レベルで運用するための **ポータル埋め込み・ディープリンク状態共有・マルチ環境昇格・GitHub Actions CI/CD・ガバナンス＆課金** を学ぶ [Lab 09 — ポータル埋め込み・ディープリンク・CI/CD・ガバナンス](09-portal-deeplink-cicd-governance.md) へ進みます 🚀
