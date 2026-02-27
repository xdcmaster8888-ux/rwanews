@echo off
REM RWA News Auto-Post ローカル実行スクリプト

cd /d "C:\Users\yuji\rwanews"

REM Python 仮想環境を有効化（必要に応じて）
REM call venv\Scripts\activate.bat

REM メインスクリプト実行
python main.py

REM 実行結果をログに記録
echo [%date% %time%] RWA News Post executed >> logs\rwa_news.log
