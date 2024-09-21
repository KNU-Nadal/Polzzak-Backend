from flask import Flask
from flask_restx import Resource, reqparse, Namespace
from .models import Review
from .models import User, Review, Place, Image

ReviewList_ns = Namespace(name='reviewlist', description='Reviewlist 반환을 위한 API') 

@ReviewList_ns.route('/')
class NotepadList(Resource):
    def get(self):
        review_list = Review.query.all()
        reviews = []

        for review in review_list:
            user = User.query.get(review.user_id)
            place = Place.query.get(review.place_id)
            image = Image.query.get(review.image_id)

            tmp = {'id' : review.id,
                   'title' : review.title,
                   'content' : review.content,
                   'user_name' : user.name,
                   'address' : place.address,
                   'place_name' : place.name,
                   'lat' : place.lat,
                   'lng' : place.lng,
                   'image_name' : image.name}
            reviews.append(tmp)

        return {'review': reviews}
