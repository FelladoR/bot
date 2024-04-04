from discord.ext import commands
import discord
from pymongo import MongoClient
from bot import cluster
db = cluster['testbase'] 
clans_collection = db["clans"]
class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_custom_emoji(self, guild, emoji_name):
        # Your logic to get custom emoji here, assuming guild is a valid Guild object
        # For example:
        emoji = discord.utils.get(guild.emojis, name=emoji_name)
        return str(emoji) if emoji else ''

    @commands.command(name='profile')
    async def profile(self, ctx, member: discord.Member = None):
        try:
            if member is None:
                member = ctx.author

            # Use the correct collection and database names (collusers and testbase)
            usr = cluster.testbase.collusers.find_one({"_id": member.id})
            clan = clans_collection.find_one({"members": ctx.author.id})
            clan_name = clan.get('name') if clan is not None else 'немає'
            exp = usr.get('experience')
            if exp is None:
                exp = 0
            level = usr.get('level', 0)
            if clan is None:
                clan = 'немає'
            embed = discord.Embed(title=f'Профіль користувача {member}',
                                    color=0x2471A3)

            # Check if member has an avatar
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')
            embed.set_thumbnail(url=avatar_url)  # Set user's avatar as thumbnail

            embed.add_field(name='📌Ім\'я', value=member.name, inline=True)
            embed.add_field(name='#⃣Тег', value=member.discriminator, inline=True)
            embed.add_field(name='🔷ID', value=f'``{member.id}``', inline=False)
            
            embed.add_field(name='☄Рівень', value=f'Рівень: **{level}**\nEXP: **{exp}**', inline=False)
            if usr is not None:
                # Check if "balance" key is present in the document
                money = usr.get("money", 0)
                embed.add_field(name='💰Цінності', value=f'Монетки: **{money}**{moneyemoji}\nКлан: **{clan_name}**', inline=False)

                # Check if "warns" key is present in the document
                warns = usr.get("warns", 0)
                embed.add_field(
                    name='🔰Інформація про акаунт',
                    value=f'Дата реєстрації акаунту: {member.created_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                            f'Дата приєднання до гільдії: {member.joined_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                            f'Попереджень: {warns}',
                    inline=False
                )
            else:
                embed.add_field(name='💰Цінності', value='Гроші: 0', inline=False)
                #embed.add_field(name='Рівень', value=f'EXP: **{exp}**\nРівень: {level}', inline=False)
                embed.add_field(
                    name='🔰Інформація про акаунт',
                    value=f'Дата реєстрації акаунту: {member.created_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                            f'Дата приєднання до гільдії: {member.joined_at.strftime("%d-%m-%Y %H:%M:%S")}\n'
                            f'Попереджень: 0',
                    inline=False
                )

            await ctx.send(embed=embed)
            await ctx.message.delete()
        except Exception as e:
            print(f'Помилка у команді profile: {e}')
            return

async def setup(bot):
    await bot.add_cog(Profile(bot))
