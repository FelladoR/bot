from discord.ext import commands
import discord
import asyncio

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ban', help='Ban a member from the server')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, duration: int = None, *, reason='No reason provided'):
        try:
            if duration is not None:
                duration_seconds = duration * 60
                await member.ban(reason=reason)
                await ctx.send(f'{member.mention} has been temporarily banned for {duration} minutes. Reason: {reason}')

                # Unban the user after the specified duration
                await asyncio.sleep(duration_seconds)
                await member.unban(reason='Temporary ban expired')
            else:
                await member.ban(reason=reason)
                await ctx.send(f'{member.mention} has been permanently banned. Reason: {reason}')
        except Exception as e:
            print(f'Error banning member: {e}')
            await ctx.send(f'An error occurred while banning {member.mention}.')

    @ban.error
    async def ban_error(self, ctx, error):  # Add self as the first parameter
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found. Please provide a valid member to ban.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid arguments. Please use the correct format: !ban @user [duration_in_minutes] [reason]")
        else:
            await ctx.send(f"An error occurred: {error}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
