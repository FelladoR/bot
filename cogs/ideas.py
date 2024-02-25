from discord.ext import commands
import time
from bot import discord, logs
from discord.ext.commands import cooldown, BucketType
class Message(commands.Cog):
    
    
    def __init__(self, bot):
        self.bot = bot
        self.message_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user

    @commands.Cog.listener()
    async def on_message(self, message):
        target_channel_id = 1154481844306317482  # Channel ID for automatic reactions
        target_channel = self.bot.get_channel(target_channel_id)
        member = message.author
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

        if message.author.bot:
            return

        if target_channel and message.channel == target_channel:
            try:
                if len(message.content.split()) < 10:
                    await message.reply("**❌Ваша ідея дуже коротка! Опишіть краще.**")
                    await message.delete()
                    return



                # Check for cooldown manually
                bucket = self.message_cooldown.get_bucket(message)
                retry_after = bucket.update_rate_limit()
                if retry_after:
                    
                    await message.reply(f"**⏳У вас перерва! Спробуйте через {retry_after:.2f} секунд.**", delete_after=30)
                    await message.delete()
                    return

                embed = discord.Embed(title=f"Ідея від {message.author.name} | Очікування", color=0xf5ec6e)
                embed.set_thumbnail(url=avatar_url)
                embed.description = f'{message.content}'
                embed.set_footer(text=time.ctime(time.time()))

                sent_message = await target_channel.send(embed=embed)  # Save the sent message
                await message.delete()  # Add parentheses to actually call the method

                await sent_message.add_reaction('👍')  # Use the sent_message variable
                await sent_message.add_reaction('👎')  # Use the sent_message variable
            except Exception as e:
                print(f'{e}')
                await message.delete()
                await message.channel.send('Сталась помилка під час виконання модулю ideas')
                return

class Accept(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"**⏳У вас перерва! Спробуйте через {error.retry_after:.2f} секунд.**", delete_after=30)
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply("У вас немає прав на використання цієї команди", delete_after=30)
        else:
            await ctx.reply(f"Сталась помилка: {error}")

    @commands.command(name='accept')
    async def accept(self, ctx, message_id, answer):
        try:
            current_time = time.time()

            logchannel = self.bot.get_channel(logs)
            allowed_user_id = 558945911980556288  # Remove quotes to make it an integer
            if ctx.author.id != allowed_user_id:
                return

            target_channel_id = 1154481844306317482  # Channel ID for automatic reactions
            target_channel = self.bot.get_channel(target_channel_id)

            ideamessage = await target_channel.fetch_message(message_id)
            original_embed = ideamessage.embeds[0].to_dict() if ideamessage.embeds else {}  # Copy existing embed if any

            new_embed = original_embed.copy()  # Create a copy of the original embed

            new_embed['title'] = f"{original_embed['title'].split('|')[0]} | Схвалено"
            new_embed['color'] = 0x94f56e
            new_embed['footer'] = {'text': time.ctime(time.time())}

            # Ensure 'fields' key exists in new_embed
            new_embed['fields'] = new_embed.get('fields', [])

            new_embed['fields'].append({'name': f'Відповідь від {ctx.author.name}', 'value': answer})

            await ideamessage.edit(embed=discord.Embed.from_dict(new_embed))
            await ctx.reply('**✅Ви успішно схвалили ідею!**', delete_after=30)

            # Check if 'fields' is present in original_embed before accessing it
            original_fields = original_embed.get('fields', [])
            await logchannel.send('``{} ``Адміністратор {}(``{}``) схвалив ідею | Ідея: {}'.format(time.ctime(current_time), ctx.author.name, ctx.author.id, original_fields))

        except Exception as e:
            print(f'Помилка у команді accept: {e}')
            return


class Decline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='decline')
    async def decline(self, ctx, message_id, answer):
        try:
            allowed_user_id = 558945911980556288  # Remove quotes to make it an integer
            if ctx.author.id != allowed_user_id:
                return
            
            target_channel_id = 1154481844306317482  # Channel ID for automatic reactions
            target_channel = self.bot.get_channel(target_channel_id)

            ideamessage = await target_channel.fetch_message(message_id)
            original_embed = ideamessage.embeds[0].to_dict() if ideamessage.embeds else {}  # Copy existing embed if any

            new_embed = original_embed.copy()  # Create a copy of the original embed

            new_embed['title'] = f"{original_embed['title'].split('|')[0]} | Відхилено"
            new_embed['color'] = 0xf56e6e
            new_embed['footer'] = {'text': time.ctime(time.time())}

            new_embed['fields'] = new_embed.get('fields', [])  # Ensure 'fields' key exists
            new_embed['fields'].append({'name': f'Відповідь від {ctx.author.name}', 'value': answer})

            await ideamessage.edit(embed=discord.Embed.from_dict(new_embed))
            await ctx.send('**✅Ви успішно відхилили ідею!**', delete_after=30)
        except Exception as e:
            print(f'Помилка у команді decline: {e}')
            return
        


async def setup(bot):
    await bot.add_cog(Message(bot))
    await bot.add_cog(Accept(bot))
    await bot.add_cog(Decline(bot))