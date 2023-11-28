import discord
from discord.ext import commands

def allowed_channel(ctx):
    allowed_channel_ids = [1154369014940844135, 1154395654945251398, 1163094113726496858, 1165624675968221184, 1165687096682479687, 1154453402303086693, 1173670958461108264, ]  # Список разрешенных ID каналов

    return ctx.channel.id in allowed_channel_ids

class lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lockdown')
    @commands.check(allowed_channel)
    async def lockdown(self, ctx, *, reason=None):
        if not ctx.author.guild_permissions.administrator:
            print('no')
            return

        if ctx.channel.permissions_for(ctx.guild.default_role).send_messages is False:
            await ctx.send('Канал вже заблокований', delete_after=5)
            return

        if reason is None:
            reason = 'причина не була вказана.'

        await ctx.channel.set_permissions(ctx.guild.default_role,
                                         send_messages=False,
                                         read_message_history=True,
                                         view_channel=True)
        await ctx.message.delete()

        embed = discord.Embed(
            title='Канал заблокований',
            description=f'Адміністратор <@{ctx.author.id}> заблокував канал. Причина: ``{str(reason)}``',
            color=discord.Color.red()
        )
        embed.set_footer(
            text="Це тимчасові міри. Адміністрація розблокує канал як тільки це стане можливо."
        )
        embed.set_thumbnail(url=ctx.author.avatar)
        await ctx.send(embed=embed)
        await ctx.delete()

    @lockdown.error
    async def lockdown_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print(f'{ctx.author.name} спробував заблокувати канал {ctx.channel.name}')

    @commands.command(name='unlockdown')

    @commands.check(allowed_channel)
    
    async def unlockdown(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            print('no')
            return
        await ctx.message.delete()
        if ctx.channel.permissions_for(ctx.guild.default_role).send_messages:
            await ctx.send('Канал не є заблокований', delete_after=5)
            return
        
        await ctx.channel.set_permissions(ctx.guild.default_role,
                                         send_messages=True,
                                         read_message_history=True,
                                         view_channel=True)

        embed = discord.Embed(
            title='Канал розблокований',
            description='Канал успішно розблокований. Ви можете продовжувати спілкування тут',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
       
    @unlockdown.error
    async def unlockdown_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            print(f'{ctx.author.name} спробував розблокувати канал {ctx.channel.name}')

async def setup(bot):
    await bot.add_cog(lockdown(bot))