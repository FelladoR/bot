from discord.ext import commands
import discord
import asyncio
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Union

# Підключення до бази даних MongoDB
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collusers = db['collusers'] 

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Команда ban
    @commands.command(name='ban', help='Блокує користувача на сервері')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, duration: str = None, *, reason='Причина не була вказана'):
        try:
            if duration is not None:
                # Отримання кількості секунд для тривалості бану
                duration_seconds = parse_duration(duration)
                if duration_seconds is None:
                    await ctx.send("Неправильно вказано формат часу. Використовуйте:'1h', '30m' і т.д.")
                    return

                # Бан користувача на вказаний час
                await member.ban(reason=reason)
                await ctx.send(f'{member.mention} був заблокований на {duration}. Причина: {reason}')

                # Збереження даних про тривалість блокування в базі даних
                await save_ban_data(member.id, duration_seconds)

                # Розбан користувача після закінчення тривалості бану
                await asyncio.sleep(duration_seconds)
                await member.unban(reason='Термін сплив')
                await ctx.send(f'{member.mention} був розблокований через {duration}.')

            else:
                # Бан користувача назавжди
                await member.ban(reason=reason)
                await ctx.send(f'{member.mention} був заблокований назавжди. Причина: {reason}')
        except Exception as e:
            print(f'Error banning member: {e}')
            await ctx.send(f'Сталась помилка при видачі блокування. {member.mention}.')

    # Функція для обробки помилок команди ban
    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Ти не маєш права використовувати цю команду")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Учасника не знайдено.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Неправильно вказано аргументи. Вводьте: >ban @user [час] [причина]")
        else:
            await ctx.send(f"An error occurred: {error}")

# Функція для перетворення тривалості в секунди
def parse_duration(duration: str) -> Union[int, None]:
    units = {
        's': 1, 
        'm': 60, 
        'h': 3600, 
        'd': 86400, 
        'w': 604800
    }
    try:
        num = int(duration[:-1])
        unit = duration[-1]
        if unit not in units:
            return None
        return num * units[unit]
    except (ValueError, KeyError):
        return None

# Функція для збереження даних про тривалість блокування в базі даних
async def save_ban_data(user_id: int, ban_duration_seconds: int):
    try:
        # Отримання поточного часу
        current_time = datetime.now()

        # Розрахунок часу розблокування
        unban_time = current_time + timedelta(seconds=ban_duration_seconds)

        # Збереження даних в базі даних
        ban_data = {"user_id": user_id, "unban_time": unban_time}
        await collusers.update_one({"_id": user_id}, {"$set": ban_data}, upsert=True)
    except Exception as e:
        print(f'Error saving ban data: {e}')


async def check_bans(guild):
    try:
        # Отримання поточного часу
        current_time = datetime.now()

        # Пошук користувачів, у яких закінчився термін покарання
        users_to_unban = collusers.find({"unban_time": {"$lte": current_time}})

        # Зняття блокування з користувачів, у яких закінчився термін покарання
        for user in users_to_unban:
            member = guild.get_member(user["user_id"])  # Отримання об'єкта користувача
            if member:
                await member.unban(reason='Термін сплив')
                print(f'{member} був розблокований.')

    except Exception as e:
        print(f'Error checking bans: {e}')

# Функція для запуску перевірки термінів блокування
async def start_ban_checking(guild):
    while True:
        await check_bans(guild)
        await asyncio.sleep(60)  # Перевіряти кожну хвилину

async def setup(bot, guild):
    await bot.add_cog(Moderation(bot))
    await bot.loop.create_task(start_ban_checking(guild))