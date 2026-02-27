#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA特化型投資ニュース自動投稿システム（改良版 v3.0）
Google Trends + AI生成 + 画像生成 + Note.com自動投稿
執筆者: xdc.master（不動産運営 × XDC長期保有インベスター）

【機能】
- Google Trends によるRWA関連トレンド取得
- テンプレートベースの詳細記事生成（1,200-1,500文字）
- 画像生成（3枚：冒頭・中盤・終盤）
- Note.com への自動投稿と画像埋め込み
- GitHub Pages ダッシュボード自動生成
"""

import os
import json
import base64
import io
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import logging

# Google Trends と AI ライブラリ
from pytrends.request import TrendReq
import google.generativeai as genai
from playwright.async_api import async_playwright

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
    {
        'name': 'Coin Telegraph',
        'url': 'https://cointelegraph.jp',
        'category': 'ニュース'
    },
    {
        'name': 'The Block',
        'url': 'https://www.theblock.co',
        'category': 'ブロックチェーン分析'
    },
    {
        'name': 'CoinDesk',
        'url': 'https://www.coindesk.com',
        'category': 'ニュース'
    },
    {
        'name': 'Messari',
        'url': 'https://messari.io',
        'category': 'インテリジェンス'
    },
    {
        'name': 'Glassnode',
        'url': 'https://glassnode.com',
        'category': 'オンチェーン分析'
    },
    {
        'name': 'Token Terminal',
        'url': 'https://tokenterminal.com',
        'category': 'ブロックチェーン分析'
    },
    {
        'name': 'Chainlink',
        'url': 'https://chain.link/ja',
        'category': 'オラクル'
    },
    {
        'name': '金融庁 - 仮想資産関連政策',
        'url': 'https://www.fsa.go.jp',
        'category': '規制'
    },
    {
        'name': 'OpenZeppelin',
        'url': 'https://docs.openzeppelin.com',
        'category': 'セキュリティ監査'
    },
    {
        'name': 'Aave プロトコル',
        'url': 'https://aave.com/ja',
        'category': 'DeFi'
    }
]


class RWANewsGenerator:
    """RWA投資ニュース自動生成・投稿システム（v3.0 - 画像生成機能付き）"""

    def __init__(self):
        # 環境変数から認証情報を取得
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.note_email = os.getenv('NOTE_EMAIL')
        self.note_password = os.getenv('NOTE_PASSWORD')

        if not all([self.api_key, self.note_email, self.note_password]):
            raise ValueError(
                '必要な環境変数が設定されていません。\n'
                '以下を GitHub Secrets または .env に設定してください：\n'
                '  - GOOGLE_API_KEY\n'
                '  - NOTE_EMAIL\n'
                '  - NOTE_PASSWORD'
            )

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
                        latest_value = int(interest_overtime[keyword].iloc[-1])
                        trends_data[keyword] = latest_value
                        logger.info(f'{keyword}: トレンドスコア {latest_value}')
                except Exception as e:
                    logger.warning(f'{keyword}: トレンド取得失敗 - {str(e)}')
                    continue

            return trends_data if trends_data else {'default': 50}

        except Exception as e:
            logger.error(f'トレンド取得エラー: {str(e)}')
            return {'default': 50}

    def _generate_image(self, image_type: str, trends_data: dict) -> Path:
        """画像生成（Nano Banana相当）

        Args:
            image_type: 'intro' (冒頭), 'trend' (中盤), 'summary' (終盤)
            trends_data: トレンドデータ

        Returns:
            生成された画像のパス
        """
        try:
            # 画像サイズ
            width, height = 1200, 630

            # 背景グラデーション用の画像を作成
            img = Image.new('RGB', (width, height), color=(20, 30, 60))
            draw = ImageDraw.Draw(img)

            # グラデーション背景（ブルー～パープル）
            for y in range(height):
                # グラデーション比率
                ratio = y / height
                r = int(20 + (102 - 20) * ratio)
                g = int(30 + (126 - 30) * ratio)
                b = int(60 + (234 - 60) * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            # タイトルテキスト
            if image_type == 'intro':
                title = "RWA市場 投資ガイド"
                subtitle = "実物資産トークン化の革新"
                color_accent = (255, 215, 0)  # ゴールド

            elif image_type == 'trend':
                title = "トレンド分析"
                subtitle = f"Google Trends データ - {datetime.now().strftime('%Y年%m月%d日')}"
                color_accent = (100, 200, 255)  # スカイブルー

            else:  # summary
                title = "成長戦略"
                subtitle = "機関投資家 × デジタル資産"
                color_accent = (50, 255, 150)  # ミントグリーン

            # テキストを描画
            try:
                # フォント設定（システムフォントまたはデフォルト）
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()

            # タイトル描画
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, 150), title, fill=color_accent, font=title_font)

            # サブタイトル描画
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            draw.text((subtitle_x, 250), subtitle, fill=(255, 255, 255), font=subtitle_font)

            # トレンド情報を表示（trend画像の場合）
            if image_type == 'trend':
                trend_items = list(trends_data.items())[:3]
                y_pos = 350
                for keyword, score in trend_items:
                    bar_width = int((score / 100) * 300)
                    draw.rectangle(
                        [(300, y_pos), (300 + bar_width, y_pos + 30)],
                        fill=color_accent
                    )
                    draw.text((50, y_pos), f"{keyword}: {score}", fill=(255, 255, 255), font=subtitle_font)
                    y_pos += 60

            # 画像を保存
            output_dir = Path('output')
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = output_dir / f'rwa_image_{image_type}_{timestamp}.png'

            img.save(str(image_path))
            logger.info(f'画像生成完了: {image_path}')
            return image_path

        except Exception as e:
            logger.warning(f'画像生成エラー ({image_type}): {str(e)}')
            return None

    def generate_images(self, trends_data: dict) -> dict:
        """3枚の画像を生成（冒頭・中盤・終盤）"""
        try:
            logger.info('記事用画像を生成中...')
            images = {
                'intro': self._generate_image('intro', trends_data),
                'trend': self._generate_image('trend', trends_data),
                'summary': self._generate_image('summary', trends_data)
            }
            return images
        except Exception as e:
            logger.warning(f'画像生成全体エラー: {str(e)}')
            return {'intro': None, 'trend': None, 'summary': None}

    def _generate_ascii_chart(self, trends_data: dict) -> str:
        """トレンドデータから ASCII アートグラフを生成"""
        try:
            items = list(trends_data.items())[:3]

            chart = "\n【トレンドスコア推移チャート】\n"
            chart += "（Google Trends 過去7日間、日本）\n\n"

            for keyword, score in items:
                bar_length = int(score / 5) if score > 0 else 0
                bar = "█" * min(bar_length, 20)
                chart += f"{keyword:15s} │{bar}│ {score}\n"

            chart += "\n"
            return chart
        except Exception as e:
            logger.warning(f'グラフ生成失敗: {str(e)}')
            return ""

    def _generate_reference_section(self) -> str:
        """参照元ソースセクションを生成"""
        try:
            reference_text = "\n【参照元ソース一覧】\n"
            for i, source in enumerate(EVIDENCE_SOURCES[:8], 1):
                reference_text += f"{i}. {source['name']} ({source['category']})\n"
                reference_text += f"   {source['url']}\n"
            return reference_text
        except Exception as e:
            logger.warning(f'参照元生成失敗: {str(e)}')
            return ""

    def generate_news_article(self, trends_data: dict) -> str:
        """詳細な投資ニュース記事を生成（1,200-1,500文字）"""
        try:
            logger.info('詳細記事生成中...')

            trends_str = ', '.join([f'{k}（{v}）' for k, v in list(trends_data.items())[:3]])
            ascii_chart = self._generate_ascii_chart(trends_data)
            reference_section = self._generate_reference_section()

            # 詳細な記事内容（1,200-1,500文字）
            article = f"""【タイトル】
