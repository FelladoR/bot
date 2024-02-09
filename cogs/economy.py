import discord
from discord.ext import commands
import random
from bot import pymongo, logs, time
from pymongo import MongoClient
# Встановлення з'єднання з базою даних
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collection = db['testcollection'] 


class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='work')
    @commands.cooldown(1, 43200, commands.BucketType.user)
    async def work(self, ctx):
        try:
            # Отримання користувача з бази даних
            user_data = db.collusers.find_one_and_update(
                {"_id": ctx.author.id},
                {"$setOnInsert": {"money": 0}},  # Додати поле, якщо документ не існує
                upsert=True,  # Створювати документ, якщо його немає
                return_document=True  # Повертати оновлений документ
            )

            earned_money = random.randint(5, 20)

            # Оновити баланс користувача
            new_balance = user_data.get("money", 0) + earned_money
            db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_balance}})
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')

            # Використовуйте ctx.author.avatar_url напряму
            avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

            embed = discord.Embed(title="Робота", color=0xF8C471)
            embed.set_thumbnail(url=avatar_url)
            embed.description = f'{ctx.author.mention} успішно попрацював на роботі, та отримав {earned_money}{moneyemoji}'
            await ctx.send(embed=embed)
            channel = self.bot.get_channel(logs)
            current_time = time.time()
            await channel.send(f'``{time.ctime(current_time)} ``💰Учасник {ctx.author.name}(``{ctx.author.id}``) отримав гроші(work) | Старий баланс: **{user_data.get("money", 0)}{moneyemoji}** | Новий баланс: **{new_balance}{moneyemoji}**')
        except Exception as e:
            print(f'Помилка у команді work: {e}')
            return

        
    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням

    @work.error
    async def work_error(self, context, error):
        if isinstance(error, commands.CommandOnCooldown):
            try:
                seconds = error.retry_after
                hours, remainder = divmod(seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                embed = discord.Embed(title=f"❌Не так швидко", color=0xff0000)
                embed.set_thumbnail(url=context.author.avatar.url)
                embed.description = f'{context.author.mention}, перепочинь, ти недавно працював на роботі. Приходи через **{int(hours)}** год. **{int(minutes)}** хвилин.'
                await context.send(embed=embed)
            except Exception as e:
                print(f'Помилка помилки: {e}')
    
class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = {
            '1': {'name': '1.Роль "Транжира"', 'price': 100, 'description': 'Можете придбати цю унікульну роль xD', 'role_id': 1168323046545829969},
            '2': {'name': '2.Предмет 2', 'price': 20, 'description': 'Опис предмета 2'},
            # Додайте інші товари за аналогією
        }

    @commands.command(name='shop')
    async def shop(self, ctx):
        embed = await self.create_shop_embed()
        await ctx.send(embed=embed)

    async def create_shop_embed(self):
        embed = discord.Embed(title='Серверний магазин', color=discord.Color.blue())
        
        for item_id, item_info in self.items.items():
            embed.set_footer('Придбати предмет: -buy (номер)')
            embed.add_field(
                name=f"{item_info['name']} - {item_info['price']} грн",
                value=item_info['description'],
                inline=False
            )

        return embed

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.items = {
            '1': {'name': '1.Роль "Транжира"', 'price': 100, 'description': 'Можете придбати цю унікульну роль xD', 'role_id': 1168323046545829969},
            '2': {'name': '2.Предмет 2', 'price': 20, 'description': 'Опис предмета 2'},
            # Додайте інші товари за аналогією
        }

    @commands.command(name='buy')
    async def buy(self, ctx, item_id):
        try:    
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')
            # Переконайтеся, що self.items доступне у вашому класі
            if item_id not in self.items:
                await ctx.send("Цього товару не існує.")
                return

            item_info = self.items[item_id]
            price = item_info['price']

            # Отримання користувача з бази даних
            user_data = db.collusers.find_one_and_update(
                {"_id": ctx.author.id},
                {"$setOnInsert": {"money": 0}},  # Додати поле, якщо документ не існує
                upsert=True,  # Створювати документ, якщо його немає
                return_document=True  # Повертати оновлений документ
            )

            user_balance = user_data.get("money", 0)

            if user_balance < price:
                embed = discord.Embed(title=f"❌Не так швидко", color=0xff0000)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.description = f'{ctx.author.mention}, у тебе недостатньо грошей на балансі для покупки.'
                await ctx.send(embed=embed)
                return

            # Видалення грошей та додавання товару
            new_balance = user_balance - price
            db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_balance}})

            # Додавання ролі або іншого ефекту від покупки
            # Наприклад, додавання ролі на сервері
            role_id = item_info.get('role_id')
            if role_id:
                role = ctx.guild.get_role(role_id)
                if role:
                    await ctx.author.add_roles(role)

            embed = discord.Embed(title=f"✅Успішно", color=0xa3f046)
            embed.set_thumbnail(url=ctx.author.avatar.url)
            embed.description = f'{ctx.author.mention}, покупка успішна! З вашого балансу було списано **{price}{moneyemoji}**'
            await ctx.send(embed=embed)
            channel = self.bot.get_channel(logs)
            current_time = time.time()
            await channel.send(f'``{time.ctime(current_time)} ``💰Учасник {ctx.author.name}(``{ctx.author.id}``) придбав предмет ({item_info["name"]} | Старий баланс: **{user_data.get("money", 0)}{moneyemoji}** | Новий баланс: **{new_balance}{moneyemoji}**')

        except KeyError:
            await ctx.send("Виникла помилка. Зазначений товар не існує.")
        except pymongo.errors.PyMongoError as e:
            await ctx.send(f"Виникла помилка при взаємодії з базою даних: {e}")


    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням
        

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        try:
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')

            # Знаходження користувачів, які мають ключ "монетки" у базі даних
            users = db.collusers.find({"money": {"$exists": True}}).sort("money", pymongo.DESCENDING).limit(10)
            
            embed = discord.Embed(title=f'Топ 10 користувачів серверу по категорії монетки', color=0x3498db)
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

            for idx, user_data in enumerate(users, start=1):
                user = self.bot.get_user(user_data['_id'])
                money = user_data.get("money", 0)
                embed.add_field(name=f"{idx}. {user.display_name}", value=f"Монетки: **{money}**{moneyemoji}", inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Помилка: {e}")
        except pymongo.errors.PyMongoError as e:
            await ctx.send(f"Сталась помилка при виконанні даної команди")

    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням

class Rob(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 43200, commands.BucketType.user)
    @commands.command(name='rob')
    async def rob(self, ctx, member: discord.Member = None):
        try:
            if member is None:
                embed = discord.Embed(title=f"❌Помилка", color=0xf24835)
                embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
                embed.description = f'{ctx.author.mention}, Ти неправильно використав команду. Правильно: \n``-rob @тег користувача``'
                await ctx.send(embed=embed)
                self.rob.reset_cooldown(ctx)
                return
            # Знаходження користувача в базі даних
            user_data = db.collusers.find_one({"_id": member.id})
            author_data = db.collusers.find_one({"_id": ctx.author.id})
            avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url

            # Визначення кількості грошей для пограбування
            robbed = random.randint(100, 500)

            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')

            # Якщо користувача немає в базі даних, то створити його з балансом 0
            if user_data is None:
                user_data = {"_id": ctx.author.id, "money": 0}
                db.collusers.insert_one(user_data)

            user_balance = user_data.get("money", 0)

            if user_balance <= 500:
                await ctx.send('Неможливо пограбувати данного користувача.')
                return

            new_balance = user_balance - robbed
            new_authorbalance = author_data.get("money", 0) + robbed
            new_authorbalancefailed = author_data.get("money", 0) - robbed
            if random.randint(0, 100) <= 45:
                embed = discord.Embed(title=f"❌Невдача", color=0xf24835)
                embed.set_thumbnail(url=avatar_url)
                embed.description = f'{ctx.author.mention}, тобі не вдалося пограбувати {member.mention}! Натомість, ти втратив **{robbed}**{moneyemoji}!'
                await ctx.send(embed=embed)
                channel = self.bot.get_channel(logs)
                current_time = time.time()
                await channel.send(f'``{time.ctime(current_time)} ``💰Учасник {ctx.author.name}(``{ctx.author.id}``) втратив гроші (rob)| Старий баланс: **{author_data.get("money", 0)}{moneyemoji}** | Новий баланс: **{new_authorbalance}{moneyemoji}**')
                db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_authorbalancefailed}})
                
            else:
                embed = discord.Embed(title=f"✅Успішно", color=0xa3f046)
                embed.set_thumbnail(url=avatar_url)
                embed.description = f'{ctx.author.mention}, ви успішно пограбували {member.mention}. Ви викрали **{robbed}**{moneyemoji}'
                await ctx.send(embed=embed)
                channel = self.bot.get_channel(logs)
                current_time = time.time()
                await channel.send(f'``{time.ctime(current_time)} ``💰Учасник {ctx.author.name}(``{ctx.author.id}``) отримав гроші (rob)| Старий баланс: **{author_data.get("money", 0)}{moneyemoji}** | Новий баланс: **{new_authorbalance}{moneyemoji}**')
                db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_authorbalancefailed}})
                channel = self.bot.get_channel(logs)
                current_time = time.time()
                await channel.send(f'``{time.ctime(current_time)} ``💰Учасник {member.name}(``{member.id}``) втратив гроші (rob)| Старий баланс: **{user_data.get("money", 0)}{moneyemoji}** | Новий баланс: **{new_balance}{moneyemoji}**')
                db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_authorbalancefailed}})
                # Оновлення балансу користувача
                db.collusers.update_one({"_id": member.id}, {"$set": {"money": new_balance}})
                db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_authorbalance}})

        except Exception as e:
            print(f'rob error: {e}')
    @rob.error
    async def work_error(self, context, error):
        if isinstance(error, commands.CommandOnCooldown):
            try:
                seconds = error.retry_after
                hours, remainder = divmod(seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                embed = discord.Embed(title=f"❌Зупинись", color=0xff0000)
                embed.set_thumbnail(url=context.author.avatar.url)
                embed.description = f'{context.author.mention}, грабіжник, заспокійся, ти недавно вже робив пограбування!. Приходи через **{int(hours)}** год. **{int(minutes)}** хвилин.'
                await context.send(embed=embed)
            except Exception as e:
                print(f'Помилка помилки: {e}')

    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням

async def setup(bot):   
    await bot.add_cog(Work(bot))
    await bot.add_cog(Shop(bot))
    await bot.add_cog(Buy(bot))
    await bot.add_cog(Leaderboard(bot))
    await bot.add_cog(Rob(bot))