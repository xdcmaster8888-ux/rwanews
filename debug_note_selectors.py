#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com ログインページのセレクター確認スクリプト
"""

import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_note_selectors():
    """Note.comのログインページを確認"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('Note.comログインページへアクセス...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(5000)
            
            # ページのHTMLを取得
            html = await page.content()
            
            # 重要なセレクターをチェック
            logger.info('=== セレクター確認開始 ===')
            
            # メールフィールド関連
            try:
                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[placeholder*="メール"]',
                    'input[placeholder*="Email"]',
                    '#email',
                    '[data-test*="email"]',
                ]
                
                for selector in email_selectors:
                    try:
                        element = page.locator(selector)
                        if await element.is_visible():
                            logger.info(f'✅ FOUND: {selector}')
                        else:
                            logger.info(f'❌ Hidden: {selector}')
                    except:
                        logger.info(f'❌ NOT FOUND: {selector}')
                
                # ボタン関連
                logger.info('\n=== ボタン確認 ===')
                buttons = page.locator('button')
                for i in range(await buttons.count()):
                    button = buttons.nth(i)
                    text = await button.text_content()
                    logger.info(f'Button {i}: "{text}"')
                
            except Exception as e:
                logger.error(f'エラー: {e}')
            
            # スクリーンショット保存
            await page.screenshot(path='output/note_login_page.png')
            logger.info('✅ スクリーンショット保存: output/note_login_page.png')
            
            await context.close()
            
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(check_note_selectors())
