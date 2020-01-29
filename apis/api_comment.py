# import os
# import re
# import sys
# import copy
# import json
# from itertools import chain

# from apis import app
# from apis import db
# from model.models import (ServiceLocation, Company, Localization, 
#                         LocSerTagMapping, Tag)
# from apis.utils.helper import (parameter_check, tag_key_check, 
#                                 company_id_check, tag_id_check)

# from flask import request
# from flask import jsonify
# from sqlalchemy.orm import relationship
# from sqlalchemy import or_

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
    parameter_check(request.args)
    try:
        company = request.args.get('company')
        tag = request.args.get('tag')
        tags = tag.split('|') if tag else []

        '''
        company,tag가 둘다 value가 있거나 없을 때 에러 메시지
        '''
        if company and tag:
            return dict(success=False, messsage='MethodNotAllowed'), 405, dict()

        elif not company and not tag:
            Company.query.all()
            return dict(success=False, messsage='NoParamsValue'), 400, dict()

        elif company and not tag: # company로 검색 할 경우
            '''
            Localization에서 사용자 요청한 데이터 검색 후
            company_id값을 가져옴 
            '''
            company_query = Localization.query.filter(Localization.localization_company_name.contains(company)).all()
            get_company_id = [id.for_company_id for id in company_query]
            sorted_company_id = list(sorted(set(get_company_id)))
            '''
            부모 모델인 Company에서 company_id를 바탕으로
            다시 Localization에 다른 이름은 없는 지 확인 후 
            결과 오브젝트 리스트에 저장
            '''
            local_obj = []
            for element in sorted_company_id:
                company_all = Company.query.filter(Company.company_id == element)
                for local in company_all:
                    local_obj.append(local.localization_company)
            '''
            ORM관계 맵핑을 통해서 Company,Tag,ServiceLocation모델들이
            Mapping된 DB모델로 태그 데이터를 찾고 
            모든 데이터들을 Json화 하였습니다.
            번역이 되어 있지 않으면 출력을 하지 않도록 구현하였습니다.
            '''
            result = []
            for idx, element in enumerate(local_obj,0):
                result.append({})
                
                for index in element:
                    result[idx].update({
                        f"{index.language}_company_name" : index.localization_company_name,
                        "company_id" : index.for_company_id,
                        "tag_ko" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_ko)) for x in index.company_localization.locsertagmapping_company),
                        "tag_jp" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_jp)) for x in index.company_localization.locsertagmapping_company),
                        "tag_en" :  '|'.join(''.join(map(str, x.tag_locsertagmapping.tag_en)) for x in index.company_localization.locsertagmapping_company)
                    })

            if result == []:
                return dict(Success=True, Messsage='Data Not Found',), 404, dict()
            return dict(success=True, messsage='Success', data=result), 200, dict()

        elif not company and tag:  # tag로 검색을 할 경우
            '''
            사용자에게 요청받은 태그에 데이터들을 ORM객체에 다 넣고
            ORM에서는 SQL의 OR조건으로 관련된 데이터들을 위와는 다르게 비교값(=)으로 찾습니다. 
            다시 말해 정확하게 값을 입력을 해야합니다.
            OR조건을 사용한 이유는 문제에서 "|" 로 표현 된 데이터 셋을 보고 진행 하였습니다.
            '''
            tag_ko_filter = [Tag.tag_ko == tag for tag in tags]
            tag_jp_filter = [Tag.tag_jp == tag for tag in tags]
            tag_en_filter = [Tag.tag_en == tag for tag in tags]
            tags_result = Tag.query.filter(or_(*tag_ko_filter,*tag_jp_filter,*tag_en_filter)).all()
            '''
            태그의 object를 가지고 Company,Tag,ServiceLocation모델들이 Mapping된
            DB모델에서의 object 바꾸어 주고 중첩리스트를 해지합니다.
            회사의 아이디 값 또한 추출합니다.
            '''
            mapping_objects = [tag.locsertagmapping_tag for tag in tags_result]
            mapping_objects = list(chain.from_iterable(mapping_objects))
            company_ids = [tag.for_company_id for tag in mapping_objects]
            '''
            결과값에 해당하는 회사의 아이디로 Company에 비교연산자로 쿼리를 사용하고
            결과값에 해당하는 Company object는 company_obj입니다.
            Company object하나당 가지는 여러 번역된 Localization object를 
            local_ids에 저장합니다.
            '''
            company_obj = []
            local_ids = []
            for element in company_ids:
                company_all = Company.query.filter(Company.company_id == element).all()
                company_obj.extend(company_all)
                for local in company_all:
                    local_ids.append(local.localization_company)
            '''
            위에서의 여러 번역된 Localization object에서 
            정보들을 리스트 안의 딕셔너리 형태로 저장합니다.
            (순서는 위에서 정렬된 상태입니다.)
            result: JSON 출력을 위해 담는 리스트
            '''
            result = []
            for idx, element in enumerate(local_ids,0):
                result.append({})
                for index in element:
                    result[idx].update({
                        f"{index.language}_company_name" : index.localization_company_name,
                        "company_id" : index.for_company_id
                    })
            '''
            위에서의 Company object 리스트에서
            Company,Tag,ServiceLocation모델들이 Mapping된
            모델을 통해 Mapping object를 가집니다.
            하나의 회사에 대한 정보를 위해 for문을 돌 때
            여려 태그에 대한 정보를 위에 안에 for문이 돕니다.
            company_tag : 하나의 서로 다른 Company object입니다.
            company_obj : 회사와 태그정보가 Mapping 객체입니다.
            태그 정보들을 리스트 안의 딕셔너리 형태로 저장합니다.
            (순서는 위에서 정렬된 상태입니다.)
            '''
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
            '''
            위에 tag_data의 회사명 데이터와 result의 태그 데이터가
            1대1대응함으로 합쳐 주고  
            만일 태그가 여러개 존재 할시 |로 구분하여 결과값을 출력합니다.
            '''
            for idx, tag in enumerate(tag_data, 0):
                result[idx].update({
                    k: '|'.join(''.join(map(str, v.get(k))) for v in tag)
                    for k in set().union(*tag)
                })
            if result == []:
                return dict(Success=True, Messsage='Data Not Found',), 404, dict()
            return dict(Success=True, Messsage='Success', data=result), 200, dict()


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
    json_data = request.get_json()
    tag_key_check(json_data)
    company_id_check(json_data['company_id'])

    tag_id = [int(sub.split('_')[1]) for sub in json_data['tag']]
    tag_id_check(tag_id)

    set_tag_id = set(tag_id)
    if len(set_tag_id) != len(tag_id):
        return dict(success=False, messsage='DuplicatedTagId'), 400, dict()

    try:
        '''
        태그에 관련된 맵핑 객채를 가져옵니다.
        맵핑테이블에 필요한 FK키인 회사id,위치id,태그id를 찾는 과정입니다.
        '''
        mapping_objs = LocSerTagMapping.query.filter(LocSerTagMapping.for_company_id == json_data['company_id']).all()
        servic_location = 0
        '''
        만약 회사에서 기존에 가지고 있는 태그를 중복으로 추가 할려고 할 시
        에러를 호출합니다. 
        회사의 위치에 대한 id를 servic_location에 추가합니다. 
        '''
        for element in mapping_objs:
            if element.for_tag_id in tag_id:
                return dict(success=False, messsage='BadTagRequest'), 400, dict()
            servic_location = element.for_service_location_id
        '''
        태그 아이디 별로 맵핑 객체를 생성하고 커밋합니다.
        '''
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
    json_data = request.get_json()
    tag_key_check(json_data)
    company_id_check(json_data['company_id'])

    tag_id = [int(sub.split('_')[1]) for sub in json_data['tag']] 
    tag_id_check(tag_id)

    set_tag_id = set(tag_id)
    if len(set_tag_id) != len(tag_id):
        return dict(success=False, messsage='DuplicatedTagId'), 400, dict()

    try:

        tag_id = [int(sub.split('_')[1]) for sub in json_data['tag']] 
        tag_id_check(tag_id)
        set_tag_id = set(tag_id)
        if len(set_tag_id) != len(tag_id):
            return dict(success=False, messsage='DuplicatedTagId'), 400, dict()
        '''
        mapping_objs : 태그와 연관된 맵핑테이블에서 객체를 가져옵니다
        맵핑테이블에 필요한 FK키인 회사id,위치id,태그id를 찾는 과정입니다.
        '''
        mapping_objs = LocSerTagMapping.query.filter(LocSerTagMapping.for_company_id == json_data['company_id']).all()
        servic_location = 0
        element_tag_id =[]
        '''
        만약 회사에서 없는 태그를 삭제 하려 할 시 에러를 호출합니다. 
        회사의 위치에 대한 id를 servic_location에 추가합니다. 
        '''
        for element in mapping_objs:
            element_tag_id.append(element.for_tag_id)
            servic_location = element.for_service_location_id
        compare_list = list(set(tag_id).intersection(set(element_tag_id)))
        '''
        회사에 없는 태그를 삭제 요청시 발생합니다.
        '''
        if sorted(tag_id) != sorted(compare_list):
            return dict(success=False, messsage='BadTagRequest'), 400, dict()
        '''
        회사와 연관되어있는 객체를 삭제하고 커밋합니다.
        '''
        for id in tag_id:   
            LocSerTagMapping.query.filter_by(for_company_id=json_data['company_id'],for_tag_id = id,for_service_location_id = servic_location).delete()
        db.session.commit()             
        return dict(Success=True, Messsage='Success'), 200, dict()

    except Exception as e:
        print(e)
        db.session.rollback()
        return dict(success=False, messsage='InternetServerError'), 500, dict() 
