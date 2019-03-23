from decouple import config
from decouple import Config, RepositoryEnv


class Settings:
    secret = Config(RepositoryEnv('.secret'))
    TOKEN = secret.get('TOKEN')

    PATTERN_FILTER = config('PATTERN_FILTER')
    KEYFORGE_API = config('KEYFORGE_API')
    LOGGING_PATH = config('LOGGING_PATH')
