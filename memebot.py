import os
from typing import Any
from telegram import (
    Update,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from custom_exceptions import MemeException
from memes import Meme
import memes


TOKEN = os.getenv('BOT_TOKEN')


async def get_statistics(update: Update, _: CallbackContext) -> None:
    file_name = 'stats.csv'
    memes.get_db_stats(file_name)
    await update.effective_chat.send_document(document=open(file_name, 'rb'))


async def add_text(update: Update, _: CallbackContext) -> None:
    msg = update.message
    text_info = await _prep_info_for_db(msg, meme_type='text')
    added_meme = await _add_meme(text_info)
    await _reply_on_added_meme(msg, added_meme)


async def add_photo(update: Update, _: CallbackContext) -> None:
    msg = update.message
    photo_info = await _prep_info_for_db(msg, meme_type='photo')
    added_meme = await _add_meme(photo_info)
    await _reply_on_added_meme(msg, added_meme)


async def add_video(update: Update, _: CallbackContext) -> None:
    msg = update.message
    video_info = await _prep_info_for_db(msg, meme_type='video')
    added_meme = await _add_meme(video_info)
    await _reply_on_added_meme(msg, added_meme)


async def add_animation(update: Update, _: CallbackContext) -> None:
    msg = update.message
    animation_info = await _prep_info_for_db(msg, meme_type='animation')
    added_meme = await _add_meme(animation_info)
    await _reply_on_added_meme(msg, added_meme)


async def add_voice(update: Update, _: CallbackContext) -> None:
    msg = update.message
    voice_info = await _prep_info_for_db(msg, meme_type='voice')
    added_meme = await _add_meme(voice_info)
    await _reply_on_added_meme(msg, added_meme)


async def add_video_note(update: Update, _: CallbackContext) -> None:
    msg = update.message
    video_note_info = await _prep_info_for_db(msg, meme_type='video_note')
    added_meme = await _add_meme(video_note_info)
    await _reply_on_added_meme(msg, added_meme)


async def delete_meme_button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    msg_text, user_id = query.data.split('|')
    try:
        ans_msg = await _delete_meme(msg_text, int(user_id))
    except MemeException as e:
        ans_msg = str(e)
    # deletes pressed button from markup
    keyboard = query.message.reply_markup.inline_keyboard
    keyboard = [row for row in keyboard if row[0].callback_data != query.data]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f'{query.message.text}\n{ans_msg}', reply_markup=markup)


async def length_button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    ans_msg = await _len_meme_que()
    await query.answer(text=ans_msg)


async def send_next_meme(update: Update, _: CallbackContext) -> None:
    chat = update.effective_chat
    try:
        meme = memes.get_next_meme()
    except MemeException as e:
        await chat.send_message(str(e))
        return
    send_meme = None
    match meme.meme_type:
        case 'photo':
            send_meme = chat.send_photo
        case 'video':
            send_meme = chat.send_video
        case 'voice':
            send_meme = chat.send_voice
        case 'animation':
            send_meme = chat.send_animation
        case 'video_note':
            await chat.send_video_note(meme.file_id)
            return
        case 'text':
            await chat.send_message(meme.comment)
            return
    await send_meme(meme.file_id, caption=meme.comment)


async def len_meme_que(update: Update, _: CallbackContext) -> None:
    ans_msg = await _len_meme_que()
    await update.message.reply_text(ans_msg)


async def delete_meme(update: Update, _: CallbackContext) -> None:
    msg = update.message
    ans_msg = await _delete_meme(msg.text, msg.from_user.id)
    await msg.reply_text(ans_msg, reply_to_message_id=msg.message_id)


async def _prep_info_for_db(msg: Message, meme_type: str) -> dict[str, Any]:
    msg_info = getattr(msg, meme_type)
    if meme_type == 'text':
        info = {
            'comment': msg_info.removeprefix('/text_meme').lstrip(' \n'),
            'file_id': None,
            'file_unique_id': None,
            'file_size': len(msg.text.encode("utf8"))
        }
    else:
        if meme_type == 'photo':
            msg_info = msg_info[-1]
        info = msg_info.to_dict()
        info['comment'] = msg.caption

    info.update({'user_id': msg.from_user.id,
                 'meme_type': meme_type})
    return info


async def _get_ans_msg(added_meme: Meme | MemeException) -> tuple[str, InlineKeyboardMarkup | None]:
    if isinstance(added_meme, Meme):
        is_comment = 'С указанным текстом.\n' if added_meme.comment else ''
        ans_text = (f'Добавил {added_meme.meme_type} в очередь и сборник.\n'
                    f'{is_comment}\n')
        keyboard = [
            [InlineKeyboardButton("Удалить из очереди",
                                  callback_data=f'/delfromque_{added_meme.id} | {added_meme.user_id}')],
            [InlineKeyboardButton("Удалить из сборника",
                                  callback_data=f'/delfromdb_{added_meme.id} | {added_meme.user_id}')],
            [InlineKeyboardButton("Мемов в очереди",
                                  callback_data='/length')]
        ]
        ans_buttons = InlineKeyboardMarkup(keyboard)
        return ans_text, ans_buttons
    else:
        ans_text = str(added_meme)
        return ans_text, None


async def _add_meme(meme_info: dict[str, Any]) -> Meme | MemeException:
    try:
        meme: Meme = memes.add_meme(meme_info)
        return meme
    except MemeException as e:
        return e


async def _reply_on_added_meme(msg, added_meme: Meme | MemeException):
    text, markup = await _get_ans_msg(added_meme)
    return await msg.reply_text(text, reply_markup=markup, reply_to_message_id=msg.message_id)


async def _len_meme_que() -> str:
    try:
        ans_msg = memes.length()
    except MemeException:
        ans_msg = 0
    return str(ans_msg)


async def _delete_meme(msg_text: str, user_id: int) -> str:
    try:
        if msg_text.startswith('/delfromdb_'):
            ans_msg = memes.delete_meme_from_db(int(msg_text.removeprefix('/delfromdb_')), user_id)
        else:
            ans_msg = memes.delete_meme_from_que(int(msg_text.removeprefix('/delfromque_')), user_id)
    except MemeException as e:
        ans_msg = e
    return str(ans_msg)


def main() -> None:
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("stats", get_statistics))
    app.add_handler(CommandHandler("length", len_meme_que))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, add_photo))
    app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, add_video))
    app.add_handler(MessageHandler(filters.VOICE & filters.ChatType.PRIVATE, add_voice))
    app.add_handler(MessageHandler(filters.ANIMATION & filters.ChatType.PRIVATE, add_animation))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE & filters.ChatType.PRIVATE, add_video_note))
    app.add_handler(MessageHandler(filters.Regex(r'^/text_meme ?\n.+') & filters.ChatType.PRIVATE, add_text))
    app.add_handler(MessageHandler(filters.Regex(r'^/delfrom(db|que)_\d+$') & filters.ChatType.PRIVATE, delete_meme))
    app.add_handler(MessageHandler(filters.Regex(r'^[мМ]ем$'), send_next_meme))
    app.add_handler(CallbackQueryHandler(length_button, pattern='/length'))
    app.add_handler(CallbackQueryHandler(delete_meme_button, pattern=r'^/delfrom(db|que)_\d+ | '))

    app.run_polling()


if __name__ == "__main__":
    main()
