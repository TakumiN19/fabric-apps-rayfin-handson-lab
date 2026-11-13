# Lab 10 — Fabric Apps Gallery ＆ `awesome-rayfin` 全テンプレート解剖・設計選定カタログ

所要時間: 約 15 分（リファレンス＆任意スキャフォールド演習）

このラボでは、Microsoft 公式テンプレートギャラリー **[microsoft/awesome-rayfin](https://github.com/microsoft/awesome-rayfin)**（全 20 テンプレート）と、コミュニティショーケース **Fabric Apps Gallery** の代表アプリを **7 つの業務アーキテクチャ類型** に分類して解説します。

顧客提案や社内ハッカソンで「どんな業務アプリが Fabric Apps に向いているか？」「どのテンプレートをベースに始めるべきか？」を判断する実践カタログとして活用してください。

---

## 🏛️ 1. `microsoft/awesome-rayfin` ＆ Fabric Apps Gallery 7 大アーキテクチャ類型

すべての公式テンプレートは以下のワンライナー（対話ピッカー付き）で手元にスキャフォールドできます：

```bash
npm create @microsoft/rayfin -- --template https://github.com/microsoft/awesome-rayfin
```

### 類型 ①：セマンティックモデル分析 ＋ 業務 Write-back（王道「Insight to Action」型）
Power BI の強み（Direct Lake・DAX メジャー・RLS）をそのまま活かしつつ、レポートでは不可能な「発注・予測修正・承認サインオフ」を同じ画面で行う最頻出パターンです。

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`caldova-reorder`** *(LTG291 公式セッション事例)* | 医薬品卸の地域マネージャー向け欠品補充アプリ。Direct Lake セマンティックモデルを `fabric-semanticmodel`（`delegated` + RLS）で読み、`sendReorder` **Function** 経由でアプリ SQL DB に発注を書き込み、OneLake ミラーでモデルへ還流させる本ハンズオンの原典構成 | Auth, Data, Functions, Semantic Model Connector |
| **`caldova-finance-ibcs`** | IBCS（国際ビジネスコミュニケーション標準）準拠の P&L・BS・CF 3 財務諸表アプリ。コントローラーが予測値を調整すると 3 表が連動し、差異コメントと月次サインオフを Rayfin Data に記録 | Auth, Data, IBCS Visuals |
| **`caldova-cologne-digital-twin`** | ケルン物流拠点のフォトリアル 3D デジタルツイン＋配送ルート＋ `caldova-reorder` ＋ `caldova-finance-ibcs` を 1 アプリに統合した総合ショーケース | Auth, Data, Semantic Model, 3D Geodata |

### 類型 ②：現場オペレーション・フィールドワーク管理（CRUD ＋ ロール別 UX 型）
スプレッドシートとチャットに散在していた現場作業・点検・ディスパッチを 1 つの業務アプリに統合するパターンです。

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`field-technician`** | ディスパッチャー（配車担当）とフィールド技術者のロール別ダッシュボード、作業指示（Job / TaskItem / JobLog）、機器・顧客検索を備えた現場業務アプリ | Auth, Data（8 エンティティ・リレーション） |
| **Community: `Ray\|Works`** (`sinedied/rayworks`) | 業務入力フォーム、ライブ聴衆エンゲージメント、出張精算レポート、データ駆動プレゼンを揃えた業務アプリ群 | Auth, Data, Functions, Static Hosting |

### 類型 ③：Fabric / Power BI ガバナンス・運用管理ツール（Platform-on-Platform 型）
Fabric 自身の管理 API・メタデータ・スケジュール・ベストプラクティス診断を、Rayfin アプリとして内製ツール化する非常に人気の高いパターンです（Fabric Apps Gallery でも多数公開）。

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`pbi-fixer`** | Power BI セマンティックモデルと PBIR レポートの Best Practice Analyzer。ワンクリック／一括修正、PBIR diff 表示、AI メタデータ整理をサーバーサイド **User Data Functions** 経由で実行 | Auth, Functions (UDF), Fabric API |
| **`fabric-user-manager`** | ワークスペースロール・アプリ Audience・RLS/OLS の背後にある Entra グループへの **委任型アクセス申請＆オーナー承認ワークフロー**。SP 不要でサインインユーザー権限で動作＋オフラインモック（`VITE_UM_MOCK=true`）搭載 | Auth, Data（申請・監査ログ）, Graph / Fabric REST |
| **`fabric-atlas`** | マルチワークスペース横断のカタログ・リネージ・アクセスレビューアプリ | Auth, Data（検証済みスナップショット） |
| **`semantic-directory`** | 任意のセマンティックモデルのメジャー・列・リネージ・変更影響範囲（Measure DNA）を横断検索できる辞書アプリ | Auth, Static Hosting |
| **Gallery: `Schedule Inventory`** (`kilianbs/fabric-schedule-inventory`) | Fabric Apps Gallery 代表作。参照可能な全ワークスペースのスケジュール設定済みアイテムを UDF `syncInventory` で走査し、24 時間 **Gantt タイムライン** と同時実行ピーク負荷を可視化 | Auth, Data, Functions (UDF) |
| **Gallery: `Data Quality Monitor`** | 完全性・妥当性・一意性など 7 ルールでデータ品質を監視し、実行履歴と課題解消（Issue Resolution）を記録する品質管理アプリ | Auth, Data |

### 類型 ④：経営企画・FP&A・高度分析（エクスポート＆オフライン対応型）

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`finance-analytics`** | 設定駆動の FP&A 分析アプリ。予実差異・トレンド・滞留表、Excel ネイティブコピー、クロスフィルタ、決定論的インテリジェンスレール、**PowerPoint / Excel / CSV エクスポート** を備え、オフライン標本とライブモデルの両対応 | Auth, Semantic Model, Export |

### 類型 ⑤：Real-Time Intelligence（Eventhouse）＆ 3D 空間デジタルツイン型

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`helsinki-public-transport`** | Fabric Real-Time Intelligence（Eventhouse）上の DirectQuery モデルからヘルシンキ公共交通のリアルタイム位置を 2D マップ＆オープン地理空間 3D 都市ツインに描画 | Auth, RTI / Eventhouse |
| **`campus-scheduler`** | ドイツ 8 大学の LoD2 3D キャンパスツイン上で時間割のハード制約衝突を検知し、OR-Tools CP-SAT ソルバーで最小変更の修復案を提示 | Auth, Data, 3D + Solver |
| **`maritime-insights` / `paragliding-insights`** | 1m 地形 DEM と LoD2 建物を用いた沿岸センサー可視域シミュレーション／アルプス飛行リプレイ＆ライブ動態 | Auth, 3D Geodata |

### 類型 ⑥：コラボレーション・学習・ゲーミフィケーション型

| テンプレート / 事例 | 概要と注目アーキテクチャ | 使用機能 |
|---|---|---|
| **`slide-deck`** | セッション共有・リアルタイムのスライド進行同期・聴衆チャットを備えたインタラクティブ登壇アプリ | Auth, Data (`Slideshow`, `Session`, `ChatMessage`) |
| **`ibcs-trainer`** | HTML5 Canvas プラットフォーマーゲーム形式で IBCS チャート設計ルールを学び、スコアを `GameStats` エンティティに永続化 | Auth, Data |

### 類型 ⑦：最小スターター・マルチフレームワーク・ローカル実験型

| テンプレート | 特徴と選びどころ |
|---|---|
| **`universal-app`** *(既定推奨)* | Capability Router 内蔵。プロンプトに応じて `authentication`, `data-modeling`, `graphein-visuals`, `analytics` をオンデマンド有効化 |
| **`static-blankapp`** | フレームワーク無しの素の TypeScript + Vite 最小構成 |
| **`angular-blankapp` / `angular-dashboard`** | Angular + Angular Material 採用組織向けの認証済みスターター／ダッシュボード |
| **`todo-local-experimental`** | Docker ローカル開発（`--provider docker`）とパスワード認証を試す実験用スターター |

---

## 🧭 2. 案件・ユースケース別 アーキテクチャ選定ディシジョンマトリクス

「Power BI レポートで作るべきか？ Fabric App で作るべきか？ どの Rayfin 機能を組み合わせるべきか？」を即断するための指針です。

### Q1. Power BI レポート vs Fabric Apps（Rayfin）の境界線は？
- **Power BI レポートが最適**: 定型 KPI 監視、スライサー／ドリルダウン分析、既存 BI ガバナンス内での閲覧完結（書き込み不要）。
- **Fabric Apps（Rayfin）が最適**:
  1. **分析のすぐ横で業務アクション（発注・承認・コメント・計画値修正・ファイル添付）を完結** させたい
  2. **マルチステップ業務フロー・ロール／ペルソナ別の専用 UI・3D／地図／Gantt 等の自由なカスタム UX** が必要
  3. **AI エージェントの提案 → 人間のレビュー承認 → OneLake 還流（Decision Loop）** を 1 画面に組み込みたい

### Q2. どのデータ接続・書き込みパターンを選ぶべきか？

| 要件 | 推奨構成 |
|---|---|
| 既存のセマンティックモデルのメジャーと RLS をそのまま活かしたい | `fabric-semanticmodel` コネクタ（`delegated`） |
| 全ユーザーにモデルの Build 権限を配らず高速に集計を見せたい | Warehouse コネクタ（`application`）またはアプリ SQL DB へのスナップショット投入 |
| 単純なユーザー個人メモ・設定の保存 | `client.data.<Entity>` ＋ `@role('authenticated', '*', { policy: claims.sub.eq(...) })` |
| 業務承認・購買連携・改ざん防止の監査記録・外部 API／AI 呼び出し | **Rayfin Functions（`UserDataFunctions`）** 経由でサーバー側から `ctx.getDataClient()` 書き込み |
| 写真・PDF・証憑ファイルの保管 | SQL には相対パスのみ保存し、実体は **Rayfin Storage（OneLake）** へ保存 |

---

## 🧪 10-1.（任意演習）ギャラリーテンプレートを 1 つスキャフォールドして構造を比較する

気になるギャラリーテンプレートを別フォルダに展開し、自分たちが作った `smart-ops-hub` と見比べてみましょう！

> 🗣️ **プロンプト**
> ```text
> ルート直下の `gallery-sandbox/` フォルダに、`microsoft/awesome-rayfin` の `field-technician`（または `caldova-reorder`）テンプレートをスキャフォールドして（デプロイはしない）、
> その `rayfin/rayfin.yml`、エンティティ設計、オフライン／認証切り替えの工夫を `smart-ops-hub` と比較して解説して。確認が終わったら一時フォルダの扱いも案内して。
> ```

🤖 **Copilot の動き**
- `npx @microsoft/rayfin-cli init gallery-sandbox -t microsoft/awesome-rayfin --template-name "Field Technician App"` 等でテンプレートを取得し、設計上の工夫（ロール別 UI、複数エンティティ間の `@one`/`@many`、デュアルモード認証など）を抽出して解説します。

---

## 🎉 全ラボ完了！おつかれさまでした！

これで **Fabric Apps by Rayfin ハンズオン（Lab 00〜10）** の全カリキュラムが完了です！

あなたがこのハンズオンで習得・実践したこと：
- ✅ **Universal App ＆ Entra SSO 認証** によるガバナンス準拠のアプリ基盤構築
- ✅ **宣言的データモデル（`@entity`）・`@role` 行／列レベル認可・OneLake 自動ミラーリング** による Zero-ETL Write-back
- ✅ **ネイティブ Fabric Data Connectors** による Semantic Model（ライブ DAX / RLS）＆ Warehouse 連携
- ✅ **Visuals Pack ＆ Linear スタイル × Z の法則** による洗練されたコントロールタワー UX
- ✅ **Rayfin Functions（UDF）＆ Secrets** によるサーバーサイド業務ロジックと会話型 AI ドロワー統合
- ✅ **OneLake マネージド Storage** による型安全な証憑・画像管理
- ✅ **Spec-Driven 開発（Sujata Narayana 氏 FabCon セッション流）** による Markdown 仕様更新からの反復収束
- ✅ **ディープリンク・マルチ環境・GitHub Actions CI/CD・Fabric Apps Gallery 設計パターン** の体系的理解

ぜひ自社のデータ資産（Semantic Model / Lakehouse / Warehouse）と `specs/` テンプレートを掛け合わせて、**「見るだけの BI」を超えるアクション指向のエンタープライズ Fabric Apps** を生み出してください 🚀
