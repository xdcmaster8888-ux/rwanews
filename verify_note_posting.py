#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com ダッシュボードで投稿確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def verify_posting():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('Note.comダッシュボード確認を開始...')
            
            # ログイン処理
            logger.info('ログイン...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            await page.wait_for_timeout(2000)
            
            email_input = page.locator('#email')
            await email_input.fill(os.getenv('NOTE_EMAIL'))
            await page.wait_for_timeout(500)
            
            password_input = page.locator('#password')
            await password_input.fill(os.getenv('NOTE_PASSWORD'))
            await page.wait_for_timeout(500)
            
            await page.click('button:has-text("ログイン")')
            
            # ホームページまで待機
            for i in range(10):
                await page.wait_for_timeout(2000)
                if 'login' not in page.url:
                    break
            
            logger.info('✅ ログイン完了')
            await page.wait_for_timeout(2000)
            
            # 投稿済み記事一覧へ移動
            logger.info('投稿済み記事一覧へ移動...')
            # ユーザーのプロフィールページ or 投稿一覧
            await page.goto(f'https://note.com/{os.getenv("NOTE_EMAIL").split("@")[0]}/articles', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # 最新の記事を確認
            articles_info = await page.evaluate('''() => {
                const articles = document.querySelectorAll('[data-test-id*="article"], article, .note-item');
                const result = [];
                articles.forEach((el, idx) => {
                    if (idx < 5) {  // 最新5件
                        result.push({
                            index: idx,
                            title: el.querySelector('[data-test-id*="title"], h2, .title')?.textContent || 'No title',
                            url: el.querySelector('a')?.href || 'No URL',
                            text: el.textContent.substring(0, 100)
                        });
                    }
                });
                return result;
            }''')
            
            logger.info('\n=== 投稿済み記事一覧 ===')
            if articles_info:
                for item in articles_info[:3]:
                    logger.info(f'記事 {item["index"]}: {item["title"]}')
                    logger.info(f'  URL: {item["url"]}')
            else:
                logger.info('記事が見つかりません。URL確認...')
                logger.info(f'現在のURL: {page.url}')
            
            # スクリーンショット保存
            await page.screenshot(path='output/note_dashboard_check.png')
            logger.info('\n✅ ダッシュボードスクリーンショット保存')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(verify_posting())
