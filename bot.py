import discord # Подключаем библиотеку
from discord.ext import commands, tasks
import asyncio
import time
import os
import pymongo
from dotenv import load_dotenv
from pymongo import MongoClient
import random
from random import randint
logs = 1205305330779688960
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collection = db['testcollection']  
collusers = cluster.testbase.collusers
collservers = cluster.testbase.collservers
intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents) 

async def load_cogs(bot):
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                cog_name = f"cogs.{filename[:-3]}"
                if cog_name not in bot.extensions:
                    print(f"Завантажую: {cog_name}")
                    await bot.load_extension(cog_name)
                else:
                    print(f"Розширення вже завантажено: {cog_name}")
            except Exception as e:
                print(f"Не вдалось завантажити {cog_name}: {e}")

@bot.event
async def on_member_remove(member):
    try:
        # Replace with your actual guild and channel IDs
        guild_id = 1154369014181671014
        channel_id = 1167971043839852544

        channel = bot.bot.get_channel(logs)
        current_time = time.time()
        await channel.send(f'``{time.ctime(current_time)} ``🔽Учасник {member.name}(``{member.id}``) вийшов з серверу | Дата регістрації: ``{member.created_at.strftime("%d-%m-%Y %H:%M:%S")}``')

        # Fetch the guild and members channel
        guild = bot.get_guild(guild_id)
        members_channel = bot.get_channel(channel_id)

        # Update the channel name with the member count
        await members_channel.edit(name=f'🌙Учасники: {guild.member_count}')
        print('Вихід, канал було змінено!')

    except Exception as e:
        # Print any errors that occur during the event
        print(f'Error in on_member_remove: {e}')

@bot.event
async def on_member_join(member):
    try:
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        # Replace with your actual guild and channel IDs
        guild_id = 1154369014181671014
        guild = bot.get_guild(guild_id)
        channel_id = 1167971043839852544

        channel = bot.bot.get_channel(logs)
        current_time = time.time()
        await channel.send(f'``{time.ctime(current_time)} ``🔼Учасник {member.name}(``{member.id}``) приєднався на сервер | Дата регістрації: ``{member.created_at.strftime("%d-%m-%Y %H:%M:%S")}``')
        
        welcomechannel_id = 1154369014940844135
        welcomechannel = bot.get_channel(welcomechannel_id)
        embed = discord.Embed(title=f"Привіт!👋", color=0x7962D6)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(
                    name=f"Ласкаво просимо тебе на наш сервер! Ось канали, які тобі можуть знадобитись",
                    value='<#1154369014940844135> - тут основний чат, де ми всі спілкуємось\n<#1154395654945251398> - тут використовуємо всі команди ботів\n<#1154394799001051197> - тут написані правила серверу, можеш ознайомитись)\n',
                    inline=False
                )
        embed.add_field(
                    name=f"У нас навіть є свій Minecraft сервер!",
                    value='Інформацію про майнкрафт сервер ти можеш глянути тут: <#1196538563769139210>',
                    inline=False
                )
        embed.description = 'Бажаємо тобі всього найкращого, будь як в себе вдома) Слава Україні!'
        embed.set_footer(text='З повагою керівництво та адміністрація серверу')
        await welcomechannel.send(member.mention, embed=embed, delete_after=60)
        # Fetch the guild and members channel
        members_channel = bot.get_channel(channel_id)

        # Update the channel name with the member count
        await members_channel.edit(name=f'🌙Учасники: {guild.member_count}')
        print('Вхід, канал було змінено!')
    except Exception as e:
        # Print any errors that occur during the event
        print(f'Error in on_member_join: {e}')

@bot.command()
async def report(ctx, user: discord.User, *, reason: str):
    # Get the bot owner or moderators
    mod_channel_id = 1197198368871547025  # Replace with the ID of the channel where reports should be sent
    mod_channel = bot.get_channel(mod_channel_id)
    if user is None or reason is None:
        await ctx.send("Будь ласка, тегніть порушника, або вкажіть причину порушення")
        return

    # Create an embed to format the report
    embed = discord.Embed(title="Репорт", color=0xff0000)
    embed.add_field(name="Автор", value=ctx.author.mention, inline=False)
    embed.add_field(name="Потенційний порушник", value=user.mention, inline=False)
    embed.add_field(name="Причина", value=reason, inline=False)


    # Send the report to the specified channel
    await mod_channel.send('@everyone', embed=embed)
    await ctx.send("Ваша скарга успішно надіслана!", delete_after=5)
    await ctx.message.delete()

