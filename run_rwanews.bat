@echo off
REM RWA News Auto-Post System - Scheduled Execution
REM このバッチファイルは Windows Task Scheduler から毎日 08:00 と 18:00 に実行されます

cd /d C:\Users\yuji\rwanews

REM Python スクリプト実行
python main.py

REM 実行結果をログに記録
echo [%date% %time%] Execution completed >> logs\scheduler.log
