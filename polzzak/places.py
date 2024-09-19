from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Place

Place_ns = Namespace(name="place",description="플로깅 장소를 위한 API")

placeForm = reqparse.RequestParser()
#placeForm.add_argument('user_id', type=int, default=None, help='user id')
#placeForm.add_argument('id', type=int, default=None, help='event id')

place_create_fields = Place_ns.model('place_create', {
    'address': fields.String,
    'name': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float
}) #장소 생성 필드

place_modify_fields = Place_ns.model('place_modify', {
    'id': fields.Integer,
    'address': fields.String,
    'name': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float
}) #장소 수정 필드

place_delete_fields = Place_ns.model('place_delete', {
    'id': fields.Integer,
}) #장소 삭제  필드

@Place_ns.route('/')
class places(Resource):
    """
    @Place_ns.expect(placeForm)
    def get(self):
        user_id = int(request.args.get('user_id'))
        id = request.args.get('id')
        event = event.query.get_or_404(id)

        if user_id == session.get('user_id'):
            return {
                'message' : 'can modfiy and delete',
                'event' : {
                    'id' : event.id,
                    'title' : event.title,
                    'content' : event.content,
                    'start_time' : event.start_time,
                    'end_time' : event.end_time,
                    'place_id' : event.place_id
                }
            }, 200
        else:
            return {
                'message' : 'can modfiy and delete',
                'event' : {
                    'id' : event.id,
                    'title' : event.title,
                    'content' : event.content,
                    'start_time' : event.start_time,
                    'end_time' : event.end_time,
                    'place_id' : event.place_id
                }
            }, 200
"""

    @Place_ns.expect(place_create_fields)
    def post(self):
        address = request.json.get('address')
        name = request.json.get('name')
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')

        new_place = Place(address = address, name = name, latitude = latitude, longitude = longitude)
        
        db.session.add(new_place)
        db.session.commit()

        return {'message': 'Place created successfully!'}, 201

    @Place_ns.expect(place_modify_fields)
    def put(self):
        id = request.json.get('id')
        address = request.json.get('address')
        name = request.json.get('name')
        latitude = request.json.get('latitude')
        longitude = request.json.get('longitude')

        place = Place.query.filter(Place.id==id).first()
        if not place:
            return {'message' : 'place number <{}> does not exist!'.format(id)}, 404
        else:
            place.address = address 
            place.name =name 
            place.latitude = latitude 
            place.longitude = longitude
            return {'message' : 'place modified successfully'}, 200
        
    @Place_ns.expect(place_delete_fields)
    def delete(self):
        id = request.json.get('id')
        place = Place.query.get_or_404(id)
        db.session.delete(place)
        db.session.commit()

        return {'message' : 'place deleted successfully'}, 200