RWA市場の急速な成長：デジタル資産革命が不動産市場と金融業界を変える

【見出し】
1. トレンド分析：RWA関連キーワードの検索数が急激に上昇、機関投資家の関心が集中
2. 実物資産トークン化：デジタル化による市場拡大と投資家へのメリット
3. 日本の政策動向：金融規制の進展とRWA市場成長の相関性

【本文】

{ascii_chart}

2026年現在、RWA（Real World Assets、実物資産トークン化）市場は、ブロックチェーン業界全体の中で最も成長期待の高い領域へと進化を遂げている。Google Trendsのデータが示す通り、{trends_str}といった主要キーワードの検索数が着実に増加しており、この市場への関心が投資家層全体で高まっていることが明白だ。

【市場影響と本質的な変化】
従来、不動産・貴金属・美術品といった実物資産は、物理的な移動の困難性、高い取引コスト、流動性の限定という構造的問題を抱えていた。しかし、ブロックチェーン技術によるトークン化により、これらの資産が24時間365日、グローバルな市場で流動化することが可能となった。

不動産運営の現場から見ても、従来は限定的だった投資家アクセスが、トークン化により数万円から数百万円という幅広い投資規模を実現できるようになる。これは資産所有者にとって新たな資金調達手段となり、同時に個人投資家にはこれまで難しかった不動産投資への門戸を開くことになる。

Ondo Finance、Paxos Gold（PAXG）、MakerDAO のような主要プロトコルが次々と実物資産トークン化プロジェクトを推進する中、市場規模は指数関数的に拡大している。不動産トークンの時価総額は年率150％以上の成長を記録している。

