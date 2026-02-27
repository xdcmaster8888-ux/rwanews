#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com 完全自動投稿パイプライン
セッション保存 → 記事生成 → 自動投稿（すべて自動化）
"""

import asyncio
import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import subprocess
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

SESSION_DIR = Path('output/note_sessions')
SESSION_DIR.mkdir(exist_ok=True, parents=True)
SESSION_FILE = SESSION_DIR / 'auth_context.json'

async def auto_login_and_save_session():
    """自動ログインしてセッション保存"""
    logger.info('\n【ステップ 1】セッション自動保存開始')
    logger.info('=' * 60)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
            page = await context.new_page()

            logger.info('📱 ブラウザ起動 - Note.com ログイン中...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(2000)

            # 自動入力（credentials を自動入力）
            logger.info('📝 認証情報を自動入力中...')

            # メール入力
            email_field = page.locator('#email')
            await email_field.click()
            await page.wait_for_timeout(300)
            await email_field.type(os.getenv('NOTE_EMAIL'), delay=50)
            await page.wait_for_timeout(500)
            logger.info(f'  ✅ メール入力: {os.getenv("NOTE_EMAIL")}')

            # パスワード入力
            password_field = page.locator('#password')
            await password_field.click()
            await page.wait_for_timeout(300)
            await password_field.type(os.getenv('NOTE_PASSWORD'), delay=50)
            await page.wait_for_timeout(500)
            logger.info(f'  ✅ パスワード入力: {len(os.getenv("NOTE_PASSWORD"))} 文字')

            # ボタンをクリック
            logger.info('🖱️  ログインボタンをクリック...')
            try:
                await page.click('button[data-type="primaryNext"]', timeout=5000)
            except:
                # フォールバック
                await page.click('button:has-text("ログイン")', timeout=5000)

            # ログイン完了を待機
            logger.info('⏳ ログイン完了を待機中（最大60秒）...')
            login_success = False
            for i in range(60):
                await page.wait_for_timeout(1000)
                current_url = page.url
                if 'login' not in current_url:
                    login_success = True
                    logger.info(f'✅ ログイン成功！ ({i+1}秒)')
                    break

            if not login_success:
                logger.error('❌ ログインタイムアウト')
                await context.close()
                await browser.close()
                return False

            # セッション保存
            logger.info('💾 セッション保存中...')
            await context.storage_state(path=str(SESSION_FILE))
            logger.info(f'✅ セッション保存完了: {SESSION_FILE}')

            await page.wait_for_timeout(2000)
            await context.close()
            await browser.close()

            logger.info('✅ ステップ 1 完了\n')
            return True

        except Exception as e:
            logger.error(f'❌ エラー: {e}')
            import traceback
            traceback.print_exc()
            return False

def run_main_posting():
    """記事生成・投稿を実行"""
    logger.info('\n【ステップ 2】記事生成・自動投稿開始')
    logger.info('=' * 60)

    try:
        result = subprocess.run(
            [sys.executable, 'main.py'],
            cwd=Path(__file__).parent,
            capture_output=False
        )

        if result.returncode == 0:
            logger.info('✅ ステップ 2 完了\n')
            return True
        else:
            logger.error(f'❌ main.py 実行失敗 (終了コード: {result.returncode})')
            return False

    except Exception as e:
        logger.error(f'❌ エラー: {e}')
        return False

async def main():
    logger.info('\n' + '=' * 60)
    logger.info('🚀 Note.com 完全自動投稿パイプライン開始')
    logger.info('=' * 60)

    # ステップ 1: セッション保存
    if not SESSION_FILE.exists():
        logger.info('\n⚠️  セッションファイルが見つかりません')
        logger.info('セッション自動保存を実行します...\n')

        success = await auto_login_and_save_session()
        if not success:
            logger.error('\n❌ セッション保存失敗 - 中止')
            return False
    else:
        logger.info('\n✅ セッションファイルが存在します - スキップ\n')

    # ステップ 2: 記事投稿
    success = run_main_posting()

    if success:
        logger.info('\n' + '=' * 60)
        logger.info('🎉 完全自動投稿が完了しました！')
        logger.info('=' * 60)
        return True
    else:
        logger.error('\n' + '=' * 60)
        logger.error('❌ 自動投稿が失敗しました')
        logger.error('=' * 60)
        return False

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
