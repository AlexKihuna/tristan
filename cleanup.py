"""Remove unwanted files"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_LIST = ['media', 'static', BASE_DIR, 'Tristan']
FILE_LIST = ['run_once.log', 'db.sqlite3']
PRESERVE_LIST = ['0002.py']

for root, dirs, files in os.walk(BASE_DIR):
    # print root, BASE_DIR
    if os.path.split(root)[1] in DIR_LIST and root != BASE_DIR:
        continue
    if os.path.split(root)[1] == 'migrations':
        for f in files:
            if f not in PRESERVE_LIST:
                FILE_LIST.append(f)
    for d in dirs:
        if d == 'migrations':
            d_path = os.path.join(root, d)
            # shutil.rmtree(d_path)
    for f in files:
        if f.endswith('.pyc') or f in FILE_LIST:
            f_path = os.path.join(root, f)
            print 'Deleted:', f_path
            os.remove(f_path)
raw_input('Press Enter to continue...')