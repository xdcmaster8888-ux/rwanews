#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA News 完全自動公開パイプライン（GitHub Pages）
記事生成 → HTML 生成 → GitHub Pages 自動公開
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_name, description):
    """スクリプトを実行"""
    logger.info(f'\n{description}')
    logger.info('=' * 60)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=False
        )

        if result.returncode == 0:
            logger.info(f'✅ {description} 完了\n')
            return True
        else:
            logger.error(f'❌ {description} 失敗 (終了コード: {result.returncode})\n')
            return False

    except Exception as e:
        logger.error(f'❌ エラー: {e}\n')
        return False

def main():
    logger.info('\n' + '=' * 70)
    logger.info('🚀 RWA News 完全自動公開パイプライン (GitHub Pages)')
    logger.info('=' * 70)

    steps = [
        ('main.py', '【ステップ 1】RWA ニュース記事生成'),
        ('github_pages_publisher.py', '【ステップ 2】GitHub Pages へ自動公開')
    ]

    success = True
    for script, description in steps:
        if not run_script(script, description):
            success = False
            break

    if success:
        logger.info('=' * 70)
        logger.info('🎉 完全自動公開が完了しました！')
        logger.info('=' * 70)
        logger.info('\n📡 サイト URL: https://[username].github.io/rwanews/')
        logger.info('⏰ GitHub Pages は数秒～数分で自動更新されます\n')
    else:
        logger.error('❌ パイプライン処理が失敗しました')

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
