'''
GET 메서드 관련 헬퍼 함수
'''

'''
쿼리스트링으로 데이터 입력시
파라미터의 키 값이 정확한 지 확인하는 함수입니다
'''
def parameter_check(params):
    data = ['company', 'tag']
    for keys in dict(params):
        if keys not in data:
            return dict(success=False, messsage='WrongParamsRequest'), 400, dict()
'''
PUT, DELETE 메서드 관련 헬퍼 함수
'''

'''
JSON으로 데이터 입력시
JSON 키 값이 정확한 지 확인하는 함수입니다
'''
def tag_key_check(json_data):
    data = ['company_id', 'tag']
    for keys in json_data:
        if keys not in data or len(json_data) != 2:
            return dict(success=False, messsage='WrongKey'), 400, dict()
'''
유효한 회사 아이디인지 검사하는 함수입니다.
'''
def company_id_check(json_data):
    if json_data not in range(1,101):
        return dict(success=False, messsage='NotExistCompany'), 404, dict()
'''
유효한 태그 아이디인지 검사하는 함수입니다.
'''
def tag_id_check(tag_id):
    set_tag_id = set(tag_id)
    for id in tag_id:
        if id not in range(1,51):
            return dict(success=False, messsage='NotExistTag'), 404, dict()
