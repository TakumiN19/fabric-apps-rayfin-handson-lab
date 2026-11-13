# 受講者向け — Microsoft Fabric ポータルへのサインイン手順

所要時間: 約 5 分

Fabric Apps（Rayfin）は **Microsoft Entra ID（Fabric SSO）** と深く統合されており、ブラウザ上で現在サインインしているアカウントの権限を使ってアプリ認証やセマンティックモデルへの委任クエリ（`delegated`）を行います。
会社の通常アカウントと混ざるのを防ぐため、**シークレット／InPrivate ウィンドウ** の利用を強く推奨します。

---

## 手順 1. InPrivate / シークレットウィンドウを開く

- **Microsoft Edge**: 右上 `…` メニュー → **新しい InPrivate ウィンドウ**（<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> / macOS は <kbd>⌘</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd>）
- **Google Chrome**: 右上 `⋮` メニュー → **新しいシークレット ウィンドウ**（<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> / macOS は <kbd>⌘</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd>）

## 手順 2. Fabric ポータルへサインインする

1. アドレスバーに `https://app.fabric.microsoft.com` を入力して開きます。
2. [Lab 00](00-prerequisites.md) で登録した自分のアカウント（例: `student3@M365x43914722.onmicrosoft.com` または自分の検証テナント UPN）でサインインします。
3. すでに別アカウントでサインインされていた場合は、右上のプロフィールアイコン → **Sign out（サインアウト）** を実行してから入り直します。

## 手順 3. ワークスペースと容量割り当てを確認する

1. 左ナビゲーションの **Workspaces（ワークスペース）** をクリックし、自分のワークスペース（例: `student3`）を開きます。
2. ワークスペース名の横に **ダイヤモンドアイコン（💎 Fabric 容量割り当て済み）** が表示されていることを確認します。
   - ダイヤモンドがない場合、Fabric Apps や SQL Database・Warehouse を作成できません。講師または管理者に容量割り当てを確認してください。

## 手順 4. （Lab 01・04 でセマンティックモデルを使う場合）ライセンス確認

右上のプロフィールアイコンをクリックし、**Power BI Pro**・**Premium Per User (PPU)** または有効なトライアルが付与されているか確認します。

> [!IMPORTANT]
> 個人ライセンスのトライアルを開始する場合でも、**自分のワークスペースが割り当てられている共有の有料 Fabric 容量（F2 / F32 等）は絶対に変更しないでください**。別の Trial 容量へ移動すると Data Agent 等の機能が利用できなくなります。

## 手順 5. Fabric Apps が作成可能か目視確認する（任意）

自分のワークスペース内で **+ New item（新しいアイテム）** をクリックし、検索欄に `App` または `User data functions` と入力してアイテム候補が表示されれば、テナント設定の準備は完了しています。
（本ハンズオンではポータルから手作業で作るのではなく、Lab 02 以降で **Rayfin CLI + Copilot CLI** からコードファーストで自動作成します。）
