#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com詳細セレクター確認スクリプト
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_selectors_detailed():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(locale='ja-JP', timezone_id='Asia/Tokyo')

        try:
            logger.info('Note.comログインページへアクセス...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # 詳細なセレクター情報をJSで取得
            form_info = await page.evaluate('''() => {
                const formElements = {
                    email_inputs: [],
                    password_inputs: [],
                    buttons: [],
                    form_structure: []
                };
                
                // すべての input を確認
                document.querySelectorAll('input').forEach((el, idx) => {
                    formElements.email_inputs.push({
                        index: idx,
                        type: el.type,
                        id: el.id,
                        name: el.name,
                        placeholder: el.placeholder,
                        visible: el.offsetParent !== null
                    });
                });
                
                // すべてのボタンを確認
                document.querySelectorAll('button').forEach((el, idx) => {
                    formElements.buttons.push({
                        index: idx,
                        text: el.textContent.trim().substring(0, 50),
                        type: el.type,
                        class: el.className,
                        id: el.id
                    });
                });
                
                // フォーム構造
                const form = document.querySelector('form');
                if (form) {
                    formElements.form_structure = {
                        id: form.id,
                        class: form.className,
                        children_count: form.children.length
                    };
                }
                
                return formElements;
            }''')
            
            logger.info('\n=== INPUT フィールド ===')
            for inp in form_info['email_inputs']:
                logger.info(f"  Index: {inp['index']}, Type: {inp['type']}, ID: {inp['id']}, Name: {inp['name']}, Placeholder: {inp['placeholder']}, Visible: {inp['visible']}")
            
            logger.info('\n=== ボタン ===')
            for btn in form_info['buttons']:
                logger.info(f"  Index: {btn['index']}, Text: {btn['text']}, Type: {btn['type']}, ID: {btn['id']}")
            
            logger.info('\n=== フォーム構造 ===')
            logger.info(f"  {form_info['form_structure']}")
            
            # 特定のセレクター試行
            logger.info('\n=== セレクター試行 ===')
            test_selectors = {
                'email': [
                    '#email',
                    'input#email',
                    'input[name="email"]',
                    'input[placeholder*="example"]',
                ],
                'password': [
                    'input[type="password"]',
                    '#password',
                    'input[name="password"]',
                ],
                'login_button': [
                    'button:has-text("ログイン")',
                    'button[type="submit"]',
                    'button:nth-of-type(3)',
                ]
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
                        logger.info(f'  ❌ {selector}: error - {str(e)[:50]}')
            
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(check_selectors_detailed())
