#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RWA News System - Master Configuration
RWA厳選50銘柄 + キーパーソン + ファンダメンタルズマトリックス
"""

# ===== RWA 厳選 50 銘柄 =====
RWA_TOKENS = {
    # インフラストラクチャ層 (10銘柄)
    "インフラ": [
        {"symbol": "XDC", "name": "XDC Network", "focus": "企業向けブロックチェーン"},
        {"symbol": "OM", "name": "MANTRA", "focus": "RWA オラクル"},
        {"symbol": "POLYX", "name": "Polymesh", "focus": "証券トークン基盤"},
        {"symbol": "LINK", "name": "Chainlink", "focus": "オンチェーンデータ"},
        {"symbol": "QNT", "name": "Quant Network", "focus": "ブロックチェーン相互運用"},
        {"symbol": "AVAX", "name": "Avalanche", "focus": "RWA DeFi プラットフォーム"},
        {"symbol": "DUSK", "name": "Dusk Network", "focus": "プライバシー RWA"},
        {"symbol": "LTO", "name": "LTO Network", "focus": "エンタープライズブロックチェーン"},
        {"symbol": "CHR", "name": "Chromatic Protocol", "focus": "RWA デリバティブ"},
        {"symbol": "CTC", "name": "Creditcoin", "focus": "クレジット履歴ブロックチェーン"},
    ],

    # 証券・国債トークン化 (10銘柄)
    "証券・国債": [
        {"symbol": "ONDO", "name": "Ondo Finance", "focus": "機関向け国債トークン"},
        {"symbol": "CFG", "name": "Centrifuge", "focus": "企業債・リースファイナンス"},
        {"symbol": "NXRA", "name": "Nexera", "focus": "IPO トークン化"},
        {"symbol": "RIO", "name": "Rio Network", "focus": "国境を超えた証券取引"},
        {"symbol": "TOKEN", "name": "Tokenomics", "focus": "トークンセキュリティ"},
        {"symbol": "STBU", "name": "Stability AI", "focus": "ステーブルアセット"},
        {"symbol": "SMT", "name": "Summit Token", "focus": "機関向け証券"},
        {"symbol": "IXS", "name": "IX Swap", "focus": "セキュリティトークン取引"},
        {"symbol": "FACTR", "name": "Factor", "focus": "RWA ファクタリング"},
        {"symbol": "TRADE", "name": "Trade Finance", "focus": "貿易金融トークン化"},
    ],

    # プライベートクレジット (10銘柄)
    "プライベートクレジット": [
        {"symbol": "MPL", "name": "Maple Finance", "focus": "企業向けローン"},
        {"symbol": "GFI", "name": "Goldfinch Finance", "focus": "開発途上国融資"},
        {"symbol": "TRU", "name": "TrueFi", "focus": "コーポレートローン"},
        {"symbol": "CPOOL", "name": "Clearpool", "focus": "カウンターパーティ融資"},
        {"symbol": "CREDI", "name": "Credix", "focus": "新興市場融資"},
        {"symbol": "SOIL", "name": "Soil Finance", "focus": "農業融資"},
        {"symbol": "RWA", "name": "RWA Token", "focus": "RWA エコシステム"},
        {"symbol": "HIFI", "name": "hifi Finance", "focus": "短期融資"},
        {"symbol": "NAOS", "name": "Naos Finance", "focus": "P2P レンディング"},
        {"symbol": "FLX", "name": "Flux Finance", "focus": "不動産担保融資"},
    ],

    # 不動産・物理資産 (10銘柄)
    "不動産・物理資産": [
        {"symbol": "PRO", "name": "Proptech Investment", "focus": "不動産テック"},
        {"symbol": "PRCL", "name": "Parcel", "focus": "土地所有権トークン化"},
        {"symbol": "BST", "name": "Blockstate", "focus": "不動産登記ブロックチェーン"},
        {"symbol": "LAND", "name": "Land DAO", "focus": "土地資産DAO"},
        {"symbol": "UBXS", "name": "UBX", "focus": "不動産ファイナンス"},
        {"symbol": "BOSON", "name": "Boson Protocol", "focus": "デジタル商品のトークン化"},
        {"symbol": "LNDX", "name": "LandIndex", "focus": "不動産インデックス"},
        {"symbol": "ELITE", "name": "Elite Residential", "focus": "レジデンシャル RWA"},
        {"symbol": "LABS", "name": "Labs DAO", "focus": "リアルエステートDAO"},
        {"symbol": "OPUL", "name": "Opulous", "focus": "音楽・知的財産権トークン化"},
    ],

    # コモディティ・DeFi (10銘柄)
    "コモディティ・DeFi": [
        {"symbol": "MKR", "name": "MakerDAO", "focus": "DAI ステーブルコイン"},
        {"symbol": "PAXG", "name": "Paxos Gold", "focus": "金現物トークン"},
        {"symbol": "XAUT", "name": "Tether Gold", "focus": "金現物ペッグ"},
        {"symbol": "KAU", "name": "Kinesis Gold", "focus": "貴金属トークン化"},
        {"symbol": "KLIMA", "name": "Klima DAO", "focus": "カーボンクレジット"},
        {"symbol": "MCO2", "name": "Moss Carbon Credit", "focus": "カーボンオフセット"},
        {"symbol": "BCT", "name": "Base Carbon Tonne", "focus": "カーボン市場"},
        {"symbol": "PENDLE", "name": "Pendle", "focus": "利回りトークン化"},
        {"symbol": "SNX", "name": "Synthetix", "focus": "シンセティック RWA"},
        {"symbol": "DIMO", "name": "DIMO", "focus": "自動車データ・資産"},
    ]
}

# ===== RWA 業界のキーパーソン（30名） =====
KEY_FIGURES = [
    # RWA インフラ・プロトコル創業者
    {
        "name": "Atul Khekade",
        "affiliation": "Ondo Finance",
        "role": "Founder & CEO",
        "focus": "機関向け国債トークン",
        "recent_focus": "BlackRock、UBS との協業"
    },
    {
        "name": "Ritesh Kakkad",
        "affiliation": "Maple Finance",
        "role": "Founder",
        "focus": "企業向けローンプール",
        "recent_focus": "機関投資家による大型融資"
    },
    {
        "name": "Andre Casterman",
        "affiliation": "Centrifuge",
        "role": "CEO",
        "focus": "企業債・リース資産トークン化",
        "recent_focus": "TradFi との統合"
    },
    {
        "name": "Sergey Nazarov",
        "affiliation": "Chainlink",
        "role": "Co-Founder & CEO",
        "focus": "RWA オラクル基盤",
        "recent_focus": "金融機関との連携拡大"
    },
    {
        "name": "John Patrick Mullin",
        "affiliation": "Clearpool",
        "role": "Founder",
        "focus": "カウンターパーティ融資",
        "recent_focus": "機関向け融資市場"
    },
    {
        "name": "Emin Gün Sirer",
        "affiliation": "Avalanche",
        "role": "Founder & CEO",
        "focus": "RWA DeFi プラットフォーム",
        "recent_focus": "企業向けスケーラビリティ"
    },
    {
        "name": "Nathan Allman",
        "affiliation": "Polymesh",
        "role": "CEO",
        "focus": "証券トークン基盤",
        "recent_focus": "規制クリア加速"
    },
    {
        "name": "Carlos Domingo",
        "affiliation": "IX Swap",
        "role": "CEO",
        "focus": "セキュリティトークン取引",
        "recent_focus": "STO マーケット拡大"
    },
    {
        "name": "Robert Leshner",
        "affiliation": "Compound",
        "role": "Founder",
        "focus": "RWA 担保 DeFi",
        "recent_focus": "機関向け市場"
    },
    {
        "name": "Charles Cascarilla",
        "affiliation": "Paxos",
        "role": "CEO",
        "focus": "ステーブルコイン・RWA",
        "recent_focus": "金融機関との提携"
    },

    # 規制・金融大手
    {
        "name": "Larry Fink",
        "affiliation": "BlackRock",
        "role": "Founder & CEO",
        "focus": "RWA 投資ファンド",
        "recent_focus": "仮想資産戦略転換"
    },
    {
        "name": "Robert Mitchnick",
        "affiliation": "BlackRock",
        "role": "Digital Assets Senior Managing Director",
        "focus": "RWA 戦略推進",
        "recent_focus": "機関向け RWA プロダクト開発"
    },
    {
        "name": "Jeremy Allaire",
        "affiliation": "Circle & USDC",
        "role": "Co-Founder & CEO",
        "focus": "ステーブルコイン・RWA",
        "recent_focus": "USDCのRWA統合"
    },
    {
        "name": "Dante Disparte",
        "affiliation": "Circle",
        "role": "Co-Founder & Chief Strategy Officer",
        "focus": "RWA 市場戦略",
        "recent_focus": "規制クリア推進"
    },
    {
        "name": "Paolo Ardoino",
        "affiliation": "Tether",
        "role": "CEO",
        "focus": "USDT・RWA 統合",
        "recent_focus": "ステーブルコイン規制対応"
    },
    {
        "name": "Nic Carter",
        "affiliation": "Castle Island Ventures",
        "role": "Partner & Crypto Policy Expert",
        "focus": "RWA 規制・政策",
        "recent_focus": "規制環境分析"
    },
    {
        "name": "Hester Peirce",
        "affiliation": "SEC",
        "role": "Commissioner",
        "focus": "RWA 規制フレームワーク",
        "recent_focus": "トークン化資産ガイダンス"
    },
    {
        "name": "Jenny Johnson",
        "affiliation": "Franklin Templeton",
        "role": "President & CEO",
        "focus": "RWA 投資",
        "recent_focus": "ブロックチェーン投資ファンド"
    },
    {
        "name": "Umar Farooq",
        "affiliation": "LSEG (London Stock Exchange)",
        "role": "CEO, LSEG Technology",
        "focus": "RWA 市場基盤",
        "recent_focus": "取引所 RWA サポート"
    },
    {
        "name": "Brian Armstrong",
        "affiliation": "Coinbase",
        "role": "Co-Founder & CEO",
        "focus": "RWA プラットフォーム",
        "recent_focus": "機関向け RWA 取引"
    },

    # アナリスト・インフルエンサー
    {
        "name": "Ryan Sean Adams",
        "affiliation": "Bankless & Ethereum Research",
        "role": "Researcher & Content Creator",
        "focus": "RWA トレンド分析",
        "recent_focus": "機関化フェーズ解説"
    },
    {
        "name": "Arthur Hayes",
        "affiliation": "BitMEX / Maelstrom",
        "role": "Co-Founder & Former CEO",
        "focus": "RWA マーケット分析",
        "recent_focus": "TradFi 融合戦略"
    },
    {
        "name": "Tarun Chitra",
        "affiliation": "Gauntlet Networks",
        "role": "Founder & CEO",
        "focus": "RWA リスク管理",
        "recent_focus": "機関向け安全性"
    },
    {
        "name": "Mike Sall",
        "affiliation": "Nexus Mutual",
        "role": "Founder & CEO",
        "focus": "RWA 保険",
        "recent_focus": "機関向け保護メカニズム"
    },
    {
        "name": "Robert Alcorn",
        "affiliation": "tBTC & Thesis",
        "role": "CEO",
        "focus": "RWA 担保BTC",
        "recent_focus": "ビットコイン RWA 統合"
    },
    {
        "name": "Rune Christensen",
        "affiliation": "MakerDAO",
        "role": "Founder",
        "focus": "RWA 担保 DAI",
        "recent_focus": "機関向けステーブルコイン"
    },
    {
        "name": "Lucas Vogelsang",
        "affiliation": "Centrifuge",
        "role": "Co-Founder",
        "focus": "RWA 資産トークン化",
        "recent_focus": "企業向け統合"
    },
    {
        "name": "Paul Grewal",
        "affiliation": "Coinbase",
        "role": "Chief Legal Officer",
        "focus": "RWA 規制戦略",
        "recent_focus": "金融機関との提携推進"
    },
    {
        "name": "Tyrone Lobban",
        "affiliation": "DeFi Alliance",
        "role": "Executive Director",
        "focus": "RWA 業界連携",
        "recent_focus": "規制機関との協議"
    },
    {
        "name": "Sidney Powell",
        "affiliation": "Global RWA Initiative",
        "role": "Advisor",
        "focus": "RWA 国際規制",
        "recent_focus": "クロスボーダー RWA 標準化"
    }
]

# ===== ファンダメンタルズスコアリングマトリックス =====
FUNDAMENTALS_CATEGORIES = {
    "機関投資家参入": {
        "weight": 0.25,
        "indicators": [
            "BlackRock/Vanguard/Fidelity などのファンド投資",
            "銀行・証券会社との提携発表",
            "大型ファンド成立のニュース",
            "機関向けプロダクト追加",
            "流動性プール拡大"
        ]
    },
    "規制・コンプライアンス": {
        "weight": 0.25,
        "indicators": [
            "SEC/金融庁 からのガイダンス",
            "ライセンス取得",
            "規制テストネット承認",
            "国家レベルの法案可決",
            "金融監督当局との公式連携"
        ]
    },
    "技術・インフラ": {
        "weight": 0.20,
        "indicators": [
            "スケーラビリティ向上",
            "セキュリティ監査完了",
            "相互運用性実装",
            "ガス代削減",
            "キャパシティ拡張"
        ]
    },
    "提携・エコシステム": {
        "weight": 0.15,
        "indicators": [
            "大手 TradFi 企業との提携",
            "公式なエンタープライズ採用",
            "インテグレーション拡大",
            "戦略的パートナーシップ発表",
            "クロスチェーン連携"
        ]
    },
    "市場動向": {
        "weight": 0.15,
        "indicators": [
            "取引高の拡大",
            "保有者数の増加",
            "オンチェーンアクティビティ",
            "新規プロジェクト立ち上げ",
            "セクター全体の成長"
        ]
    }
}

# ===== ニュースカテゴリ分類 =====
NEWS_CATEGORIES = [
    "機関投資家参入",
    "規制クリア",
    "技術アップデート",
    "提携発表",
    "資金調達",
    "セキュリティ監査",
    "市場データ",
    "テックエコシステム",
    "規制動向",
    "業界分析"
]

# ===== 信頼度レベル =====
CREDIBILITY_SOURCES = {
    "超高": ["SEC", "金融庁", "FCA", "Bloomberg", "Reuters", "Wall Street Journal"],
    "高": ["CoinDesk", "Cointelegraph", "The Block", "Messari"],
    "中": ["Twitter (X)/ブロック", "Medium", "GitHubリリース"],
    "参考": ["個人ブログ", "YouTube", "Reddit"]
}

# ===== 厳選RWA情報源（ターゲットドメイン） =====
TARGET_DOMAINS = [
    # トークン化専門・トップクリプトメディア
    "rwa.xyz",
    "thetokenizer.com",
    "blockworks.co",
    "dlnews.com",
    "theblock.co",
    "coindesk.com",
    "cointelegraph.com",
    "bankless.com",
    "thedefiant.io",
    "cryptoslate.com",
    "wublock12.com",
    "decrypt.co",
    "ledgerinsights.com",

    # TradFi・マクロ経済・リサーチ機関
    "bloomberg.com",
    "ft.com",
    "wsj.com",
    "forbes.com",
    "reuters.com",
    "cnbc.com",
    "messari.io",
    "delphidigital.io",
    "binance.com",
    "defillama.com",
    "nansen.ai"
]

if __name__ == "__main__":
    print(f"RWA トークン総数: {sum(len(v) for v in RWA_TOKENS.values())}")
    print(f"キーパーソン数: {len(KEY_FIGURES)}")
    print(f"ファンダメンタルズカテゴリ: {len(FUNDAMENTALS_CATEGORIES)}")
