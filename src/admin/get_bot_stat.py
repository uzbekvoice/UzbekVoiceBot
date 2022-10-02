from main import bot, users_db


# Function to get bot statistics
async def get_bot_stat_func(chat_id):
    users_count = users_db.dbsize()
    admin_text = 'Всего пользователей: {}'.format(users_count)

    await bot.send_message(chat_id, admin_text, parse_mode='markdown')


