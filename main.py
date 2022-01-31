import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, \
    InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Dispatcher, InlineQueryHandler, \
    CallbackContext, CallbackQueryHandler
from telegram.update import Update
from typing import Optional

logging.basicConfig(
    format='%(asctime)s - %(name)s -%(levelname)s - %(message)s',
    level=logging.INFO)

updater = Updater(token='2020672175:AAHPf7o1s_2hTA0x7JCjMbQK3wA6f40av-I')

dispatcher: Dispatcher = updater.dispatcher

class Game:
    def __init__(self, context: CallbackContext):
        self._context = context
        self._bot_data = context.bot_data
        self._bot_data.update({
            'games_increment': 1,
        })
        self.game_name = None
        self.game = None

    def get_next_game_id(self):
        _id = self._bot_data['games_increment']
        self._bot_data.update({
            'games_increment': _id + 1
        })
        return _id
    def store_data(self):
        self._bot_data.update({
            self.game_name: self.game
        })

    def new_game(self):
        self.game_name = 'game' + str(self.get_next_game_id())
        self.game_name = {
            'player1': None,
             'player2': None,
             'game': [0, 0, 0, 0, 0, 0, 0, 0, 0],
             'turn': False, # False <- player1 / True <- player2
        }
        self.store_data()

    def get_game(self, name):
        self.game = self._bot_data.get(name, None)

def generate_keyboard(game: Optional[Game]):
    NONE = '🌄'
    CROSS = '❌'
    CIRCLE = '⭕️'

    keyboard = []

    for i in range(3):
        temp_keyboard = []
        for j in range(3):
            index = i * 3 + j
            if game is None:
                item = 0
                callback_data = f'new_game'
            else:
                item = game.game['game'][index]
                callback_data = f'{game.game_name}|{index}'
            text = NONE  if item == 0 else CROSS if item == 1 else CIRCLE
            temp_keyboard.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data
                )
            )
        keyboard.append(temp_keyboard)

    return keyboard

def inline_query(update: Update, context: CallbackContext) -> None:
    keyboard = generate_keyboard(None)
    update.inline_query.answer([
        InlineQueryResultArticle(
            id="x", title='X',
            input_message_content=InputTextMessageContent('X'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
        InlineQueryResultArticle(
            id="o", title='O',
            input_message_content=InputTextMessageContent('O'),
            reply_markup=InlineKeyboardMarkup(keyboard),
        ),
    ])

def callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    game = Game(context)

    if query.data == 'new_game':
        game.new_game()
    else:
        game_name, index = query.data.split('|')
        game.get_game(game_name)

    query.edit_message_text(text=f"Selected option",
                reply_markup=InlineKeyboardMarkup(
                    generate_keyboard(game)))
    # index = int(query.data)
    # game = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # game[index] = 1
    # query.edit_message_text(
    #     text=f"Selected option",
    #     reply_markup=InlineKeyboardMarkup(generate_keyboard(game)))

dispatcher.add_handler(InlineQueryHandler(inline_query))
dispatcher.add_handler(CallbackQueryHandler(callback_query))

updater.start_polling()
updater.idle()