#!/usr/bin/env python3
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

import utils
from settings import Settings


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


def card(bot, update, args):
    lang = update.message.from_user.language_code
    if(lang not in ('es', 'en', 'fr', 'it', 'de')):
        lang = 'en'
    logger.debug('lang of user: %s' % lang)
    reply_to = update.message.chat_id
    multi = False
    messages = []
    raw = update.message.text.replace('/get ', '')
    url = utils.formalize_request(Settings.KEYFORGE_API, lang, raw)
    logger.debug('Summoning backing-service: %s' % (url))
    try:
        r = requests.get(url)
        logger.debug('request: %s' % r.status_code)
        if(r.status_code == 200):
            values = r.json().values()
            logger.debug('Obtains from backing-service: %s' % values)
            if(values and len(values) < 2):
                messages = [record.get('url') for record in values]
            else:
                reply_to = update.message.from_user.id
                multi = True
                for record in values:
                    messages.append('`{id}`: `{name}` [{type}]'.format(
                        id=record.get('id') or '<None>',
                        name=record.get('name') or '<None>',
                        type=record.get('type') or '<None>'
                    ))

                messages = ['\n'.join(messages)]
                logger.debug('Message: %s' % messages)
        else:
            messages = [r.json().get('message')]

        for message in messages:
            if(multi):
                bot.send_message(
                    chat_id=reply_to,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                bot.send_message(
                    chat_id=reply_to,
                    text=message,
                )
    except(Exception) as e:
        bot.send_message(
            chat_id=update.message.chat_id,
            text='ERROR! %s' % e,
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


card_handler = CommandHandler('get', card, pass_args=True)
random_handler = CommandHandler('random', help)
help_handler = CommandHandler('help', help, pass_args=True)
unknown_handler = MessageHandler(Filters.command, unknown)

dispatcher.add_handler(card_handler)
dispatcher.add_handler(random_handler)
dispatcher.add_handler(help_handler)

updater.start_polling()
