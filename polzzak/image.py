from flask import request, jsonify
import requests  # 이미지 서버와의 통신을 위해 필요
from flask_restx import Namespace, Resource
from .models import Image  # Image 모델 가져오기
from .database import db  # 데이터베이스 사용
from werkzeug.datastructures import FileStorage 

# 이미지 서버 URL 설정
IMAGE_SERVER_UPLOAD_URL = 'http://localhost:5001/upload'
Image_ns = Namespace(name="image",description="이미지 업로드를 위한 API")

file_upload_parser = Image_ns.parser()
file_upload_parser.add_argument('file', location='files', type=FileStorage, required=True, help='Upload image file')

# 이미지 업로드 API (프론트엔드에서 이미지를 받아 이미지 서버로 전송)
@Image_ns.route('/upload')
class UploadImage(Resource):
    @Image_ns.expect(file_upload_parser)
    def post(self):
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        try:
            # 이미지 서버로 파일 전송
            files = {'file': (file.filename, file, file.content_type)}
            response = requests.post(IMAGE_SERVER_UPLOAD_URL, files=files)
            print(response)
            print("Sending request to:", IMAGE_SERVER_UPLOAD_URL)
            print("File info:", {'file': (file.filename, file, file.content_type)})
            print("Response received:", response.status_code, response.json())
            response.raise_for_status()  # 서버 오류가 있을 경우 예외 발생

            # 응답을 JSON으로 변환하고 파일 이름 추출
            response_data = response.json()
            image_name = response_data['file_name']
            print(image_name)
            # 새 이미지 레코드 생성 및 데이터베이스 저장
            #new_image = Image(imgname=image_name)
            print("error_point")
            new_image = Image(imgname=image_name)
            print(new_image.imgname)
            db.session.add(new_image)
            db.session.commit()
            print(new_image.id)
            return {'message': "Image uploaded successfully", "image_id": new_image.id}, 200
        except requests.exceptions.RequestException as e:
            return jsonify({'error': 'Image server communication failed', 'exception': str(e)}), 500
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'exception': str(e)}), 500


