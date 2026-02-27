# 画像を埋め込む HTML 生成ロジック
def inject_images_into_article(article_content, image_urls):
    """記事に画像を適材適所に埋め込む"""
    if not image_urls or len(image_urls) < 3:
        return article_content
    
    # 画像タグ生成
    img_tags = [f'<img src="{url}" alt="RWA分析" class="article-image" style="width:100%; border-radius:10px; margin:20px 0;">' 
                for url in image_urls[:3]]
    
    # 適材適所に埋め込む
    # 画像1: 最初の h2 後
    article_content = article_content.replace('<h2>📊', img_tags[0] + '\n<h2>📊', 1)
    
    # 画像2: 投資戦略セクション後
    article_content = article_content.replace('<h2>💰', img_tags[1] + '\n<h2>💰', 1)
    
    # 画像3: 結論セクション前
    article_content = article_content.replace('<h2>🎯 結論', img_tags[2] + '\n<h2>🎯 結論', 1)
    
    return article_content
