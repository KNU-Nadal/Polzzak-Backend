from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Team
import requests
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
        user_id = int(request.args.get('user_id'))
        id = request.args.get('id')
        team = Team.query.get_or_404(id)

        if user_id == session.get('user_id'):
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
        else:
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

    @Team_ns.expect(team_modify_fields)
    def put(self):
        title = request.json.get('title')
        content = request.json.get('content')
        start_time_str = request.json.get('start_time')
        end_time_str = request.json.get('end_time')
        place_id = request.json.get('place_id')

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        team = Team.query.filter(Team.id==id).first()

        if not team:
            return {'message' : 'team number <{}> does not exist!'.format(id)}, 404
        else:
            team.title = title
            team.content = content
            team.start_time = start_time
            team.end_time = end_time
            team.place_id = place_id
            return {'message' : 'Team modified successfully'}, 200
        
    @Team_ns.expect(team_delete_fields)
    def delete(self):
        id = request.json.get('id')
        team = Team.query.get_or_404(id)
        db.session.delete(team)
        db.session.commit()

        return {'message' : 'Team deleted successfully'}, 200