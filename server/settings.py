# -*- coding: utf-8 -*-
from decouple import config
from decouple import Csv


class Settings:
    DEBUG = config('DEBUG', default=False, cast=bool)
    LOGGING_PATH = config('LOGGING_PATH')

    CSV_DELIMITER = config('CSV_DELIMITER', default='|')
    CSV_QUOTECHAR = config('CSV_QUOTECHAR', default="'")

    DATABASE_PATH = config('DATABASE_PATH')
    DATABASE_URI = config('DATABASE_URI')

    QUERY_LIMIT = config('QUERY_LIMIT', default=5, cast=int)
    SUPPORTED_LANG = \
        config('SUPPORTED_LANG', default=('en'), cast=Csv(post_process=tuple))
