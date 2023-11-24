import discord # Подключаем библиотеку
from discord.ext import commands
import asyncio
intents = discord.Intents.default() # Подключаем "Разрешения"
intents.message_content = True
# Задаём префикс и интенты
bot = commands.Bot(command_prefix='>', intents=intents) 

# С помощью декоратора создаём первую команду

@bot.event
async def on_ready():
    print('Запущено!')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    # Перевірте, чи у бота є права на блокування користувачів
    if member is None:
        await ctx.send('Вкажіть користувача, якого потрібно заблокувати')
        return
    else:
        if reason is None:
            await ctx.send('Вкажіть причину блокування')
            return
        else:
            if ctx.author.guild_permissions.ban_members:
                embed = discord.Embed(
                    title='Блокування',
                    description=f'Адміністратор <@{ctx.message.author.id}> заблокував користувача <@{member.id}>. Причина: {str(reason)}',
                    color=discord.Color.red()  # Колір вбудованого повідомлення
                )

                await ctx.guild.ban(member, reason=reason)
                await ctx.message.delete()
                # Створення об'єкта вбудованого повідомлення
                await ctx.send(embed=embed)
            else:
                await ctx.send('У вас недостатньо прав для блокування користувачів.')
    
@bot.command(name='clear')
async def clear(ctx, amount: int = 0):
    role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if role not in ctx.author.roles:
        await ctx.send(f'<@{ctx.author.id}>, у вас немає прав на використання даної команди.')
        return
    else:
        # Змінив message_content на 'Processing...'
        # Перевірка, чи вказано коректну кількість повідомлень для видалення
        if amount is None or amount <= 0:
            await ctx.send(f'<@{ctx.author.id}>, будь ласка, вкажіть коректну кількість повідомлень для видалення.', delete_after=10)
            return

        # Видалення повідомлень
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 для включення оригінального повідомлення

        # Відправлення повідомлення про кількість видалених повідомлень
        await ctx.send(f'**✅ Успішно видалено {len(deleted) - 1} повідомлень.**')  # -1, оскільки ми включили оригінальне повідомлення

@bot.command(name='profile')
async def profile(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    embed = discord.Embed(
        title=f'Профіль користувача {member}',
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.avatar)  # Додаємо зображення аватара користувача

    embed.add_field(name='Ім\'я', value=member.name, inline=True)
    embed.add_field(name='Тег', value=member.discriminator, inline=True)
    embed.add_field(name='ID', value=member.id, inline=False)
    
    # Отримання ролей користувача та додавання їх до Embed
    roles_str = ', '.join([role.name for role in member.roles])
    embed.add_field(name='Інформація про акаунт', value=f'Дата регістрації акаунту: '+member.created_at.strftime('%d-%m-%Y %H:%M:%S')+
    '\nДата приєднання до гільдії: '+ member.joined_at.strftime('%d-%m-%Y %H:%M:%S') , inline=False)

    #embed.set_footer(text=f'Запитано {ctx.author.name}', icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)
bot.run('MTEyODM2NTQ2MTQ0MTA5NzcyOA.GOl2JP.ZX1VDMB0N6VtqRKh12M_GctoeWC2MWe91MYOGU')