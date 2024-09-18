from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Event
from datetime import datetime

Event_ns = Namespace(name="event",description="플로깅 팀을 위한 API")

eventForm = reqparse.RequestParser()
eventForm.add_argument('user_id', type=int, default=None, help='user id')
eventForm.add_argument('id', type=int, default=None, help='event id')

event_create_fields = Event_ns.model('event_create', {
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String,
    'end_time': fields.String,
    'place_id': fields.Integer
}) #리뷰 생성 필드

event_modify_fields = Event_ns.model('event_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String,
    'end_time': fields.String,
    'place_id' : fields.Integer
}) #리뷰 수정 필드

event_delete_fields = Event_ns.model('event_delete', {
    'id' : fields.Integer
}) #리뷰 삭제 필드

@Event_ns.route('/')
class events(Resource):
    @Event_ns.expect(eventForm)
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

    @Event_ns.expect(event_create_fields)
    def post(self):
        title = request.json.get('title')
        content = request.json.get('content')
        start_time_str = request.json.get('start_time')
        end_time_str = request.json.get('end_time')
        admin_id = session.get('user_id')
        place_id = request.json.get('place_id')

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        new_event = Event(title=title, content=content, start_time=start_time, end_time=end_time,admin_id=admin_id, place_id=place_id)
     
        db.session.add(new_event)
        db.session.commit()

    @Event_ns.expect(event_modify_fields)
    def put(self):
        title = request.json.get('title')
        content = request.json.get('content')
        start_time_str = request.json.get('start_time')
        end_time_str = request.json.get('end_time')
        place_id = request.json.get('place_id')

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        event = Event.query.filter(Event.id==id).first()

        if not event:
            return {'message' : 'event number <{}> does not exist!'.format(id)}, 404
        else:
            event.title = title
            event.content = content
            event.start_time = start_time
            event.end_time = end_time
            event.place_id = place_id
            return {'message' : 'event modified successfully'}, 200
        
    @Event_ns.expect(event_delete_fields)
    def delete(self):
        id = request.json.get('id')
        event = event.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()

        return {'message' : 'event deleted successfully'}, 200