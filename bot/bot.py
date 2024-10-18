from aiogram.methods import DeleteWebhook

from .handlers import starting, other, write_journal, read_journal, edit_feeling
from .init_bot import *

logger = logging.getLogger(__name__)


async def start_():
    dp.include_router(starting.router)
    dp.include_router(other.router)
    dp.include_router(write_journal.router)
    dp.include_router(read_journal.router)
    dp.include_router(edit_feeling.router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)
