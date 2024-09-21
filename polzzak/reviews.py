from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Review, Place, Image
from .places import Places

Review_ns = Namespace(name="review",description="플로깅 후기 작성을 위한 API")

reviewForm = reqparse.RequestParser()
reviewForm.add_argument('id', type=int, default=None, help='review id')

review_create_fields = Review_ns.model('review_create', {
    'title': fields.String(description='Review title'),
    'content': fields.String(description='Review content'),

    'place': fields.Nested(Review_ns.model('Place', {
        'address': fields.String(default='대구광역시 북구 대학로 80'),
        'name': fields.String(default='경북대학교'),
        'lat': fields.Float(default=35.8906),
        'lng': fields.Float(default=128.6121)
    }), description='Place data'),

    'image': fields.Nested(Review_ns.model('Image',{
        'id': fields.Integer,
    }))
})

review_modify_fields = Review_ns.model('review_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,

    'place': fields.Nested(Review_ns.model('Place', {
        'address': fields.String(default='대구광역시 북구 대학로 80'),
        'name': fields.String(default='경북대학교'),
        'lat': fields.Float(default=35.8906),
        'lng': fields.Float(default=128.6121)
    }), description='Place data')
}) #리뷰 수정 필드

review_delete_fields = Review_ns.model('review_delete', {
    'id' : fields.Integer
}) #리뷰 삭제 필드


@Review_ns.route('/')
class Reviews(Resource):
    @Review_ns.expect(reviewForm)
    def get(self):
        id = request.args.get('id')
        review = Review.query.filter_by(id=id).first()
        place = Place.query.get(review.place_id)
        image = Image.query.get(review.image_id)

        review_info = {
            'id' : review.id,
            'title' : review.title,
            'content' : review.content,
            'user_id' : review.user_id,
            'address' : place.address,
            'place_name' : place.name,
            'lat' : place.lat,
            'lng' : place.lng,
            'image_name' : image.name
        }

        if review.user_id == session.get('user_id'):
            return {
                'isown' : True,
                'review' : review_info
            }, 200
        else:
            return {
                'isown' : False,
                'review' : review_info
            }, 200
        
    @Review_ns.expect(review_create_fields)
    def post(self):
        review_data = Review_ns.payload  # 리뷰 데이터 받기
        place_data = review_data['place']  # 장소 정보 추출
        image_data = image_data['image'] # 이미지 정보 추출

        # 장소 POST 함수 호출
        place_post_response = Places().post(place_data=place_data)
        place_id = place_post_response[0]['id']  # 장소 ID 가져오기

        # 리뷰 저장
        new_review = Review(
            title=review_data['title'],
            content=review_data['content'],
            user_id=session.get('user_id'),  # 임시 사용자 ID
            place_id=place_id,  # 방금 생성된 장소 ID
            image_id=image_data['id']  # 임시 장소 ID
        )
        db.session.add(new_review)
        db.session.commit()

        return {'review':{
                    'id': new_review.id
                }}, 201
    
    @Review_ns.expect(review_modify_fields)
    def put(self):
        review_data = Review_ns.payload  # 팀 데이터 받기
        place_data = review_data['place']  # 장소 정보 추출

        review = Review.query.filter_by(id=review_data['id']).first()

        Places().put(id=review.place_id, place_data=place_data) # 장소 수정 함수 
        review.title = review_data['title']
        review.content = review_data['content']

        db.session.commit()
        return {'review':{
                    'id': review.id
                }}, 201

    @Review_ns.expect(review_delete_fields)
    def delete(self):
        id = request.json.get('id')
        review = Review.query.filter_by(id=id).first()
        Places().delete(id=review.place_id)
        
        db.session.delete(review)
        db.session.commit()

        return {'message' : 'Team deleted successfully'}, 200
    