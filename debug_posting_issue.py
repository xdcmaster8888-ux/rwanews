#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投稿失敗の原因を特定するデバッグスクリプト
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def debug_posting():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # ブラウザを見える状態で起動
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('【投稿デバッグ】ブラウザで確認しながら実行開始')
            
            # ログイン
            logger.info('\n▶ ログイン...')
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
                    logger.info('✅ ログイン完了')
                    break
            
            await page.wait_for_timeout(3000)
            
            # 記事作成ページへ
            logger.info('\n▶ 記事作成ページへ...')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)
            
            # 簡単なテスト記事を作成
            logger.info('\n▶ テスト記事を作成...')
            title_input = page.locator('textarea[placeholder*="タイトル"]')
            await title_input.fill('【テスト投稿】RWA銘柄が一気加速へ')
            await page.wait_for_timeout(1000)
            
            editor = page.locator('div[contenteditable="true"]')
            await editor.click()
            await page.wait_for_timeout(500)
            await editor.type('これはテスト投稿です。\n\n記事の内容がここに入ります。', delay=1)
            await page.wait_for_timeout(2000)
            
            # スクリーンショット（投稿前）
            await page.screenshot(path='output/debug_before_post.png')
            logger.info('✅ スクリーンショット: before_post')
            
            # 保存
            logger.info('\n▶ 記事を保存...')
            await page.click('button:has-text("ほぞん"), button:has-text("保存")')
            await page.wait_for_timeout(3000)
            logger.info('✅ 保存ボタンをクリック')
            
            # 「公開に進む」
            logger.info('\n▶ 「公開に進む」をクリック...')
            await page.click('button:has-text("公開に進む")')
            await page.wait_for_timeout(3000)
            logger.info('✅ 「公開に進む」をクリック')
            logger.info(f'   現在のURL: {page.url}')
            
            # スクリーンショット（公開ページ）
            await page.screenshot(path='output/debug_publish_page.png')
            logger.info('✅ スクリーンショット: publish_page')
            
            # 公開ページで利用可能なボタンを確認
            logger.info('\n▶ 公開ページのボタンを確認...')
            buttons = await page.evaluate('''() => {
                const btns = [];
                document.querySelectorAll('button').forEach((btn, idx) => {
                    if (btn.textContent.trim()) {
                        btns.push({
                            index: idx,
                            text: btn.textContent.trim().substring(0, 30),
                            visible: btn.offsetParent !== null,
                            disabled: btn.disabled
                        });
                    }
                });
                return btns.slice(0, 15);
            }''')
            
            logger.info('   利用可能なボタン:')
            for btn in buttons:
                status = '✅' if btn['visible'] and not btn['disabled'] else '❌'
                logger.info(f'   {status} {btn["index"]}: {btn["text"]} (visible={btn["visible"]}, disabled={btn["disabled"]})')
            
            # 「投稿する」ボタンを探してクリック
            logger.info('\n▶ 「投稿する」ボタンをクリック...')
            try:
                await page.click('button:has-text("投稿する")')
                logger.info('✅ 「投稿する」ボタンをクリック')
            except Exception as e:
                logger.error(f'❌ ボタンクリック失敗: {e}')
                
                # 代替方法を試す
                logger.info('   代替方法を試しています...')
                try:
                    post_button = page.locator('button').nth(10)
                    await post_button.click()
                    logger.info('✅ 代替ボタンをクリック')
                except:
                    logger.error('❌ すべての方法が失敗しました')
            
            await page.wait_for_timeout(5000)
            logger.info(f'   現在のURL: {page.url}')
            
            # スクリーンショット（クリック後）
            await page.screenshot(path='output/debug_after_click.png')
            logger.info('✅ スクリーンショット: after_click')
            
            # ページのHTML要素を確認
            logger.info('\n▶ ページのHTML要素を確認...')
            page_content = await page.evaluate('''() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    body_text: document.body.textContent.substring(0, 200)
                };
            }''')
            
            logger.info(f'   ページタイトル: {page_content["title"]}')
            logger.info(f'   URL: {page_content["url"]}')
            
            # 数秒待機して最終的なページ遷移を確認
            logger.info('\n▶ 最終ページ遷移を待機（10秒）...')
            for i in range(10):
                await page.wait_for_timeout(1000)
                logger.info(f'   {i+1}秒: {page.url}')
                
                if '/n/' in page.url and 'editor' not in page.url:
                    logger.info('✅ 投稿完了ページへ到達！')
                    await page.screenshot(path='output/debug_success.png')
                    break
            
            logger.info('\n【デバッグ完了】')
            logger.info(f'最終URL: {page.url}')
            
            await context.close()
            
        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()
        
        finally:
            # ブラウザはユーザーが手動で閉じるまで開いたままにしておく
            logger.info('\nℹ️  ブラウザはそのまま開いています。確認後、手動で閉じてください。')
            await page.wait_for_timeout(30000)  # 30秒待機
            await browser.close()

if __name__ == '__main__':
    asyncio.run(debug_posting())
