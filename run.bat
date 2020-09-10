@echo off
echo Installing required packages
@pip install -r requirements.txt
@C:
@cd C:\Python36\Scripts\
@pip install -r E:\13DTP\FH4_Cars\requirements.txt
echo Finished installing any required packages
@python routes.py
@cd C:\Python36\
@python E:\13DTP\FH4_Cars\routes.py
echo Program crashed/quit
pause()