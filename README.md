# RWA特化型投資ニュース自動投稿システム 📰

**Google Trends + AI生成 + Note.com自動投稿** による完全自動化されたRWA投資ニュース配信システム

---

## 🎯 プロジェクト概要

このシステムは以下の処理を完全に自動化します：

1. **Google Trends分析** - RWA関連キーワード（Ondo、PAXG等）のリアルタイムトレンド取得
2. **AI記事生成** - Google Generative AI（Gemini）による信頼性の高いエビデンスベースの記事作成
3. **自動投稿** - Playwright ブラウザ自動化によるNote.com への自動投稿
4. **定時実行** - GitHub Actions により毎日08:00/18:00（日本時間）に完全自動実行

**実行環境:** 全処理はGitHub Actionsサーバーで実行するため、**ローカルPC側は低スペックでも対応** ✓

---

## 📋 システム構成

```
rwanews/
├── main.py                          # メインスクリプト
├── requirements.txt                 # Pythonライブラリ依存関係
├── .env.example                     # 環境変数テンプレート
├── README.md                        # このファイル
└── .github/
    └── workflows/
        └── post_news.yml            # GitHub Actions 定時実行設定
```

---

## 🚀 セットアップ手順

### ステップ1: リポジトリをGitHubに作成

```bash
# ローカルでリポジトリを初期化（まだ行っていない場合）
git init
git add .
git commit -m "Initial commit: RWA News Auto-Post System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rwanews.git
git push -u origin main
```

### ステップ2: GitHub Secrets を設定

GitHub リポジトリの **Settings → Secrets and variables → Actions** で以下を追加：

| Secret名 | 説明 | 取得方法 |
|---------|------|--------|
| `GOOGLE_API_KEY` | Google Generative AI APIキー | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `NOTE_EMAIL` | Note.com登録メールアドレス | Note.comアカウント |
| `NOTE_PASSWORD` | Note.comパスワード | Note.comアカウント |
| `SLACK_WEBHOOK` | Slack通知用（オプション） | [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks) |

**設定手順:**
1. GitHub リポジトリを開く
2. `Settings` → `Secrets and variables` → `Actions`
3. `New repository secret` をクリック
4. 各Secretを入力

### ステップ3: ローカルテスト（オプション）

ローカルで動作確認したい場合：

```bash
# 1. Python環境構築
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 依存ライブラリをインストール
pip install -r requirements.txt

# 3. .envファイルを作成
cp .env.example .env
# .envを編集して、Google APIキーとNote.comの認証情報を設定

# 4. Playwright ブラウザをインストール
playwright install chromium

# 5. スクリプト実行
python main.py
```

---

## 🔐 環境変数設定

### `.env.example` から `.env` を作成

```bash
cp .env.example .env
```

### `.env` ファイルの内容

```
# Google Generative AI
GOOGLE_API_KEY=your_api_key_here

# Note.com 認証情報
NOTE_EMAIL=your_email@example.com
NOTE_PASSWORD=your_password_here
```

**⚠️ セキュリティ注意:**
- `.env` ファイルを **必ず `.gitignore` に追加** してください
- APIキーやパスワードを **絶対にGitHubにコミットしないでください**
- GitHub Secretsを使用してください

---

## ⏰ 自動実行スケジュール

GitHub Actions により以下のスケジュールで自動実行されます：

| 時刻（日本時間） | 説明 |
|---------------|------|
| **08:00 JST** | 朝の市場開場時にRWAニュース投稿 |
| **18:00 JST** | 夕方の市場解説タイムにRWA分析投稿 |

**注:** Cron式は UTC 時間で指定されているため：
- `0 23 * * *` → 08:00 JST
- `0 9 * * *` → 18:00 JST

---

## 📊 生成される記事の構成

システムが生成するRWAニュース記事は以下の構成で投稿されます：

```
【タイトル】
キャッチーで正確なタイトル（最大60文字）

【見出し】
1. トレンドポイント
2. 市場への影響
3. 投資家への示唆

【本文】
300-400文字の詳細解説
- Google Trendsトレンドデータに基づく分析
- 主要20ソースからの信頼性の高い情報

【投資展望】
RWA市場の現状と今後の展開予測

【リスク要因】
重要な注意点と潜在的リスク
```

### 参考ソース（20個）

システムは以下の信頼性の高い20個のソースをエビデンスとして参考にします：

1. Coin Telegraph
2. The Block
3. Cointelegraph Japan
4. CoinDesk
5. The Defiant
6. Messari
7. Glassnode
8. DeFi Japan
9. Ethereum Foundation公式ブログ
10. Token Terminal
11. Web3 Foundation
12. DTJA（Digital Trade Japan Association）
13. 日本暗号資産取引業協会
14. 金融庁（仮想資産関連政策）
15. ブロックチェーン推進協会
16. Smart Contract Platform ドキュメント
17. Chainlink（オラクルニュース）
18. OpenZeppelin（スマートコントラクト監査）
19. Aave プロトコルニュース
20. MakerDAO（ステーブルコイン関連）

