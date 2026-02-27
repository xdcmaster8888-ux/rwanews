#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com 自動ログインシステム
セッション保存・復元機能付き
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
import json
from pathlib import Path
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# セッション保存ディレクトリ
SESSION_DIR = Path('output/note_sessions')
SESSION_DIR.mkdir(exist_ok=True)
SESSION_FILE = SESSION_DIR / 'auth_context.json'

async def save_session(context):
    """ブラウザのセッション情報を保存"""
    try:
        # context の状態を保存
        state = await context.storage_state(path=str(SESSION_FILE))
        logger.info(f'✅ セッション保存完了: {SESSION_FILE}')
        return True
    except Exception as e:
        logger.error(f'❌ セッション保存失敗: {e}')
        return False

async def load_session(browser):
    """保存されたセッション情報を復元したコンテキストを作成"""
    if SESSION_FILE.exists():
        try:
            # 保存されたストレージ状態を読み込んでコンテキストを作成
            context = await browser.new_context(
                locale='ja-JP',
                timezone_id='Asia/Tokyo',
                storage_state=str(SESSION_FILE)
            )
            logger.info('✅ セッション復元完了')
            return context
        except Exception as e:
            logger.error(f'⚠️  セッション復元失敗: {e}')
            return None
    else:
        logger.info('⚠️  保存されたセッションが見つかりません')
        return None

async def login_manual(page):
    """手動ログイン（初回のみ）"""
    logger.info('\n▶ 手動ログインモード（ブラウザを見てください）')
    logger.info('  Note.com ログインページが開きます')
    logger.info('  メールアドレスとパスワードを入力してログインしてください')
    logger.info('  （ログイン完了まで、ブラウザは自動的に待機します）')

    await page.goto('https://note.com/login', wait_until='domcontentloaded')

    # ログイン完了を待つ（URL が変わるまで待機）
    for i in range(60):  # 最大60秒待機
        await page.wait_for_timeout(1000)
        if 'login' not in page.url:
            logger.info(f'✅ ログイン成功！ ({i+1}秒)')
            logger.info(f'   現在のURL: {page.url}')
            return True

    logger.error('❌ タイムアウト: ログインが完了しませんでした')
    return False

async def test_session(page):
    """セッションが機能しているか確認"""
    await page.goto('https://note.com/', wait_until='domcontentloaded')
    await page.wait_for_timeout(2000)

    # ホームページが読み込まれたか確認
    page_content = await page.evaluate('() => ({ url: window.location.href, title: document.title })')

    if 'login' not in page_content['url']:
        logger.info('✅ セッション有効 - ログイン状態で Note.com に アクセス可能')
        return True
    else:
        logger.warning('❌ セッション無効 - ログインが必要です')
        return False

async def main():
    async with async_playwright() as p:
        context = None
        try:
            # ブラウザ起動
            logger.info('【Note.com 自動ログインシステム】')
            logger.info('ブラウザ起動中...')
            browser = await p.chromium.launch(headless=False)

            # セッションファイルの有無を確認
            session_exists = SESSION_FILE.exists()
            logger.info(f'\n保存済みセッション: {"✅ あり" if session_exists else "❌ なし"}')

            if session_exists:
                # セッション復元を試す
                logger.info('\n▶ ステップ1: 保存されたセッションを復元')
                context = await load_session(browser)

                if context:
                    page = await context.new_page()

                    logger.info('\n▶ ステップ2: セッション確認')
                    if await test_session(page):
                        logger.info('\n【結論】セッション復元成功 - 自動ログイン可能！')
                        await page.screenshot(path='output/auto_login_success.png')
                        await context.close()
                        await browser.close()
                        return True
                    else:
                        logger.info('\n▶ セッションが無効化されているため、新規ログインが必要です')
                        await context.close()
                        context = None

            # 新規ログイン
            if context is None:
                context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')

            page = await context.new_page()

            logger.info('\n▶ ステップ1: 手動ログイン')
            if await login_manual(page):
                logger.info('\n▶ ステップ2: セッション保存')
                if await save_session(context):
                    logger.info('\n✅ セッション保存完了')
                    logger.info('   次回からは自動ログインが機能します')

                    # セッション確認
                    logger.info('\n▶ ステップ3: セッション確認')
                    if await test_session(page):
                        logger.info('\n【結論】セッション保存・復元が正常に機能します！')
                    else:
                        logger.warning('\n⚠️  セッション確認に失敗しました')
            else:
                logger.error('\n❌ ログイン失敗')

            await page.screenshot(path='output/auto_login_result.png')
            await context.close()
            await browser.close()

        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