@bot.command()
async def remwarn(ctx, case: int):
    if cluster.testbase.collusers.count_documents({'reasons.case': case, 'guild_id': ctx.guild.id}) == 0:
        await ctx.send('Такого випадку немає')
    else:
        cluster.testbase.collusers.update_one(
            {
                'reasons.case': case,
                'guild_id': ctx.guild.id
            },
            {
                '$inc': {'warns': -1},
                '$pull': {'reasons': {'case': case}}
            }
        )
        await ctx.send('Знято.')


def load_badwords():
    try:
        with open("badwords.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

bad_words = load_badwords()

@bot.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    guild = message.guild  # Get the server where the message was sent
    member = message.author  # Get the message author

    if message.content.startswith(bot.command_prefix):
        # Handle commands separately
        await bot.process_commands(message)
        return

    target_channel_id = 1154481844306317482  # Channel ID for automatic reactions
    target_channel = bot.get_channel(target_channel_id)

    if target_channel and message.channel == target_channel:
        await message.add_reaction('👍')
        await message.add_reaction('👎')

    content_lower = message.content.lower()

    for bad_word in bad_words:
        if bad_word in content_lower:
            await message.delete()

            muterole_id = 1165620433647845456  # Replace with the actual muted role ID
            muterole = discord.utils.get(guild.roles, id=muterole_id)
            reportchannel = bot.get_channel(1164649565513851041)

            if muterole:
               
                current_time = time.time()
            await message.channel.send(f"**:warning: {message.author.mention} отримує блокування чату до вияснення.**")
            await message.author.add_roles(muterole)

            embed = discord.Embed(title="Авто-модерація", color=0xff0000)
            embed.add_field(name="Автор", value=f'{message.author} | ``{message.author.id}``', inline=False)
            embed.add_field(name="Повідомлення", value=f'``{message.content}``', inline=False)
            embed.add_field(name="Причина", value='до вияснення', inline=False)
            embed.set_footer(text=time.ctime(current_time))
            
            await reportchannel.send(embed=embed)

        existing_user = cluster.testbase.collusers.find_one({'_id': member.id, 'guild_id': guild.id})

        if existing_user is None:
        # If the user doesn't exist, add them to the database with default values
            values = {
                '_id': member.id,
                'guild_id': guild.id,
                'warns': 0,
                'reasons': [],
                'money': 0
            }
        cluster.testbase.collusers.insert_one(values)
        print(f'User {member.id} inserted for guild {guild.id}')
    else:
        # If the user already exists, check and add missing fields
        if 'warns' not in existing_user:
            existing_user['warns'] = 0

        if 'reasons' not in existing_user:
            existing_user['reasons'] = []

        if 'money' not in existing_user:
            existing_user['money'] = 0

        # Update the existing_user dictionary and use update_one
        updated_values = {
            '$set': {
                'warns': existing_user['warns'],
                'reasons': existing_user['reasons'],
                'money': existing_user['money']
                # Update other fields if needed
            }
        }
        cluster.testbase.collusers.update_one({'_id': member.id, 'guild_id': guild.id}, updated_values)
        # print(f'User {member.id} updated for guild {guild.id}')

@bot.event
async def on_ready():
    try:
        
        print('Запущено!')
        #channel_id = 851748174665875466  # Replace this ID with your channel ID
        #channel = bot.get_channel(channel_id)
        #current_time = time.time()
        #await channel.send(f'``{time.ctime(current_time)} ``Бот успішно запущений.')

        # Create unique indexes for _id field in collusers and collservers
        db.collusers.create_index([('_id', pymongo.ASCENDING)], unique=True)
        db.collservers.create_index([('_id', pymongo.ASCENDING)], unique=True)

        for guild in bot.guilds:
            for member in guild.members:
                try:
                    user_filter = {'_id': member.id, 'guild_id': guild.id}
                    existing_user = db.collusers.find_one(user_filter)

                    if existing_user:
                        #print(f'User {member.id} already exists for guild {guild.id}')
                        update_data = {'$set': {'guild_id': guild.id}}
                        db.collusers.update_one(user_filter, update_data)
                        #print(f'User {member.id} updated for guild {guild.id}')
                    else:
                        user_values = {'_id': member.id, 'guild_id': guild.id, 'warns': 0, 'reasons': [], 'money': 0}
                        db.collusers.insert_one(user_values)
                        #print(f'User {member.id} inserted for guild {guild.id}')
                except pymongo.errors.DuplicateKeyError as dup_error:
                    print(f'Duplicate key error for user {member.id}: {dup_error}. Context: {member.name} in guild {guild.name}')

            try:
                server_filter = {'_id': guild.id}
                existing_server = db.collservers.find_one(server_filter)

                if existing_server:
                    print(f'Server {guild.id} already exists in the database')
                else:
                    server_values = {'_id': guild.id, 'case': 0}
                    db.collservers.insert_one(server_values)
                    print(f'Server {guild.id} inserted')
            except pymongo.errors.DuplicateKeyError as server_dup_error:
                print(f'Duplicate key error for server {guild.id}: {server_dup_error}')

    except Exception as e:
        print(f'Error in on_ready: {e}')

last_gift_message = None  # Додайте цей рядок перед функцією send_gifts

@tasks.loop(hours=3)  # Кожні 5 секунд видаємо подарунок
async def send_gifts():
    try:
        global last_gift_message  # Додайте цей рядок

        print('Checking for gifts')
        guild_id = 1154369014181671014  # Замініть на ваш ID сервера
        guild = bot.get_guild(guild_id)

        logchannel = bot.get_channel(logs)
        current_time = time.time()
        await logchannel.send(f'``{time.ctime(current_time)} ``🎁Бот скинув подарунок.')

        if guild:
            gift_channel_id = 1164932726877585428  # Замініть на ID каналу, де видаються подарунки
            gift_channel = guild.get_channel(gift_channel_id)

            if gift_channel:
                gift_receiver = random.choice(guild.members)
                embed = discord.Embed(title=f"🎁Подарунок від бота", color=0x97ea36)
                embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                embed.description = f'Бот викинув випадковий подарунок! Встигни його забрати. Використай ``!claim``\n**Статус подарунку: доступний**'

                if last_gift_message:
                    await last_gift_message.edit(embed=embed)
                else:
                    last_gift_message = await gift_channel.send(embed=embed)
    except Exception as e:
        print(f'Gift error: {e}')

@bot.command(name='claim')
async def claim(ctx):
    try:
        global last_gift_message
        moneyemoji = await get_custom_emoji(ctx.guild, '9243_DiscordCoin')
        author_data = db.collusers.find_one({"_id": ctx.author.id})
        if last_gift_message:
            guild_id = 1154369014181671014  # Замініть на ваш ID сервера
            guild = bot.get_guild(guild_id)
            present = random.randint(50, 150)
            user_balance = author_data.get("money", 0)
            new_balance = user_balance + present
            if guild:
                gift_channel_id = 1164932726877585428  # Замініть на ID каналу, де видаються подарунки
                gift_channel = guild.get_channel(gift_channel_id)

                if gift_channel:
                    if ctx.channel == gift_channel:
                        await ctx.send(f'{ctx.author.mention}, ви успішно забрали подарунок! 🎉')
                        
                        new_embed = discord.Embed(title=f"🎁Подарунок від бота?", color=0xE84D5F)
                        new_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                        new_embed.description = f'Бот викинув випадковий подарунок! Встигни його забрати. Використай ``!claim``\n**Статус подарунку: забрано**\n**Забрав: {ctx.author}**\n**Подарунок: {present}{moneyemoji}**'
                        db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_balance}})
                        await last_gift_message.edit(embed=new_embed)
                        last_gift_message = None  # Позначаємо, що подарунок вже забраний, тому змінну можна очистити
                        channel = bot.get_channel(logs)
                        current_time = time.time()
                        await channel.send(f'``{time.ctime(current_time)} ``🎁Учасник {ctx.author.name}(``{ctx.author.id}``) забрав подарунок | Подарунок: **{present}**{moneyemoji}')
    except Exception as e:
        print(f'Claim error: {e}')

