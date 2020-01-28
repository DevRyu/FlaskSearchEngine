import os
import re
import sys
import copy
import json

from itertools import chain

from apis import app
from apis import db
from model.models import ServiceLocation, Company, Localization, LocSerTagMapping, Tag

from flask import request
from flask import jsonify
from sqlalchemy.orm import relationship
from sqlalchemy import or_

'''
GET
서버 핑 테스트용 api
'''
@app.route("/", methods=['GET']) 
def ping():
    return "pong"

'''
GET
회사의 태그명 또는 회사명으로 검색하는 api
요청 받는 파라미터 : ['company', 'tag']
'''
@app.route('/search', methods=['GET'])
def search():
    data = ['company', 'tag']
    for keys in dict(request.args):
        if keys not in data:
            return dict(success=False, messsage='WrongParamsRequest'), 400, dict()
    try:
        company = request.args.get('company')
        tag = request.args.get('tag')
        tags = tag.split('|') if tag else []

        '''
        company,tag가 둘다 value가 있거나 없을 때 에러메시지
        '''
        if company and tag:
            return dict(success=False, messsage='MethodNotAllowed'), 405, dict()

        elif not company and not tag:
            Company.query.all()
            return dict(success=False, messsage='NoParamsValue'), 400, dict()

        elif company and not tag: # company로 검색 할 경우
            company_query = Localization.query.filter(Localization.localization_company_name.contains(company)).all()
            
            get_company_case = [id.for_company_id for id in company_query]
            get_company_id = list(sorted(set(get_company_case)))

            result = []
            for element in get_company_id:
                company_all = Company.query.filter(Company.company_id == element)
                for local in company_all:
                    result.append(local.localization_company)

            final = []
            for idx, element in enumerate(result,0):
                final.append({})
                
                for index in element:
                    final[idx].update({
                        f"{index.language}_company_name" : index.localization_company_name,
                        "company_id" : index.for_company_id,
                        "tag_ko" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_ko)) for x in index.company_localization.locsertagmapping_company),
                        "tag_jp" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_jp)) for x in index.company_localization.locsertagmapping_company),
                        "tag_en" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_en)) for x in index.company_localization.locsertagmapping_company)
                    })
            if final == []:
                return dict(Success=True, Messsage='DataNotFound',), 404, dict()
            return dict(success=True, messsage='Success', data=final), 200, dict()

        elif not company and tag:  # tag로 검색을 할 경우

            tag_ko_filter = [Tag.tag_ko == tag for tag in tags]
            tag_jp_filter = [Tag.tag_jp == tag for tag in tags]
            tag_en_filter = [Tag.tag_en == tag for tag in tags]
            tags_result = Tag.query.filter(or_(*tag_ko_filter,*tag_jp_filter,*tag_en_filter)).all()
        
            mapping_objects = [tag.locsertagmapping_tag for tag in tags_result]
            mapping_objects = list(chain.from_iterable(mapping_objects))

            company_ids = [tag.for_company_id for tag in mapping_objects]
            
            company_obj = []
            local_ids = []
            for element in company_ids:
                company_all = Company.query.filter(Company.company_id == element).all()
                company_obj.extend(company_all)
                for local in company_all:
                    local_ids.append(local.localization_company)

            company_data = []
            for idx, element in enumerate(local_ids,0):
                company_data.append({})
                for index in element:
                    company_data[idx].update({
                        f"{index.language}_company_name" : index.localization_company_name,
                        "company_id" : index.for_company_id
                    })

            company_tag = [i.locsertagmapping_company for i in company_obj]
            tag_data = []
            for idx, company_obj in enumerate(company_tag,0):
                tag_data.append([])
                for tag in company_obj:
                    tag_data[idx].append({
                        "tag_ko" : ''.join(''.join(map(str, tag_name )) for tag_name in tag.tag_locsertagmapping.tag_ko),
                        "tag_jp" : ''.join(''.join(map(str, tag_name )) for tag_name in tag.tag_locsertagmapping.tag_jp),
                        "tag_en" : ''.join(''.join(map(str, tag_name )) for tag_name in tag.tag_locsertagmapping.tag_en)
                        })

            for idx, tag in enumerate(tag_data, 0):
                company_data[idx].update({
                    k: '|'.join(''.join(map(str, v.get(k))) for v in tag)
                    for k in set().union(*tag)
                })
            if company_data == []:
                return dict(Success=True, Messsage='DataNotFound',), 404, dict()
            return dict(Success=True, Messsage='Success', data=company_data), 200, dict()


    except Exception as e:
        print(e)
        return dict(success=False, messsage='InternetServerError'), 500, dict() 

