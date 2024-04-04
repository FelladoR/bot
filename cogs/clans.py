import discord
from discord.ext import commands
import random
from bot import pymongo, logs, time
from pymongo import MongoClient
# Встановлення з'єднання з базою даних
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collection = db['testcollection'] 
clans_collection = db["clans"]
collservers = db['collservers']

#class Createclan(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot

#    @commands.command()
#    async def create_clan(self, ctx, clan_name):  # Додайте параметр self
#        try:
#            # Перевірка, чи клан з такою назвою вже існує
#            existing_clan = clans_collection.find_one({"name": clan_name})
#            if existing_clan:
#                await ctx.send("**❌Клан з такою назвою вже існує.**")
#                return
#            max_member_limit = 20

            # Запис даних про новий клан в MongoDB
#            new_clan = {
#                "name": clan_name,
#                "leader_id": ctx.author.id,
#                "members": [ctx.author.id],
#                "moderator1_id": None,  # Початковий лідер також буде модератором
#                "moderator2_id": None,  # Початкове значення для другого модератора
#                "clanbank": 0, # Початкове значення для другого модератора
#                "max_member_limit": max_member_limit
#            }
#            clans_collection.insert_one(new_clan)

#            await ctx.send(f"**✅Клан {clan_name} успішно створено!**")
#        except Exception as e:
#            print(f'Create_clan error: {e}')
#            return

class Clanleaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clanleaderboard', aliases=['clb'])
    async def clanleaderboard(self, ctx):
        try:
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')

            # Знаходження кланів з кланбанком у базі даних та сортування їх за кланбанком
            clans = db.clans.find({"clanbank": {"$exists": True}}).sort("clanbank", pymongo.DESCENDING).limit(10)
            
            embed = discord.Embed(title=f'Топ 10 кланів серверу за банком клану', color=0x3498db)
            #embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)

            for idx, clan_data in enumerate(clans, start=1):
                clan_name = clan_data['name']
                clanbank = clan_data.get("clanbank", 0)
                clan_members = clan_data.get("members") or []  # Перевірка наявності ключа "members" та встановлення порожнього списку, якщо відсутній
                status = "відкритий" if clan_data.get("open", True) else "закритий"
                num_members = len(clan_members)  # Використання len() після виправлення

                embed.add_field(name=f"{idx}. {clan_name}", value=f"Банк клану: **{clanbank}**{moneyemoji}\nКількість учасників: **{num_members}**\nСтатус клану: **{status}** ", inline=False)

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

