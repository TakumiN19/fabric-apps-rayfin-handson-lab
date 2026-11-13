# Product Specification (v2 Iteration) — ペルソナ切替・ホバーカード・補充スケジュールタブの追加

> 💡 **Lab 08（Spec-Driven 開発の実践）用ファイル**:
> FabCon / Build での **Sujata Narayana 氏**のデモ（「チャットで場当たり的に指示を足すのではなく、Markdown 仕様書を更新して Copilot にアプリを収束（Converge）させる」）を体験するための v2 仕様差分です。

`specs/spec.md` の全要件を維持したまま、以下の 3 機能を追加する。

## 追加要件 1: ペルソナ別ビュー切替（Persona Switcher）

ヘッダー右上に **ペルソナ切替セグメント** を追加し、役割に応じた最適ビューへ切り替える：
1. **Executive（経営サマリー）**: 全社 KPI 4 枚、リージョン別リスク比較、トップ 5 緊急補充リストのみに絞ったエグゼクティブ向け簡潔ビュー。
2. **Regional Manager（リージョン運用・既定）**: 既存のフル機能コントロールタワー（クロスフィルタ＋発注起票＋AI エージェント質問）。
3. **Store Staff（店舗現場）**: 店舗セレクター（`ST-001`〜`ST-012`）を最上部に固定し、自店舗の点検メモ（`StoreNote`）登録と検品写真／PDF アップロードに集中できる現場向けビュー。

## 追加要件 2: 商品・店舗ホバーカード（Rich Hover Card Tooltip）

要補充キュー（Low-Stock Action Queue）の商品コード（`sku`）または店舗名にマウスホバー／キーボードフォーカスした際、画面遷移なしで以下の詳細カードを表示する：
- 商品カテゴリ、単価（`unit_price`）、リードタイム（`lead_time_days` 日）、発注ロット単位（`reorder_pack_qty` 個）
- 店舗ティア（`Flagship` / `Standard` / `Compact`）、担当マネージャー連絡先（`manager_upn`）、ワンクリック「担当へ連絡（mailto リンク）」

## 追加要件 3: 補充入荷スケジュールタブ（Replenishment Calendar Tab）

メインナビゲーションに **「補充スケジュール（Schedule）」タブ** を追加する：
- 起票済みの `RestockOrder` について、`requested_at` ＋ 商品の `lead_time_days` から **入荷予定日（Expected Arrival Date）** を算出し、7 日間のタイムライン／カレンダーリスト形式で店舗別に入荷予定を一覧表示する。
- 各予定アイテムに「予定を `.ics` カレンダーファイルとしてダウンロード（Outlook 連携用）」ボタンを設ける。

## 追加受入基準（v2 Convergence Checks）

1. ヘッダーで 3 ペルソナ（Executive / Regional Manager / Store Staff）を切り替えると、各ペルソナ専用のレイアウトが即座に描画されること。
2. `ST-005 × SKU-120` 行のホバーカードに `Devices / ¥8,900 / リードタイム 8 日 / ロット 8 個` が正確に表示されること。
3. 補充発注を 1 件登録すると、「補充スケジュール」タブにリードタイム加算後の入荷予定日が表示され、`.ics` ファイルがダウンロードできること。
4. `specs/constitution.md` のデザイン原則（単一アクセント色・グラデーション禁止・WCAG AA）および `npm run build` が引き続きすべてパスすること。
