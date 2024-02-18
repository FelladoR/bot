from discord.ext import commands
import time
from bot import discord

current_time = time.time()

class Messagedelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        try:
            logs_channel_id = 1165690450443780206
            logchannel = self.bot.get_channel(logs_channel_id)  # logs_channel_id - ID каналу для логів
            member = message.author
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            
            embed = discord.Embed(title=f"Повідомлення видалено", color=0xf56e6e)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name='Повідомлення', value=message.content, inline=False)
            embed.add_field(name='Канал', value=f'<#{message.channel.id}>', inline=True)
            embed.add_field(name='Користувач', value=f'{member.name} | ``{member.id}``', inline=True)
            embed.set_footer(text=time.ctime(time.time()))
            await logchannel.send(embed=embed)
        except Exception as e:
            print(f'Deletemessage error: {e}')
            return

async def setup(bot):
    await bot.add_cog(Messagedelete(bot))
