from discord.ext import commands
import discord

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clear')
    async def clear(self, ctx, amount: int = 0):

        if not ctx.author.guild_permissions.administrator:
            print('no')
            return
        else:
            # Перевірка, чи вказано коректну кількість повідомлень для видалення
            if amount <= 0:
                await ctx.send(f'<@{ctx.author.id}>, будь ласка, вкажіть коректну кількість повідомлень для видалення.', delete_after=10)
                return

            # Видалення повідомлень
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 для включення оригінального повідомлення

            # Відправлення повідомлення про кількість видалених повідомлень
            await ctx.send(f'**✅ Успішно видалено {len(deleted) - 1} повідомлень.**')  # -1, оскільки ми включили оригінальне повідомлення

async def setup(bot):
    await bot.add_cog(Clear(bot))
