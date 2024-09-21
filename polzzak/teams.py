from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Team, User, Place, Image
from datetime import datetime
from .places import Places

Team_ns = Namespace(name="team",description="플로깅 팀을 위한 API")

teamForm = reqparse.RequestParser()
teamForm.add_argument('id', type=int, default=None, help='team id')

team_create_fields = Team_ns.model('team_create', {
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String(default='2024-09-25T14:30'),
    'end_time': fields.String(default='2024-09-29T14:30'),

    'place': fields.Nested(Team_ns.model('Place', {
        'address': fields.String(default='대구광역시 북구 대학로 80'),
        'name': fields.String(default='경북대학교'),
        'lat': fields.Float(default=35.8906),
        'lng': fields.Float(default=128.6121)
    }), description='Place data'),

    'image': fields.Nested(Team_ns.model('Image',{
        'id': fields.Integer,
    }))
})

team_modify_fields = Team_ns.model('team_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String(default='2024-09-25T14:30'),
    'end_time': fields.String(default='2024-09-29T14:30'),
    
    'place': fields.Nested(Team_ns.model('Place', {
        'address': fields.String(default='대구광역시 북구 대학로 80'),
        'name': fields.String(default='경북대학교'),
        'lat': fields.Float(default=35.8906),
        'lng': fields.Float(default=128.6121)
    }), description='Place data')
})

team_delete_fields = Team_ns.model('team_delete', {
    'id' : fields.Integer
}) #리뷰 삭제 필드

@Team_ns.route('/')
class Teams(Resource):
    @Team_ns.expect(teamForm)
    def get(self):
        user_id = session.get('user_id')
        id = request.args.get('id')

        team = Team.query.get_or_404(id)

        start_time = team.start_time
        end_time = team.end_time
        # datetime 객체를 문자열로 변환
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

        admin = User.query.get(team.admin_id)
        place = Place.query.get_or_404(team.place_id)
        image = Image.query.get_or_404(team.image_id)

        team_info = {
            'id' : team.id,
            'title' : team.title,
            'content' : team.content,
            'start_time' : start_time_str,
            'end_time' : end_time_str,
            'member' : len(team.user),
            'admin_id' : admin.name,
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
                    'team' : team_info
                }, 200

        user = User.query.get(user_id)
        if team in user.user_event_set:
            return {
                'isevent' : True,
                'islogin' : True,
                'team' : team_info
            }, 200
        else:
            return {
                'isevent' : False,
                'islogin' : True,
                'team' : team_info
            }, 200

    @Team_ns.expect(team_create_fields)
    def post(self):
        team_data = Team_ns.payload  # 팀 데이터 받기
        place_data = team_data['place']  # 장소 정보 추출
        image_data = team_data['image'] # 이미지 정보 추출
        # 장소 POST 함수 호출
        place_post_response = Places().post(place_data=place_data)
        place_id = place_post_response[0]['id']  # 장소 ID 가져오기

        # 팀 저장
        new_team = Team(
            title=team_data['title'],
            content=team_data['content'],
            admin_id=session.get('user_id'),  # 사용자 ID
            start_time = datetime.fromisoformat(team_data['start_time']),
            end_time = datetime.fromisoformat(team_data['end_time']),
            place_id=place_id,  # 방금 생성된 장소 ID
            image_id = image_data['id'] # 생성된 이미지 아이디
        )
        db.session.add(new_team)

        user = User.query.filter_by(id=session.get('user_id')).first()
        team = Team.query.filter_by(id=new_team.id).first()
        user.user_team_set.append(team)
        db.session.commit()

        return {'team':{
                    'id': new_team.id
                }}, 201
    
    @Team_ns.expect(team_modify_fields)
    def put(self):
        team_data = Team_ns.payload  # 팀 데이터 받기
        place_data = team_data['place']  # 장소 정보 추출

        team = Team.query.filter_by(id=team_data['id']).first()

        Places().put(id=team.place_id, place_data=place_data) # 장소 수정 함수 호출
        
        team.title = team_data['title']
        team.content = team_data['content']
        team.start_time = datetime.fromisoformat(team_data['start_time'])
        team.end_time = datetime.fromisoformat(team_data['end_time'])
        
        db.session.commit()
        return {'team':{
                    'id': team.id
                }}, 201
        
    @Team_ns.expect(team_delete_fields)
    def delete(self):
        id = request.json.get('id')
        team = Team.query.filter_by(id=id).first()
        Places().delete(id=team.place_id)
        db.session.delete(team)
        db.session.commit()

        return {'message' : 'Team deleted successfully'}, 200
    