'''
PUT
회사의 태그명을 하나 이상 추가하는 API
요청 받는 JSON 데이터(필수) : ['company_id' : id, 'tag' : ['태그_1','태그_2']]
가정을 이미 기존에 있는 데이터 추가 시 에러를 일으키게 했습니다.
사유는 API를 통해서 제 3자가 사용자의 데이터 상태를 유추할 수 있겟습니다만 
그러한 가정은 애초에 보안이 문제가 되는 것이 문제이고 
제 기능에 충실하게 하는 것이 정답이라고 생각했습니다. 
'''
@app.route('/tag', methods=['PUT'])
def tag_put():
    data = ['company_id', 'tag']
    json_data = request.get_json()
    for keys in json_data:
        if keys not in data or len(json_data) != 2:
            return dict(success=False, messsage='WrongKey'), 400, dict()
    try:
        if json_data['company_id'] not in range(1,101):
            return dict(success=False, messsage='NotExistCompany'), 404, dict()

        tag_id = [int(sub.split('_')[1]) for sub in json_data['tag']] 
        for id in tag_id:
            if id not in range(1,51):
                return dict(success=False, messsage='NotExistTag'), 404, dict()

        mapping_objs = LocSerTagMapping.query.filter(LocSerTagMapping.for_company_id == json_data['company_id']).all()

        servic_location = 0
        for element in mapping_objs:
            if element.for_tag_id in tag_id:
                return dict(success=False, messsage='BadTagRequest'), 400, dict()
            servic_location = element.for_service_location_id

        for id in tag_id:
            data = LocSerTagMapping(json_data['company_id'],id,servic_location)
            db.session.add(data)
        db.session.commit()             

        return dict(Success=True, Messsage='Success'), 200, dict()

    except Exception as e:
        print(e)
        db.session.rollback()
        return dict(success=False, messsage='InternetServerError'), 500, dict() 

'''
DELETE
회사의 태그명을 하나 이상 삭제하는 API
요청 받는 JSON 데이터(필수) : ['company_id', 'tag']
가정을 기존에 없는 데이터를 삭제 요청 시 에러를 일으키게 했습니다.
사유는 위의 PUT과 같습니다.
'''
@app.route('/tag', methods=['DELETE'])
def tag_delete():
    data = ['company_id', 'tag']
    json_data = request.get_json()

    for keys in json_data.keys():
        if keys not in data or len(json_data) != 2:
            return dict(success=False, messsage='WrongKey'), 400, dict()

    try:
        if json_data['company_id'] not in range(1,101):
            return dict(success=False, messsage='NotExistCompany'), 404, dict()

        tag_id = [int(sub.split('_')[1]) for sub in json_data['tag']] 
        for id in tag_id:
            if id not in range(1,51):
                return dict(success=False, messsage='NotExistTag'), 404, dict()
        
        mapping_objs = LocSerTagMapping.query.filter(LocSerTagMapping.for_company_id == json_data['company_id']).all()
        servic_location = 0
        element_tag_id =[]
        
        for element in mapping_objs:
            element_tag_id.append(element.for_tag_id)
            servic_location = element.for_service_location_id
        
        compare_list = list(set(tag_id).intersection(set(element_tag_id)))

        if tag_id != compare_list:
            return dict(success=False, messsage='BadTagRequest'), 400, dict()

        for id in tag_id:   
            LocSerTagMapping.query.filter_by(for_company_id=json_data['company_id'],for_tag_id = id,for_service_location_id = servic_location).delete()
        db.session.commit()             
        return dict(Success=True, Messsage='Success'), 200, dict()

    except Exception as e:
        print(e)
        db.session.rollback()
        return dict(success=False, messsage='InternetServerError'), 500, dict() 