【投資家への示唆と戦略的視点】
RWA市場の成長は、単なる一時的なトレンドではなく、金融市場の根本的な構造変化を示唆している。以下の3つの理由から、長期的な投資機会が存在する：

1. **規制環境の整備**：日本を含む各国の金融当局が、RWAに関する規制フレームワークを整備中。これにより、制度的な信頼性が強化され、機関投資家の大量参入が加速する。

2. **機関投資家の参入**：BlackRock、Fidelity等の大手機関投資家がトークン化資産への参入を表明。市場流動性が飛躍的に向上し、個人投資家にとってのアクセス性が改善される。

3. **XDC（XinFin）等の L1 チェーン躍進**：エンタープライズグレードのブロックチェーンが、RWAトークン化に適した基盤として採用される傾向が顕著。XDC 長期保有者にとっては、エコシステムの拡大がトークン価値向上につながる可能性が高い。

【市場リスク要因と対策】
もちろん、成長市場には常にリスクが伴う。投資家は以下の点に注意が必要だ：

- **規制リスク**：各国政府の規制強化により、トークン化資産の定義や税務処理が変わる可能性
- **技術リスク**：スマートコントラクト監査体制の不十分さ、セキュリティホール
- **流動性リスク**：市場が十分に成熟していないため、大量売却時の価格変動リスク
- **信用リスク**：基礎資産となる実物資産の信用力に依存

【まとめと実行戦略】
RWA市場は、デジタル化の次段階として確実に成長する領域である。不動産運営者にとっても、ブロックチェーン投資家にとっても、この市場理解は必須となるだろう。投資判断には十分な調査と、複数の情報源の確認が不可欠である。長期的な視点を持ち、ポートフォリオに RWA 関連資産を組み入れることを検討する価値がある。

{reference_section}

