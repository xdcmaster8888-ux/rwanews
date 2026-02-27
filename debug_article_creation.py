#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com 記事作成ページのセレクター確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def check_article_creation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('ログイン処理を実行...')
            # ログインページへ
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # メール入力
            email_input = page.locator('#email')
            await email_input.fill(os.getenv('NOTE_EMAIL'))
            await page.wait_for_timeout(1000)
            
            # パスワード入力
            password_input = page.locator('#password')
            await password_input.fill(os.getenv('NOTE_PASSWORD'))
            await page.wait_for_timeout(1000)
            
            # ログインボタンクリック
            await page.click('button:has-text("ログイン")')
            logger.info('ログインボタンをクリック')
            
            # ホームページまで待機（最大30秒）
            for i in range(10):
                await page.wait_for_timeout(3000)
                current_url = page.url
                logger.info(f'URL: {current_url}')
                
                if 'note.com' in current_url and 'login' not in current_url:
                    logger.info('✅ ホームページに到達')
                    break
            
            await page.wait_for_timeout(2000)
            
            # 記事作成ページへ移動
            logger.info('\n記事作成ページへ移動...')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(5000)
            
            # ページのスクリーンショット
            await page.screenshot(path='output/note_article_creation_page.png')
            logger.info('✅ スクリーンショット保存: note_article_creation_page.png')
            
            # セレクター確認
            logger.info('\n=== セレクター確認 ===')
            test_selectors = {
                'title': [
                    'input[placeholder*="タイトル"]',
                    'input[type="text"]',
                    'input[value*=""]',
                    'textarea[placeholder*="タイトル"]',
                    '[contenteditable="true"]',
                ],
                'body': [
                    'div[contenteditable="true"]',
                    'textarea',
                    'div.editor',
                    '[role="textbox"]',
                ],
            }
            
            for field_type, selectors in test_selectors.items():
                logger.info(f'\n{field_type}:')
                for selector in selectors:
                    try:
                        element = page.locator(selector)
                        count = await element.count()
                        if count > 0:
                            visible = await element.first.is_visible() if count > 0 else False
                            logger.info(f'  ✅ {selector}: count={count}, visible={visible}')
                        else:
                            logger.info(f'  ❌ {selector}: not found')
                    except Exception as e:
                        logger.info(f'  ❌ {selector}: error')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            await page.screenshot(path='output/debug_article_error.png')
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(check_article_creation())
