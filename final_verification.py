#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終確認：Note.comで記事が投稿されているか
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def final_verification():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('【最終確認】Note.comで記事が投稿されているか確認')
            
            # ログイン
            logger.info('\nStep 1: ログイン処理...')
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
            
            # ホームページへ
            logger.info('\nStep 2: ホームページへ移動...')
            await page.goto('https://note.com/', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # 最新の記事を確認
            logger.info('\nStep 3: フィード確認...')
            articles = await page.evaluate('''() => {
                const items = [];
                document.querySelectorAll('[data-test-id*="note-feed"], article, .article-item').forEach((el) => {
                    const title = el.querySelector('h2, h3, [data-test-id*="title"]')?.textContent || '';
                    const desc = el.textContent.substring(0, 100);
                    if (title && title.length > 0) {
                        items.push(title.trim());
                    }
                });
                return items.slice(0, 5);
            }''')
            
            logger.info('\nフィードの最新記事（最初5件）:')
            for i, article in enumerate(articles):
                logger.info(f'  {i+1}. {article[:80]}')
            
            # RWA関連の記事を確認
            logger.info('\nStep 4: 「RWA」キーワードで検索...')
            search_box = page.locator('input[placeholder*="キーワード"], input[type="search"]')
            if await search_box.count() > 0:
                await search_box.first.fill('RWA')
                await page.wait_for_timeout(2000)
            
            # スクリーンショット
            await page.screenshot(path='output/final_verification_home.png')
            logger.info('\n✅ スクリーンショット保存: final_verification_home.png')
            
            logger.info('\n【確認完了】')
            logger.info('記事が正常に投稿されているか、ブラウザ画面で目視確認してください。')
            logger.info(f'現在のURL: {page.url}')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(final_verification())
