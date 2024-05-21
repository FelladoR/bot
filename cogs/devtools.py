import discord
from discord.ext import commands
import random
from bot import pymongo, logs, time, asyncio
from pymongo import MongoClient
from bson import ObjectId
# Встановлення з'єднання з базою даних
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
db = cluster['testbase'] 
collection = db['testcollection'] 
clans_collection = db["clans"]
collservers = db['collservers']

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.has_any_role('Розробник', 'Куратор серверу')
    async def set_commission(self, ctx, commission_rate: float):
        try:
            # Перевірка, чи вказана комісія менша або рівна 100%
            if commission_rate > 100:
                await ctx.send("**❌Комісія повинна бути не більша 100%.**")
                return
            
            # Оновлення значення комісії в базі даних
            server_id = ctx.guild.id
            collservers.update_one({"_id": server_id}, {"$set": {"commission_rate": commission_rate}}, upsert=True)
            
            await ctx.send(f"**✅Комісія для сервера встановлена на {commission_rate}%.**")
            
        except ValueError:
            await ctx.send("**❌Будь ласка, введіть числове значення для комісії.**")
        except Exception as e:
            print(f'Set_commission error: {e}')
            await ctx.send("**❌Під час встановлення комісії виникла помилка. Будь ласка, спробуйте ще раз пізніше.**")

    @commands.command()
    @commands.has_any_role('Розробник', 'Куратор серверу')
    async def devpanel(self, ctx):
        commission_data = collservers.find_one({"_id": ctx.guild.id})
        commission_rate = commission_data.get("commission_rate", 0.0)
        embed = discord.Embed(
            title='Панель розробника',
            description=f'Комісія переказу грошей на сервері: **{commission_rate}%**\nЗмінити комісію: ``>set_commission процент``\nОтримати id клану: ``>getclanid назва``\nВидалити клан: ``>deleteclan айді``\n',
            color=discord.Color.red()
            )
        embed.set_thumbnail(url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_any_role('Розробник', 'Куратор серверу')
    async def getclanid(self, ctx, *, clan_name: str):
        try:
            # Пошук клану за назвою у базі даних
            clan = clans_collection.find_one({"name": clan_name})
            
            if clan:
                clan_id = clan["_id"]
                await ctx.send(f"ID клану '{clan_name}': {clan_id}")
            else:
                await ctx.send(f"Клан з назвою '{clan_name}' не знайдено.")
        
        except Exception as e:
            print(f'Error getting clan ID: {e}')
            await ctx.send("Виникла помилка при спробі отримати ID клану. Будь ласка, спробуйте ще раз пізніше.")

    @commands.command()
    @commands.has_any_role('Розробник')
    async def deleteclan(self, ctx, clan_id: str):
        try:
            # Перевірка, чи користувач має право на видалення клану (наприклад, чи є він адміністратором)
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("**❌Ви не маєте дозволу видаляти клани на цьому сервері.**")
                return
            
            # Перевірка, чи існує клан з вказаним ID
            existing_clan = clans_collection.find_one({"_id": ObjectId(clan_id)})
            if not existing_clan:
                await ctx.send("**❌Клан з вказаним ID не знайдено.**")
                return
            
            # Видалення клану з бази даних
            clans_collection.delete_one({"_id": ObjectId(clan_id)})
            
            await ctx.send("**✅Клан успішно видалено.**")
            
        except Exception as e:
            print(f'Delete_clan error: {e}')
            await ctx.send("**❌Під час видалення клану виникла помилка. Будь ласка, спробуйте ще раз пізніше.**")

async def setup(bot):   
    await bot.add_cog(Settings(bot))