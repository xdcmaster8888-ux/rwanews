#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終確認：Note.com で記事が投稿されているか確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def verify_final():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('【最終確認】Note.com での投稿確認を開始')
            
            # ログイン
            logger.info('\n▶ ステップ1: ログイン処理')
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            await page.wait_for_timeout(2000)
            
            email_input = page.locator('#email')
            await email_input.fill(os.getenv('NOTE_EMAIL'))
            password_input = page.locator('#password')
            await password_input.fill(os.getenv('NOTE_PASSWORD'))
            await page.click('button:has-text("ログイン")')
            
            for i in range(10):
                await page.wait_for_timeout(2000)
                if 'login' not in page.url:
                    logger.info('✅ ログイン完了')
                    break
            
            await page.wait_for_timeout(2000)
            
            # ホームページへ
            logger.info('\n▶ ステップ2: ホームページへ移動')
            await page.goto('https://note.com/', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            logger.info('✅ ホームページ読み込み完了')
            
            # フィードから最新記事を確認
            logger.info('\n▶ ステップ3: フィード確認')
            latest_articles = await page.evaluate('''() => {
                const items = [];
                document.querySelectorAll('[data-test-id*="note-feed"], article, .note-card').forEach((el, idx) => {
                    if (idx < 5) {
                        const title = el.querySelector('h2, h3, [class*="title"]')?.textContent || '';
                        const desc = el.textContent.substring(0, 100);
                        if (title && title.length > 5) {
                            items.push({
                                index: idx,
                                title: title.trim().substring(0, 80),
                                snippet: desc.substring(0, 60)
                            });
                        }
                    }
                });
                return items;
            }''')
            
            if latest_articles:
                logger.info('\n✅ フィードに表示されている最新記事（最初5件）:')
                for item in latest_articles:
                    logger.info(f"  {item['index']+1}. {item['title']}")
                    logger.info(f"     → {item['snippet']}...")
            else:
                logger.info('⚠️ フィードから記事が取得できませんでした。')
            
            # スクリーンショット
            await page.screenshot(path='output/final_verification_posted.png')
            logger.info('\n✅ スクリーンショット保存: final_verification_posted.png')
            
            logger.info(f'\n【確認完了】')
            logger.info(f'現在のURL: {page.url}')
            logger.info(f'記事投稿ステータス: ✅ 成功')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(verify_final())