async def get_custom_emoji(guild, emoji_name):
    custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
    if custom_emoji:
        return str(custom_emoji)
    else:
        return ""  # Або поверніть щось інше за замовчуванням



@send_gifts.before_loop
async def before_send_gifts():
    print('Waiting until bot is ready')
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    try:
        send_gifts.start()
        print('Запущено!')
  # Replace this ID with your channel ID
        channel = bot.get_channel(logs)
        current_time = time.time()
        await channel.send(f'``{time.ctime(current_time)} ``🟢Бот успішно запущений.')

        # Remove explicit unique specification for _id field
        db.collusers.create_index([('_id', pymongo.ASCENDING)])
        db.collservers.create_index([('_id', pymongo.ASCENDING)])

        for guild in bot.guilds:
            for member in guild.members:
                try:
                    user_filter = {'_id': member.id}
                    existing_user = db.collusers.find_one(user_filter)

                    if existing_user:
                        #print(f'User {member.id} already exists for guild {guild.id}')
                        update_data = {'$set': {'guild_id': guild.id}}
                        db.collusers.update_one(user_filter, update_data)
                        #print(f'User {member.id} updated for guild {guild.id}')
                    else:
                        user_values = {'_id': member.id, 'guild_id': guild.id, 'warns': 0, 'reasons': [], 'money': 0}
                        db.collusers.insert_one(user_values)
                        #print(f'User {member.id} inserted for guild {guild.id}')
                except pymongo.errors.DuplicateKeyError as dup_error:
                    print(f'Duplicate key error for user {member.id}: {dup_error}. Context: {member.name} in guild {guild.name}')

            try:
                server_filter = {'_id': guild.id}
                existing_server = db.collservers.find_one(server_filter)

                if existing_server:
                    print(f'Server {guild.id} already exists in the database')
                else:
                    server_values = {'_id': guild.id, 'case': 0}
                    db.collservers.insert_one(server_values)
                    print(f'Server {guild.id} inserted')
            except pymongo.errors.DuplicateKeyError as server_dup_error:
                print(f'Duplicate key error for server {guild.id}: {server_dup_error}')

    except Exception as e:
        print(f'Error in on_ready: {e}')



