import os
import sys
parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
data = {
    'user'     : 'root',
    'password' : '1397',
    'host'     : 'localhost',
    'port'     : 3306,
    'database' : 'wanted'
}
SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['database']}?charset=utf8"
SQLALCHEMY_TRACK_MODIFICATIONS = True
DEBUG = True

test_db = {
    'user'     : 'root',
    'password' : '1397',
    'host'     : 'localhost',
    'port'     : 3306,
    'database' : 'wanted_test'
}
test_config = {
    'DB_URL' : f"mysql+mysqlconnector://{test_db['user']}:{test_db['password']}@{test_db['host']}:{test_db['port']}/{test_db['database']}?charset=utf8",
}
