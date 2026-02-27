#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com メニューから投稿確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def verify_via_menu():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('Note.com投稿確認（メニュー経由）')
            
            # ログイン
            logger.info('\nログイン処理...')
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
            
            # ナビゲーション確認
            logger.info('\nナビゲーション確認...')
            nav_items = await page.evaluate('''() => {
                const items = [];
                document.querySelectorAll('[role="navigation"] a, nav a, .menu a').forEach(el => {
                    const text = el.textContent.trim();
                    const href = el.href;
                    if (text && href) {
                        items.push({ text, href });
                    }
                });
                return items;
            }''')
            
            logger.info(f'\nナビゲーション項目（最初10件）:')
            for item in nav_items[:10]:
                logger.info(f'  {item["text"]}: {item["href"]}')
            
            # マイページへのリンクを探す
            logger.info('\nマイページへ移動...')
            # 右上のユーザーメニュー
            try:
                user_menu = page.locator('[role="button"]:has-text("プロフィール"), [role="button"]:has-text("投稿")')
                if await user_menu.count() > 0:
                    await user_menu.first.click()
                    logger.info('✅ ユーザーメニューをクリック')
                    await page.wait_for_timeout(2000)
            except:
                logger.info('ユーザーメニュー見つけられず')
            
            # 投稿一覧へ遷移を試みる
            logger.info('\nマイページへのURL形式を確認...')
            # https://note.com/user_id/articles
            await page.goto('https://note.com/my/articles', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            logger.info(f'現在のURL: {page.url}')
            
            # ページのスクリーンショット
            await page.screenshot(path='output/note_my_articles.png')
            logger.info('✅ スクリーンショット保存')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(verify_via_menu())
