import os
import sys
import csv
import json

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(parent_dir)

from apis import db
from model.models import ServiceLocation, Company, Localization, LocSerTagMapping, Tag
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
'''
ORM으로 사용시 Insert Or Update으로 데이터 삽입에 대한 대한 방법이(merge) 있으나 
속도적인 측면에서 문제가 있어 자주 사용되지 않는것 같았습니다.
그래서 bulk_save_objects
'''

'''
원래 선호하는 방법은 sqlalchemy에서 지원하는 로우쿼리를 사용하는 방법입니다.
아래의 예시와 같습니다.
def tag(database):
    f = open('Tag.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    for idx, list_ in enumerate(reader, 1):
        row = dict(list_)
        print(row['tag_ko'])
        sql = 'INSERT IGNORE tag (tag_ko, tag_jp, tag_en) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE tag_ko = VALUES(tag_ko)'
        result = database.execute(sql, (row['tag_ko'], row['tag_jp'], row['tag_en']))

def init():
    # database = create_engine(SQLALCHEMY_DATABASE_URI, encoding = 'utf-8', max_overflow = 0)
    # tag(database)
    # database.dispose()

'''


def tag():
    f = open('Tag.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    table = []
    
    for list_ in reader:
        row = dict(list_)
        table.append(row)
    result = [Tag(tag_ko=item['tag_ko'], tag_jp=item['tag_jp'], tag_en=item['tag_en']) for item in table]
    
    try:
        db.session.bulk_save_objects(result)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print('Tag 테이블 데이터들은 이미 들어가 있습니다.')
    
    return "Tag 테이블 데이터 삽입을 완료하였습니다."

def service_location():
    f = open('ServiceLocation.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    table = []
    
    for list_ in reader:
        row = dict(list_)
        table.append(row)
    result = [ServiceLocation(country_code=item['country_code'], language_code=item['language_code']) for item in table]
    
    try:
        db.session.bulk_save_objects(result)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        print('ServiceLocation 테이블 데이터들은 이미 들어가 있습니다.')

    return "ServiceLocation 테이블 데이터 삽입을 완료하였습니다."

def company():
    f = open('Company.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    table = []
    
    for list_ in reader:
        row = dict(list_)        
        table.append(row)
    result = [Company(for_service_location=item['for_service_location'], company_id=item['company_id'], represent_company_name=item['represent_company_name']) for item in table]

    try:
        db.session.bulk_save_objects(result)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        print('Company 테이블 데이터들은 이미 들어가 있습니다.')

    return "Company 테이블 데이터 삽입을 완료하였습니다."

def localization():
    f = open('Localization.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    table = []
    
    for list_ in reader:
        row = dict(list_)
        table.append(row)
    result = [Localization(language=item['language'], localization_company_name=item['localization_company_name'], for_company_id=item['for_company_id']) for item in table]
    
    try:
        db.session.bulk_save_objects(result)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        print('Localization 테이블 데이터들은 이미 들어가 있습니다.')

    return "Localization 테이블 데이터 삽입을 완료하였습니다."

def loc_ser_tag_mapping():
    f = open('LocSerTagMapping.csv', 'r', encoding='utf-8')
    reader = csv.DictReader(f)
    table = []
    
    for list_ in reader:
        row = dict(list_)
        table.append(row)
    result = [LocSerTagMapping(for_company_id=item['for_company_id'], for_tag_id=item['for_tag_id'], for_service_location_id=item['for_service_location_id']) for item in table]
    
    try:
        db.session.bulk_save_objects(result)
        db.session.commit()
    
    except Exception as e:
        db.session.rollback()
        print('LocSerTagMapping 테이블 데이터들은 이미 들어가 있습니다.')

    return "LocSerTagMapping 테이블 데이터 삽입을 완료하였습니다."

if __name__ == "__main__":
    tag()
    service_location()
    company()
    localization()
    loc_ser_tag_mapping()
    print('정상적으로 데이터 삽입을 완료하였습니다.')