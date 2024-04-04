from discord.ext import commands, tasks
import discord
from bot import logs, db, random, time

class Claim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_gift_message = None
        self.send_gifts.start()

    @commands.command(name='claim')
    async def claim(self, ctx):
        try:
            moneyemoji = await self.get_custom_emoji(ctx.guild, '9243_DiscordCoin')
            author_data = db.collusers.find_one({"_id": ctx.author.id})
            if self.last_gift_message:
                guild_id = 1154369014181671014
                guild = self.bot.get_guild(guild_id)
                present = random.randint(50, 150)
                user_balance = author_data.get("money", 0)
                new_balance = user_balance + present
                if guild:
                    gift_channel_id = 1154369014940844135
                    gift_channel = guild.get_channel(gift_channel_id)

                    if gift_channel:
                        if ctx.channel == gift_channel:
                            await ctx.send(f'{ctx.author.mention}, ви успішно забрали подарунок! 🎉', delete_after=30)

                            new_embed = discord.Embed(title=f"🎁Подарунок від бота", color=0xE84D5F)
                            new_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                            new_embed.description = f'Бот викинув випадковий подарунок! Встигни його забрати. Використай ``>claim``\n**Статус подарунку: забрано**\n**Забрав: {ctx.author}**\n**Подарунок: {present}{moneyemoji}**'
                            db.collusers.update_one({"_id": ctx.author.id}, {"$set": {"money": new_balance}})
                            await self.last_gift_message.edit(embed=new_embed, delete_after=30)
                            self.last_gift_message = None
                            channel = self.bot.get_channel(logs)
                            current_time = time.time()
                            await channel.send(f'``{time.ctime(current_time)} ``🎁Учасник {ctx.author.name}(``{ctx.author.id}``) забрав подарунок | Подарунок: **{present}**{moneyemoji}')
                            await ctx.message.delete()
        except Exception as e:
            print(f'Claim error: {e}')
    @tasks.loop(hours=6)
    async def send_gifts(self):
        try:
            #print('Checking for gifts')
            guild_id = 1154369014181671014
            guild = self.bot.get_guild(guild_id)

            if guild:
                gift_channel_id = 1154369014940844135
                gift_channel = guild.get_channel(gift_channel_id)

                if gift_channel:
                    gift_receiver = random.choice(guild.members)
                    embed = discord.Embed(title=f"🎁Подарунок від бота", color=0x97ea36)
                    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
                    embed.description = f'Бот викинув випадковий подарунок! Встигни його забрати. Використай ``>claim``\n**Статус подарунку: доступний**'
                    logchannel = self.bot.get_channel(logs)
                    current_time = time.time()
                    await logchannel.send(f'``{time.ctime(current_time)} ``🎁Бот скинув подарунок.')

                    if self.last_gift_message and self.last_gift_message.guild == guild:
                        await self.last_gift_message.edit(embed=embed)
                    else:
                        self.last_gift_message = await gift_channel.send(embed=embed)
        except Exception as e:
            print(f'Gift error: {e}')

    @send_gifts.before_loop
    async def before_send_gifts(self):
        print('Waiting until bot is ready')
        await self.bot.wait_until_ready()

    

    async def get_custom_emoji(self, guild, emoji_name):
        custom_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if custom_emoji:
            return str(custom_emoji)
        else:
            return ""  # Або поверніть щось інше за замовчуванням

async def setup(bot):
    await bot.add_cog(Claim(bot))
