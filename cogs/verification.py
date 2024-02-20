from discord.ext import commands
import time, discord, random

current_time = time.time()

class Onmemberjoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cooldown = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.user)  # 1 use per 30 seconds per user
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
            logs = 1165690496249774242  # Замініть на ваш ID каналу для логів
            def generate_captcha_code():
            
                return ''.join(random.choices('0123456789ABCDEF', k=6))
            captcha_code = generate_captcha_code()
            verifyrole_id = 1209101181163540492
            verifyrole = discord.utils.get(member.guild.roles, id=verifyrole_id)
            embed = discord.Embed(title=f"🛡Перевірка", color=0x387eff)
            embed.set_thumbnail(url=avatar_url)
            embed.description = f'Вітаю, ви попали на наш сервер!\nЩоб потрапити на сервер потрібно ввести капчу.\n** Капча:** ``{captcha_code}``'
            embed.set_footer(text=time.ctime(time.time()))
            await member.send(embed=embed)
            await member.add_roles(verifyrole)
            def check(message):
                return message.author == member and message.content == captcha_code

            try:
                response = await self.bot.wait_for('message', check=check, timeout=60)
                embed = discord.Embed(title=f"Успішно!", color=0x63ff38)
                embed.set_thumbnail(url=avatar_url)
                embed.description = f'Ви успішно пройшли перевірку. Слава Україні!🇺🇦'
                embed.set_footer(text=time.ctime(time.time()))
                await member.send(embed=embed)

                channel = self.bot.get_channel(logs)
                current_time = time.time()
                await channel.send(f'``{time.ctime(current_time)} ``🔼Учасник {member.name}(``{member.id}``) приєднався на сервер | Дата регістрації: ``{member.created_at.strftime("%d-%m-%Y %H:%M:%S")}``')

                guild_id = 1154369014181671014
                welcome_channel_id = 1154369014940844135
                channel_id = 1167971043839852544

                memberrole_id = 1154705883847217212
                memberrole = discord.utils.get(member.guild.roles, id=memberrole_id)

                guild = self.bot.get_guild(guild_id)
                welcome_channel = self.bot.get_channel(welcome_channel_id)
                members_channel = self.bot.get_channel(channel_id)

                await members_channel.edit(name=f'🌙Учасники: {guild.member_count}')
                print('Вхід, канал було змінено!')
                await member.add_roles(memberrole)
                await member.remove_roles(verifyrole)
                embed = discord.Embed(title=f"Привіт!👋", color=0x7962D6)
                embed.set_thumbnail(url=avatar_url)
                embed.add_field(
                    name=f"Ласкаво просимо тебе на наш сервер! Ось канали, які тобі можуть знадобитись",
                    value='<#1154369014940844135> - тут основний чат, де ми всі спілкуємось\n<#1154395654945251398> - тут використовуємо всі команди ботів\n<#1154394799001051197> - тут написані правила серверу, можеш ознайомитись)\n',
                    inline=False
                )
                embed.add_field(
                    name=f"У нас навіть є свій Minecraft сервер!",
                    value='Інформацію про майнкрафт сервер ти можеш глянути тут: <#1196538563769139210>',
                    inline=False
                )
                embed.description = 'Бажаємо тобі всього найкращого, будь як в себе вдома) Слава Україні!'
                embed.set_footer(text='З повагою керівництво та адміністрація серверу')
                await welcome_channel.send(member.mention, embed=embed, delete_after=120)

            except TimeoutError:
                await member.send('Час вийшов. Спробуйте ще раз.')

        except Exception as e:
            print(f'Error in on_member_join: {e}')

async def setup(bot):
    await bot.add_cog(Onmemberjoin(bot))
