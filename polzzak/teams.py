from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Team, user_team
from sqlalchemy import select, insert, delete
from datetime import datetime

Team_ns = Namespace(name="team",description="플로깅 팀을 위한 API")

teamForm = reqparse.RequestParser()
teamForm.add_argument('user_id', type=int, default=None, help='user id')
teamForm.add_argument('id', type=int, default=None, help='team id')

team_create_fields = Team_ns.model('team_create', {
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String,
    'end_time': fields.String,
    'place_id': fields.Integer
}) #리뷰 생성 필드

team_modify_fields = Team_ns.model('team_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'start_time': fields.String,
    'end_time': fields.String,
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
        user_id = int(request.args.get('user_id'))
        
        id = request.args.get('id')
        team = Team.query.get_or_404(id)
        user_team_entry = db.session.execute(
            select([user_team]).where(user_team.c.user_id == user_id, user_team.c.team_id == id)
        ).first()

        if user_team_entry:
            return {'message': 'You are already a member of this team.'}, 400
                
        return {
                'message' : 'can modfiy and delete',
                'team' : {
                    'id' : team.id,
                    'title' : team.title,
                    'content' : team.content,
                    'start_time' : team.start_time,
                    'end_time' : team.end_time,
                    'place_id' : team.place_id
                }
        }, 200


    @Team_ns.expect(team_create_fields)
    def post(self):
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
        db.session.commit()
        return {'message': 'Team created successfully!'}, 201
    
    @Team_ns.expect(team_modify_fields)
    def put(self):
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
        id = request.json.get('id')
        team = Team.query.get_or_404(id)
        db.session.delete(team)
        db.session.commit()

        return {'message' : 'Team deleted successfully'}, 200
    

userteam_create_fields = Team_ns.model('userteam_create',{
    'team_id':fields.Integer,
    'user_id':fields.Integer
    })

userteam_delete_fields = Team_ns.model('userteam_delete', {
    'team_id':fields.Integer,
    'user_id':fields.Integer
    }) 

@Team_ns.route('/join/')
class Join(Resource):
    #team_id, user_id 가 들어오면 team_user table에 각각 저장
    @Team_ns.expect(userteam_create_fields)
    def post(self):
        team_id = request.json.get('team_id')
        user_id = request.json.get('user_id')

        # user_team 테이블에 데이터 삽입
        new_user_team = insert(user_team).values(user_id=user_id, team_id=team_id)
        db.session.execute(new_user_team)
        db.session.commit()   
        return {'message': 'User added to team successfully'}, 201
    
    # team_id와 user_id를 조건으로 데이터 삭제
    @Team_ns.expect(userteam_delete_fields)
    def delete(self):
        team_id = request.json.get('team_id')
        user_id = request.json.get('user_id')

        # user_team 테이블에서 해당 데이터 삭제
        delete_user_team = delete(user_team).where(user_team.c.user_id == user_id, user_team.c.team_id == team_id)
        db.session.execute(delete_user_team)
        db.session.commit()

        return {'message': 'User removed from team successfully'}, 200

