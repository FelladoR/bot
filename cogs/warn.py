import discord
from discord.ext import commands
from pymongo import MongoClient
from random import randint
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='>', intents=intents) 
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
            if user_data['warns'] >=2:
                # Ресет варнів і попереджень
                cluster.testbase.collusers.update_one(
                    {'_id': member.id, 'guild_id': ctx.guild.id},
                    {'$set': {'warns': 0, 'reasons': []}}
                )

                # Create an Embed for the user
                embed = discord.Embed(
                    title='Блокування',
                    description=f'Ви отримали блокування на сервері {ctx.guild.name} Причина: ``максимальна кількість попереджень``.',
                    color=discord.Color.red()
                    
                )
                # Send the embed to the user's DM channel
                await member.send(embed=embed)

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
                    user_data["warns"] += 1
                    new_warns_value = user_data["warns"]
                    warningembed = discord.Embed(
                        title='Повідомлення',
                        description=f'Ви отримали попередження на сервері {ctx.guild.name} Причина: ``{str(reason)}``. Кількіть ваших попереджень: {new_warns_value}',
                        color=discord.Color.yellow()
                    )

                    await member.send(embed=warningembed)

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