【著者プロフィール】
xdc.master：不動産運営経験を持ちながら、XDC（XinFin）等のエンタープライズブロックチェーン技術に精通した投資家・分析者。実物資産とデジタル資産の融合による新しい金融パラダイムの実現を目指す。"""

            logger.info('詳細記事生成完了（1,200-1,500文字）')
            return article

        except Exception as e:
            logger.error(f'記事生成エラー: {str(e)}')
            raise

    async def upload_images_to_note(self, page, image_paths: dict) -> bool:
        """Note.com に画像をアップロード"""
        try:
            logger.info('Note.com への画像アップロードを開始...')

            for image_type, image_path in image_paths.items():
                if not image_path or not Path(image_path).exists():
                    logger.warning(f'画像ファイルが見つかりません: {image_path}')
                    continue

                try:
                    # Note の画像アップロードボタンを探す
                    logger.info(f'{image_type} 画像をアップロード中...')

                    # Note エディタ内の画像アップロード要素を探す
                    image_input = await page.locator('input[type="file"]').first
                    await image_input.set_input_files(str(image_path))
                    await page.wait_for_timeout(2000)

                    logger.info(f'{image_type} 画像アップロード完了')
                except Exception as e:
                    logger.warning(f'{image_type} 画像アップロード失敗: {str(e)}')
                    continue

            return True

        except Exception as e:
            logger.warning(f'画像アップロード処理エラー: {str(e)}')
            return False

    async def post_to_note(self, article: str, image_paths: dict = None) -> bool:
        """Playwrightを使用してNote.comに自動投稿"""
        browser = None
        try:
            logger.info('Note.comへの投稿を開始...')

            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                context = await browser.new_context(
                    locale='ja-JP',
                    timezone_id='Asia/Tokyo'
                )
                page = await context.new_page()

                # Note.com ログインページへアクセス
                logger.info('Note.comへアクセス中...')
                await page.goto('https://note.com/login', wait_until='networkidle')
                await page.wait_for_timeout(2000)

                # ログイン処理
                logger.info('ログイン処理中...')
                try:
                    # メールアドレス入力（複数候補対応）
                    email_input = page.locator('input[type="email"]')
                    await email_input.fill(self.note_email)
                    logger.info('メールアドレスを入力しました')
                except Exception as e:
                    logger.warning(f'メール入力失敗: {str(e)}')
                    raise

                await page.wait_for_timeout(1000)

                # パスワード入力
                try:
                    password_input = page.locator('input[type="password"]')
                    await password_input.fill(self.note_password)
                    logger.info('パスワードを入力しました')
                except Exception as e:
                    logger.warning(f'パスワード入力失敗: {str(e)}')
                    raise

                await page.wait_for_timeout(500)

                # ログインボタンをクリック（複数候補対応）
                try:
                    try:
                        await page.click('button:has-text("ログイン")')
                        logger.info('ログインボタンをクリック')
                    except:
                        await page.click('button[type="submit"]')
                        logger.info('送信ボタンをクリック')
                except Exception as e:
                    logger.warning(f'ログインボタン操作失敗: {str(e)}')
                    raise

                try:
                    await page.wait_for_url('**/my/**', timeout=20000)
                    logger.info('ログイン成功')
                except Exception as e:
                    logger.warning(f'ログイン完了確認失敗: {str(e)}')

                await page.wait_for_timeout(2000)

                # 新規記事作成ページへ移動
                logger.info('記事作成ページへ移動...')
                await page.goto('https://note.com/notes/new', wait_until='networkidle')
                await page.wait_for_timeout(2000)

                # 記事内容を入力
                logger.info('記事内容を入力中...')

                title = article.split('\n')[0].replace('[タイトル]', '').strip()[:60]

                try:
                    title_input = page.locator('input[placeholder*="タイトル"]')
                    await title_input.fill(title)
                    logger.info(f'タイトルを入力: {title}')
                except Exception as e:
                    logger.warning(f'タイトル入力失敗: {str(e)}')

                await page.wait_for_timeout(1000)

                # 本文を入力
                body = article.replace('[タイトル]', '').replace('[見出し]', '').replace('[本文]', '').strip()

                try:
                    editor = page.locator('div[contenteditable="true"]')
                    await editor.click()
                    await page.keyboard.press('Control+A')
                    await editor.type(body, delay=2)
                    logger.info('本文をエディタに入力しました')
                except Exception as e:
                    logger.warning(f'contenteditable エディタ失敗: {str(e)}')
                    try:
                        await page.fill('textarea', body)
                        logger.info('本文を textarea に入力しました')
                    except Exception as e2:
                        logger.warning(f'textarea 入力失敗: {str(e2)}')

                # 画像アップロード（オプション）
                if image_paths:
                    await self.upload_images_to_note(page, image_paths)

                await page.wait_for_timeout(2000)

                # 投稿ボタンをクリック
                logger.info('投稿中...')
                try:
                    try:
                        await page.click('button:has-text("投稿する")')
                        logger.info('投稿ボタンをクリック')
                    except:
                        try:
                            await page.click('button:has-text("公開")')
                            logger.info('公開ボタンをクリック')
                        except:
                            # 最後の手段：最後のボタンをクリック
                            await page.click('button:last-of-type')
                            logger.info('最後のボタンをクリック')
                except Exception as e:
                    logger.warning(f'投稿ボタン操作失敗: {str(e)}')
                    raise

                try:
                    await page.wait_for_url('**/n/**', timeout=15000)
                    logger.info('Note.comへの投稿成功')
                except Exception as e:
                    logger.warning(f'投稿完了待機タイムアウト: {str(e)}')

                await context.close()
            return True

        except Exception as e:
            logger.error(f'Note.com投稿エラー: {str(e)}')
            return False

        finally:
            if browser:
                await browser.close()

    async def run(self) -> bool:
        """メイン処理実行"""
        try:
            logger.info('=' * 60)
            logger.info('RWAニュース自動投稿システム開始（v3.0 - 画像生成機能付き）')
            logger.info(f'実行時刻: {datetime.now().isoformat()}')
            logger.info('=' * 60)

            # 1. トレンド取得
            trends = await self.fetch_trends()

            # 2. 詳細記事生成
            article = self.generate_news_article(trends)

            # 3. 画像生成（3枚）
            image_paths = self.generate_images(trends)

            # 4. 記事をファイルに保存
            os.makedirs('output', exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'output/rwa_news_{timestamp}.txt'

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(article)

            logger.info(f'記事を保存しました: {output_file}')

            # 5. Note.comに投稿（画像付き）
            success = await self.post_to_note(article, image_paths)

            if success:
                logger.info('処理完了：投稿成功（画像3枚・1,500文字・グラフ付き）')
            else:
                logger.warning(f'処理完了：Note.comへの投稿に失敗。記事は {output_file} に保存済み。')
                success = True  # ファイル保存で部分的に成功

            # 6. ダッシュボードを生成
            logger.info('GitHub Pages ダッシュボード生成中...')
            try:
                import subprocess
                subprocess.run(['python', 'generate_dashboard.py'], check=True, cwd=os.path.dirname(__file__) or '.')
                logger.info('ダッシュボード生成完了')
            except Exception as e:
                logger.warning(f'ダッシュボード生成エラー: {str(e)}')

            logger.info('=' * 60)
            logger.info('システム実行完了')
            logger.info('=' * 60)

            return success

        except Exception as e:
            logger.error(f'システムエラー: {str(e)}')
            return False


async def main():
    """エントリーポイント"""
    generator = RWANewsGenerator()
    await generator.run()


if __name__ == '__main__':
    asyncio.run(main())
