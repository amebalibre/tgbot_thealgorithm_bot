# -*- coding: utf-8 -*-
import logging
import logging.config
import random
import yaml

from flask import Flask
from flask import jsonify
from flask_msearch import Search
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy

from utils import Utils
from settings import Settings


# Load app, api and orm
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = Settings.DATABASE_URI
db = SQLAlchemy(app)
search = Search()
search.init_app(app)

utils = Utils()

with open(Settings.LOGGING_PATH, 'r') as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))
logger = logging.getLogger(__name__)

# Models
subtypes = db.Table(
    'subtypes',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True),
    db.Column('subtype_id', db.Integer, db.ForeignKey('subtype.id'), primary_key=True)
)


class Card(db.Model):
    __tablename__ = 'card'
    __searchable__ = ['kf', 'expansion', 'name', 'house', 'type', 'rarity']

    id = db.Column(db.Integer, primary_key=True)
    kf = db.Column(db.String(3), nullable=False)
    expansion = db.Column(db.String(80))
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255))
    house = db.Column(db.String(7))
    type = db.Column(db.String(8))
    rarity = db.Column(db.String(1))
    subtypes = db.relationship(
        'Subtype',
        secondary='subtypes',
        lazy='subquery',
        backref=db.backref('cards', lazy=True)
    )

    def __repr__(self):
        return '<Card %r (name: %r, house: %r, type: %r, rarity: %r)>' % (
            self.kf, self.name, self.house, self.type, self.rarity)


class House(db.Model):
    __searchable__ = 'house'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        return '<House %r>' % self.name


class Rarity(db.Model):
    __searchable__ = 'rarity'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), nullable=False)
    description = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Rarity %r>' % self.description


class Subtype(db.Model):
    __searchable__ = 'subtype'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Subtype %r>' % self.name


class Type(db.Model):
    __searchable__ = 'type'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.name


# API
class Service(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('criteria', type=str, case_sensitive=False, trim=True)

    @app.route("/search")
    def get(self, lang='en'):
        criteria = self.parser.parse_args(strict=True).get('criteria')
        cards = Card.query.order_by('kf').msearch(
            criteria,
            fields=['kf', 'expansion', 'name', 'house', 'type', 'rarity'],
            limit=Settings.QUERY_LIMIT)
        if(not cards):
            abort(400, message='No card was found!')

        payload = utils.dictify(cards, lang)
        logger.debug('data was prepared to send')
        return jsonify(payload)


class Random(Resource):

    def get(self, lang='en'):
        query = Card.query
        choice = random.choice(range(query.count()))
        card = query.offset(choice).first()
        payload = utils.dictify([card], lang)
        return jsonify(payload)


# Routers
api.add_resource(Service, '/', '/<lang>/')
api.add_resource(Random, '/random/', '/<lang>/random/')


# Utility
def create_ddbb():
    """Generate database and import initial data from data/*.csv."""
    db.create_all()
    for data in utils.master_data(House, Rarity, Subtype, Type, Card):
        db.session.add(data)
        logger.info('Add on transaction %s' % data)
    db.session.commit()
    logger.info('Commited recordset.')
    for data in utils.rel_models():
        card = Card.query.filter_by(id=data['card_id']).first()
        subtype = Subtype.query.filter_by(id=data['subtype_id']).first()
        if(card and subtype):
            card.subtypes.append(subtype)
            db.session.add(card)
            logger.info('Assigning %s to %s' % (subtype, card))
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=Settings.DEBUG)
