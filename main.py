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

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数読み込み
load_dotenv()

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

        if not self.api_key:
            raise ValueError('GOOGLE_API_KEY が設定されていません')

        genai.configure(api_key=self.api_key)
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
        """AI を使用して RWA 投資ニュース記事を生成"""
        try:
            logger.info('AI ニュース記事を生成中...')

            prompt = f"""
            【RWA（Real World Assets）投資ニュース記事の生成】

            現在の Google Trends データ: {json.dumps(trends_data, ensure_ascii=False, indent=2)}
            執筆者: xdc.master

            以下の形式で、RWA市場に関する投資情報記事を生成してください：

            1. 冒頭 - 今日のRWA市場の重要ポイント（箇条書き）
            2. 主要分析 - Google Trendsデータとオンチェーン分析の関連性
            3. 投資戦略 - 1,000円の具体的な配分案
            4. リスク・機会 - 24時間～1週間の見通し
            5. 結論 - 次のアクション

            【制約】
            - 1,200～1,500文字程度
            - 日本語
            - 実在のプロジェクト（ONDO、XDC）を含める
            - 投資家向けの専門的な内容
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)

            if response.text:
                logger.info('✅ AI 記事生成完了')
                return response.text
            else:
                logger.error('AI 応答が空です')
                return self._get_default_article()

        except Exception as e:
            logger.error(f'AI 記事生成失敗: {str(e)}')
            return self._get_default_article()

    def _get_default_article(self) -> str:
        """デフォルト記事テンプレート"""
        return """
<h2>RWA市場の最新分析</h2>

<p>
本日のRWA（Real World Assets）市場では、機関投資家の参入が加速しています。
Google Trends データとオンチェーン指標が同期し、市場の成熟化が進行中です。
</p>

<h2>投資戦略：1,000円の配分案</h2>

<p>
現在の市場環境に基づいた推奨配分：
</p>

<ul>
  <li><strong>ONDO（ディフェンス：60%）</strong> - 600円：安定した成長を見込む</li>
  <li><strong>XDC（グロース：40%）</strong> - 400円：上昇ポテンシャルに賭ける</li>
</ul>

<h2>リスク＆機会（24時間～1週間）</h2>

<p>
<strong>潜在的なリスク：</strong>
</p>

<ul>
  <li>FOMC 議事録の発表による市場変動</li>
  <li>SEC による規制強化の可能性</li>
  <li>流動性の急速な変化</li>
</ul>

<p>
<strong>期待できる機会：</strong>
</p>

<ul>
  <li>BlackRock による RWA ファンド発表</li>
  <li>日本の金融庁による RWA 規制フレームワーク承認</li>
  <li>新興 RWA プロジェクトの IDO 発表</li>
</ul>

<h2>結論</h2>

<p>
RWA セクターは制度化フェーズに突入しており、個人投資家にとって
買い場が形成されています。リスク管理を徹底しながら、この機会を
活用することをお勧めします。
</p>
"""

    def generate_html_page(self, article_title: str, article_content: str,
                          image_paths: list = None) -> str:
        """HTML ページを生成（GitHub Pages 用）"""
        try:
            logger.info('HTML ページを生成中...')

            if image_paths is None:
                image_paths = []

            # 画像タグの生成
            images_html = ''
            for img_path in image_paths[:3]:
                if img_path:
                    # 相対パスに変換
                    img_relative = img_path.replace('\\', '/')
                    images_html += f'<img src="../{img_relative}" alt="RWA分析" class="article-image">\n'

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

            # ステップ 3: 画像生成
            logger.info('\n画像を生成中...')
            image_paths = [
                self.generate_gradient_image(title='RWA Trend Analysis'),
                self.generate_gradient_image(title='Investment Strategy'),
                self.generate_gradient_image(title='Market Outlook')
            ]
            image_paths = [p for p in image_paths if p]

            # ステップ 4: AI 記事生成
            article_content = self.generate_news_article(trends_data)

            if not article_content:
                logger.error('記事生成に失敗しました')
                return False

            # ステップ 5: HTML ページ生成
            article_title = '🔥 RWA 市場の最新動向と投資戦略'
            html_file = self.generate_html_page(article_title, article_content, image_paths)

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
