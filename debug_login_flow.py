#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com ログインフロー詳細確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def debug_login_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            locale='ja-JP',
            timezone_id='Asia/Tokyo',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        try:
            logger.info('=== Note.com ログイン フロー テスト ===')
            
            # ログインページへアクセス
            logger.info('ログインページへアクセス...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            
            # メール入力
            logger.info('メール入力...')
            email_input = page.locator('#email')
            await email_input.fill(os.getenv('NOTE_EMAIL'))
            await page.wait_for_timeout(1000)
            
            # パスワード入力
            logger.info('パスワード入力...')
            password_input = page.locator('#password')
            await password_input.fill(os.getenv('NOTE_PASSWORD'))
            await page.wait_for_timeout(1000)
            
            # スクリーンショット（ログイン前）
            await page.screenshot(path='output/debug_before_login.png')
            logger.info('✅ スクリーンショット保存: before_login')
            
            # ログインボタンクリック
            logger.info('ログインボタンをクリック...')
            await page.click('button:has-text("ログイン")')
            logger.info('✅ クリック完了')
            
            # ボタンクリック後のページ変化を観察
            for i in range(10):
                await page.wait_for_timeout(3000)
                current_url = page.url
                logger.info(f'  [{i+1}秒] URL: {current_url}')
                
                # ページのスクリーンショット
                await page.screenshot(path=f'output/debug_after_login_{i+1}.png')
                
                # DOMの確認
                document_ready = await page.evaluate('() => document.readyState')
                logger.info(f'         Document Ready State: {document_ready}')
                
                # エラーメッセージの確認
                error_msg = await page.evaluate('''() => {
                    const errorEl = document.querySelector('[role="alert"]') || document.querySelector('.error');
                    return errorEl ? errorEl.textContent : null;
                }''')
                if error_msg:
                    logger.warning(f'         エラーメッセージ: {error_msg}')
                
                # URLが変わったか確認
                if '/my/' in current_url or '/notes/new' in current_url:
                    logger.info('✅ ログイン成功！')
                    break
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            await page.screenshot(path='output/debug_error.png')
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_login_flow())
