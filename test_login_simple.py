#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなログインテスト
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def test_login():
    async with async_playwright() as p:
        try:
            logger.info('ブラウザ起動中...')
            browser = await p.chromium.launch(headless=True)  # headless mode で開始
            context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
            page = await context.new_page()

            logger.info('ログインページへ...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded', timeout=30000)
            logger.info(f'✅ ログインページ読み込み完了')
            logger.info(f'   URL: {page.url}')

            # 入力フィールドの存在確認
            email_exists = await page.locator('#email').is_visible(timeout=5000)
            password_exists = await page.locator('#password').is_visible(timeout=5000)

            logger.info(f'✅ Email フィールド存在: {email_exists}')
            logger.info(f'✅ Password フィールド存在: {password_exists}')

            if email_exists and password_exists:
                logger.info('ログイン認証を試みます...')
                await page.locator('#email').fill(os.getenv('NOTE_EMAIL'))
                await page.locator('#password').fill(os.getenv('NOTE_PASSWORD'))

                logger.info('ログインボタンをクリック...')
                await page.click('button:has-text("ログイン")')

                # ログイン完了を待つ
                try:
                    await page.wait_for_url('**/dashboard/**', timeout=10000)
                    logger.info('✅ ログイン成功！')
                    logger.info(f'   URL: {page.url}')
                except:
                    logger.warning('Dashboard への遷移がタイムアウト...')
                    logger.info(f'   現在のURL: {page.url}')

            await page.screenshot(path='output/test_login_result.png')
            logger.info('✅ スクリーンショット保存')

            await context.close()
            await browser.close()
            logger.info('✅ ブラウザクローズ')

        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_login())
