#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログインテスト - type() メソッドとイベント トリガー
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def test_login_type():
    async with async_playwright() as p:
        try:
            logger.info('ブラウザ起動中...')
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
            page = await context.new_page()

            logger.info('ログインページへ...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            logger.info(f'✅ URL: {page.url}')

            # メールフィールドを取得
            logger.info('\n▶ メールフィールド処理')
            email_field = page.locator('#email')

            # 方法1: フィールドをクリック後、type() を使用
            await email_field.click()
            await page.wait_for_timeout(200)

            logger.info(f'  入力: {os.getenv("NOTE_EMAIL")}')
            await email_field.type(os.getenv('NOTE_EMAIL'), delay=50)

            await page.wait_for_timeout(300)

            # 入力値を確認
            email_value = await email_field.input_value()
            logger.info(f'  確認: {email_value}')

            # パスワードフィールド処理
            logger.info('\n▶ パスワードフィールド処理')
            password_field = page.locator('#password')
            await password_field.click()
            await page.wait_for_timeout(200)

            logger.info(f'  入力中...')
            await password_field.type(os.getenv('NOTE_PASSWORD'), delay=50)

            await page.wait_for_timeout(300)

            password_value = await password_field.input_value()
            logger.info(f'  確認: {len(password_value)} 文字')

            # ボタン状態確認
            logger.info('\n▶ ボタン状態確認')
            button_state = await page.evaluate('''() => {
                const btn = document.querySelector('button[data-type="primaryNext"]');
                return btn ? { disabled: btn.disabled, visible: btn.offsetParent !== null } : null;
            }''')
            logger.info(f'  状態: {button_state}')

            # ボタンクリック
            if button_state and not button_state['disabled']:
                logger.info('\n▶ ボタンクリック')
                await page.click('button[data-type="primaryNext"]')
                logger.info('  ✅ クリック完了')
            else:
                logger.info('\n▶ ボタンが disabled のため、強制的に enabled にしてクリック')
                await page.evaluate('''() => {
                    const btn = document.querySelector('button[data-type="primaryNext"]');
                    if (btn) {
                        btn.disabled = false;
                        btn.removeAttribute('disabled');
                    }
                }''')
                await page.click('button[data-type="primaryNext"]')
                logger.info('  ✅ 強制クリック完了')

            # ログイン結果待機
            logger.info('\n▶ ログイン結果待機（15秒）')
            for i in range(15):
                await page.wait_for_timeout(1000)
                current_url = page.url
                if 'login' not in current_url:
                    logger.info(f'✅ ログイン成功！ URL: {current_url}')
                    break
                else:
                    logger.info(f'  {i+1}秒: {current_url}')

            # スクリーンショット
            await page.screenshot(path='output/login_type_result.png')
            logger.info('✅ スクリーンショット保存')

            await context.close()
            await browser.close()
            logger.info('✅ 完了')

        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_login_type())
