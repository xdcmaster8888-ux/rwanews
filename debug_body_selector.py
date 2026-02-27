#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com 本文エディタ詳細セレクター確認
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def find_body_editor():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            # ログイン処理
            logger.info('ログインを実行...')
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
            
            await page.wait_for_timeout(2000)
            
            # 記事作成ページへ
            logger.info('\n記事作成ページへ移動...')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # contenteditable 要素を詳細に確認
            logger.info('\n=== contenteditable 要素の詳細確認 ===')
            info = await page.evaluate('''() => {
                const elements = document.querySelectorAll('[contenteditable="true"]');
                const result = [];
                elements.forEach((el, idx) => {
                    result.push({
                        index: idx,
                        tagName: el.tagName,
                        id: el.id,
                        className: el.className,
                        placeholder: el.placeholder,
                        textContent: el.textContent.substring(0, 50),
                        parentTagName: el.parentElement?.tagName,
                        ariaLabel: el.getAttribute('aria-label'),
                        dataTestId: el.getAttribute('data-test-id'),
                        role: el.getAttribute('role'),
                        visible: el.offsetParent !== null
                    });
                });
                return result;
            }''')
            
            for item in info:
                logger.info(f'\nIndex: {item["index"]}')
                logger.info(f'  Tag: {item["tagName"]}')
                logger.info(f'  Class: {item["className"]}')
                logger.info(f'  Placeholder: {item["placeholder"]}')
                logger.info(f'  Parent: {item["parentTagName"]}')
                logger.info(f'  Role: {item["role"]}')
                logger.info(f'  Visible: {item["visible"]}')
            
            logger.info('\n=== セレクター試行 ===')
            
            # 2番目のcontenteditable (本文)
            if len(info) >= 2:
                selector = f'div[contenteditable="true"]'
                elements = page.locator(selector)
                count = await elements.count()
                logger.info(f'\n{selector}: {count} 個')
                
                if count >= 2:
                    # 2番目をクリック
                    second = elements.nth(1)
                    await second.click()
                    logger.info('✅ 2番目の contenteditable をクリック')
                    await page.wait_for_timeout(500)
                    
                    # 入力テスト
                    await second.type('これは本文です')
                    logger.info('✅ テキスト入力成功')
            
            await page.screenshot(path='output/debug_body_editor.png')
            logger.info('\n✅ スクリーンショット保存')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(find_body_editor())
