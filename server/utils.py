# -*- coding: utf-8 -*-
import csv
from settings import Settings
from collections import namedtuple


class Utils():
    def add_filters(self, arg, args, query):
        """Add new filter into query and return it.

        :param arg: The argument to add in query filter
        :param args: List of arguments. arg is finded in this list.
        :param query: sqlalchemy query.
        :return: query
        """
        if(args.get(arg)):
            criteria = {arg: args.get(arg)}
            return query.filter_by(**criteria)
        return query

    def change_lang(self, url, lang):
        """Change language on url.

        :param url:
        :param lang:
        :return: url changed.
        """
        if(lang):
            if(lang not in Settings.SUPPORTED_LANG):
                raise ValueError

            card_front = 'card_front/%s/'
            png = '_%s.png'
            return url. \
                replace(card_front % 'en', card_front % lang). \
                replace(png % 'en', png % lang)
        else:
            return url

    def dictify(self, cards, lang):
        """Parse all cards to dictset.

        :param cards: recordset of cards.
        :param lang: language.
        :return: dict of cards
        """
        payload = {}
        for card in cards:
            payload[card.id] = dict(
                id=card.kf,
                name=card.name.title(),
                expansion=card.expansion.title(),
                house=card.house.title(),
                type=card.type.title(),
                subtypes=[subtype.name.title() for subtype in card.subtypes],
                rarity=card.rarity.title(),
                url=self.change_lang(card.url, lang),
            )
        return payload

    def master_data(self, *models):
        data = []
        File = namedtuple('Point', ['model', 'path'])
        files = [
            File(model, '%s/%s.csv' % (Settings.DATABASE_PATH, model.__tablename__))
            for model in models
        ]
        for file in files:
            with open(file.path, newline='') as csvfile:
                reader = csv.reader(
                    csvfile,
                    delimiter=Settings.CSV_DELIMITER,
                    quotechar=Settings.CSV_QUOTECHAR)
                keys = None
                for row in reader:
                    if(not keys):
                        keys = row
                    else:
                        payload = file.model(**dict(zip(keys, row)))
                        data.append(payload)
        return data

    def rel_models(self, ):
        data = []
        subtype_path = '%s/%s.csv' % (Settings.DATABASE_PATH, 'card_subtype_rel')
        with open(subtype_path, newline='') as csvfile:
            reader = csv.reader(
                csvfile,
                delimiter=Settings.CSV_DELIMITER,
                quotechar=Settings.CSV_QUOTECHAR)
            keys = None
            for row in reader:
                if(not keys):
                    keys = row
                else:
                    payload = dict(zip(keys, row))
                    data.append(payload)
        return data
