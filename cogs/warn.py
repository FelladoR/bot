import discord
from discord.ext import commands
from pymongo import MongoClient
from random import randint
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents) 
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')
class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='warn')
    async def warn(self, ctx, member: discord.Member = None, *, reason='причина не вказана'):
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("У вас недостатньо прав для використання цієї команди.")
            await ctx.message.delete()
            return
        
        if member is None:
            await ctx.send(f'<@{ctx.author.id}>, вкажіть користувача, якому потрібно видати попередження.')
            await ctx.message.delete()
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

    @commands.command(name='warns')
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

async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Эта команда не существует.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("У вас недостаточно прав для выполнения этой команды.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Вы пропустили необходимый аргумент.")
        else:
            # Логирование других ошибок, которые не были обработаны
            print(f"Произошла ошибка: {error}")
async def setup(bot):
    await bot.add_cog(Warn(bot))
