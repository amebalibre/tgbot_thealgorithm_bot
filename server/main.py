# -*- coding: utf-8 -*-
import logging
import logging.config
import random
import yaml
from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource

from utils import Utils
from utils import Settings


# Load app, api and orm
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = Settings.DATABASE_URI
db = SQLAlchemy(app)

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
    model = 'card'
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
    model = 'house'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        return '<House %r>' % self.name


class Rarity(db.Model):
    model = 'rarity'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), nullable=False)
    description = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Rarity %r>' % self.description


class Subtype(db.Model):
    model = 'subtype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Subtype %r>' % self.name


class Type(db.Model):
    model = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.name


# API
class KeyForge(Resource):
    def __init__(self):

        # Populate all CHOICES_
        CHOICES_HOUSE = CHOICES_RARITY = CHOICES_TYPE = CHOICES_SUBTYPE = []
        try:
            CHOICES_HOUSE = [record.name for record in House.query.all()]
            CHOICES_RARITY = [record.name for record in Rarity.query.all()]
            CHOICES_SUBTYPE = [record.name for record in Subtype.query.all()]
            CHOICES_TYPE = [record.name for record in Type.query.all()]
        except Exception:
            pass

        # Expected params for API
        defaults = dict(type=str, case_sensitive=False, trim=True)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', **defaults)  # going to kf
        self.parser.add_argument('name', **defaults)
        self.parser.add_argument('expansion', **defaults)
        self.parser.add_argument('house', choices=CHOICES_HOUSE, **defaults)
        self.parser.add_argument(
            'subtype', action='append', choices=CHOICES_SUBTYPE, **defaults)
        self.parser.add_argument('type', choices=CHOICES_TYPE, **defaults)
        self.parser.add_argument('rarity', choices=CHOICES_RARITY, **defaults)

    def get(self, lang='en'):
        args = self.parser.parse_args(strict=True)
        if(not any([value for value in args.values() if value])):
            cards = Card.query.order_by(Card.id.desc()).limit(Settings.QUERY_LIMIT)

        else:
            logger.info('Finding on the library... [CRITERIA: %s]' % args)
            query = Card.query
            if(args.get('name')):
                query = query.filter(Card.name.like(args.get('name')))
            if(args.get('id')):
                query = query.filter_by(kf=args.get('id'))
            for field in ['expansion', 'house', 'type', 'rarity']:
                query = utils.add_filters(field, args, query)
            if(args.get('subtype')):
                # TODO: .any no me vale. quiero .all pero no existe. investigar
                query = query.filter(
                    Card.subtypes.any(Subtype.name.in_(args.get('subtype'))))

            cards = query.order_by(Card.id.desc()).limit(Settings.QUERY_LIMIT)
            if(not cards):
                abort(400, message='No card was found!')
            logger.info('%s was found!' % cards)

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
api.add_resource(KeyForge, '/', '/<lang>/')
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
