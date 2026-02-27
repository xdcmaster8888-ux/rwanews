#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公開ボタン詳細デバッグ
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def debug_publish():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            # 最小限の処理：ログインと記事作成まで
            logger.info('ログイン処理...')
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
            
            # 記事作成ページへ
            logger.info('\n記事作成ページへ...')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # タイトル入力
            title_input = page.locator('textarea[placeholder*="タイトル"]')
            await title_input.fill('テスト記事')
            await page.wait_for_timeout(1000)
            
            # 本文入力
            editor = page.locator('div[contenteditable="true"]')
            await editor.click()
            await page.wait_for_timeout(1000)
            await editor.type('これはテスト記事です。')
            await page.wait_for_timeout(2000)
            
            # スクリーンショット（投稿前）
            await page.screenshot(path='output/debug_before_submit.png')
            logger.info('✅ スクリーンショット: before_submit')
            
            # 投稿ボタンを探して確認
            logger.info('\n投稿ボタン確認...')
            all_buttons = await page.evaluate('''() => {
                const buttons = [];
                document.querySelectorAll('button').forEach((btn, idx) => {
                    buttons.push({
                        index: idx,
                        text: btn.textContent.trim().substring(0, 50),
                        class: btn.className
                    });
                });
                return buttons;
            }''')
            
            logger.info('\nすべてのボタン:')
            for btn in all_buttons:
                if btn['text']:
                    logger.info(f'  {btn["text"]}')
            
            # 投稿ボタンをクリック
            logger.info('\n投稿ボタンをクリック...')
            try:
                await page.click('button:has-text("投稿する")')
                logger.info('✅ 投稿ボタンをクリック')
            except:
                logger.info('❌ 「投稿する」ボタンが見つかりません')
                # 他のボタンを試す
                await page.click('button:has-text("保存")')
                logger.info('  「保存」ボタンをクリック')
            
            await page.wait_for_timeout(3000)
            
            # スクリーンショット（投稿後）
            await page.screenshot(path='output/debug_after_submit.png')
            logger.info('✅ スクリーンショット: after_submit')
            
            logger.info(f'\n現在のURL: {page.url}')
            
            # ボタン確認
            logger.info('\n現在のボタン:')
            all_buttons_after = await page.evaluate('''() => {
                const buttons = [];
                document.querySelectorAll('button').forEach((btn) => {
                    if (btn.textContent.trim()) {
                        buttons.push(btn.textContent.trim().substring(0, 50));
                    }
                });
                return buttons;
            }''')
            
            for btn_text in all_buttons_after[:10]:
                logger.info(f'  {btn_text}')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_publish())
