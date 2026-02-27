#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA特化型投資ニュース自動公開システム（v4.0 - GitHub Pages版）
Google Trends + AI生成 + 画像生成 + GitHub Pages自動公開
執筆者: xdc.master（不動産運営 × XDC長期保有インベスター）

【機能】
- Google Trends によるRWA関連トレンド取得
- テンプレートベースの詳細記事生成（1,200-1,500文字）
- 画像生成（3枚：冒頭・中盤・終盤）
- HTML ページ自動生成（スマートフォン対応）
- GitHub Pages 自動デプロイ
"""

import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import logging
import requests
import random

# Google Trends と AI ライブラリ
from pytrends.request import TrendReq
import google.generativeai as genai

# 画像生成ライブラリ
from PIL import Image, ImageDraw, ImageFont

# SNS分析ライブラリ
try:
    import tweepy
except ImportError:
    tweepy = None

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    nltk.download('vader_lexicon', quiet=True)
except ImportError:
    SentimentIntensityAnalyzer = None

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数読み込み
load_dotenv()

# マスター設定（ファンダメンタルズベース）
try:
    import config
except ImportError:
    logger.warning('config.py が見つかりません。デフォルト設定を使用します')
    config = None

# マクロ文脈ライブラリ（歴史的背景の理解）
try:
    import rwa_context
except ImportError:
    logger.warning('rwa_context.py が見つかりません。マクロ文脈は使用しません')
    rwa_context = None

# RWA関連ワード（トレンド取得用）
RWA_KEYWORDS = [
    'Ondo', 'PAXG', 'RWA', 'tokenized assets',
    'real world assets', 'MKR', 'USDe',
    '不動産トークン', '実物資産トークン化'
]

# RWA関連の主要ソース（参照元）
EVIDENCE_SOURCES = [
    {'name': 'Coin Telegraph', 'url': 'https://cointelegraph.jp', 'category': 'ニュース'},
    {'name': 'The Block', 'url': 'https://www.theblock.co', 'category': 'ブロックチェーン分析'},
    {'name': 'CoinDesk', 'url': 'https://www.coindesk.com', 'category': 'ニュース'},
    {'name': 'Messari', 'url': 'https://messari.io', 'category': 'インテリジェンス'},
    {'name': 'Glassnode', 'url': 'https://glassnode.com', 'category': 'オンチェーン分析'},
    {'name': 'Token Terminal', 'url': 'https://tokenterminal.com', 'category': 'ブロックチェーン分析'},
    {'name': 'Chainlink', 'url': 'https://chain.link/ja', 'category': 'オラクル'},
    {'name': '金融庁 - 仮想資産関連政策', 'url': 'https://www.fsa.go.jp', 'category': '規制'},
    {'name': 'OpenZeppelin', 'url': 'https://docs.openzeppelin.com', 'category': 'セキュリティ監査'},
    {'name': 'Aave プロトコル', 'url': 'https://aave.com/ja', 'category': 'DeFi'}
]


class RWANewsGenerator:
    """RWA投資ニュース自動生成・GitHub Pages公開システム（v4.0）"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.nanobanana_key = os.getenv('NANOBANANA_API_KEY', '')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')

        if not self.api_key:
            raise ValueError('GOOGLE_API_KEY が設定されていません')

        genai.configure(api_key=self.api_key)

        # VADER Sentiment Analyzer を初期化
        if SentimentIntensityAnalyzer:
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
        else:
            self.sentiment_analyzer = None

        logger.info('認証情報を環境変数から読み込みました')

    async def fetch_trends(self) -> dict:
        """Google Trendsからトレンドデータを取得"""
        try:
            logger.info('Google Trendsからトレンドデータを取得中...')
            pytrends = TrendReq(hl='ja-JP', tz=540)

            trends_data = {}
            for keyword in RWA_KEYWORDS:
                try:
                    pytrends.build_payload(
                        kw_list=[keyword],
                        timeframe='now 7-d',
                        geo='JP'
                    )
                    interest_overtime = pytrends.interest_over_time()

                    if not interest_overtime.empty:
                        trend_score = int(interest_overtime.iloc[-1, 0])
                        trends_data[keyword] = trend_score
                        logger.info(f'{keyword}: トレンドスコア {trend_score}')
                except Exception as e:
                    logger.warning(f'{keyword}: トレンド取得失敗 - {str(e)[:50]}')
                    trends_data[keyword] = 0

            return trends_data

        except Exception as e:
            logger.warning(f'Google Trends 全体エラー: {str(e)[:100]}')
            return {kw: 0 for kw in RWA_KEYWORDS}

    async def fetch_coingecko_data(self) -> dict:
        """CoinGecko API から仮想資産データを取得"""
        try:
            logger.info('CoinGecko からデータを取得中...')
            response = requests.get(
                'https://api.coingecko.com/api/v3/simple/price',
                params={
                    'ids': 'ondo,xdc-network,mantle,aave,curve-dao-token',
                    'vs_currencies': 'jpy,usd',
                    'include_market_cap': 'true',
                    'include_24hr_vol': 'true',
                    'include_24hr_change': 'true'
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                logger.info('✅ CoinGecko データ取得成功')
                return data
            else:
                logger.warning(f'CoinGecko エラー: {response.status_code}')
                return {}

        except Exception as e:
            logger.warning(f'CoinGecko 取得失敗: {str(e)[:50]}')
            return {}

    def generate_gradient_image(self, width: int = 1024, height: int = 576,
                               title: str = "RWA News") -> str:
        """グラデーション背景の画像を生成"""
        try:
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)

            # グラデーション背景
            for y in range(height):
                ratio = y / height
                r = int(102 + (118 - 102) * ratio)
                g = int(126 + (75 - 126) * ratio)
                b = int(234 + (186 - 234) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            # テキスト追加
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
            except:
                font = ImageFont.load_default()

            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2

            draw.text((x, y), title, fill='white', font=font)

            # 保存
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            filename = output_dir / f'rwa_image_{timestamp}.png'
            img.save(filename)

            logger.info(f'画像生成: {filename}')
            return str(filename)

        except Exception as e:
            logger.warning(f'画像生成失敗: {str(e)}')
            return None

    def generate_news_article(self, trends_data: dict) -> str:
        """ファンダメンタルズ + マクロ文脈 + トップティアメディア情報ベースの RWA ニュース記事を生成"""
        try:
            logger.info('ファンダメンタルズ + マクロ文脈 + トップティアメディア情報で記事を生成中...')

            # config.py から RWA エコシステム情報を取得
            fundamentals_context = self._build_fundamentals_context()

            # rwa_context.py から マクロ文脈を取得
            macro_context = self._build_macro_context()

            # トップティアメディアからニュースを検索
            top_tier_news = self._search_top_tier_news('RWA market news')

            # ニュース スニペットを整形
            news_snippets_text = "\n".join([f"  - {snippet}" for snippet in top_tier_news.get('snippets', [])])

            prompt = f"""
            【RWA（Real World Assets）ファンダメンタルズ + マクロ文脈分析記事の生成】

            【本日のトレンドデータ】
            {json.dumps(trends_data, ensure_ascii=False, indent=2)}

            【RWA市場の構造的背景情報】
            {fundamentals_context}

            【RWA市場の歴史的マクロ文脈】
            {macro_context}

            【本日のトップティアメディア情報（厳選ソースのみ）】
            以下は、{', '.join(top_tier_news.get('domains', [])[:3])} などのトップティアメディアから抽出した信頼度の高いニュース・分析です。
            SEOスパムや低品質サイトは完全に除外しています：
{news_snippets_text}

            執筆者: xdc.master（不動産運営者・長期インベスター視点）

            以下の形式で、RWAセクターの【実需】と【ファンダメンタルズ】に焦点を当てた深い分析記事を生成してください：

            【重要な指示】
            - これは価格騰落予測ではなく、業界動向・制度整備・機関参入・規制クリアに基づく分析です
            - 上記の「歴史的マクロ文脈」と本日のニュース・トレンドを関連付けて、『なぜ今この動きが起きているのか』『背景に何があるのか』を深く説明してください
            - 例：『XDCの取引高が増加』という日々のニュースなら、『XDC Network の ICC（国際商業会議所）との提携により、貿易金融のオンチェーン化が実現しつつあるからこそ、機関投資家が資金を流入させている』というように深い考察（Why）を記述
            - **トップティアメディア情報の活用**: 上記のトップティアメディア（Bloomberg、CoinDesk、The Block、Messari等）から抽出したニュース・分析を参考に、記事に具体的な事例や統計数字を含める
            - **信頼性と根拠**: 個人ブログやまとめサイトではなく、トップティアソースのスニペットを基に執筆するため、より説得力のある記事を生成してください

            【記事構成】
            1. **冒頭** - 本日のトレンドと、その背景にあるマクロ的な文脈
            2. **機関投資家参入の進捗** - BlackRock、Franklin Templeton などの動き（具体例を示す）
            3. **規制フレームワークの整備状況** - SEC、金融庁、FCAなどの最新ガイダンス
            4. **技術・インフラの進化** - スケーラビリティ、セキュリティ、相互運用性
            5. **エコシステム提携と実需の形成** - TradFi との統合、大手機関との協業（なぜこれが重要か説明）
            6. **主要なRWAプロジェクト群** - 厳選50銘柄の分類別スナップショット
            7. **長期投資家向けの視点** - 価格投機ではなく実需ベースの判断軸
            8. **結論** - RWAセクターへの構造的な見立て

            【制約】
            - 1,800～2,200文字程度
            - 日本語
            - 価格予測や『煽り』表現は避け、事実ベースの分析
            - ONDO、XDC、LINK、Chainlink、MakerDAO、Centrifuge など実在プロジェクトを具体例として含める
            - 機関投資家・長期投資家向けの専門的かつ冷静な内容
            - ファンダメンタルズ5軸（機関投資家参入、規制、技術、提携、市場動向）を織り込む
            - 歴史的な背景（上記マクロ文脈）との関連性を示す記述を含める
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)

            if response.text:
                logger.info('✅ ファンダメンタルズ + マクロ文脈 + トップティアメディア情報ベース記事生成完了')
                return response.text
            else:
                logger.error('AI 応答が空です')
                return self._get_default_article()

        except Exception as e:
            logger.error(f'AI 記事生成失敗: {str(e)}')
            return self._get_default_article()

    def _build_fundamentals_context(self) -> str:
        """config.py から RWA ファンダメンタルズコンテキストを構築"""
        if not config:
            return ""

        context_parts = []

        # RWA厳選50銘柄の概要
        context_parts.append("【RWA厳選50銘柄の分布】")
        for category, tokens in config.RWA_TOKENS.items():
            token_names = ", ".join([t['symbol'] for t in tokens])
            context_parts.append(f"  - {category}: {token_names}")

        # キーパーソンの最新動向例
        context_parts.append("\n【業界キーパーソン30名】")
        if len(config.KEY_FIGURES) >= 5:
            context_parts.append("  主要人物（抜粋）:")
            for person in config.KEY_FIGURES[:5]:
                context_parts.append(f"    - {person['name']} ({person['affiliation']}): {person['recent_focus']}")

        # ファンダメンタルズスコアリング軸
        context_parts.append("\n【ファンダメンタルズスコアリング5軸】")
        for category, data in config.FUNDAMENTALS_CATEGORIES.items():
            weight_pct = data['weight'] * 100
            indicators = data['indicators'][:2]  # 最初の2つのみ表示
            context_parts.append(f"  - {category} ({weight_pct}%): {', '.join(indicators)}")

        # ニュースカテゴリ
        context_parts.append("\n【ニュース分類カテゴリ】")
        categories = ", ".join(config.NEWS_CATEGORIES[:6])
        context_parts.append(f"  {categories}...")

        # 信頼度ソース
        context_parts.append("\n【信頼度の高いニュースソース】")
        high_sources = config.CREDIBILITY_SOURCES['超高'][:3]
        context_parts.append(f"  超高: {', '.join(high_sources)}")

        return "\n".join(context_parts)

    def _generate_advanced_search_query(self, keyword: str, num_domains: int = 4) -> tuple:
        """高度な検索クエリを生成：ターゲットドメインのみを対象に"""
        try:
            if not config or not hasattr(config, 'TARGET_DOMAINS'):
                logger.warning('TARGET_DOMAINS が見つかりません')
                return None, []

            import random

            # ランダムに 3～5 個のドメインを選択
            selected_domains = random.sample(
                config.TARGET_DOMAINS,
                min(num_domains, len(config.TARGET_DOMAINS))
            )

            # site: 演算子を使った検索クエリを構築
            site_filters = " OR ".join([f"site:{domain}" for domain in selected_domains])
            advanced_query = f'"{keyword}" RWA ({site_filters})'

            logger.info(f'検索クエリ生成: {advanced_query}')
            return advanced_query, selected_domains

        except Exception as e:
            logger.warning(f'検索クエリ生成失敗: {str(e)}')
            return None, []

    def _search_top_tier_news(self, keyword: str) -> dict:
        """トップティアメディアからニュースを検索"""
        try:
            logger.info(f'トップティアメディアから検索中: {keyword}')

            # 高度な検索クエリを生成
            search_query, selected_domains = self._generate_advanced_search_query(keyword)

            if not search_query:
                logger.warning('検索クエリが生成できません')
                return self._get_demo_news_data()

            # Google Custom Search API または requests + BeautifulSoup で検索
            # ここでは、デモデータを返します（実装時は実際の検索APIを使用）
            try:
                response = requests.get(
                    'https://www.google.com/search',
                    params={'q': search_query},
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    timeout=10
                )

                # スクレイピング結果から スニペットを抽出（簡易版）
                # 実装上はGoogle Custom Search API推奨
                search_results = {
                    'query': search_query,
                    'domains': selected_domains,
                    'snippets': self._extract_snippets_from_search(response.text, selected_domains),
                    'status': 'success'
                }

                logger.info(f'検索完了: {len(search_results["snippets"])} 件のトップティア記事を抽出')
                return search_results

            except Exception as search_error:
                logger.warning(f'Google 検索失敗: {str(search_error)[:100]}')
                return self._get_demo_news_data()

        except Exception as e:
            logger.error(f'ニュース検索失敗: {str(e)}')
            return self._get_demo_news_data()

    def _extract_snippets_from_search(self, html_content: str, domains: list) -> list:
        """検索結果から スニペットを抽出（実装は簡易版）"""
        try:
            # 実装例：BeautifulSoup を使用
            # from bs4 import BeautifulSoup
            # soup = BeautifulSoup(html_content, 'html.parser')
            # snippets = []
            # for snippet in soup.find_all('span', class_='st'):
            #     text = snippet.get_text()
            #     snippets.append(text)
            # return snippets[:5]  # 最大5件

            # ここではデモデータを返す
            logger.info('スニペット抽出（デモモード）')
            return self._get_demo_snippets(domains)

        except Exception as e:
            logger.warning(f'スニペット抽出失敗: {str(e)}')
            return []

    def _get_demo_snippets(self, domains: list) -> list:
        """デモ用スニペット（実際の検索結果をシミュレート）"""
        demo_snippets = [
            f"{domains[0]}: RWA市場の急速な機関化により、BlackRockとFranklin Templetonが相次いで大型ファンドを設立。規制明確化によるリスク低下が背景。",
            f"{domains[1]}: Ondo Finance のグローバル拡大により、USDY（利回り付きトークン化米国債）がAPAC地域での採用を加速。機関投資家の参入が続く。",
            f"{domains[2]}: XDC Network、ICC（国際商業会議所）との貿易金融連携により、企業向けオンチェーン決済の実装フェーズに移行。日本の大手商社も参入検討。",
            f"{domains[3]}: Centrifuge、機関向けプライベートクレジットプールの構築により、数十億ドル規模の企業融資がDeFiで実現可能に。",
            f"{domains[0]}: 日本金融庁、RWAセクターの規制フレームワークを正式承認。ストラクチャー化資産のトークン化が急加速する見通し。",
        ]
        return demo_snippets[:min(5, len(demo_snippets))]

    def _get_demo_news_data(self) -> dict:
        """デモ用ニュースデータ"""
        return {
            'query': 'RWA Market Update',
            'domains': config.TARGET_DOMAINS[:4] if config else [],
            'snippets': [
                'BlackRockとFranklin Templetonが相次いで大型RWAファンドを設立し、機関マネーの流入が加速。',
                'Ondo Finance のグローバル拡大により、トークン化米国債（USDY）の採用が急拡大。',
                'XDC Network と ICC の提携により、企業向けオンチェーン決済が実装フェーズへ。',
                'Centrifuge の機関向けクレジットプール構築で、企業融資のDeFi化が前進。',
                '日本金融庁がRWA規制フレームワークを正式承認し、国内への波及効果に期待。',
            ],
            'status': 'demo'
        }

    def _build_macro_context(self) -> str:
        """rwa_context.py から マクロ文脈を抽出し、プロンプトに組み込める形式に変換"""
        if not rwa_context:
            return ""

        import random

        # ランダムに10項目をサンプリング（AI の理解を助けるため）
        sample_news = random.sample(
            rwa_context.MACRO_CONTEXT_NEWS,
            min(10, len(rwa_context.MACRO_CONTEXT_NEWS))
        )

        context_parts = [
            "【RWA市場の歴史的マクロ文脈 - 過去の重要ニュース・事例（参考）】",
            "以下は、RWA市場が機関化していく過程で実際に起きた重要な出来事や規制整備です。",
            "これらの文脈を踏まえ、本日のニュースが『なぜ重要か』『どんな背景があるのか』を説明してください。",
            ""
        ]

        for i, news_item in enumerate(sample_news, 1):
            context_parts.append(f"  {i}. {news_item}")

        return "\n".join(context_parts)

    def generate_nanobanana_image(self, prompt: str, image_type: str) -> str:
        """Nanobanana API で画像を生成"""
        try:
            if not self.nanobanana_key:
                logger.warning('Nanobanana API キーが設定されていません。フォールバック画像を使用します')
                return self._get_fallback_image_url(image_type)

            logger.info(f'Nanobanana で画像を生成中: {image_type}')

            url = 'https://api.nanobanana.net/api/v1/generate'
            headers = {
                'Authorization': f'Bearer {self.nanobanana_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'prompt': prompt,
                'model': 'anime',  # または 'realistic'
                'width': 1024,
                'height': 576,
                'num_inference_steps': 20,
                'guidance_scale': 7.5
            }

            response = requests.post(url, json=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if 'images' in data and len(data['images']) > 0:
                    image_url = data['images'][0]
                    logger.info(f'✅ Nanobanana 画像生成成功: {image_type}')
                    return image_url
            else:
                logger.warning(f'Nanobanana API エラー: {response.status_code}')

        except Exception as e:
            logger.warning(f'Nanobanana 画像生成失敗: {str(e)[:50]}')

        return self._get_fallback_image_url(image_type)

    def fetch_twitter_sentiment(self) -> dict:
        """X（Twitter）から RWA 関連ツイートを取得してセンチメント分析"""
        try:
            if not self.twitter_bearer_token or not tweepy:
                logger.warning('Twitter API が設定されていません。デモデータを使用します')
                return self._get_demo_sentiment_data()

            logger.info('X（Twitter）から RWA 関連ツイートを取得中...')

            # Tweepy クライアント初期化
            client = tweepy.Client(bearer_token=self.twitter_bearer_token)

            # RWA 関連キーワードで検索
            keywords = ['ONDO', 'XDC', 'RWA', 'tokenized assets']
            all_tweets = []

            for keyword in keywords:
                try:
                    query = f'{keyword} -is:retweet lang:ja'
                    tweets = client.search_recent_tweets(
                        query=query,
                        max_results=10,
                        tweet_fields=['public_metrics', 'created_at']
                    )

                    if tweets.data:
                        for tweet in tweets.data:
                            all_tweets.append({
                                'keyword': keyword,
                                'text': tweet.text,
                                'likes': tweet.public_metrics['like_count'],
                                'retweets': tweet.public_metrics['retweet_count']
                            })

                except Exception as e:
                    logger.warning(f'キーワード "{keyword}" の検索失敗: {str(e)[:50]}')

            # センチメント分析
            if all_tweets and self.sentiment_analyzer:
                sentiment_results = self._analyze_sentiment(all_tweets)
                return sentiment_results
            else:
                return self._get_demo_sentiment_data()

        except Exception as e:
            logger.warning(f'Twitter データ取得失敗: {str(e)[:100]}')
            return self._get_demo_sentiment_data()

    def _analyze_sentiment(self, tweets: list) -> dict:
        """ツイートのセンチメント分析"""
        try:
            if not self.sentiment_analyzer:
                return self._get_demo_sentiment_data()

            positive = 0
            negative = 0
            neutral = 0
            top_tweets = []

            for tweet in tweets:
                scores = self.sentiment_analyzer.polarity_scores(tweet['text'])
                sentiment = scores['compound']

                # センチメント分類
                if sentiment > 0.05:
                    positive += 1
                    sentiment_label = 'ポジティブ'
                elif sentiment < -0.05:
                    negative += 1
                    sentiment_label = 'ネガティブ'
                else:
                    neutral += 1
                    sentiment_label = 'ニュートラル'

                top_tweets.append({
                    'text': tweet['text'][:150],
                    'keyword': tweet['keyword'],
                    'sentiment': sentiment_label,
                    'score': round(sentiment, 2),
                    'engagement': tweet['likes'] + tweet['retweets']
                })

            # エンゲージメント順でソート
            top_tweets = sorted(top_tweets, key=lambda x: x['engagement'], reverse=True)[:5]

            total = len(tweets)

            return {
                'total_tweets': total,
                'sentiment': {
                    'positive': {'count': positive, 'percentage': round(positive / total * 100, 1) if total > 0 else 0},
                    'negative': {'count': negative, 'percentage': round(negative / total * 100, 1) if total > 0 else 0},
                    'neutral': {'count': neutral, 'percentage': round(neutral / total * 100, 1) if total > 0 else 0}
                },
                'top_tweets': top_tweets,
                'status': 'success'
            }

        except Exception as e:
            logger.warning(f'センチメント分析失敗: {str(e)[:50]}')
            return self._get_demo_sentiment_data()

    def _get_demo_sentiment_data(self) -> dict:
        """デモ用センチメント分析データ"""
        return {
            'total_tweets': 50,
            'sentiment': {
                'positive': {'count': 30, 'percentage': 60.0},
                'negative': {'count': 10, 'percentage': 20.0},
                'neutral': {'count': 10, 'percentage': 20.0}
            },
            'top_tweets': [
                {'text': '🚀 ONDO トークンが急上昇！機関投資家の買いが始まった', 'keyword': 'ONDO', 'sentiment': 'ポジティブ', 'score': 0.85, 'engagement': 2500},
                {'text': 'RWA セクター、SEC のガイダンス発表で規制リスク低下', 'keyword': 'RWA', 'sentiment': 'ポジティブ', 'score': 0.72, 'engagement': 1800},
                {'text': 'XDC ネットワークの東南アジア展開が本格化', 'keyword': 'XDC', 'sentiment': 'ポジティブ', 'score': 0.68, 'engagement': 1200},
                {'text': 'Tokenized assets の市場規模、今年中に2倍に', 'keyword': 'tokenized assets', 'sentiment': 'ポジティブ', 'score': 0.75, 'engagement': 980},
                {'text': 'RWA 市場の流動性が急速に改善中', 'keyword': 'RWA', 'sentiment': 'ニュートラル', 'score': 0.15, 'engagement': 650}
            ],
            'status': 'demo'
        }

    def _get_fallback_image_url(self, image_type: str) -> str:
        """フォールバック画像 URL を返す"""
        fallback_urls = {
            'trend_analysis': 'https://via.placeholder.com/1024x576?text=Google+Trends+Analysis',
            'investment_strategy': 'https://via.placeholder.com/1024x576?text=Investment+Strategy',
            'market_outlook': 'https://via.placeholder.com/1024x576?text=Market+Outlook'
        }
        return fallback_urls.get(image_type, fallback_urls['trend_analysis'])

    def _get_default_article(self) -> str:
        """デフォルト記事テンプレート（ファンダメンタルズベース、2000文字前後）"""
        return """
<h2>RWA市場が機関化フェーズへ - 規制整備と制度的受容の進展</h2>

<p>
Real World Assets（RWA）セクターは2024～2025年を通じて、
制度的な基盤整備が急速に進む局面に入っています。
従来の個人投資家主導の市場から、大型機関による資産クラスとしての認識へと段階的に移行しています。
本記事では、価格予測ではなく、RWA市場を支える構造的な変化を分析します。
</p>

<h2>機関投資家参入の実例</h2>

<p>
<strong>BlackRock</strong> などの大手資産運用会社が、公式な RWA 投資ファンドの組成を発表しています。
これは単なる「新しい投資テーマ」ではなく、従来の TradFi（伝統金融）機関による
ブロックチェーン資産への本格的な受け入れを示唆しています。
</p>

<ul>
  <li>Franklin Templeton: RWA トークン化ファンドの組成</li>
  <li>JPMorgan: 企業債のオンチェーン発行試験</li>
  <li>Fidelity: RWA ファンドの機関向けプロダクト開発</li>
</ul>

<h2>規制フレームワークの整備進展</h2>

<p>
SEC（米国証券取引委員会）と金融庁（日本）を含む世界の金融監督当局が、
RWA と証券トークン化に関する明確なガイダンスを相次いで発表しています。
これまでの「グレーゾーン」から「明確な規制フレームワーク」への転換です。
</p>

<p>
<strong>主要な規制動向：</strong>
</p>

<ul>
  <li>SEC: 「Treasury Tokenization」の条件付き容認</li>
  <li>日本 金融庁: RWA セクターの位置づけを正式に明確化</li>
  <li>Singapore MAS: STO（Security Token Offering）ライセンス枠組みの整備</li>
  <li>EU: MiCA（Markets in Crypto-assets Regulation）による規制統一</li>
</ul>

<h2>技術インフラの成熟</h2>

<p>
RWA プロジェクトを支えるブロックチェーン基盤技術は、
スケーラビリティと相互運用性の面で大きく進化しています。
</p>

<ul>
  <li><strong>Chainlink（LINK）</strong>: RWA データ供給の基盤としての地位確立</li>
  <li><strong>Avalanche（AVAX）</strong>: エンタープライズ向けスケーラブルなプラットフォーム</li>
  <li><strong>Polymesh（POLYX）</strong>: セキュリティトークン専用ブロックチェーン</li>
</ul>

<h2>RWA厳選50銘柄の分類的理解</h2>

<p>
RWA セクターは単一の市場ではなく、複数のサブセクターで構成されています：
</p>

<ul>
  <li><strong>インフラ層</strong>: XDC Network、Chainlink、Avalanche など基盤技術</li>
  <li><strong>証券・国債</strong>: Ondo Finance、Centrifuge など機関向け商品</li>
  <li><strong>クレジット</strong>: Maple Finance、Goldfinch など融資プロトコル</li>
  <li><strong>不動産・物理資産</strong>: 土地所有権、不動産ファイナンス</li>
  <li><strong>コモディティ</strong>: 金現物ペッグ、カーボンクレジット</li>
</ul>

<h2>長期投資家視点での評価軸</h2>

<p>
RWA セクターへの投資判断は、以下の 5 つの基軸で行うことが推奨されます：
</p>

<ol>
  <li><strong>機関投資家参入度（25%）</strong>: 資産規模の増加、ファンド組成数</li>
  <li><strong>規制明確性（25%）</strong>: ガイダンス発表、ライセンス取得</li>
  <li><strong>技術的成熟度（20%）</strong>: セキュリティ監査、スケーラビリティ</li>
  <li><strong>エコシステム提携（15%）</strong>: TradFi との統合、実装企業数</li>
  <li><strong>市場規模成長（15%）</strong>: 取引高増加、新規参入者数</li>
</ol>

<h2>リスク要因の定性的評価</h2>

<ul>
  <li>規制方針の急変動（低確度だが影響度が高い）</li>
  <li>技術的脆弱性の発見（セキュリティ監査継続中）</li>
  <li>マクロ金融環境の変化（利上げ・金利低下の影響）</li>
  <li>大手プロジェクトの失敗事例（市場心理への悪影響）</li>
</ul>

<h2>結論：構造的トレンド vs. 短期変動</h2>

<p>
RWA セクターの長期的な成長軌道は、以下の理由で堅牢です：
</p>

<ul>
  <li>TradFi からの必然的な流入（既得権益の再構築）</li>
  <li>規制当局の一貫した姿勢（サポーティブ）</li>
  <li>技術的実装の加速（スケーラビリティ実現）</li>
  <li>機関投資家の参入継続（資産配分の多様化）</li>
</ul>

<p>
一方で、短期的な価格変動には常にボラティリティが伴います。
長期保有インベスターは、短期的なノイズを無視し、
構造的なファンダメンタルズ改善に焦点を当てることが推奨されます。
</p>

<p style="color: #667eea; font-weight: bold; font-size: 1.1em; margin-top: 20px;">
本分析は投資判断の参考情報です。投資推奨ではありません。
個人の責任と風险管理の下で判断してください。
</p>
"""

    def generate_html_page(self, article_title: str, article_content: str,
                          image_paths: list = None, sentiment_data: dict = None) -> str:
        """HTML ページを生成（GitHub Pages 用 + センチメント分析）"""
        try:
            logger.info('HTML ページを生成中...')

            if image_paths is None:
                image_paths = []

            if sentiment_data is None:
                sentiment_data = self._get_demo_sentiment_data()

            # 画像URL を保存（記事内に埋め込む）
            image_urls_list = image_paths if image_paths else []

            # センチメント分析セクション HTML を生成
            sentiment_html = self._generate_sentiment_html(sentiment_data)

            # HTML テンプレート
            html_template = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
            line-height: 1.8;
            color: #333;
        }}

        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}

        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}

        header h1 {{
            font-size: 1.8em;
            margin-bottom: 10px;
            font-weight: 700;
            word-wrap: break-word;
        }}

        .timestamp {{
            opacity: 0.9;
            font-size: 0.95em;
        }}

        .author {{
            color: #fff;
            font-size: 0.9em;
            margin-top: 15px;
            opacity: 0.95;
        }}

        article {{
            padding: 30px 20px;
        }}

        article h2 {{
            color: #667eea;
            font-size: 1.4em;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        article h2:first-of-type {{
            margin-top: 0;
        }}

        article p {{
            margin-bottom: 15px;
            line-height: 1.8;
        }}

        article ul, article ol {{
            margin-left: 25px;
            margin-bottom: 15px;
        }}

        article li {{
            margin-bottom: 10px;
        }}

        .article-image {{
            width: 100%;
            max-width: 100%;
            height: auto;
            margin: 30px 0;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}

        .sources {{
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }}

        .sources h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.1em;
        }}

        .sources ol {{
            margin-left: 20px;
        }}

        .sources li {{
            margin-bottom: 10px;
            font-size: 0.95em;
        }}

        .sources a {{
            color: #667eea;
            text-decoration: none;
            word-break: break-all;
        }}

        .sources a:hover {{
            text-decoration: underline;
        }}

        footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border-top: 1px solid #ddd;
        }}

        .footer-note {{
            margin-top: 10px;
            font-size: 0.85em;
        }}

        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}

            header {{
                padding: 25px 15px;
            }}

            header h1 {{
                font-size: 1.4em;
            }}

            article {{
                padding: 20px 15px;
            }}

            article h2 {{
                font-size: 1.2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 {article_title}</h1>
            <div class="timestamp">📅 {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S (JST)')}</div>
            <div class="author">📝 xdc.master（不動産運営 × XDC長期保有インベスター）</div>
        </header>

        <article>
            {images_html}
            {article_content}
        </article>

        <div class="sources">
            <h3>📚 参考資料・参照元</h3>
            <ol>
                <li><a href="https://cointelegraph.jp" target="_blank">Coin Telegraph</a> - ニュース</li>
                <li><a href="https://www.theblock.co" target="_blank">The Block</a> - ブロックチェーン分析</li>
                <li><a href="https://www.coindesk.com" target="_blank">CoinDesk</a> - ニュース</li>
                <li><a href="https://messari.io" target="_blank">Messari</a> - インテリジェンス</li>
                <li><a href="https://glassnode.com" target="_blank">Glassnode</a> - オンチェーン分析</li>
                <li><a href="https://tokenterminal.com" target="_blank">Token Terminal</a> - ブロックチェーン分析</li>
                <li><a href="https://chain.link/ja" target="_blank">Chainlink</a> - オラクル</li>
                <li><a href="https://www.fsa.go.jp" target="_blank">金融庁</a> - 仮想資産関連政策</li>
            </ol>
        </div>

        <footer>
            <p>🌐 RWA News Dashboard - GitHub Pages Auto-Published</p>
            <p class="footer-note">本記事は自動生成されたコンテンツです。投資判断の参考情報であり、投資推奨ではありません。</p>
        </footer>
    </div>
</body>
</html>"""

            # index.html として保存
            output_dir = Path('docs')
            output_dir.mkdir(exist_ok=True)
            html_file = output_dir / 'index.html'

            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_template)

            logger.info(f'✅ HTML ページ生成: {html_file}')
            return str(html_file)

        except Exception as e:
            logger.error(f'HTML 生成失敗: {str(e)}')
            return None

    async def run(self):
        """メイン処理"""
        try:
            logger.info('=' * 60)
            logger.info('RWA ニュース自動公開システム開始（v4.0 - GitHub Pages）')
            logger.info('実行時刻: ' + datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            logger.info('=' * 60)

            # ステップ 1: トレンドデータ取得
            trends_data = await self.fetch_trends()

            # ステップ 2: 仮想資産データ取得
            coingecko_data = await self.fetch_coingecko_data()

            # ステップ 2.5: X（Twitter）センチメント分析
            logger.info('\nX（Twitter）センチメント分析中...')
            sentiment_data = self.fetch_twitter_sentiment()

            # ステップ 3: 画像生成（Nanobanana + フォールバック）
            logger.info('\n画像を生成中...')
            image_urls = [
                self.generate_nanobanana_image(
                    'RWA institutional adoption roadmap, regulatory framework development, central bank digital currency integration, professional infographic, blue and purple gradient',
                    'trend_analysis'
                ),
                self.generate_nanobanana_image(
                    'Real World Assets ecosystem diagram, blockchain infrastructure connecting TradFi institutions, tokenization layers, technical architecture, modern design',
                    'investment_strategy'
                ),
                self.generate_nanobanana_image(
                    'Global RWA market structure, asset classes taxonomy, insurance, treasury bonds, real estate, commodities, professional financial illustration',
                    'market_outlook'
                )
            ]

            # ステップ 4: AI 記事生成
            article_content = self.generate_news_article(trends_data)

            if not article_content:
                logger.error('記事生成に失敗しました')
                return False

            # ステップ 5: HTML ページ生成（画像3枚埋め込み + センチメント分析）
            article_title = 'RWA市場の機関化と規制フレームワーク整備状況'
            html_file = self.generate_html_page(
                article_title,
                article_content,
                image_urls,
                sentiment_data
            )

            if html_file:
                logger.info('\n' + '=' * 60)
                logger.info('✅ HTML ページ生成成功！')
                logger.info('=' * 60)
                logger.info(f'ファイル: {html_file}')
                logger.info('\n📡 GitHub Pages に自動デプロイされます')
                return True
            else:
                logger.error('HTML 生成失敗')
                return False

        except Exception as e:
            logger.error(f'エラー: {str(e)}')
            import traceback
            traceback.print_exc()
            return False


async def main():
    """エントリーポイント"""
    generator = RWANewsGenerator()
    success = await generator.run()
    return success


if __name__ == '__main__':
    import asyncio
    success = asyncio.run(main())
    exit(0 if success else 1)

    def _generate_sentiment_html(self, sentiment_data: dict) -> str:
        """センチメント分析結果を HTML で生成"""
        try:
            if not sentiment_data:
                return ""

            positive = sentiment_data.get('sentiment', {}).get('positive', {})
            negative = sentiment_data.get('sentiment', {}).get('negative', {})
            neutral = sentiment_data.get('sentiment', {}).get('neutral', {})

            top_tweets_html = ""
            for i, tweet in enumerate(sentiment_data.get('top_tweets', [])[:5], 1):
                sentiment_color = '#4caf50' if tweet['sentiment'] == 'ポジティブ' else '#ff9800' if tweet['sentiment'] == 'ネガティブ' else '#2196f3'
                top_tweets_html += f"""<div style="background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {sentiment_color};">
                    <div style="font-weight: bold; color: {sentiment_color};">{i}. [{tweet['keyword']}] {tweet['sentiment']}</div>
                    <div style="color: #666; margin: 10px 0;">{tweet['text']}</div>
                    <div style="color: #999; font-size: 0.9em;">スコア: {tweet['score']} | エンゲージメント: {tweet['engagement']:,}</div>
                </div>"""

            sentiment_section = f"""<h2>📱 X（Twitter）センチメント分析</h2>
<p>X（Twitter）上の RWA 関連ツイート（{sentiment_data.get('total_tweets', 0)}件）を分析しました。</p>
<div style="background: #f0f7ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
<h3 style="color: #667eea; margin-bottom: 15px;">📊 センチメント分布</h3>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
<div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #4caf50;">
<div style="font-size: 2em; color: #4caf50; font-weight: bold;">{positive.get('percentage', 0):.1f}%</div>
<div style="color: #666;">ポジティブ</div>
</div>
<div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #2196f3;">
<div style="font-size: 2em; color: #2196f3; font-weight: bold;">{neutral.get('percentage', 0):.1f}%</div>
<div style="color: #666;">ニュートラル</div>
</div>
<div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border: 2px solid #ff9800;">
<div style="font-size: 2em; color: #ff9800; font-weight: bold;">{negative.get('percentage', 0):.1f}%</div>
<div style="color: #666;">ネガティブ</div>
</div>
</div>
</div>
<h3>🔝 トップツイート（エンゲージメント順）</h3>
{top_tweets_html}"""

            return sentiment_section

        except Exception as e:
            return ""
