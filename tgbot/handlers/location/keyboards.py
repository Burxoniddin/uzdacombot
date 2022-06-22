from telegram import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.location.static_text import BOOK_LIST, PROG_ADD, PROG_LIST, SEND_LOCATION, BOOKS, VIDEO_ADD, VIDEO_LIST, VIDEOS, PROGS, SEARCH, BOOK_ADD ,BOOK_LIST, PROG_ADD, PROG_LIST, VIDEO_ADD, VIDEO_LIST


def send_location_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=SEND_LOCATION, request_location=True)]],
        resize_keyboard=True
    )
def main_keyboards() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=BOOKS)],
         [KeyboardButton(text=VIDEOS)],
         [KeyboardButton(text=PROGS)],
         [KeyboardButton(text=SEARCH)]
         ],
        resize_keyboard=True
    )
    
def book_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=BOOK_ADD)],
         [KeyboardButton(text=BOOK_LIST)],
         [KeyboardButton(text="Orqaga")]
         ],
        resize_keyboard=True, one_time_keyboard=True
    )

def prog_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=PROG_ADD)],
         [KeyboardButton(text=PROG_LIST)],
         [KeyboardButton(text="Orqaga")]
         ],
        resize_keyboard=True, one_time_keyboard=True
    )
    
def video_keyboard() -> ReplyKeyboardMarkup:
    # resize_keyboard=False will make this button appear on half screen (become very large).
    # Likely, it will increase click conversion but may decrease UX quality.
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=VIDEO_ADD)],
         [KeyboardButton(text=VIDEO_LIST)],
         [KeyboardButton(text="Orqaga")]
         ],
        resize_keyboard=True, one_time_keyboard=True
    )

