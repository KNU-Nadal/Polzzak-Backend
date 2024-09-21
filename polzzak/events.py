from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Event, User, Place, Image
from datetime import datetime
from .places import Places

Event_ns = Namespace(name="event",description="플로깅 이벤트를 위한 API")

eventForm = reqparse.RequestParser()
eventForm.add_argument('id', type=int, default=None, help='event id')

event_create_fields = Event_ns.model('event_create', {
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String(default='2024-09-25T14:30'),
    'end_time': fields.String(default='2024-09-29T14:30'),

    'place': fields.Nested(Event_ns.model('Place', {
        'address': fields.String(default='대구광역시 북구 대학로 80'),
        'name': fields.String(default='경북대학교'),
        'lat': fields.Float(default=35.8906),
        'lng': fields.Float(default=128.6121)
    }), description='Place data'),

    'image': fields.Nested(Event_ns.model('Image',{
        'id': fields.Integer,
    }))
}) #이벤트 생성 필드

# event_modify_fields = Event_ns.model('event_modify', {
#     'id' : fields.Integer,
#     'title': fields.String,
#     'content': fields.String,
#     'start_time': fields.String,
#     'end_time': fields.String,
#     'place_id' : fields.Integer
# }) #리뷰 수정 필드

# event_delete_fields = Event_ns.model('event_delete', {
#     'id' : fields.Integer
# }) #리뷰 삭제 필드

@Event_ns.route('/')
class Events(Resource):
    @Event_ns.expect(eventForm)
    def get(self):
        user_id = session.get('user_id')
        id = request.args.get('id')
        event = Event.query.get(id)
        start_time = event.start_time
        end_time = event.end_time
        # datetime 객체를 문자열로 변환
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        place = Place.query.get(event.place_id)
        image = Image.query.get(event.image_id)

        event_info = {
            'id' : event.id,
            'title' : event.title,
            'content' : event.content,
            'start_time' : start_time_str,
            'end_time' : end_time_str,
            'address' : place.address,
            'place_name' : place.name,
            'lat' : place.lat,
            'lng' : place.lng,
            'image_name' : image.name
        }

        if user_id == None:
            return {
                    'isevent' : False,
                    'islogin' : False,
                    'event' : event_info
                }, 200

        user = User.query.get(user_id)
        if event in user.user_event_set:
            return {
                'isevent' : True,
                'islogin' : True,
                'event' : event_info
            }, 200
        else:
            return {
                'isevent' : False,
                'islogin' : True,
                'event' : event_info
            }, 200
            

    @Event_ns.expect(event_create_fields)
    def post(self):
        event_data = Event_ns.payload  # 이벤트 데이터 받기
        place_data = event_data['place']  # 장소 정보 추출
        image_data = event_data['image'] # 이미지 정보 추출
        # 장소 POST 함수 호출
        place_post_response = Places().post(place_data=place_data)
        place_id = place_post_response[0]['id']  # 장소 ID 가져오기

        # 이벤트 저장
        new_event = Event(
            title=event_data['title'],
            content=event_data['content'],
            start_time = datetime.fromisoformat(event_data['start_time']),
            end_time = datetime.fromisoformat(event_data['end_time']),
            place_id=place_id,  # 방금 생성된 장소 ID
            image_id = image_data['id'] # 생성된 이미지 아이디
        )
        db.session.add(new_event)
        db.session.commit()
        return {'event':{
                    'id': new_event.id
                }}, 201

    # @Event_ns.expect(event_modify_fields)
    # def put(self):
    #     id = request.json.get('id')
    #     title = request.json.get('title')
    #     content = request.json.get('content')
    #     start_time_str = request.json.get('start_time')
    #     end_time_str = request.json.get('end_time')
    #     place_id = request.json.get('place_id')

    #     start_time = datetime.fromisoformat(start_time_str)
    #     end_time = datetime.fromisoformat(end_time_str)

    #     event = Event.query.filter_by(id=id).first()

    #     if not event:
    #         return {'message' : 'event number <{}> does not exist!'.format(id)}, 404
    #     else:
    #         event.title = title
    #         event.content = content
    #         event.start_time = start_time
    #         event.end_time = end_time
    #         event.place_id = place_id
    #         db.session.commit()
    #         return {'message' : 'Event modified successfully'}, 200
        
    # @Event_ns.expect(event_delete_fields)
    # def delete(self):
    #     id = request.json.get('id')
    #     event = Event.query.get(id)
    #     db.session.delete(event)
    #     db.session.commit()

    #     return {'message' : 'event deleted successfully'}, 200
    

userevent_create_fields = Event_ns.model('userevent_create',{
    'event_id':fields.Integer,
})

userevent_delete_fields = Event_ns.model('userevent_delete', {
    'event_id':fields.Integer,
})

@Event_ns.route('/join/')
class Join(Resource):
    #event_id, user_id 가 들어오면 event_user table에 각각 저장
    @Event_ns.expect(userevent_create_fields)
    def post(self):
        event_id = request.json.get('event_id')
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        user = User.query.filter_by(id=user_id).first()
        event = Event.query.filter_by(id=event_id).first()

        # 유저가 존재하고 이벤트가 존재할 경우에만 처리
        if user and event:
            # 유저가 해당 팀에 속하지 않은 경우에만 추가
            if event not in user.user_event_set:
                user.user_event_set.append(event)
                db.session.commit()
                return {'message': 'User added to event successfully'}, 201
    
    # event_id와 user_id를 조건으로 데이터 삭제
    @Event_ns.expect(userevent_delete_fields)
    def delete(self):
        event_id = request.json.get('event_id')
        user_id = session.get('user_id')

        # user_event 테이블에서 해당 데이터 삭제
        user = User.query.get_or_404(user_id)
        event = Event.query.get_or_404(event_id)

        if user and event:
            if event in user.user_event_set:
                user.user_event_set.remove(event)  # 관계 제거
                db.session.commit()  # 변경 사항 커밋
                return {'message': 'User removed from event successfully'}, 200


@Event_ns.route('/list/')
class Eventlist(Resource):
    def get(self):
        event_list = Event.query.all()
        events = []

        for event in event_list:
            place = Place.query.get(event.place_id)
            image = Image.query.get(event.image_id)

            tmp = {'id' : event.id,
                   'title' : event.title,
                   'content' : event.content,
                   'start_time' : event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'end_time' : event.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'address' : place.address,
                   'place_name' : place.name,
                   'lat' : place.lat,
                   'lng' : place.lng,
                   'image_name' : image.name}
            events.append(tmp)

        return {'events': events}, 200
    
@Event_ns.route('/list/my/')
class Myeventlist(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}, 401
        
        user = User.query.get(user_id)

        user_events = user.user_event_set
        myevents = []

        for event in user_events:
            place = Place.query.get(event.place_id)
            image = Image.query.get(event.image_id)

            tmp = {'id' : event.id,
                   'title' : event.title,
                   'content' : event.content,
                   'start_time' : event.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'end_time' : event.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'address' : place.address,
                   'place_name' : place.name,
                   'lat' : place.lat,
                   'lng' : place.lng,
                   'image_name' : image.name}
            myevents.append(tmp)

        return {'myevents': myevents}, 200