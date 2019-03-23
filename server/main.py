# -*- coding: utf-8 -*-
import os
import logging
import logging.config
import yaml
from dotenv import load_dotenv, find_dotenv

from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import reqparse, abort, Api, Resource

# Load .env
load_dotenv(find_dotenv())

# Load logger config
with open(os.getenv('LOGGING'), 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

# Load app, api and orm
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)


# Models
subtypes = db.Table(
    'subtypes',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id'), primary_key=True),
    db.Column('subtype_id', db.Integer, db.ForeignKey('subtype.id'), primary_key=True)
)


class Card(db.Model):
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
        return '<Card %r (house: %r, type: %r, rarity: %r)>' % (
            self.name, self.house, self.type, self.rarity)


class House(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        return '<House %r>' % self.name


class Rarity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1), nullable=False)
    description = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Rarity %r>' % self.description


class Subtype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return '<Subtype %r>' % self.name


class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8), nullable=False)

    def __repr__(self):
        return '<Type %r>' % self.name


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
parser = reqparse.RequestParser()
parser.add_argument('lang', choices=('en', 'es', 'it'), **defaults)
parser.add_argument('id', **defaults)  # going to kf
parser.add_argument('name', **defaults)
parser.add_argument('expansion', **defaults)
parser.add_argument('house', choices=CHOICES_HOUSE, **defaults)
parser.add_argument('subtype', choices=CHOICES_SUBTYPE, action='append', **defaults)
parser.add_argument('type', choices=CHOICES_TYPE, **defaults)
parser.add_argument('rarity', choices=CHOICES_RARITY, **defaults)


# API
class KeyForge(Resource):
    def get(self):
        args = parser.parse_args(strict=True)
        if(not any([v for v in args.values() if v])):
            abort(400, message='You must declare any filter!')

        logger.info('Finding on deck %s' % args)

        query = Card.query
        if(args.get('name')):
            query = query.filter(Card.name.like(args.get('name')))
        if(args.get('id')):
            query = query.filter_by(kf=args.get('id'))
        if(args.get('expansion')):
            query = query.filter_by(expansion=args.get('expansion'))
        if(args.get('house')):
            query = query.filter_by(house=args.get('house'))
        if(args.get('type')):
            query = query.filter_by(type=args.get('type'))
        if(args.get('rarity')):
            query = query.filter_by(rarity=args.get('rarity'))
        if(args.get('subtype')):
            # TODO: .any no me vale. quiero .all pero no existe. investigar
            query = query.filter(
                Card.subtypes.any(Subtype.name.in_(args.get('subtype'))))

        records = query.all()
        logger.info('%s was found!' % records)

        payload = {}
        for record in records:
            url = record.url
            if(args.get('lang')):
                url = url.replace('card_front/en/', 'card_front/%s/' % args.get('lang'))
                url = url.replace('_en.png', '_%s.png' % args.get('lang'))
            payload[record.id] = dict(
                id=record.kf,
                name=record.name.title(),
                expansion=record.expansion.title(),
                house=record.house.title(),
                type=record.type.title(),
                subtypes=[subtype.name.title() for subtype in record.subtypes],
                rarity=record.rarity.title(),
                url=url,

            )
        return jsonify(payload)

    # def delete(self, todo_id):
    #     abort_if_todo_doesnt_exist(todo_id)
    #     del TODOS[todo_id]
    #     return '', 204
    #
    # def put(self, todo_id):
    #     args = parser.parse_args()
    #     task = {'task': args['task']}
    #     TODOS[todo_id] = task
    #     return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
# class TodoList(Resource):
#     def get(self):
#         return TODOS
#
#     def post(self):
#         args = parser.parse_args()
#         todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
#         todo_id = 'todo%i' % todo_id
#         TODOS[todo_id] = {'task': args['task']}
#         return TODOS[todo_id], 201


# Routers
api.add_resource(KeyForge, '/')


# Utility
def create_ddbb():
    """Generate database and import initial data."""
    import csv
    from collections import namedtuple
    File = namedtuple('Point', ['klass', 'path'])
    path = os.getenv('PATH_DATA_DATABASE')
    files = [
        File(House, '%s/%s.csv' % (path, 'house')),
        File(Rarity, '%s/%s.csv' % (path, 'rarity')),
        File(Subtype, '%s/%s.csv' % (path, 'subtype')),
        File(Type, '%s/%s.csv' % (path, 'type')),
        File(Card, '%s/%s.csv' % (path, 'card')),
    ]

    db.create_all()
    logger.info('Tables was created!')
    for file in files:
        with open(file.path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='|', quotechar="'")
            keys = None
            for row in reader:
                if(not keys):
                    keys = row
                else:
                    data = file.klass(**dict(zip(keys, row)))
                    logger.info('Add to tail: %s' % data)
                    db.session.add(data)
        db.session.commit()
        logger.info('commit all data')
        subtype_path = '%s/%s.csv' % (path, 'card_subtype_rel')
        logger.info('Going to populate m2m [cards - subtypes]')
        has_assigned = False
        with open(subtype_path, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='|', quotechar="'")
            keys = None
            for row in reader:
                if(not keys):
                    keys = row
                else:
                    card = Card.query.filter_by(id=row[0]).first()
                    subtype = Subtype.query.filter_by(id=row[1]).first()
                    if(card and subtype):
                        logger.info('Assigning %s to %s' % (subtype, card))
                        card.subtypes.append(subtype)
                        db.session.add(card)
                        has_assigned = True
        db.session.commit()
        if(has_assigned):
            logger.info('commit assignments')


if __name__ == '__main__':
    app.run(debug=True)