class Clanupdates(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clan_updates(self, ctx):  # Додайте параметри self та ctx
        try:
            updates = {
                '1': {'name': 'Збільшення ліміту учасників клану на 10 слотів', 'price': 100000, 'description': 'Дане покращення збільшує максимальну кількість учасників на 10 учасників.'},
                '2': {'name': 'Купівля персональної ролі клану', 'price': 20000, 'description': 'Придбавши дане покращення всім учасникам клану видастся роль клану, яку можна буде кастомізувати'},
                # Додайте інші покращення за потребою
            }

            # Вивід інформації про покращення
            embed = discord.Embed(title=f'Покращення для клану', color=discord.Color.green())
            for key, value in updates.items():
                embed.add_field(name=f'{key}. {value["name"]}', value=f'Ціна: {value["price"]} гривень\nОпис: {value["description"]}', inline=False)
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            print(f'Clan_updates error: {e}')
            await ctx.send("Виникла помилка при обробці запиту.")


class Clanupdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.updates = {
            '1': {'name': 'Збільшення ліміту учасників клану до 30-ти', 'price': 50000, 'description': 'Дане покращення збільшує кількість максимальних учасників до 30-ти.'},
            '2': {'name': 'Купівля персональної ролі клану', 'price': 20000, 'description': 'Придбавши дане покращення всім учасникам клану видастся роль клану, яку можна буде кастомізувати'},
            # Додайте інші покращення за потребою
        }

    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням
        
    @commands.command()
    async def clan_donate(self, ctx, amount: int):
        try:
            # Отримання даних про клан користувача
            user_clan = clans_collection.find_one({"members": ctx.author.id})
            user_data = db.collusers.find_one({"_id": ctx.author.id})
            user_money = user_data.get("money", 0)
            
            if amount <= 0:
                await ctx.send("**❌Будь ласка, введіть додатнє число для внесення в банк клану.**")
                return
            # Перевірка, чи користувач належить до якого-небудь клану
            if not user_clan:
                await ctx.send("**❌Ви не є членом жодного клану.**")
                return
            
            # Отримання даних про комісію з бази даних
            commission_data = collservers.find_one({"_id": ctx.guild.id})
            if commission_data:
                commission_rate = commission_data.get("commission_rate", 0.03)  # За замовчуванням 3%
            else:
                commission_rate = 0.03  # За замовчуванням 3%
            
            # Обчислення суми комісії
            commission = amount * commission_rate
            
            # Перевірка, чи користувач має достатньо грошей для переказу
            if not user_money >= amount:
                await ctx.send('**❌У вас недостатньо грошей.**')
                return
            
            # Обчислення суми, яка буде додана до банку клану
            amount_to_deposit = amount - commission
            
            # Оновлення балансу банку клану
            clans_collection.update_one({"_id": user_clan["_id"]}, {"$inc": {"clanbank": amount_to_deposit}})
            
            # Віднімання коштів з балансу користувача
            new_balance = user_money - amount
            db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_balance}})
            
            # Відправка повідомлення про успішний внесок
            await ctx.send(f"**✅Ви успішно внесли {amount_to_deposit} у банк клану. Комісія {commission} була врахована.**")
        
        except Exception as e:
            print(f'Deposit error: {e}')
            await ctx.send("**❌Під час обробки вашого запиту виникла помилка. Будь ласка, спробуйте ще раз пізніше.**")


    @commands.command(name='clan_update')
    async def clan_update(self, ctx, item_id):
        try:
            is_leader = False
            existing_clan = clans_collection.find_one({"leader_id": ctx.author.id})
            if existing_clan is False:
                ctx.send('**❌Ви не є лідером клану**')
                return
                
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')
            # Переконайтеся, що self.updates доступне у вашому класі
            if item_id not in self.updates:
                await ctx.send("**❌Цього покращення не існує.**")
                return

            item_info = self.updates[item_id]
            price = item_info['price']
            
            user_clan = clans_collection.find_one({"members": ctx.author.id})
            if not user_clan:
                await ctx.send("**❌Ви не є учасником жодного клану.**")
                return

            clan_balance = user_clan.get("clanbank", 0)
            print(f'bal: {clan_balance}')
            if clan_balance < price:
                embed = discord.Embed(title=f"❌Не так швидко", color=0xff0000)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.description = f'{ctx.author.mention}, у клану недостатньо грошей на балансі для покупки.'
                await ctx.send(embed=embed)
                return

            # Видалення грошей та додавання товару
            new_balance = clan_balance - price
            clan_data = db.clans.find_one({"members": ctx.author.id})
            clan_name = clan_data.get("name", "Невідомий клан")
            clans_collection.update_one({"_id": user_clan["_id"]}, {"$set": {"clanbank": new_balance}})

            # Додавання покращення клану
            if item_id == '1':  # Перевірка для покращення "Збільшення ліміту учасників клану до 30-ти"
                new_max_member_limit = user_clan.get("max_member_limit", 20) + 10  # Збільшення ліміту на 10
                clans_collection.update_one({"_id": user_clan["_id"]}, {"$set": {"max_member_limit": new_max_member_limit}})

            if item_id == '2':  # Перевірка для покращення "Збільшення ліміту учасників клану до 30-ти"
    # Перевірка, чи клан вже має роль
                if "clan_role" in db.clans.find_one({"name": clan_name}, {"clan_role": 1}):
                    await ctx.send("**❌Цей клан вже має свою роль.**")
                    return

                # Створення нової ролі для клану
                new_role = await ctx.guild.create_role(name=clan_name)
                db.clans.update_one({"name": clan_name}, {"$set": {"clan_role": new_role.id}}, upsert=True)

                # Отримання ролі клану
                clan_role = ctx.guild.get_role(new_role.id)

                embed = discord.Embed(title=f"✅Успішно", color=0xa3f046)
                embed.set_thumbnail(url=ctx.author.avatar.url)
                embed.description = f'{ctx.author.mention}, покупка успішна! З вашого балансу було списано **{price}{moneyemoji}**'
                await ctx.send(embed=embed)

                # Перевірка, чи вдалося отримати роль клану
                if clan_role:
                    # Додавання новоствореної ролі учасникам клану
                    user_clan = db.clans.find_one({"members": ctx.author.id})
                    for member_id in user_clan.get("members", []):
                        member = ctx.guild.get_member(member_id)
                        if member:
                            try:
                                await member.add_roles(new_role)
                            except Exception as e:
                                print(f'Не вдалося додати роль користувачеві {member}: {e}')
                else:
                    print('Роль клану не знайдена')


        except KeyError:
            await ctx.send("Виникла помилка. Зазначене покращення не існує.")
        except pymongo.errors.PyMongoError as e:
            await ctx.send(f"Виникла помилка при взаємодії з базою даних: {e}")




    


