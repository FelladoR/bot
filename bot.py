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
import uuid
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
        logs = 1165690496249774242  # Replace with your actual logs channel ID
        channel = bot.get_channel(logs)
        current_time = time.time()
        await channel.send(f'``{time.ctime(current_time)} ``🔽Учасник {member.name}(``{member.id}``) вийшов з серверу | Дата регістрації: ``{member.created_at.strftime("%d-%m-%Y %H:%M:%S")}``')

        # Replace the following with your actual guild and channel IDs
        guild_id = 1154369014181671014
        channel_id = 1167971043839852544

        guild = bot.get_guild(guild_id)
        members_channel = bot.get_channel(channel_id)

        # Update the channel name with the member count
        await members_channel.edit(name=f'🌙Учасники: {guild.member_count}')
        print('Вихід, канал було змінено!')

    except Exception as e:
        print(f'Error in on_member_remove: {e}')


@bot.command()
async def report(ctx, user: discord.User, *, reason: str):
    mod_channel_id = 1197198368871547025
    mod_channel = bot.get_channel(mod_channel_id)
    if user is None or reason is None:
        await ctx.send("Будь ласка, тегніть порушника, або вкажіть причину порушення")
        return

    embed = discord.Embed(title="Репорт", color=0xff0000)
    embed.add_field(name="Автор", value=ctx.author.mention, inline=False)
    embed.add_field(name="Потенційний порушник", value=user.mention, inline=False)
    embed.add_field(name="Причина", value=reason, inline=False)

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
    logs_id = '1200083767423938661'
    bot.get_channel(logs_id)
    if message.author.bot or message.guild is None:
        return

    guild = message.guild  # Get the server where the message was sent
    member = message.author  # Get the message author

    if message.content.startswith(bot.command_prefix):
        # Handle commands separately
        await bot.process_commands(message)
        return
    
    
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
             # Додайте користувача, якщо його немає в базі даних

    # Rest of your code...

      # Stop further processing if a bad word is found

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



@bot.event
async def on_ready():
    print('Бот запущений!')
    from cogs.gifts import send_gifts
    send_gifts.start()


@bot.event
async def on_guild_join(guild, member):

    server_values = {
                '_id': guild.id,
                'case': 0
                
            }
    if cluster.testbase.collservers.count_documents({'_id': guild.id}) == 0:
        cluster.testbase.collservers.insert_one(server_values)
    
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