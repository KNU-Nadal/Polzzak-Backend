from . import db
user_team = db.Table(
    'user_team',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key = True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id', ondelete='CASCADE'), primary_key = True)
) #user와 team을 연결하는 테이블

user_event = db.Table(
    'user_event',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key = True),
    db.Column('event_id', db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), primary_key = True)
) #user와 event를 연결하는 테이블

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kakao_id = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)

    def __init__(self, kakao_id, name, profile_image=None):
        self.kakao_id = kakao_id
        self.name = name
        self.profile_image = profile_image

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id', ondelete='CASCADE'), nullable=False)

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(150), nullable=False) #도로명 주소
    name = db.Column(db.String(150), nullable=False) #상세 주소
    lat = db.Column(db.Float, nullable=False) #위도
    lng = db.Column(db.Float, nullable=False) #경도


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    end_time = db.Column(db.DateTime(), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', secondary=user_team, backref=db.backref('user_team_set'), cascade='all')


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    end_time = db.Column(db.DateTime(), nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('place.id', ondelete='CASCADE'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', secondary=user_event, backref=db.backref('user_event_set'), cascade='all')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)