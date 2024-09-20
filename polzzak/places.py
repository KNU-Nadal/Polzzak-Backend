from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Place

Place_ns = Namespace(name="place",description="플로깅 장소를 위한 API")

place_create_fields = Place_ns.model('place_create', {
    'address': fields.String(default='대구광역시 북구 대학로 80'),
    'name': fields.String(default='경북대학교'),
    'latitude': fields.Float(default=35.8906),
    'longtitude': fields.Float(default=128.6121)
}) #장소 생성 필드

place_modify_fields = Place_ns.model('place_modify', {
    'id': fields.Integer,
    'address': fields.String(default='대구광역시 북구 대학로 80'),
    'name': fields.String(default='경북대학교'),
    'latitude': fields.Float(default=35.8906),
    'longtitude': fields.Float(default=128.6121)
}) #장소 수정 필드

place_delete_fields = Place_ns.model('place_delete', {
    'id': fields.Integer,
}) #장소 삭제  필드

@Place_ns.route('/')
class Places(Resource):
    @Place_ns.expect(place_create_fields)
    def post(self, place_data=None):
        if place_data is None:
            place_data = Place_ns.payload  # 클라이언트에서 받은 데이터를 사용
        new_place = Place(
            address=place_data['address'],
            name=place_data['name'],
            latitude=place_data['latitude'],
            longtitude=place_data['longtitude']
        )
        db.session.add(new_place)
        db.session.commit()
        return {'message': 'place created successfully', 'id': new_place.id}, 201

    @Place_ns.expect(place_modify_fields)
    def put(self, id, place_data=None):
        if place_data is None:
            place_data = Place_ns.payload

        place = Place.query.filter(Place.id==id).first()
        place.address = place_data['address'] 
        place.name = place_data['name']
        place.latitude = place_data['latitude']
        place.longtitude = place_data['longtitude']
        db.session.commit()
        return {'message': 'place created successfully'}, 201
        
    @Place_ns.expect(place_delete_fields)
    def delete(self, id):
        place = Place.query.filter_by(id=id).first()
        db.session.delete(place)
        db.session.commit()

        return {'message' : 'place deleted successfully'}, 200
