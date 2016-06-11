@echo off
for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set ldt=%ldt:~0,4%-%ldt:~4,2%-%ldt:~6,2% %ldt:~8,2%:%ldt:~10,2%:%ldt:~12,6%
echo Local date is %ldt% >> run_once.log
echo Installing project requirements...
pip install -r requirements.txt >> run_once.log
echo Making migrations....
python manage.py makemigrations core >> run_once.log
python manage.py migrate >> run_once.log
echo Enter the admin user details below.
python manage.py createsuperuser
pause