userteam_create_fields = Team_ns.model('userteam_create',{
    'team_id':fields.Integer,
    })

userteam_delete_fields = Team_ns.model('userteam_delete', {
    'team_id':fields.Integer,
    })

@Team_ns.route('/join/')
class Join(Resource):
    #team_id, user_id 가 들어오면 team_user table에 각각 저장
    @Team_ns.expect(userteam_create_fields)
    def post(self):
        team_id = request.json.get('team_id')
        user_id = session.get('user_id')
        if user_id == 0:
            return {'message' : 'login plz'}
        
        user = User.query.filter_by(id=user_id).first()
        team = Team.query.filter_by(id=team_id).first()

        # 유저가 존재하고 팀이 존재할 경우에만 처리
        if user and team:
            # 유저가 해당 팀에 속하지 않은 경우에만 추가
            if team not in user.user_team_set:
                user.user_team_set.append(team)
                db.session.commit()
                return {'message': 'User added to team successfully'}, 201
    
    # team_id와 user_id를 조건으로 데이터 삭제
    @Team_ns.expect(userteam_delete_fields)
    def delete(self):
        team_id = request.json.get('team_id')
        user_id = session.get('user_id')

        # user_team 테이블에서 해당 데이터 삭제
        user = User.query.get_or_404(user_id)
        team = Team.query.get_or_404(team_id)

        if user_id == team.admin_id:
            team = Team.query.filter_by(id=team_id).first()
            Places().delete(id=team.place_id)
            db.session.delete(team)
            db.session.commit()
            return {'message' : 'Team deleted successfully'}, 200
        # 유저가 팀에 속해 있는지 확인한 후 삭제
        if user and team:
            if team in user.user_team_set:
                user.user_team_set.remove(team)  # 관계 제거
                db.session.commit()  # 변경 사항 커밋
                return {'message': 'User removed from team successfully'}, 200
            
@Team_ns.route('/list/')
class Teamlist(Resource):
    def get(self):
        team_list = Team.query.all()
        teams = []

        for team in team_list:
            admin = User.query.get(team.admin_id)
            place = Place.query.get(team.place_id)
            image = Image.query.get(team.image_id)

            tmp = {'id' : team.id,
                   'title' : team.title,
                   'content' : team.content,
                   'start_time' : team.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'end_time' : team.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'member' : len(team.user),
                   'admin_name' : admin.name,
                   'address' : place.address,
                   'place_name' : place.name,
                   'lat' : place.lat,
                   'lng' : place.lng,
                   'image_name' : image.name}
            teams.append(tmp)

        return {'teams': teams}, 200
    
@Team_ns.route('/list/my/')
class Myteamlist(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}, 401
        
        user = User.query.get(user_id)

        user_teams = user.user_team_set
        myteams = []

        for team in user_teams:
            admin = User.query.get(team.admin_id)
            place = Place.query.get(team.place_id)
            image = Image.query.get(team.image_id)

            tmp = {'id' : team.id,
                   'title' : team.title,
                   'content' : team.content,
                   'start_time' : team.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'end_time' : team.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                   'member' : len(team.user),
                   'admin_name' : admin.name,
                   'address' : place.address,
                   'place_name' : place.name,
                   'lat' : place.lat,
                   'lng' : place.lng,
                   'image_name' : image.name}
            myteams.append(tmp)

        return {'myteams': myteams}, 200
