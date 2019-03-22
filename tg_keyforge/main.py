#!/usr/bin/env python3
import os
import re
import requests
from pathlib import Path
import yaml
import logging
import logging.config
import random
from dotenv import load_dotenv, find_dotenv

from telegram import (
    ParseMode,
    # InlineQueryResultArticle,
    # InputTextMessageContent
)
from telegram.ext import (
    Updater,
    CommandHandler,
    # InlineQueryHandler,
    MessageHandler,
    Filters,
    # RegexHandler,
    # ConversationHandler
)

quyznaro_respuestas = [
    'Contigo no me hablo',
    'Fulgencio, que te calles',
    'Que meh eres',
    'Ves con a contarselo a Chewaka',
    'Eso es mentira',
    'pene e.e',
    'Que te caies caion',
    'Ays, que risa me doy',
    'Quiero comino',
    'Vete a currar, que estas siempre igual',
    'Illo ke me dehe ya',
    'Esternocleidomastoideo',
]

# Load .env
load_dotenv(dotenv_path=Path('.') / '.secret')
load_dotenv(find_dotenv())

# Load logger config
with open(os.getenv('logging'), 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)


NAY = 14573680
FILTERS = ('l.', 'n.', 'h.', 't.', 's.', 'i.', 'r.', 'e.')
WEB_FILTERS = ('lang', 'name', 'house', 'type', 'subtype', 'id', 'rarity', 'expansion')


updater = Updater(token=os.getenv('token'))
dispatcher = updater.dispatcher


def log(update):
    # XXX Log all commands execute by user!
    alias = update.message.from_user.username and \
        ' (@' + update.message.from_user.username + ')' or ''
    logger.info('{name}{alias} runs: "{command}"'.format(
        name=update.message.from_user.first_name,
        alias=alias,
        command=update.message.text,
    ))


def get(bot, update, args):
    """Get a card."""
    messages = []
    try:
        # FIXME remove this
        uname = update.message.from_user.username
        if(uname and uname.upper() == 'Quyznaro'.upper()):
            messages.append(random.choices(quyznaro_respuestas))

        else:
            raw = update.message.text.replace('/get', '')
            params = []
            for m in re.findall(os.getenv('pattern_filter'), raw):
                key = WEB_FILTERS[FILTERS.index(m[1:3])]
                value = m[3:]
                params.append('%s=%s' % (key, value))
            url = '%s?%s' % (os.getenv('keyforge_api'), '&'.join(params))

            r = requests.get(url)
            if(r.status_code == 200):
                values = r.json().values()
                if(values and len(values) < 5):
                    messages = [record.get('url') for record in values]
                else:
                    messages = ['/get n.%s' % (u.get('name')) for u in values][:5]
                    messages.insert(0, 'There are many cards, try to be more specific')
            else:
                msg = r.json().get('message')
                messages = [', '.join([k + ': ' + v for k, v in msg.items()])]

    except(Exception) as e:
        logger.warning(e)
    finally:
        log(update)
        logger.debug('Redirect to backing-service: %s' % (url))
        logger.debug('Data obtained: %s' % (messages))
        for message in messages:
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
            )


def help(bot, update, args):
    """Presents all options from .commands.src to use."""
    text = """\
Hi {human}! I heard you need help.
I only respond commands. I give you examples!

```
/get n.anger
/get h.brobnar
/get t.artifact
/get s.giant.goblin
/get i.002
/get r.c
/get e.call of the archons
/get n.brobnar t.artifact s.location
```

My grace be with you, human.
""".format(human=update.message.from_user.first_name)
    log(update)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='{}'.format(text),
        parse_mode=ParseMode.MARKDOWN
    )


def unknown(bot, update):
    """Show standard message for all unrecognized commands."""
    log(update)
    bot.send_message(
        chat_id=update.message.chat_id,
        text="Ignorant human... You are talking to the algorithm! Respect!!")


get_handler = CommandHandler('get', get, pass_args=True)
help_handler = CommandHandler('help', help, pass_args=True)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(get_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
