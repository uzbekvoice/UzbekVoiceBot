from main import bot
from utils.uzbekvoice.db import session, User


# Function to get bot statistics
async def get_bot_stat_func(chat_id):
    users_count = session.query(User).count()
    admin_text = 'Total users count: {}'.format(users_count)
    await bot.send_message(chat_id, admin_text, parse_mode='markdown')