---

## 🔍 RWA関連キーワード

トレンド分析対象の9つのキーワード：

- **Ondo** - RWAプロトコル
- **PAXG** - 金現物連動トークン
- **RWA** - Real World Assets（実物資産）
- **tokenized assets** - トークン化資産
- **real world assets** - 実物資産
- **MKR** - Maker（DeFiプロトコル）
- **USDe** - Ethena（ステーブルコイン）
- **不動産トークン** - 日本語検索
- **実物資産トークン化** - 日本語検索

---

## 🛠️ トラブルシューティング

### 問題: GitHub Actions 実行失敗

**原因と解決方法:**

| エラーメッセージ | 原因 | 解決方法 |
|--------------|------|--------|
| `GOOGLE_API_KEY not found` | GitHub Secrets未設定 | Secrets設定を確認 |
| `Login failed` | Note.com認証情報が誤り | パスワード再確認 |
| `Playwright timeout` | ネットワーク接続問題 | GitHub Actions再実行 |
| `element not found` | Note.comのUI変更 | セレクタを更新 |

### 問題: ローカルでPlaywrightが動かない

```bash
# Playwrightブラウザを再インストール
playwright install chromium --with-deps
```

### 問題: Google Trends で403エラー

```
pytrends が Google から IP制限されている可能性
- GitHub Actions では自動的に回避されます
- ローカル実行時は VPN 使用を検討してください
```

### 問題: Note.com 投稿がタイムアウト

```python
# main.py の timeout値を増やす
await page.wait_for_url('**/n/**', timeout=15000)  # 15秒に変更
```

---

## 📝 実行ログ

実行ログはGitHub Actions内で自動保存されます：

1. GitHub リポジトリの `Actions` タブを開く
2. 実行履歴から対象のワークフロー実行を選択
3. `Artifacts` セクションで `execution-logs` をダウンロード

---

## 🔄 ワークフロー実行状況の確認

### GitHub Actions の確認方法

```
Settings → Actions → General → Workflow permissions
→ "Read and write permissions" を選択
```

### 手動実行（テスト）

GitHub Actions ワークフローを手動で実行：

1. `Actions` タブ
2. `RWA News Auto-Post` を選択
3. `Run workflow` をクリック

---

## 🚨 セキュリティベストプラクティス

- ✅ GitHub Secrets を使用してAPIキー・パスワードを管理
- ✅ `.env` ファイルは `.gitignore` に追加
- ✅ Note.com パスワード は **定期的に変更推奨**
- ✅ Google API キー に **利用制限を設定** （Generative AI のみに制限）
- ✅ GitHub Secrets の **アクセスログを定期確認**

---

## 📦 依存ライブラリ

| ライブラリ | バージョン | 用途 |
|----------|---------|------|
| pytrends | 4.10.0 | Google Trends データ取得 |
| playwright | 1.40.0 | ブラウザ自動化 |
| google-generativeai | 0.3.1 | Gemini API |
| python-dotenv | 1.0.0 | 環境変数管理 |

---

## 📄 ライセンス

MIT License

---

## 💬 サポート・バグ報告

問題が発生した場合：

1. **GitHub Issues** でバグ報告
2. **Discussions** で質問
3. ログファイルを添付してください

---

## 🎨 カスタマイズ例

### トレンドキーワードを追加

`main.py` の `RWA_KEYWORDS` を編集：

```python
RWA_KEYWORDS = [
    'Ondo', 'PAXG', 'RWA', 'tokenized assets',
    # 新しいキーワードを追加
    'your_keyword'
]
```

### 投稿時間を変更

`.github/workflows/post_news.yml` のスケジュールを編集：

```yaml
schedule:
  - cron: '0 0 * * *'   # 毎日09:00 JST に変更
  - cron: '0 12 * * *'  # 毎日21:00 JST に追加
```

### 記事生成プロンプトをカスタマイズ

`main.py` の `generate_news_article()` メソッドの `prompt` を編集。

---

## ✨ 今後の拡張予定

- [ ] Twitter/X 自動投稿機能
- [ ] Discord Webhook 通知
- [ ] 複数言語対応（英語、中国語）
- [ ] News API 統合
- [ ] データベース保存機能
- [ ] 投稿内容の分析・成功率追跡

---

## 📞 お問い合わせ

このプロジェクトに関するご質問・ご提案は、GitHub Issues でお願いします。

**Happy RWA News Posting! 🚀**
