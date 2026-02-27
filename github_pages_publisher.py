#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA News GitHub Pages 自動公開システム
記事自動生成 → HTML 生成 → GitHub Pages 自動プッシュ
"""

import os
import json
import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

DOCS_DIR = Path('docs')
DATA_DIR = DOCS_DIR / 'data'
ARTICLES_DIR = Path('output')

def ensure_directories():
    """必要なディレクトリを作成"""
    DOCS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    logger.info('✅ ディレクトリ確認完了')

def collect_articles():
    """記事ファイルを収集"""
    logger.info('\n【ステップ 1】記事ファイル収集')
    logger.info('=' * 60)

    articles = []
    article_files = sorted(ARTICLES_DIR.glob('rwa_news_*.txt'), reverse=True)

    for article_file in article_files[:20]:  # 最新20記事
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # メタデータ抽出
            filename = article_file.stem
            timestamp = filename.replace('rwa_news_', '')

            # 日時解析
            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                date_str = dt.strftime('%Y年%m月%d日 %H:%M')
            except:
                date_str = timestamp

            # タイトル抽出（最初の行）
            lines = content.split('\n')
            title = lines[0].replace('【タイトル】', '').strip() if lines else 'Untitled'

            articles.append({
                'id': filename,
                'title': title,
                'timestamp': timestamp,
                'date': date_str,
                'content': content[:500],  # 最初の500文字
                'url': f'article/{filename}.html'
            })

            logger.info(f'  ✅ {date_str} - {title[:50]}')

        except Exception as e:
            logger.warning(f'  ❌ {article_file.name}: {str(e)[:50]}')

    logger.info(f'\n✅ {len(articles)} 件の記事を収集\n')
    return articles

def generate_articles_json(articles):
    """articles.json を生成"""
    logger.info('【ステップ 2】JSON データ生成')
    logger.info('=' * 60)

    json_file = DATA_DIR / 'articles.json'

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'total_articles': len(articles),
            'articles': articles
        }, f, ensure_ascii=False, indent=2)

    logger.info(f'✅ JSON 生成: {json_file}')
    logger.info(f'   記事数: {len(articles)} 件\n')

def generate_article_pages(articles):
    """個別記事ページを生成"""
    logger.info('【ステップ 3】記事ページ HTML 生成')
    logger.info('=' * 60)

    articles_dir = DOCS_DIR / 'article'
    articles_dir.mkdir(exist_ok=True)

    for article in articles[:10]:  # 最新10記事のみページ化
        try:
            # 記事本文を読み込み
            article_file = ARTICLES_DIR / f'{article["id"]}.txt'
            if not article_file.exists():
                continue

            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # HTML ページ生成
            html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        article {{
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            line-height: 1.8;
        }}
        article h1 {{ color: #667eea; margin-bottom: 10px; }}
        .meta {{ color: #999; font-size: 0.9em; margin-bottom: 30px; }}
        pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        a.back {{ color: #667eea; text-decoration: none; margin-top: 30px; display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <article>
            <h1>{article['title']}</h1>
            <div class="meta">📅 {article['date']}</div>
            <pre>{content}</pre>
            <a href="../index.html" class="back">← ホームに戻る</a>
        </article>
    </div>
</body>
</html>'''

            # HTML ファイルに保存
            html_file = articles_dir / f'{article["id"]}.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f'  ✅ {article["date"]}')

        except Exception as e:
            logger.warning(f'  ❌ {article["id"]}: {str(e)[:50]}')

    logger.info(f'\n✅ 記事ページ生成完了\n')

def update_index_html(articles):
    """index.html を更新して最新記事を表示"""
    logger.info('【ステップ 4】ダッシュボード更新')
    logger.info('=' * 60)

    articles_html = '\n'.join([
        f'''        <div class="article-item">
            <h3><a href="{article['url']}">{article['title']}</a></h3>
            <time>📅 {article['date']}</time>
            <p>{article['content'][:150]}...</p>
        </div>'''
        for article in articles[:15]
    ])

    index_file = DOCS_DIR / 'index.html'

    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            html = f.read()

        # 動的セクションを更新
        import re
        html = re.sub(
            r'<!-- ARTICLES_START -->.*?<!-- ARTICLES_END -->',
            f'<!-- ARTICLES_START -->\n{articles_html}\n    <!-- ARTICLES_END -->',
            html,
            flags=re.DOTALL
        )

        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f'✅ index.html 更新')
    else:
        logger.warning(f'⚠️  index.html が見つかりません')

    logger.info(f'   最新記事: {len(articles)} 件\n')

def git_commit_and_push():
    """Git コミット＆プッシュ"""
    logger.info('【ステップ 5】GitHub へプッシュ')
    logger.info('=' * 60)

    try:
        # ステージング
        logger.info('📝 ファイルをステージング...')
        subprocess.run(['git', 'add', 'docs/', '.'], cwd=Path.cwd(), check=True, capture_output=True)

        # コミット
        commit_msg = f'🚀 RWA News Auto-Publish: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        logger.info(f'💾 コミット: {commit_msg}')
        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            cwd=Path.cwd(),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info('✅ コミット成功')
        elif 'nothing to commit' in result.stdout.lower():
            logger.info('ℹ️  変更がありません')
        else:
            logger.warning(f'⚠️  コミット警告: {result.stdout[:100]}')

        # プッシュ
        logger.info('🌐 GitHub へプッシュ...')
        result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            logger.info('✅ GitHub プッシュ成功！')
            logger.info('📱 URL: https://github.com/[username]/rwanews/tree/main/docs')
        else:
            logger.error(f'❌ プッシュ失敗: {result.stderr[:200]}')

        logger.info()

    except subprocess.TimeoutExpired:
        logger.error('❌ プッシュタイムアウト')
    except Exception as e:
        logger.error(f'❌ Git 処理エラー: {str(e)}')

def main():
    logger.info('\n' + '=' * 60)
    logger.info('🚀 RWA News GitHub Pages 自動公開')
    logger.info('=' * 60)

    # ステップ実行
    ensure_directories()
    articles = collect_articles()

    if not articles:
        logger.error('❌ 記事が見つかりません')
        return False

    generate_articles_json(articles)
    generate_article_pages(articles)
    update_index_html(articles)
    git_commit_and_push()

    logger.info('=' * 60)
    logger.info('✅ GitHub Pages 公開完了！')
    logger.info('=' * 60)
    logger.info('\n📡 サイト URL:')
    logger.info('  https://[username].github.io/rwanews/')
    logger.info('\n💡 設定方法:')
    logger.info('  1. GitHub リポジトリの Settings → Pages')
    logger.info('  2. Source: main branch /docs folder')
    logger.info('  3. 数分で自動公開されます\n')

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
