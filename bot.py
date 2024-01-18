import discord # Подключаем библиотеку
from discord.ext import commands
import asyncio
import time
import os

from pymongo import MongoClient
from random import randint
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collection = db['testcollection']  
collusers = cluster.testbase.collusers
collservers = cluster.testbase.collservers
intents = discord.Intents.default()
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

@bot.command()
async def report(ctx, user: discord.User, *, reason: str):
    # Get the bot owner or moderators
    mod_channel_id = 1164932726877585428  # Replace with the ID of the channel where reports should be sent
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
    await mod_channel.send(embed=embed)
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

            if muterole:
                await message.channel.send(f"**⚠ {member.mention} отримує блокування чату до вияснення.**")
                await member.add_roles(muterole)
            else:
                await message.channel.send("❌ Помилка: Роль для блокування не знайдена. Зверніться до адміністратора.")
            return  # Stop further processing if a bad word is found

    # Check if the user exists in the database for this guild
    existing_user = cluster.testbase.collusers.find_one({'_id': member.id, 'guild_id': guild.id})

    if existing_user is None:
        # If the user doesn't exist, add them to the database
        values = {
            '_id': member.id,
            'guild_id': guild.id,
            'warns': 0,
            'reasons': []
        }
        cluster.testbase.collusers.insert_one(values)
        print(f'User {member.id} inserted for guild {guild.id}')
    else:
        # If the user already exists, you might want to update their information
        # For example, update their warns or reasons if needed
        # You can do this by updating the existing_user dictionary and using update_one
        updated_values = {
            '$set': {
                'warns': existing_user['warns'],
                'reasons': existing_user['reasons']
                # Update other fields if needed
            }
        }
        cluster.testbase.collusers.update_one({'_id': member.id, 'guild_id': guild.id}, updated_values)
        #print(f'User {member.id} updated for guild {guild.id}')


# Прочие части вашего кода
@bot.event
async def on_ready():
    print('Запущено!')
    channel_id = 851748174665875466  # Replace this ID with your channel ID
    channel = bot.get_channel(channel_id)
    current_time = time.time()
    await channel.send(f'``{time.ctime(current_time)} ``Бот успішно запущений.')
    
    for guild in bot.guilds:
        for member in guild.members:
            existing_user = cluster.testbase.collusers.find_one({'_id': member.id, 'guild_id': guild.id})

            if existing_user is None:
                values = {
                    '_id': member.id,
                    'guild_id': guild.id,
                    'warns': 0,
                    'reasons': []
                }
                cluster.testbase.collusers.insert_one(values)
                print(f'User {member.id} inserted for guild {guild.id}')
            else:
                return

            server_values = {
                '_id': guild.id,
                'case': 0
            }
            if cluster.testbase.collservers.count_documents({'_id': guild.id}) == 0:
                cluster.testbase.collservers.insert_one(server_values)
                print(f'Server {guild.id} inserted')


@bot.event
async def on_member_join(member, guild):
    values = {
                '_id': member.id,
                'guild_id': guild.id,
                'warns': 0,
                'reasons': []
            }
    if cluster.testbase.collusers.count_documents({'_id': member.id, 'guild_id': guild.id}) == 0:
                cluster.testbase.collusers.insert_one(values)

@bot.event
async def on_guild_join(guild):
    server_values = {
                '_id': guild.id,
                'case': 0
            }
    if cluster.testbase.collservers.count_documents({'_id': guild.id}) == 0:
        cluster.testbase.collservers.insert_one(server_values)
#@bot.command()
#async def ping(ctx):
#   await ctx.send('pong')

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
    


@bot.command(name='profile')
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    usr = cluster.testbase.collusers.find_one({
        "_id": member.id,
        "guild_id": ctx.guild.id
    })

    embed = discord.Embed(title=f'Профіль користувача {member}',
                          color=discord.Color.red())

    embed.set_thumbnail(url=member.avatar)  # Set user's avatar as thumbnail

    embed.add_field(name='Ім\'я', value=member.name, inline=True)
    embed.add_field(name='Тег', value=member.discriminator, inline=True)
    embed.add_field(name='ID', value='``{member.id}``', inline=False)

    if usr:
        embed.add_field(
            name='Інформація про акаунт',
            value=f'Дата регістрації акаунту: {member.created_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                  f'Дата приєднання до гільдії: {member.joined_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                  f'Попереджень: {str(usr["warns"])}',
            inline=False
        )
    else:
        embed.add_field(
            name='Інформація про акаунт',
            value=f'Дата регістрації акаунту: {member.created_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                  f'Дата приєднання до гільдії: {member.joined_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                  f'Попереджень: 0',
            inline=False
        )

    await ctx.send(embed=embed)



async def start_bot():
    try:
        await load_cogs(bot)


        # token = os.getenv('MTEyODM2NTQ2MTQ0MTA5NzcyOA.G4g71U.dUj_ehwRoe1fT7EAOoHTmpqNr2WYue0TMVdl0k')
        await bot.start('MTEyODM2NTQ2MTQ0MTA5NzcyOA.G4g71U.dUj_ehwRoe1fT7EAOoHTmpqNr2WYue0TMVdl0k')

    except KeyboardInterrupt:
        await bot.close()
        print("Бот вимкнений.")

        token = os.getenv('TOKEN')
        await bot.start(token)

asyncio.run(start_bot())
