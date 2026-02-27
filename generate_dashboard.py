#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA News ダッシュボード自動生成スクリプト
HTML ダッシュボードを GitHub Pages 用に生成
"""

import os
import json
from datetime import datetime
from pathlib import Path

def load_articles():
    """output フォルダから記事ファイルを読み込む"""
    articles = []
    output_dir = Path('output')

    if not output_dir.exists():
        return articles

    # ファイルを日付順でソート（最新順）
    files = sorted(output_dir.glob('rwa_news_*.txt'), reverse=True)

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # ファイル名から日付を抽出
            filename = file_path.stem  # rwa_news_20260227_193218
            date_str = filename.split('_')[2:4]  # ['20260227', '193218']
            date_formatted = f"{date_str[0][:4]}/{date_str[0][4:6]}/{date_str[0][6:]}"
            time_formatted = f"{date_str[1][:2]}:{date_str[1][2:4]}"

            articles.append({
                'date': date_formatted,
                'time': time_formatted,
                'content': content,
                'filename': file_path.name
            })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    return articles

def generate_dashboard_html(articles):
    """HTML ダッシュボードを生成"""

    # 本日の記事
    today = datetime.now().strftime('%Y/%m/%d')
    today_article = None

    if articles:
        today_article = articles[0] if articles[0]['date'] == today else None

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RWA News Auto-Post Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        header h1 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}

        header p {{
            color: #666;
            font-size: 1.1em;
        }}

        .status {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .status-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}

        .status-item:last-child {{
            border-bottom: none;
        }}

        .status-label {{
            font-weight: 600;
            color: #333;
        }}

        .status-value {{
            color: #667eea;
            font-weight: bold;
            font-size: 1.1em;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }}

        .badge-success {{
            background-color: #d4edda;
            color: #155724;
        }}

        .badge-pending {{
            background-color: #fff3cd;
            color: #856404;
        }}

        .article-section {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .section-title {{
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .article-content {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            line-height: 1.8;
            margin-bottom: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 0.95em;
        }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #ddd;
        }}

        .article-date {{
            color: #666;
            font-size: 0.9em;
        }}

        .article-actions {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}

        .btn {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            text-align: center;
            text-decoration: none;
        }}

        .btn-primary {{
            background-color: #667eea;
            color: white;
        }}

        .btn-primary:hover {{
            background-color: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}

        .btn-secondary {{
            background-color: #6c757d;
            color: white;
        }}

        .btn-secondary:hover {{
            background-color: #5a6268;
        }}

        .article-list {{
            margin-top: 20px;
        }}

        .article-item {{
            background: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .article-item-date {{
            color: #667eea;
            font-weight: 600;
        }}

        .article-item-status {{
            margin-left: 10px;
        }}

        footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 0.9em;
        }}

        @media (max-width: 600px) {{
            header h1 {{
                font-size: 1.8em;
            }}

            .article-actions {{
                flex-direction: column;
            }}

            .btn {{
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📰 RWA News Dashboard</h1>
            <p>自動生成投資ニュースダッシュボード</p>
        </header>

        <div class="status">
            <div class="status-item">
                <span class="status-label">📅 今日の日付</span>
                <span class="status-value">{today}</span>
            </div>
            <div class="status-item">
                <span class="status-label">📝 本日の記事</span>
                <span class="status-value">
                    {f'<span class="badge badge-success">✅ 生成済み</span>' if today_article else '<span class="badge badge-pending">⏳ 未生成</span>'}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">📊 累計記事数</span>
                <span class="status-value">{len(articles)} 件</span>
            </div>
            <div class="status-item">
                <span class="status-label">⏰ 最終更新</span>
                <span class="status-value">{datetime.now().strftime('%Y/%m/%d %H:%M:%S')}</span>
            </div>
        </div>

        {''.join([f'''
        <div class="article-section">
            <div class="article-header">
                <span class="article-date">📅 {article['date']} {article['time']}</span>
                <span class="badge badge-success">✅ 投稿済み</span>
            </div>
            <div class="article-content">{article['content']}</div>
            <div class="article-actions">
                <button class="btn btn-primary" onclick="copyArticle('{article['filename']}')">📋 記事をコピー</button>
                <a href="https://note.com/xdcmaster8888" class="btn btn-secondary" target="_blank">📝 Note.comで投稿</a>
            </div>
        </div>
        ''' for article in articles if article])}

        <footer>
            <p>🤖 RWA News Auto-Post System v1.0</p>
            <p>毎日 08:00 / 18:00 に自動実行</p>
        </footer>
    </div>

    <script>
        async function copyArticle(filename) {{
            // 実装例：ファイル内容をクリップボードにコピー
            alert('📋 記事の内容をコピーしました！\\nNote.comで貼り付けてください。');
            // 実際のコピー機能は、ここで fetch を使用してファイルを取得
        }}
    </script>
</body>
</html>
"""

    return html_content

def main():
    """メイン処理"""
    import sys
    import io

    # Windows の CP932 エンコーディング問題を回避
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 50)
    print("RWA News Dashboard generating...")
    print("=" * 50)

    # 記事を読み込む
    articles = load_articles()
    print(f"[OK] Loaded {len(articles)} articles")

    # HTML ダッシュボードを生成
    html = generate_dashboard_html(articles)

    # docs フォルダを作成
    docs_dir = Path('docs')
    docs_dir.mkdir(exist_ok=True)

    # index.html を保存
    index_path = docs_dir / 'index.html'
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[OK] Dashboard generated: {index_path}")
    print("=" * 50)

if __name__ == '__main__':
    main()
