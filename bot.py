import discord # Подключаем библиотеку
from discord.ext import commands
import asyncio
import time
import os

from pymongo import MongoClient
from random import randint
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase']  # Выбор базы данных
collection = db['testcollection']  # Выбор коллекции
collusers = cluster.testbase.collusers
collservers = cluster.testbase.collservers

intents = discord.Intents.default() # Подключаем "Разрешения"
intents.message_content = True
# Задаём префикс и интенты
bot = commands.Bot(command_prefix='-', intents=intents) 

# С помощью декоратора создаём первую команду

@bot.command()
async def warn(ctx, member: discord.Member = None, *, reason='причина не вказана'):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("У вас недостатньо прав для використання цієї команди.")
        ctx.message.delete()
        return
    
    if member is None:
        await ctx.send(f'<@{ctx.author.id}>, вкажіть користувача якому потрібно видати попередження.')
        ctx.message.delete()
        return
    
    user_data = cluster.testbase.collusers.find_one({'_id': member.id, 'guild_id': ctx.guild.id})
    
    if user_data:
        if user_data['warns'] >= 3:
            # Reset warns and reasons
            cluster.testbase.collusers.update_one(
                {'_id': member.id, 'guild_id': ctx.guild.id},
                {'$set': {'warns': 0, 'reasons': []}}
            )
        else:
            server_data = cluster.testbase.collservers.find_one({'_id': ctx.guild.id})
            if server_data:
                # Increment warns and add reason
                cluster.testbase.collservers.update_one(
                    {'_id': ctx.guild.id},
                    {'$inc': {'case': 1}}
                )
                cluster.testbase.collusers.update_one(
                    {'_id': member.id, 'guild_id': ctx.guild.id},
                    {
                        '$inc': {'warns': 1},
                        '$push': {
                            'reasons': {
                                'author_id': ctx.author.id,
                                'case': server_data['case'],
                                'reason': reason
                            }
                        }
                    }
                )
                await ctx.send(f"{ctx.author} видав попередження {member}, причина: ``{reason}``. Case: {server_data['case']}")
            else:
                await ctx.send("Server data not found")
    else:
        # Додайте користувача, якщо його немає в базі даних
        cluster.testbase.collusers.insert_one({
            '_id': member.id,
            'guild_id': ctx.guild.id,
            'warns': 1,
            'reasons': [{
                'author_id': ctx.author.id,
                'case': 1,
                'reason': reason
            }]
        })
        await ctx.send(f"{ctx.author} видав перше попередження {member}, причина: ``{reason}``. Case: 1")





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



@bot.command()
async def warns(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    usr = cluster.testbase.collusers.find_one({"_id": member.id, "guild_id": ctx.guild.id})
    if usr and "reasons" in usr:
        embed = discord.Embed(title="Попередження: " + str(usr['warns']), color=discord.Color.orange())
        for value in usr["reasons"]:
            if 'warns' in value and (value['warns'] == 0 or value['warns'] is None):
                await ctx.send('Користувач або попередження не знайдені.')
                return
            else:
                moderator = await bot.fetch_user(value['author_id'])
                embed.add_field(
                    name=f"Модератор: {moderator}", 
                    value=f"ID: {value['case']}\n Причина: ``{value['reason']}``", 
                    inline=False
                )
        await ctx.send(embed=embed)
    else:
        await ctx.send("Користувач або попередження не знайдені.")
@bot.event
async def on_message(message):
    guild = message.guild  # Get the server where the message was sent
    member = message.author  # Get the message author
    if message.author.bot:
        return
    if message.content.startswith(bot.command_prefix):
        splitted_content = message.content.split()
        splitted_content[0] = splitted_content[0].lower()
        message.content = ' '.join(splitted_content)
        await bot.process_commands(message)

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
        print(f'User {member.id} updated for guild {guild.id}')


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
@bot.command()
async def ping(ctx):
    await ctx.send('pong')

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
    
@bot.command(name='clear')
async def clear(ctx, amount: int = 0):
    role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if role not in ctx.author.roles:
        await ctx.send(f'<@{ctx.author.id}>, у вас немає прав на використання даної команди.')
        return
    else:
        # Змінив message_content на 'Processing...'
        # Перевірка, чи вказано коректну кількість повідомлень для видалення
        if amount is None or amount <= 0:
            await ctx.send(f'<@{ctx.author.id}>, будь ласка, вкажіть коректну кількість повідомлень для видалення.', delete_after=10)
            return

        # Видалення повідомлень
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 для включення оригінального повідомлення

        # Відправлення повідомлення про кількість видалених повідомлень
        await ctx.send(f'**✅ Успішно видалено {len(deleted) - 1} повідомлень.**')  # -1, оскільки ми включили оригінальне повідомлення

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
    embed.add_field(name='ID', value=member.id, inline=False)

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



# Функция проверки канала






bot.run('MTE1NzQyNjEzMTE1OTQ5MDU4MQ.GHWPDt.-hQ3N_hH6wqZyTQ98UXSh1LMVMef538lg_edqo')