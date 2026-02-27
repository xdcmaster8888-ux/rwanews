#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログイン詳細デバッグ - ボタン disabled 問題調査
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def test_login_advanced():
    async with async_playwright() as p:
        try:
            logger.info('ブラウザ起動中...')
            browser = await p.chromium.launch(headless=False)  # 見える状態で確認
            context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
            page = await context.new_page()

            logger.info('ログインページへ...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded')
            logger.info(f'✅ URL: {page.url}')

            # Step 1: ページの初期状態を確認
            logger.info('\n▶ Step 1: 初期ボタン状態')
            login_button_state = await page.evaluate('''() => {
                const btn = document.querySelector('button[data-type="primaryNext"]');
                return {
                    text: btn ? btn.textContent : 'NOT FOUND',
                    disabled: btn ? btn.disabled : null,
                    class: btn ? btn.className : null
                };
            }''')
            logger.info(f'  ボタン状態: {login_button_state}')

            # Step 2: メールを入力
            logger.info('\n▶ Step 2: メールアドレス入力')
            email_field = page.locator('#email')
            await email_field.fill(os.getenv('NOTE_EMAIL'))
            logger.info(f'  入力値: {os.getenv("NOTE_EMAIL")}')

            # 入力後の状態確認
            await page.wait_for_timeout(500)
            email_value = await email_field.input_value()
            logger.info(f'  実際の値: {email_value}')

            # Step 3: パスワードを入力
            logger.info('\n▶ Step 3: パスワード入力')
            password_field = page.locator('#password')
            await password_field.fill(os.getenv('NOTE_PASSWORD'))
            logger.info(f'  パスワード入力完了')

            # 入力後の状態確認
            await page.wait_for_timeout(500)
            password_value = await password_field.input_value()
            logger.info(f'  パスワード長: {len(password_value)} 文字')

            # Step 4: ボタンの状態を確認
            logger.info('\n▶ Step 4: 入力後のボタン状態')
            await page.wait_for_timeout(1000)  # イベント処理を待つ

            button_state_after = await page.evaluate('''() => {
                const btn = document.querySelector('button[data-type="primaryNext"]');
                if (!btn) return 'NOT FOUND';
                return {
                    text: btn.textContent.trim(),
                    disabled: btn.disabled,
                    visible: btn.offsetParent !== null,
                    class: btn.className,
                    attr_disabled: btn.getAttribute('disabled')
                };
            }''')
            logger.info(f'  ボタン状態: {button_state_after}')

            # Step 5: ボタンの disabled 属性を削除して強制クリック
            logger.info('\n▶ Step 5: ボタン disabled 属性を除去してクリック')
            await page.evaluate('''() => {
                const btn = document.querySelector('button[data-type="primaryNext"]');
                if (btn) {
                    btn.disabled = false;
                    btn.removeAttribute('disabled');
                }
            }''')
            logger.info('  disabled 属性を除去')

            # ボタンをクリック
            await page.click('button[data-type="primaryNext"]')
            logger.info('  ✅ ボタンをクリック')

            # ログイン結果を待つ
            logger.info('\n▶ Step 6: ログイン結果待機')
            try:
                await page.wait_for_url('**/dashboard/**', timeout=15000)
                logger.info('✅ ダッシュボードへ遷移成功！')
            except:
                await page.wait_for_timeout(3000)
                logger.info(f'⚠️  現在のURL: {page.url}')

            # スクリーンショット
            await page.screenshot(path='output/login_result_advanced.png')
            logger.info('✅ スクリーンショット保存')

            await page.wait_for_timeout(5000)  # 確認用に5秒待機

            await context.close()
            await browser.close()

        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_login_advanced())
