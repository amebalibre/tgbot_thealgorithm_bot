#!/usr/bin/env python3
import re
import requests
import yaml
import logging
import logging.config

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

from utils import Utils
from utils import Settings

utils = Utils()

# Load logger config
with open(Settings.LOGGING_PATH, 'r') as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))
logger = logging.getLogger(__name__)


updater = Updater(token=Settings.TOKEN)
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
        raw = update.message.text.replace('/get', '')
        url = '%s?%s' % (Settings.KEYFORGE_API, '&'.join(utils.verbalize_params(raw)))
        logger.debug('Summoning backing-service: %s' % (url))
        r = requests.get(url)
        if(r.status_code == 200):
            values = r.json().values()
            if(values and len(values) < 2):
                messages = [record.get('url') for record in values]
            else:
                cards = ', '.join([u.get('name') for u in values])
                messages = ['There are many cards, try to be more specific: %s' % cards]
        else:
            msg = r.json().get('message')
            if(isinstance(msg, str)):
                messages = [msg]
            else:
                messages = [', '.join([k + ': ' + v for k, v in msg.items()])]

    except(Exception) as e:
        logger.warning(e)
    finally:
        log(update)
        logger.debug('Data obtained: %s' % (messages))
        for message in messages:
            bot.send_message(
                chat_id=update.message.chat_id,
                text=message,
            )


def random(bot, update, args):
    """Gets a random card."""
    r = requests.get('%s/random/' % Settings.KEYFORGE_API)
    if(r.status_code == 200):
        messages = [record.get('url') for record in r.json().values()]
    else:
        messages = [r.json().get('message')]

    log(update)
    logger.debug('Random obtained: %s' % (messages))
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
random_handler = CommandHandler('random', help)
help_handler = CommandHandler('help', help, pass_args=True)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(get_handler)
dispatcher.add_handler(random_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
