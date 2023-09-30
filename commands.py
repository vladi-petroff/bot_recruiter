from aiogram import Dispatcher, types


async def set_bot_commands(dp: Dispatcher) -> None:
    commands = [
        types.BotCommand(command='start', description='Start the bot'),
        types.BotCommand(command='change', description='Change job description'),
    ]

    await dp.bot.set_my_commands(commands)