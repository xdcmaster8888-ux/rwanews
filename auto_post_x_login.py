#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Note.com 自動投稿パイプライン（X/Twitter ログイン対応）
セッション保存 → 記事生成 → 自動投稿
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

async def login_with_x():
    """X（Twitter）アカウントでログインしてセッション保存"""
    logger.info('\n【ステップ 1】X アカウント経由でセッション保存開始')
    logger.info('=' * 60)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
            page = await context.new_page()

            logger.info('📱 ブラウザ起動 - Note.com にアクセス...')
            await page.goto('https://note.com/login', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)

            # X ログインボタンを探す
            logger.info('🔍 X ログインボタンを探索中...')
            x_buttons = await page.evaluate('''() => {
                const buttons = [];
                document.querySelectorAll('button, a').forEach((el) => {
                    const text = el.textContent.toLowerCase();
                    if (text.includes('twitter') || text.includes('x') || text.includes('続行')) {
                        buttons.push({
                            text: el.textContent.trim().substring(0, 50),
                            tag: el.tagName,
                            class: el.className
                        });
                    }
                });
                return buttons;
            }''')

            logger.info(f'🔎 見つかったボタン: {len(x_buttons)} 個')
            for btn in x_buttons:
                logger.info(f'  - {btn["text"]}')

            # X ログインボタンをクリック
            logger.info('\n🖱️  X ログインボタンをクリック...')
            x_login_clicked = False

            # 複数のセレクター試行
            selectors = [
                'button:has-text("X")',
                'button:has-text("twitter")',
                'button:has-text("続行")',
                'a:has-text("X")',
                'a:has-text("twitter")',
                '[data-testid*="twitter"]',
                '[data-testid*="x-login"]'
            ]

            for selector in selectors:
                try:
                    await page.click(selector, timeout=2000)
                    logger.info(f'✅ クリック成功: {selector}')
                    x_login_clicked = True
                    break
                except:
                    continue

            if not x_login_clicked:
                logger.warning('⚠️  特定のセレクターが見つかりません')
                logger.info('ページ内のすべてのボタンを表示:')
                all_buttons = await page.evaluate('''() => {
                    const btns = [];
                    document.querySelectorAll('button, a').forEach((el) => {
                        if (el.textContent.trim()) {
                            btns.push(el.textContent.trim().substring(0, 60));
                        }
                    });
                    return btns;
                }''')
                for btn_text in all_buttons[:15]:
                    logger.info(f'  - {btn_text}')

                logger.info('\n💡 手動でクリックしてください（ブラウザをご確認）')
                await page.screenshot(path='output/note_x_login_page.png')

            # リダイレクト待機
            logger.info('\n⏳ X の認証フロー待機中（最大60秒）...')
            initial_url = page.url

            for i in range(60):
                await page.wait_for_timeout(1000)
                current_url = page.url

                # X 認証ページへのリダイレクト確認
                if 'twitter.com' in current_url or 'x.com' in current_url:
                    logger.info(f'✅ X 認証ページへリダイレクト')
                    logger.info(f'   URL: {current_url}')
                    await page.screenshot(path='output/x_auth_page.png')
                    break

                # Note.com へ戻ったか確認
                if 'login' not in current_url and 'note.com' in current_url:
                    logger.info(f'✅ Note.com へ戻ってきました！({i+1}秒)')
                    logger.info(f'   URL: {current_url}')
                    break

            # X ログイン完了確認
            logger.info('\n⏳ 最終確認待機（最大30秒）...')
            login_success = False

            for i in range(30):
                await page.wait_for_timeout(1000)
                current_url = page.url

                if 'login' not in current_url and 'note.com' in current_url:
                    login_success = True
                    logger.info(f'✅ X ログイン成功！({i+1}秒)')
                    logger.info(f'   URL: {current_url}')
                    break

            if login_success:
                # セッション保存
                logger.info('\n💾 セッション保存中...')
                await context.storage_state(path=str(SESSION_FILE))
                logger.info(f'✅ セッション保存完了: {SESSION_FILE}')
            else:
                logger.warning('⚠️  ログイン完了確認タイムアウト')
                logger.info('ブラウザを確認して、手動でログインしてください')
                logger.info('Enterキーを押して続行...')
                input()

                # 再度セッション保存を試みる
                try:
                    await context.storage_state(path=str(SESSION_FILE))
                    logger.info('✅ セッション保存完了')
                except Exception as e:
                    logger.error(f'セッション保存失敗: {e}')

            await page.wait_for_timeout(3000)
            await page.screenshot(path='output/note_after_x_login.png')

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
    logger.info('🚀 Note.com 自動投稿パイプライン (X ログイン)')
    logger.info('=' * 60)

    # ステップ 1: セッション保存
    if not SESSION_FILE.exists():
        logger.info('\n⚠️  セッションファイルが見つかりません')
        logger.info('X アカウントでログインしてセッションを保存します...\n')

        success = await login_with_x()
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
