#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公開ページのボタン確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def debug_publish_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            # ログイン
            logger.info('ログイン...')
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
                    break
            
            # 記事作成
            logger.info('\n記事作成...')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            title_input = page.locator('textarea[placeholder*="タイトル"]')
            await title_input.fill('テスト記事')
            editor = page.locator('div[contenteditable="true"]')
            await editor.click()
            await editor.type('本文テスト')
            await page.wait_for_timeout(1000)
            
            # 保存
            logger.info('\n保存...')
            await page.click('button:has-text("ほぞん"), button:has-text("保存")')
            await page.wait_for_timeout(3000)
            
            # 公開に進む
            logger.info('\n「公開に進む」をクリック...')
            await page.click('button:has-text("公開に進む")')
            await page.wait_for_timeout(3000)
            
            # 公開ページでのボタン確認
            logger.info('\n公開ページのボタン確認...')
            current_url = page.url
            logger.info(f'現在のURL: {current_url}')
            
            all_buttons = await page.evaluate('''() => {
                const buttons = [];
                document.querySelectorAll('button').forEach((btn) => {
                    const text = btn.textContent.trim().substring(0, 100);
                    if (text && text.length > 0) {
                        buttons.push(text);
                    }
                });
                return buttons;
            }''')
            
            logger.info('\n公開ページのボタン一覧:')
            for btn_text in all_buttons[:15]:
                logger.info(f'  - {btn_text}')
            
            # スクリーンショット
            await page.screenshot(path='output/note_publish_page_buttons.png')
            logger.info('\n✅ スクリーンショット保存')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_publish_page())
