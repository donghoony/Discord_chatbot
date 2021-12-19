git pull
kill -9 $(ps -ef | grep fruity.py | awk '{print $2}')
python3 fruity.py
