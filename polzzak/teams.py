from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Team, User, user_team
from sqlalchemy import select, insert, delete
from datetime import datetime

Team_ns = Namespace(name="team",description="플로깅 팀을 위한 API")

teamForm = reqparse.RequestParser()
teamForm.add_argument('id', type=int, default=None, help='team id')

team_create_fields = Team_ns.model('team_create', {
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String(default = '2024-09-24T14:30'),
    'end_time': fields.String(default = '2024-09-28T14:30'),
    'place_id': fields.Integer
}) #리뷰 생성 필드

team_modify_fields = Team_ns.model('team_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String(default = '2024-09-25T14:30'),
    'end_time': fields.String(default = '2024-09-29T14:30'),
    'place_id' : fields.Integer
}) #리뷰 수정 필드

team_delete_fields = Team_ns.model('team_delete', {
    'id' : fields.Integer
}) #리뷰 삭제 필드

@Team_ns.route('/')
class Teams(Resource):
    @Team_ns.expect(teamForm)
    def get(self):
        #1.이 유저가 이미 이 팀에 가입되어있는지 확인을 하고, 가입 되었으면, return  message this user 이미 그거
        user_id = session.get('user_id')
        id = request.args.get('id')

        user = User.query.get_or_404(user_id)
        team = Team.query.get_or_404(id)

        start_time = team.start_time
        end_time = team.end_time
        # datetime 객체를 문자열로 변환
        start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
        # 유저가 팀에 속해 있는지 확인
        if user and team:
            if team in user.user_team_set:
                return {'message': 'You are already a member of this team',
                    'team' : {
                    'id' : team.id,
                    'title' : team.title,
                    'content' : team.content,
                    'start_time' : start_time_str,
                    'end_time' : end_time_str,
                    'place_id' : team.place_id
                }}, 200
            else:
                return {
                    'message' : 'can join this team',
                    'team' : {
                        'id' : team.id,
                        'title' : team.title,
                        'content' : team.content,
                        'start_time' : start_time_str,
                        'end_time' : end_time_str,
                        'place_id' : team.place_id
                    }
            }, 200

    @Team_ns.expect(team_create_fields)
    def post(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        title = request.json.get('title')
        content = request.json.get('content')
        start_time_str = request.json.get('start_time')
        end_time_str = request.json.get('end_time')
        admin_id = session.get('user_id')
        place_id = request.json.get('place_id')


        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
        new_team = Team(title=title, content=content, start_time=start_time, end_time=end_time,admin_id=admin_id, place_id=place_id)

        db.session.add(new_team)

        user = User.query.filter_by(id=admin_id).first()
        team = Team.query.filter_by(id=new_team.id).first()
        user.user_team_set.append(team)
        db.session.commit()

        return {'message': 'Team created successfully!',
                'team':{
                    'id': new_team.id
                }}, 201
    
    @Team_ns.expect(team_modify_fields)
    def put(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        id = request.json.get('id') # 전창우 수정
        title = request.json.get('title')
        content = request.json.get('content')
        start_time_str = request.json.get('start_time')
        end_time_str = request.json.get('end_time')
        place_id = request.json.get('place_id')

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        team = Team.query.filter_by(id=id).first()

        if not team:
            return {'message' : 'team number <{}> does not exist!'.format(id)}, 404
        else:
            team.title = title
            team.content = content
            team.start_time = start_time
            team.end_time = end_time
            team.place_id = place_id
            db.session.commit()  # db.session.commit() 추가
            return {'message' : 'Team modified successfully'}, 200
        
    @Team_ns.expect(team_delete_fields)
    def delete(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        id = request.json.get('id')
        team = Team.query.get(id)
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
        if user_id == None:
            return {'islogin' : False}
        
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
        if user_id == None:
            return {'islogin' : False}
        # user_team 테이블에서 해당 데이터 삭제
        user = User.query.get_or_404(user_id)
        team = Team.query.get_or_404(team_id)

        if user_id == team.admin_id:
            team = Team.query.get(team.id)
            db.session.delete(team)
            db.session.commit()
            return {'message' : 'Team deleted successfully'}, 200
        # 유저가 팀에 속해 있는지 확인한 후 삭제
        if user and team:
            if team in user.user_team_set:
                user.user_team_set.remove(team)  # 관계 제거
                db.session.commit()  # 변경 사항 커밋
                return {'message': 'User removed from team successfully'}, 200