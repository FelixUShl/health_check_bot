import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging
import dotenv

logger = logging.getLogger(__name__)

logger.info('Запущен процесс инициализация бота')
dotenv.load_dotenv('configs/.env')
logger.info('Вычитаны данные из файла .env')
bot = Bot(token=os.getenv('BOT_TOKEN'))
logger.info(f"Подготовка к запуску бота с id {os.getenv('BOT_TOKEN')}")
memory = MemoryStorage()
logger.info('Выделена память под FSM')
dp = Dispatcher(memory=memory)
admin_id = int(os.getenv('TELEGRAM_ID'))
logger.info(f'Пользователь телеграм с ID {admin_id} назначен администратором бота')
