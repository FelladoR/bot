from discord.ext import commands
import discord
from pymongo import MongoClient
from bot import cluster
cluster = MongoClient('mongodb+srv://FelladoR:maxum26072007@cluster0.o9csmz1.mongodb.net/?retryWrites=true&w=majority')

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
     
    @commands.command(name='profile')
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        usr = cluster.testbase.collusers.find_one({
            "_id": member.id,
            "guild_id": ctx.guild.id
        })

        embed = discord.Embed(title=f'Профіль користувача {member}',
                              color=discord.Color.random())

        embed.set_thumbnail(url=member.avatar)  # Set user's avatar as thumbnail

        embed.add_field(name='Ім\'я', value=member.name, inline=True)
        embed.add_field(name='Тег', value=member.discriminator, inline=True)
        embed.add_field(name='ID', value=f'``{member.id}``', inline=False)

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

async def setup(bot):
    
    await bot.add_cog(Profile(bot))