@bot.event
async def on_guild_join(guild, member):

    server_values = {
                '_id': guild.id,
                'case': 0
                
            }
    if cluster.testbase.collservers.count_documents({'_id': guild.id}) == 0:
        cluster.testbase.collservers.insert_one(server_values)
    

@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    # Перевірте, чи у бота є права на блокування користувачів
    if member is None:
        await ctx.send('Вкажіть користувача, якого потрібно заблокувати')
        return
    else:
        if reason is None:
            await ctx.send('Вкажіть причину блокування')
            return
        else:
            if ctx.author.guild_permissions.ban_members:
                embed = discord.Embed(
                    title='Блокування',
                    description=f'Адміністратор <@{ctx.message.author.id}> заблокував користувача <@{member.id}>. Причина: {str(reason)}',
                    color=discord.Color.red()  # Колір вбудованого повідомлення
                )

                await ctx.guild.ban(member, reason=reason)
                await ctx.message.delete()
                # Створення об'єкта вбудованого повідомлення
                await ctx.send(embed=embed)
            else:
                await ctx.send('У вас недостатньо прав для блокування користувачів.')
    

async def start_bot():
    try:
        await load_cogs(bot)

        load_dotenv()
        async with bot:
            await bot.start(os.getenv('TOKEN'))
    except KeyboardInterrupt:
        await bot.close()
        print("Бот вимкнений.")

if __name__ == "__main__":
    asyncio.run(start_bot())