#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
現在の Note.com セレクター調査
"""

import asyncio
from playwright.async_api import async_playwright
import logging
import os
from dotenv import load_dotenv
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def inspect_selectors():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(locale='ja-JP', timezone_id='Asia/Tokyo')
        page = await context.new_page()

        try:
            logger.info('【セレクター調査】Note.com インターフェース検査開始')

            # ログイン
            logger.info('\n▶ ステップ1: ログイン処理')
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

            # 記事作成ページへ
            logger.info('\n▶ ステップ2: 記事作成ページへ移動')
            await page.goto('https://note.com/notes/new', wait_until='domcontentloaded')
            await page.wait_for_timeout(3000)

            # DOM の全体構造を検査
            logger.info('\n▶ ステップ3: DOM 構造を検査')
            dom_structure = await page.evaluate('''() => {
                return {
                    title: document.title,
                    url: window.location.href,
                    textareas: Array.from(document.querySelectorAll('textarea')).map((el, idx) => ({
                        idx: idx,
                        id: el.id,
                        class: el.className,
                        placeholder: el.placeholder,
                        value: el.value.substring(0, 50)
                    })),
                    inputs: Array.from(document.querySelectorAll('input[type="text"]')).map((el, idx) => ({
                        idx: idx,
                        id: el.id,
                        class: el.className,
                        placeholder: el.placeholder
                    })),
                    contenteditable: Array.from(document.querySelectorAll('[contenteditable="true"]')).map((el, idx) => ({
                        idx: idx,
                        id: el.id,
                        class: el.className,
                        innerHTML_preview: el.innerHTML.substring(0, 100)
                    })),
                    buttons: Array.from(document.querySelectorAll('button')).map((el, idx) => ({
                        idx: idx,
                        text: el.textContent.trim().substring(0, 50),
                        class: el.className,
                        disabled: el.disabled
                    }))
                };
            }''')

            logger.info('\n📋 ページ情報:')
            logger.info(f'  URL: {dom_structure["url"]}')
            logger.info(f'  Title: {dom_structure["title"]}')

            logger.info('\n📌 Textareas (合計: ' + str(len(dom_structure['textareas'])) + '):')
            for ta in dom_structure['textareas']:
                logger.info(f'  [{ta["idx"]}] id="{ta["id"]}" placeholder="{ta["placeholder"]}"')

            logger.info('\n📌 Input[type=text] (合計: ' + str(len(dom_structure['inputs'])) + '):')
            for inp in dom_structure['inputs']:
                logger.info(f'  [{inp["idx"]}] id="{inp["id"]}" placeholder="{inp["placeholder"]}"')

            logger.info('\n📌 Contenteditable (合計: ' + str(len(dom_structure['contenteditable'])) + '):')
            for ed in dom_structure['contenteditable']:
                logger.info(f'  [{ed["idx"]}] id="{ed["id"]}" class="{ed["class"]}"')

            logger.info('\n📌 ボタン (合計: ' + str(len(dom_structure['buttons'])) + '):')
            for btn in dom_structure['buttons'][:20]:
                status = '✅' if not btn['disabled'] else '❌'
                logger.info(f'  {status} [{btn["idx"]}] {btn["text"]}')

            # スクリーンショット
            logger.info('\n▶ ステップ4: スクリーンショット保存')
            await page.screenshot(path='output/current_article_page.png')
            logger.info('✅ スクリーンショット保存完了')

            # JSON で詳細を保存
            with open('output/dom_structure.json', 'w', encoding='utf-8') as f:
                json.dump(dom_structure, f, ensure_ascii=False, indent=2)
            logger.info('✅ DOM 構造を JSON で保存')

            await context.close()

        except Exception as e:
            logger.error(f'エラー: {e}')
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect_selectors())
