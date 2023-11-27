import discord
from discord.ext import commands
from pymongo import MongoClient

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')

class Checkwarns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='checkwarns')
    async def checkwarns(self, ctx, member: discord.Member = None):
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
                    moderator = await self.bot.fetch_user(value['author_id'])
                    embed.add_field(
                        name=f"Модератор: {moderator}", 
                        value=f"ID: {value['case']}\n Причина: ``{value['reason']}``", 
                        inline=False
                    )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Користувач або попередження не знайдені.")

    async def cog_command_error(self, ctx, error):
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
    await bot.add_cog(Checkwarns(bot))
