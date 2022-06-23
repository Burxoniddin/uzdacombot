from calendar import c
import datetime
from xml.dom.minidom import Document

from django.utils import timezone
from telegram import ParseMode, Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import CallbackContext

from tgbot.handlers.onboarding import static_text
# from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User, TestAnswers, Test, TestOption
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
# yangilari
from tgbot.handlers.location import static_text as location_texts
from tgbot.handlers.location.keyboards import main_keyboards, book_keyboard, prog_keyboard, video_keyboard
from tgbot.handlers.utils.files import _get_file_id

from tgbot.models import Files

ADD_NAME, ADD_BOOOK, ADD_PROOG, ADD_VIDEOO = range(4)


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id


def get_buttons(view_page, typee):
    files = Files.objects.filter(type=typee)
    total_number = int(files.count())
    buttons = []
    if (int(total_number/10+1)) == view_page and total_number//10 != 0:
        files = files[view_page*10-10:]
        for file in files:
            button = InlineKeyboardButton(
                str(file.name), callback_data=f"detail-{file.id}")
            buttons.append([button])
        buttons.append([InlineKeyboardButton(
            "Oldingisi", callback_data=f"{view_page-1}")])
    elif (view_page == 1) and total_number != 1:
        files = files[0:10]
        for file in files:
            button = InlineKeyboardButton(
                str(file.name), callback_data=f"detail-{file.id}")
            buttons.append([button])
        buttons.append([InlineKeyboardButton("Keyingisi", callback_data="2")])
    elif (int(total_number/10)) == view_page and total_number//10 == 0:
        files = files[view_page*10-10:]
        for file in files:
            button = InlineKeyboardButton(
                str(file.name), callback_data=f"detail-{file.id}")
            buttons.append([button])
        buttons.append([InlineKeyboardButton(
            "Oldingisi", callback_data=f"{view_page-1}")])
    elif (view_page == 1) and total_number == 1:
        files = files[0:]
        for file in files:
            button = InlineKeyboardButton(
                str(file.name), callback_data=f"detail-{file.id}")
            buttons.append([button])
    else:
        files = files[view_page*10-10:view_page*10+1]
        for file in files:
            button = InlineKeyboardButton(
                str(file.name), callback_data=f"detail-{file.id}")
            buttons.append([button])
        buttons.append([InlineKeyboardButton(
            "Oldingisi", callback_data=f"{view_page-1}"), InlineKeyboardButton("Keyingisi", callback_data=f"{view_page+1}")])
    return buttons


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        context.bot.send_message(
            chat_id=u.user_id,
            text=location_texts.main_text,
            reply_markup=main_keyboards()
        )
    else:
        context.bot.send_message(
            chat_id=u.user_id,
            text=location_texts.main_text,
            reply_markup=main_keyboards()
        )


def cat_books(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text=location_texts.select,
            reply_markup=book_keyboard()
        )


def cat_progs(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text=location_texts.select,
            reply_markup=prog_keyboard()
        )


def cat_videos(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text=location_texts.select,
            reply_markup=video_keyboard()
        )


def add_book(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    context.user_data["status"] = "add_book"

    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text="Qo'shmoqchi bo'lgan kitobingizni nomini kiriting",
        )


def add_prog(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    context.user_data["status"] = "add_prog"

    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text="Qo'shmoqchi bo'lgan dasturingiz nomini kiriting",
        )