class Joinclan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join_clan(self, ctx, clan_name):  # Додайте параметри self та ctx
        try:
            # Перевірка, чи клан існує
            clan = clans_collection.find_one({"name": clan_name})
            if not clan:
                await ctx.send("**❌Клан з такою назвою не існує.**")
                return
            if not clan.get("open", True):
                await ctx.send("**❌Цей клан зачинений для приєднання.**")
                return
            max_member_limit = clan.get('max_member_limit')
            if max_member_limit is not None and len(clan["members"]) >= max_member_limit:
                await ctx.send("**❌Максимальна кількість учасників у цьому клані вже досягнута.**")
                return

            # Перевірка, чи користувач вже є у цьому клані
            if ctx.author.id in clan["members"]:
                await ctx.send("**❌Ви вже є членом цього клану.**")
                return

            # Додавання користувача до клану
            clans_collection.update_one({"name": clan_name}, {"$push": {"members": ctx.author.id}})
            await ctx.send(f"**Ви успішно приєдналися до клану {clan_name}!**")
        except Exception as e:
            print(f'Join_clan error: {e}')
            return

class ClanManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setmoderator(self, ctx, user: discord.User):
        try:
            # Перевірка, чи користувач є лідером клану
            clan = clans_collection.find_one({"leader_id": ctx.author.id})
            if not clan:
                await ctx.send("**❌Ви не є лідером жодного клану.**")
                return
            
            # Отримання ідентифікаторів користувачів-учасників клану
            clan_members_ids = clan.get("members", [])
            
            # Перевірка, чи є вказаний користувач учасником клану
            if user.id not in clan_members_ids:
                await ctx.send("**❌Учасника немає у вашому клані.**")
                return
            
            # Перевірка, чи користувач вже є модератором клану
            if user.id in [clan.get("moderator1_id"), clan.get("moderator2_id")]:
                await ctx.send("**❌Цей користувач вже є модератором клану.**")
                return

            # Перевірка, чи є вільний слот для модератора
            if clan.get("moderator1_id") is not None and clan.get("moderator2_id") is not None:
                await ctx.send("**❌Клан вже має двох модераторів.**")
                return

            # Призначення користувача модератором клану
            if clan.get("moderator1_id") is None:
                clans_collection.update_one({"leader_id": ctx.author.id}, {"$set": {"moderator1_id": user.id}})
                await ctx.send(f"**✅{user.mention} був призначений модератором клану.**")
            else:
                clans_collection.update_one({"leader_id": ctx.author.id}, {"$set": {"moderator2_id": user.id}})
                await ctx.send(f"**✅{user.mention} був призначений другим модератором клану.**")
        except Exception as e:
            print(f'Appoint_moderator error: {e}')
            return

    @commands.command()
    async def leave_clan(self, ctx):
        try:
            # Перевірка, чи користувач є членом клану
            existing_clan = clans_collection.find_one({"members": ctx.author.id})
            if not existing_clan:
                await ctx.send("**❌Ви не є членом жодного клану.**")
                return

            # Перевірка, чи користувач є лідером клану
            if existing_clan.get("leader") == ctx.author.id:
                await ctx.send("**❌Ви не можете покинути клан, оскільки ви є його лідером.**")
                return

            # Видалення ролі користувача (якщо вона існує)
            if "clan_role" in existing_clan:
                role = ctx.guild.get_role(existing_clan["clan_role"])
                if role:
                    await ctx.author.remove_roles(role)

            # Видалення користувача зі списку учасників клану
            clans_collection.update_one({"_id": existing_clan["_id"]}, {"$pull": {"members": ctx.author.id}})
            
            await ctx.send("**✅Ви успішно покинули клан.**")
        except Exception as e:
            print(f'Leave_clan error: {e}')
            return


    @commands.command()
    async def toggle_clan(self, ctx, action: str):
        try:
            # Перевірка, чи користувач є лідером або заступником клану
            clan = clans_collection.find_one({"$or": [{"leader_id": ctx.author.id}, {"moderator1_id": ctx.author.id}, {"moderator2_id": ctx.author.id}]})
            if not clan:
                await ctx.send("**❌Ви не є лідером або заступником жодного клану.**")
                return

            if action.lower() == "open":
                # Встановлення прапорця "відкритий" клану
                clans_collection.update_one({"_id": clan["_id"]}, {"$set": {"open": True}})
                await ctx.send("**✅Клан відкритий для нових учасників.**")
            elif action.lower() == "close":
                # Зняття прапорця "відкритий" клану
                clans_collection.update_one({"_id": clan["_id"]}, {"$set": {"open": False}})
                await ctx.send("**✅Клан закритий для нових учасників.**")
            else:
                await ctx.send("**❌Неправильно введена команда. Використайте 'open' або 'close'.**")
        except Exception as e:
            print(f'Toggle_clan error: {e}')
            return


    @commands.command()
    async def kick_member(self, ctx, member: discord.Member):
        try:
            # Перевірка, чи користувач є лідером клану
            clan = clans_collection.find_one({"leader_id": ctx.author.id})
            if not clan:
                await ctx.send("**❌Ви не є лідером жодного клану.**")
                return

            # Перевірка, чи учасник є членом клану
            if member.id not in clan["members"]:
                await ctx.send("**❌Цей користувач не є учасником вашого клану.**")
                return

            # Видалення учасника з клану
            clans_collection.update_one({"_id": clan["_id"]}, {"$pull": {"members": member.id}})
            await ctx.send(f"**✅{member.mention} успішно вигнаний з клану.**")
        except Exception as e:
            print(f'Kick_member error: {e}')
            return
class ClanInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def clan_info(self, ctx):
        try:
            # Отримання інформації про клан, до якого належить користувач
            clan = clans_collection.find_one({"members": ctx.author.id})
            if clan is None:
                await ctx.send("**❌Ви не є учасником жодного клану.**")
                return

            status = "відкритий" if clan.get("open", True) else "закритий"

            clanbank_amount = clan.get("clanbank", "0")
            leader = await self.bot.fetch_user(clan["leader_id"])
            num_members = len(clan["members"])

            max_member_limit = clan.get('max_member_limit', "не встановлено")

            # Отримання списку учасників клану
            members = [await self.bot.fetch_user(member_id) for member_id in clan["members"]]

            # Додавання інформації про лідера
            embed = discord.Embed(title=f'Інформація про клан {clan["name"]}', color=discord.Color.blue())

            # Додавання інформації про лідера
            embed.add_field(
                name="Основна інформація",
                value=f'👑Лідер клану: {leader.mention}\n👥Кількість учасників: **{num_members}/{max_member_limit}**\n♻Статус: **{status}**\n💰Банк клану: {clanbank_amount}',
                inline=True
            )

            # Отримання інформації про заступників
            moderator1_id = clan.get("moderator1_id")
            moderator2_id = clan.get("moderator2_id")

            moderator1 = ctx.guild.get_member(moderator1_id)
            moderator2 = ctx.guild.get_member(moderator2_id)

            # Додавання інформації про заступників до вбудованого об'єкта
            moderators_info = ""
            if moderator1:
                moderators_info += f"Заступник 1: {moderator1.mention}\n"
            if moderator2:
                moderators_info += f"Заступник 2: {moderator2.mention}\n"

            if moderators_info:
                embed.add_field(    
                    name="⚒Заступники",
                    value=moderators_info,
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚒Заступники",
                    value="У вашому клані немає заступників.",
                    inline=False
                )

            # Додавання інформації про учасників клану
            members_mentions = [member.mention for member in members]
            embed.add_field(
                name=f"Список учасників:",
                value=f"Учасники клану: {', '.join(members_mentions)}\n",
                inline=False
            )

            await ctx.send(embed=embed)
        except Exception as e:
            print(f'Clan_info error: {e}')
            return


#    @commands.command()
#    async def toggle_clan_status(self, ctx, status: str):
#        try:
#            # Пошук клану, лідером якого є поточний користувач
#            clan = clans_collection.find_one({"leader_id": ctx.author.id})
#            if not clan:
#                await ctx.send("**❌Ви не є лідером жодного клану.**")
#                return

#            if status.lower() == "open":
#                clans_collection.update_one({"_id": clan["_id"]}, {"$set": {"open": True}})
#               await ctx.send("**✅Доступ до клану відкритий.**")
#            elif status.lower() == "closed":
#                clans_collection.update_one({"_id": clan["_id"]}, {"$set": {"open": False}})
#                await ctx.send("**✅Доступ до клану закритий.**")
#            else:
#                await ctx.send("**❌Неправильно введена команда. Використовуйте 'open' або 'closed'.**")
#        except Exception as e:
#            print(f'Toggle_clan_status error: {e}')
#            return
async def setup(bot):   
    #await bot.add_cog(Createclan(bot))
    await bot.add_cog(Joinclan(bot))
    await bot.add_cog(ClanManagement(bot))
    await bot.add_cog(ClanInfo(bot))
    await bot.add_cog(Clanupdates(bot))
    await bot.add_cog(Clanupdate(bot))
    await bot.add_cog(Clanleaderboard(bot))
    