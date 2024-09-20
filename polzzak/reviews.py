from flask import Flask, request, session
from flask_restx import Resource, fields, reqparse, Namespace
from . import db
from .models import Review

Review_ns = Namespace(name="review",description="플로깅 후기 작성을 위한 API")

reviewForm = reqparse.RequestParser()
reviewForm.add_argument('user_id', type=int, default=None, help='user id')
reviewForm.add_argument('id', type=int, default=None, help='review id')

review_create_fields = Review_ns.model('review_create', {
    'title': fields.String,
    'content': fields.String,
    'place_id' : fields.Integer
}) #리뷰 생성 필드

review_modify_fields = Review_ns.model('review_modify', {
    'id' : fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'place_id' : fields.Integer
}) #리뷰 수정 필드

review_delete_fields = Review_ns.model('review_delete', {
    'id' : fields.Integer
}) #리뷰 삭제 필드


@Review_ns.route('/')
class Reviews(Resource):
    @Review_ns.expect(reviewForm)
    def get(self):
        user_id = int(request.args.get('user_id'))
        id = request.args.get('id')
        review = Review.query.get_or_404(id)

        if user_id == session.get('user_id'):
            return {
                'message' : 'can modfiy and delete',
                'review' : {
                    'id' : review.id,
                    'title' : review.title,
                    'content' : review.content,
                    'user_id' : review.user_id,
                    'place_id' : review.place_id
                }
            }, 200
        else:
            return {
                'message' : 'cannot modfiy and delete',
                'review' : {
                    'id' : review.id,
                    'title' : review.title,
                    'content' : review.content,
                    'user_id' : review.user_id,
                    'place_id' : review.place_id
                }
            }, 200
        
    @Review_ns.expect(review_create_fields)
    def post(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        title = request.json.get('title')
        content = request.json.get('content')
        place_id = request.json.get('place_id')
        new_review = Review(title=title, content=content, user_id=user_id, place_id=place_id)
        db.session.add(new_review)
        db.session.commit()

        return {'message': 'Review posted successfully',
                'review':{
                    'title' : title,
                    'content' : content,
                    'user_id' : user_id,
                    'place_id' : place_id
                }}, 200
    
    @Review_ns.expect(review_modify_fields)
    def put(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        id = request.json.get('id')
        title = request.json.get('title')
        content = request.json.get('content')
        place_id = request.json.get('place_id')

        review = Review.query.filter(Review.id==id).first()

        if not review:
            return {'message' : 'review number <{}> does not exist!'.format(id)}, 404
        else:
            review.title = title
            review.content = content
            review.place_id = place_id
            db.session.commit()
            return {'message' : 'Review modified successfully'}, 200

    @Review_ns.expect(review_delete_fields)
    def delete(self):
        user_id = session.get('user_id')
        if user_id == None:
            return {'islogin' : False}
        
        id = request.json.get('id')
        review = Review.query.get_or_404(id)
        db.session.delete(review)
        db.session.commit()

        return {'message' : 'Review deleted successfully'}, 200