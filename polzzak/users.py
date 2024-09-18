from flask import Flask, request, jsonify, g, session, current_app
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import User
import requests

import os

from flask_sqlalchemy import SQLAlchemy

def get_kakao_client_id():
    with current_app.app_context():  # 애플리케이션 컨텍스트 내에서 실행
        kakao_client_id = current_app.config['KAKAO_CLIENT_ID']
        return kakao_client_id

def get_kakao_redirect_uri():
    with current_app.app_context():  # 애플리케이션 컨텍스트 내에서 실행
        kakao_redirect_uri = current_app.config['KAKAO_REDIRECT_URI']
        return kakao_redirect_uri

User_ns = Namespace(name="user",description="사용자 인증을 위한 API")

@User_ns.route('/')
class Users(Resource):
    def get(self):
        KAKAO_CLIENT_ID = get_kakao_client_id()
        KAKAO_REDIRECT_URI = get_kakao_redirect_uri()
        code = request.args.get('code')

        # 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_CLIENT_ID,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code,
        }
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_response = requests.post(token_url, data=token_data, headers=token_headers)
        token_json = token_response.json()
        access_token = token_json.get('access_token')

        # 사용자 정보 요청
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        user_info_headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        user_info_response = requests.get(user_info_url, headers=user_info_headers)
        user_info = user_info_response.json()

        # 사용자 정보 추출
        kakao_id = user_info['id']
        name = user_info['kakao_account']['profile']['nickname']
        profile_image = user_info['kakao_account']['profile'].get('profile_image_url', None)

        # 사용자 정보 저장 (이미 존재하는지 확인)
        existing_user = User.query.filter_by(kakao_id=kakao_id).first()
        if existing_user:
            session.clear()
            session['user_id'] = existing_user.id
            # 5. 기존 사용자 정보와 새로운 정보를 비교 및 업데이트
            if (existing_user.name != name or existing_user.profile_image != profile_image):
                existing_user.name = name
                existing_user.profile_image = profile_image
                db.session.commit()  # 변경된 내용 저장

        else:
            new_user = User(kakao_id=kakao_id, name=name, profile_image=profile_image)
            db.session.add(new_user)
            db.session.commit()
            session.clear()
            session['user_id'] = new_user.id

        # 사용자 정보를 json으로 반환
        return jsonify({
            'message': 'User logged in successfully',
            'user': {
                'id': kakao_id,
                'name': name,
                'profile_image': profile_image
            }
        })
    
    def post(self):
        print(session.get('user_id'))

        session.clear()  # 세션에 저장된 데이터 삭제
        return {
            'message': 'User logged out successfully',
        }  # 로그아웃 후 로그인 페이지로 리디렉션