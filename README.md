# Wanted
Flask-SQLAlchemy,alembic,mysql-connector를 사용하여 구현 하였습니다.

# 파일 구조
```
├── apis/  # api 비즈니스 로직이 들어있는 폴더입니다.
│   ├── __init__.py
│   ├── __pycache__
│   └── api.py
│
├── migrations/ # alembic으로 migrations을 관리 하였습니다.
│   ├── README
│   ├── __pycache__
│   ├── env.py # 기본적인 마이그레이션 세팅 파일 입니다.
│   ├── script.py.mako
│   └── versions
│       └── __pycache__
│
├── model/ # 데이터 모델의 파일입니다. 
│   ├── Company.csv # 각각 테이블에 해당하는 csv파일입니다.
│   ├── LocSerTagMapping.csv
│   ├── Localization.csv
│   ├── ServiceLocation.csv
│   ├── Tag.csv
│   ├── setup.py  # 위의 csv파일을 Mysql에 넣는 로직입니다.
│   ├── __pycache__
│   └── models.py # class형태의 모델 파일입니다.
│
├── test/
├── config.py # 서버 구동 시 필요한 키값 저장파일입니다.
├── README.md
├── __pycache__
├── alembic.ini
├── requirements.txt # 외부 라이브러리들 버전 정보입니다.
├── run.py           # 앱 실행시 구동하는 파일입니다.
└── wanted_temp_data.csv 
```

# 실행방법


## 가상환경 설정
 
python 3.7, conda 가상환경으로 구현하였습니다.

처음에 의존하는 외부 라이브러리 설치가 필요합니다.
가상환경에서 설치를 권장 드립니다.
```bash
# requirements.txt가 있는 FlaskSearchengine환경에서 라이브러리 설치
/FlaskSearchengine pip install -r requirements.txt
```

## MYSQL DB설정
 

config.py에 들어가셔서 data 딕셔너리에서 환경에 맞게 설정해 주시고 
Mysql DB에서 create database로 data['database']와 같은 것으로 설치 해 주시면 됩니다.

```
/FlaskSearchengine/config.py
예)
data = {
    'user'     : 'root', 
    'password' : '1397',
    'host'     : 'localhost',
    'port'     : 3306,
    'database' : 'wanted'
}

MYSQL
SQL> CREATE DATABASE wanted default CHARACTER SET UTF8
```

alembic으로 마이그레이션을 세팅하였습니다.

## 마이그레이션 설정
 
```
alembic revision -m "migrate" --autogenerate # models.py 에서 모델의 변동사항을 반영하는 명령어 입니다.
alembic upgrade head # 제일 최신의 마이그레이션 버전을 사용합니다, 실제 DB에 반영이 됩니다. 
```

## 앱 실행

```
FLASK_APP=run.py FLASK_DEBUG=0 flask run
```

## api 배포 

https://documenter.getpostman.com/view/9188758/SWTABKGb?version=latest#intro