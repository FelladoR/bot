from discord.ext import commands
import discord
import random
from pymongo import MongoClient

cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collusers = db['collusers'] 
clans_collection = db["clans"]
collservers = db['collservers']

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.exp_per_level = {
            1: 100,
            2: 200,
            3: 400,
            4: 800,
            5: 1600,
            6: 3200,
            7: 6400,
            8: 12800,
            9: 25600,
            10: 51200,
            11: 102400,
            12: 204800,
            13: 409600,
            # Додайте більше рівнів, якщо потрібно
        }
        self.role_rewards = {
            3: "1163091449500405850",
            5: "1155553607194775583",
            8: "1155553677554241550",
            10: "1155553705152753694",
            15: "1155553743140552784"
            # Додайте більше ролей для інших рівнів, якщо потрібно
        }

    async def add_experience(self, user_id, exp):
        try:
            user_data = collusers.find_one({"_id": user_id})
            if user_data is None:
                # Користувача не існує, створюємо новий запис
                user_data = {"_id": user_id, "experience": exp, "level": 1}
                collusers.insert_one(user_data)
            else:
                # Перевіряємо, чи існує ключ "experience" в об'єкті користувача
                if "experience" not in user_data:
                    user_data["experience"] = 0  # Якщо відсутній, встановлюємо початкове значення
                if "level" not in user_data:
                    user_data["level"] = 0  # Якщо відсутній, встановлюємо початкове значення
                user_data["experience"] += exp
                while user_data["experience"] >= self.exp_per_level.get(user_data["level"], 100):
                    user_data["level"] += 1
                    user_data["experience"] -= self.exp_per_level[user_data["level"]]
                    await self.send_level_up_message(user_id, user_data["level"])
                    await self.check_role_rewards(user_id, user_data["level"])
                collusers.update_one({"_id": user_id}, {"$set": user_data})
        except Exception as e:
            print(f'Помилка при рівнях: {e}')
            return







    async def send_level_up_message(self, user_id, level):
        try:
            user = await self.bot.fetch_user(user_id)
            channel_id = 1154395654945251398
            channel = self.bot.get_channel(channel_id)
            if user and channel:
                embed = discord.Embed(
                    title='Вітаємо!',
                    description=f'Вітаємо учасника <@{user_id}>! Він тепер отримав рівень **{level}**',
                    color=0xcbbbf4
                )
                embed.set_thumbnail(url=user.avatar.url)
                await channel.send(embed=embed)
        except Exception as e:
            print(f'Помилка відправки: {e}')


    async def check_role_rewards(self, user_id, level):
        role = self.role_rewards.get(level)
        if role:
            guild = self.bot.get_guild(1154369014181671014)
            member = guild.get_member(user_id)
            if member:
                if discord.utils.get(member.roles, id=int(role)) is None:  # Змінено на ідентифікатор ролі
                    role_object = discord.utils.get(guild.roles, id=int(role))
                    await member.add_roles(role_object)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:

            if not message.author.bot:
                if message.channel.id == 1154395654945251398:
                    return
                user_id = message.author.id
                exp_gained = random.randint(1, 6)
                await self.add_experience(user_id, exp_gained)
        except Exception as e:
            print(f'Помилка при рівнях2: {e}')
            return


    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_data = collusers.find_one({"_id": member.id})
        if user_data:
            level = user_data.get('level', 1)
            experience = max(user_data.get('experience', 0), 0)
            next_level_exp = self.exp_per_level.get(level + 1, None)
            if next_level_exp is not None:
                exp_needed = max(next_level_exp - experience, 0)
                embed = discord.Embed(
                    title=f'Рівень користувача {member}',
                    description=f'Рівень: **{level}**\nДо отримання наступного рівня потрібно: **{exp_needed}exp**',
                    color=0xcbbbf4
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{member.display_name} має рівень {level} з {experience} exp. Досягнуто максимальний рівень..")
        else:
            await ctx.send("Користувача не знайдено.")

async def setup(bot):
    level_cog = Level(bot)
    await bot.add_cog(level_cog)
