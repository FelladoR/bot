import discord
from discord.ext import commands

def allowed_channel(ctx):
    allowed_channel_ids = [1154369014940844135, 1154395654945251398, 1163094113726496858, 1165624675968221184, 1165687096682479687, 1154453402303086693, 1173670958461108264, 1154481844306317482]
    return ctx.channel.id in allowed_channel_ids


class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lockdown')
    async def lockdown(self, ctx, *, reason=None):
        allowed_channel_ids = [1154369014940844135, 1154395654945251398, 1163094113726496858, 1165624675968221184, 1165687096682479687, 1154453402303086693, 1173670958461108264, 1154481844306317482]
        if not ctx.author.guild_permissions.administrator:
            print('no')
            return

        if reason is None:
            reason = 'причина не була вказана.'

        for channel_id in allowed_channel_ids:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.set_permissions(ctx.guild.default_role,
                                                  send_messages=False,
                                                  read_message_history=True,
                                                  view_channel=True)

                    embed = discord.Embed(
                        title='Канал заблокований',
                        description=f'Адміністратор <@{ctx.author.id}> заблокував канал {channel.mention}. Причина: ``{str(reason)}``',
                        color=discord.Color.red()
                    )
                    embed.set_footer(
                        text="Це тимчасові міри. Адміністрація розблокує канал як тільки це стане можливо."
                    )
                    embed.set_thumbnail(url=ctx.author.avatar)
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"An error occurred while processing channel {channel.mention}: {e}")

        await ctx.message.delete()

class Unlockall(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='unlockall')
    async def unlockall(self, ctx):
        allowed_channel_ids = [1154369014940844135, 1154395654945251398, 1163094113726496858, 1165624675968221184, 1165687096682479687, 1154453402303086693, 1173670958461108264, 1154481844306317482]
        if not ctx.author.guild_permissions.administrator:
            print('no')
            return

        for channel_id in allowed_channel_ids:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                try:
                    await channel.set_permissions(ctx.guild.default_role,
                                                  send_messages=True,
                                                  read_message_history=True,
                                                  view_channel=True)

                    embed = discord.Embed(
                        title='Канал розблокований',
                        description=f'Адміністратор <@{ctx.author.id}> розблокував канал {channel.mention}.',
                        color=discord.Color.green()
                    )
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"An error occurred while processing channel {channel.mention}: {e}")

        await ctx.message.delete()
async def setup(bot):
    await bot.add_cog(Lockdown(bot))
    await bot.add_cog(Unlockall(bot))