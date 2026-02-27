#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
過去記事インデックス生成スクリプト
output フォルダ内のすべての記事を JSON で管理
"""

import json
from pathlib import Path
from datetime import datetime

def generate_articles_index():
    """過去記事の JSON インデックスを生成"""

    output_dir = Path('output')
    articles = []

    # output フォルダ内の記事ファイルを収集
    for article_file in sorted(output_dir.glob('rwa_news_*.txt'), reverse=True):
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # ファイル名から日時を抽出
            timestamp = article_file.stem.replace('rwa_news_', '')

            try:
                dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                date_str = dt.strftime('%Y年%m月%d日 %H:%M')
                date_iso = dt.isoformat()
            except:
                date_str = timestamp
                date_iso = timestamp

            # タイトル抽出（最初の行）
            lines = content.split('\n')
            title = lines[0].replace('【タイトル】', '').strip() if lines else 'Untitled'

            # 記事プレビュー（最初の200文字）
            preview = content[:200].replace('\n', ' ').strip()

            articles.append({
                'id': timestamp,
                'title': title,
                'date': date_str,
                'date_iso': date_iso,
                'preview': preview,
                'word_count': len(content),
                'filename': article_file.name
            })

        except Exception as e:
            pass

    # JSON として保存
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    json_file = docs_dir / 'articles.json'

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(articles),
            'last_updated': datetime.now().isoformat(),
            'articles': articles
        }, f, ensure_ascii=False, indent=2)

    return articles

    return articles

if __name__ == '__main__':
    generate_articles_index()