def add_video(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    context.user_data["status"] = "add_video"

    if user_id:
        context.bot.send_message(
            chat_id=user_id,
            text="Qo'shmoqchi bo'lgan videodarslik nomini kiriting",
        )


def add_name(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if context.user_data.get("status", None) == "add_book":
        Files.objects.create(name=update.message.text, type="book")
        context.user_data["status"] = "send_book"
        text = "Kiritmoqchi bo'lgan kitobingizni jo'nating"
    elif context.user_data.get("status", None) == "add_prog":
        Files.objects.create(name=update.message.text,  type="prog")
        context.user_data["status"] = "send_prog"
        text = "Kiritmoqchi bo'lgan dasturingizni jo'nating"

    elif context.user_data.get("status", None) == "add_video":
        Files.objects.create(name=update.message.text,  type="video")
        context.user_data["status"] = "send_video"
        text = "Kiritmoqchi bo'lgan videodarslikni jo'nating"

    status = context.user_data.get("status")
    if user_id and status is not None:
        context.bot.send_message(
            chat_id=user_id,
            text=text,
        )


def upload_file(update: Update, context: CallbackContext) -> None:
    update_json = update.to_dict()
    user_id = update.effective_user.id

    if context.user_data.get("status", None) == "send_book":
        file = Files.objects.filter(type="book")[0]
        if file.file_id is None:
            file_id = _get_file_id(update_json["message"])
            file.file_id = file_id
            if "caption" in update_json["message"]:
                file.content = update_json["message"]['caption']
            file.save()

        context.user_data["status"] = "done"
        text = "Kitob muvafaqqiyatli qo'shildi"
        reply_keyboard = [["Bosh Menyu", location_texts.BOOK_LIST]]

    elif context.user_data.get("status", None) == "send_prog":
        file = Files.objects.filter(type="prog")[0]
        if file.file_id is None:
            file_id = _get_file_id(update_json["message"])
            file.file_id = file_id
            if "caption" in update_json["message"]:
                file.content = update_json["message"]['caption']
            file.save()

        context.user_data["status"] = "done"
        text = "Dastur muvafaqqiyatli qo'shildi"
        reply_keyboard = [["Bosh Menyu", location_texts.PROG_LIST]]

    elif context.user_data.get("status", None) == "send_video":
        file = Files.objects.filter(type="video")[0]

        if file.file_id is None:
            file_id = _get_file_id(update_json["message"])
            file.file_id = file_id
            if "caption" in update_json["message"]:
                file.content = update_json["message"]['caption']
            file.save()

        context.user_data["status"] = "done"
        text = "Videodarslik muvafaqqiyatli qo'shildi"
        reply_keyboard = [["Bosh Menyu", location_texts.VIDEO_LIST]]

    status = context.user_data.get("status")
    if user_id and status == "done":
        context.bot.send_message(
            chat_id=user_id,
            text=text,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )


def book_list(update: Update, context: CallbackContext) -> None:
    context.user_data["status"] = "books_list"
    buttons = get_buttons(1, "book")
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(f"Kitobni tanlang: ", reply_markup=reply_markup)


def prog_list(update: Update, context: CallbackContext) -> None:
    context.user_data["status"] = "progs_list"
    buttons = get_buttons(1, "prog")
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(f"Dasturni tanlang: ", reply_markup=reply_markup)


def video_list(update: Update, context: CallbackContext) -> None:
    context.user_data["status"] = "videos_list"
    buttons = get_buttons(1, "video")
    reply_markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(f"Videoni tanlang: ", reply_markup=reply_markup)


def list_view(update: Update, context: CallbackContext) -> None:

    view_page = int(update.callback_query.data)
    if context.user_data.get("status", None) == "videos_list":
        buttons = get_buttons(view_page, "video")
        text = "Videoni tanlang"
    elif context.user_data.get("status", None) == "progs_list":
        buttons = get_buttons(view_page, "prog")
        text = "Dasturni tanlang"

    elif context.user_data.get("status", None) == "books_list":
        buttons = get_buttons(view_page, "book")
        text = "Kitobni tanlang"

    reply_markup_buttons = InlineKeyboardMarkup(buttons)
    context.bot.edit_message_text(
        text=text,
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=reply_markup_buttons
    )


def detail(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_message.chat_id
    data = update.callback_query.data
    file = Files.objects.get(slug=data)

    if file.type == "book":
        context.bot.send_document(
            chat_id=user_id,
            filename=file.name,
            document=file.file_id,
            caption=file.content,
            reply_markup=ReplyKeyboardMarkup(
                [["Bosh Menyu", location_texts.BOOK_LIST]], one_time_keyboard=True, resize_keyboard=True
            )
        )
    elif file.type == "prog":
        context.bot.send_document(
            chat_id=user_id,
            filename=file.name,
            document=file.file_id,
            caption=file.content,
            reply_markup=ReplyKeyboardMarkup(
                [["Bosh Menyu", location_texts.PROG_LIST]], one_time_keyboard=True, resize_keyboard=True
            )
        )
    elif file.type == "video":
        context.bot.send_video(
            chat_id=user_id,
            filename=file.name,
            video=file.file_id,
            caption=file.content,
            reply_markup=ReplyKeyboardMarkup(
                [["Bosh Menyu", location_texts.VIDEO_LIST]], one_time_keyboard=True, resize_keyboard=True
            )
        )


def secret_level(update: Update, context: CallbackContext) -> None:

    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = update.effective_user.id
    text = location_texts.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(
            updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id

# handling Poll answers


def send_pool(update: Update, context: CallbackContext, test_answer):
    user_id = get_chat_id(update, context)

    test = Test.objects.exclude(
        id__in=test_answer.given_tests.all()).order_by("?").last()
    test_answer.given_tests.add(test)
    
    correct_option_id = 0
    index = 0
    answers = []
    for test_option in test.options.all().order_by("?"):
        if test_option.is_correct:
            correct_option_id = index
        index += 1
        answers.append(test_option.title)
    message = context.bot.send_poll(chat_id=user_id, question=f"{test_answer.current_test}|{test_answer.total_test} - {test.title}",
                                    options=answers, type=Poll.QUIZ, correct_option_id=correct_option_id)
    context.bot_data.update({message.poll.id: message.chat.id})

    test_answer.current_test +=1
    test_answer.save()

def cat_quiz(update: Update, context: CallbackContext) -> None:
    user_id = get_chat_id(update, context)
    u, _ = User.get_user_and_created(update, context)

    test_answer = TestAnswers.objects.create(user=u)

    if Test.objects.all().count() < 10:
        test_answer.total_test = Test.objects.all().count()
        test_answer.save()

    send_pool(update, context, test_answer)


def is_answer_correct(update):
    answers = update.poll.options

    ret = False
    counter = 0

    for answer in answers:
        if answer.voter_count == 1 and update.poll.correct_option_id == counter:
            ret = True
            break
        counter = counter + 1

    return ret


def poll_handler(update, context):  # Quiz question
    chat_id = get_chat_id(update, context)
    u = User.objects.get(user_id=chat_id)

    test_answer = TestAnswers.objects.filter(user=u).last()
    if is_answer_correct(update):
        test_answer.correct_answers += 1
        test_answer.save()
    send_pool(update, context, test_answer)
