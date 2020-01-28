from apis import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

'''
각 국가별 서비스 되는 원티드 사이트의 특징을 위해서 국가와 언어 통합
예로 HongKong, Canada의 경우 같은 국가지만 두가지 언어를 사용해서 정규화가 필요해 보일 수도 있으나
이러한 경우의 수는 제한적이고 크게 바뀌지 않는 데이터라고 판단했습니다.
'''
class ServiceLocation(db.Model):
    """ 
        서비스로케이션 테이블

        원티드 웹에서도 마찬가지 지만 본사와 각국의 지사는 다른 회사로 분리하기 위해서 
        각기 다른 언어를 사용하는 원티드 웹에서는 해당 언어의 태그만 검색이되도록
        ServiceLocation를 만들었습니다.

        country_code  : 나라의 코드 영문 약어 ex) ko,en,jp,ww(worldwide)
        language_code : 언어의 코드 영문 약어 ex) ko,en,jp
    """
    __tablename__ = 'servicelocation'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False, unique=True)
    language_code = db.Column(db.String(2), nullable=False)

    company_servicelocation = db.relationship('Company', back_populates='servicelocation_company')
    locsertagmapping_servicelocation = db.relationship('LocSerTagMapping', back_populates='servicelocation_locsertagmapping')

class Company(db.Model):
    """  
        회사 테이블

        company_id             : 회사의 아이디는 pk키가 아닌 유니크 키로 관리합니다.
        represent_company_name : 회사의 대표되는 이름입니다.
        for_service_location   : 서비스 로케이션의 FK키
    """
    __tablename__ = 'company'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False, unique=True)
    represent_company_name = db.Column(db.String(50), nullable=False)
    
    for_service_location = db.Column(db.Integer, db.ForeignKey('servicelocation.id'))

    servicelocation_company = db.relationship('ServiceLocation', back_populates='company_servicelocation')
    localization_company = db.relationship('Localization', back_populates='company_localization')
    locsertagmapping_company = db.relationship('LocSerTagMapping', back_populates='company_locsertagmapping')

class Localization(db.Model):
    """  
        번역이 된 로컬라제이션 테이블

        language                  : 번역이 된 언어 코드입니다. (ko, en, jp) 위의 서비스로케이션의 language와 다른 의미를 가집니다.
        localization_company_name : 번역된 회사명
        for_company_id            : 컴퍼니의 FK키
    """
    __tablename__ = 'localization'
    __table_args__ = {'extend_existing': True}
    __searchable__ = ['localization_company_name']

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(2), nullable=False)
    localization_company_name = db.Column(db.String(50), nullable=False)
    
    for_company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'))

    company_localization = db.relationship('Company', back_populates='localization_company')

class LocSerTagMapping(db.Model):
    """ 
        로컬라제이션,서비스로케이션,태그간 맵핑이 되어 있는 테이블

        for_localization_id     : 로컬라제이션의 FK키
        for_tag_id              : 태그의 FK키
        for_service_location_id : 서비스 로케이션의 FK키 

    """
    __tablename__ = 'locsertagmapping'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    for_company_id = db.Column(db.Integer, db.ForeignKey('company.id',ondelete='CASCADE'))
    for_tag_id = db.Column(db.Integer, db.ForeignKey('tag.id',ondelete='CASCADE'))
    for_service_location_id = db.Column(db.Integer, db.ForeignKey('servicelocation.id'))

    company_locsertagmapping = db.relationship('Company', back_populates='locsertagmapping_company')
    tag_locsertagmapping = db.relationship('Tag', back_populates='locsertagmapping_tag')
    servicelocation_locsertagmapping = db.relationship('ServiceLocation', back_populates='locsertagmapping_servicelocation')
    
    '''
    POST,PUT,DELETE의 경우에는 __init__ 재정의를 해야 사용이 가능했습니다.
    '''
    def __init__(self,for_company_id,for_tag_id,for_service_location_id):
        self.for_company_id = for_company_id
        self.for_tag_id = for_tag_id
        self.for_service_location_id = for_service_location_id

class Tag(db.Model):
    """  
        태그명을 담는 테이블

        tag_ko,tag_jp,tag_en : 태그는 원티드에서 주체가 되어 항상 번역이 될 수 있으므로 같은 아이디당 동일하게 관리합니다.
                               반대로 회사명은 회사가 주체가 되어 이름을 현지화 하는 것이라고 생각 했습니다.
    """
    __tablename__ = 'tag'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    tag_ko = db.Column(db.String(15), nullable=False, unique=True)
    tag_jp = db.Column(db.String(15), nullable=False, unique=True)
    tag_en = db.Column(db.String(15), nullable=False, unique=True)

    locsertagmapping_tag = db.relationship('LocSerTagMapping', back_populates='tag_locsertagmapping')
