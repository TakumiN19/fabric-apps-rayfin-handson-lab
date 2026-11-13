# Spec-Driven Development（仕様駆動開発）アーティファクト一式

このディレクトリには、FabCon / Microsoft Build のセッションで **Sujata Narayana 氏**（Principal GPM, Power BI / Microsoft Fabric）らが紹介した **Spec-Driven Development（SDD）**、および [GitHub Spec Kit](https://github.com/github/spec-kit) / Forward-Deployed Engineering のパターンを Fabric Apps（Rayfin）に適用した実ファイル一式を収録しています。

[Lab 08 — Spec-Driven 開発（FabCon セッション解説＆実践）](../labs/08-spec-driven-development.md) でそのまま使用します。

## ファイル構成と役割

| ファイル | フェーズ | 役割 |
|---|---|---|
| `constitution.md` | 0. Constitution | 組織・プロジェクト不変の品質原則・セキュリティ・Rayfin 1.36.2 ガードレール・UI デザイン規約 |
| `spec.md` | 1. Specify (v1) | `Smart Ops Hub` の初期製品仕様（ペルソナ、Zの法則画面構成、KPI、発注アクション、受入基準） |
| `spec-v2-iteration.md` | 1b. Specify (v2) | Sujata 氏のデモと同様に **仕様書を更新してアプリを進化させる** 反復開発用の差分更新仕様（ペルソナ切替・ホバーカード・補充スケジュールタブ追加） |
| `plan.md` | 2. Plan | 仕様を Rayfin サービス（Auth / Data / Connectors / Functions / Storage / Static Hosting）へマッピングした技術設計書 |
| `tasks.md` | 3. Tasks | コーディングエージェント（GitHub Copilot CLI）が境界を守って順番に実装・検証するためのタスク分解票 |
| `fit-gates/capability-assessment.md` | Fit Gate | 対象テナント・リージョン・容量での機能利用可否プローブ記録票 |
| `fit-gates/data-fit-assessment.md` | Fit Gate | アプリ専用 SQL DB・Connector・OneLake ミラー・データ粒度の適合性評価票 |
| `fit-gates/identity-fit-assessment.md` | Fit Gate | Entra SSO・`@role` ポリシー・`delegated` vs `application` 認証境界の評価票 |
