import textwrap
import discord,os
from discord.ext import commands
from make_online_bot_server import alive
import io
import contextlib
import requests, shutil, random, string
TOKEN = os.environ.get('TOKEN')
bot = commands.Bot(command_prefix='d.')
bot.remove_command('help')

HelpEmbed = discord.Embed(title="راهنما", description="**نکته مهم**\nاین بات تنها در دی ام فردی که هنگام تنظیم بات مشخص شده است کار خواهد کرد و این کامند ها اصل بات نیستند.", color=0x00ff00)
HelpEmbed.add_field(name="d.help", value="نمایش راهنمای بات", inline=False)
HelpEmbed.add_field(name="d.ping", value="میزان تاخیر بات", inline=False)
HelpEmbed.add_field(name="d.avatar", value="نمایش آواتار شما", inline=False)
HelpEmbed.add_field(name="d.serverinfo", value="نمایش اطلاعات سرور", inline=False)
HelpEmbed.add_field(name="d.userinfo", value="نمایش اطلاعات کاربر", inline=False)
HelpEmbed.add_field(name="d.run", value="اجرای کد پایتون دریافتی(تنها مختص صاحب بات)", inline=False)

Owner = os.getenv('OWNER')


@bot.event
async def on_ready():
    print(f'{bot.user.name} with id: {bot.user.id} is online')
    await bot.change_presence(activity=discord.Game(name='d.help'))
    
@bot.command()
async def help(ctx):
    await ctx.reply(embed=HelpEmbed)


@bot.command()
async def ping(ctx):
    await ctx.reply(f'Pong! {round(bot.latency * 1000)}ms')


@bot.command()
async def avatar(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    await ctx.reply(f'{member.avatar_url}')


@bot.command()
async def serverinfo(ctx):
    embed = discord.Embed(title=f'{ctx.guild.name}', description=f'{ctx.guild.description}', color=0x00ff00)
    embed.add_field(name='Owner', value=f'{ctx.guild.owner}', inline=False)
    embed.add_field(name='Members', value=f'{ctx.guild.member_count}', inline=False)
    embed.add_field(name='Region', value=f'{ctx.guild.region}', inline=False)
    embed.add_field(name='ID', value=f'{ctx.guild.id}', inline=False)
    await ctx.reply(embed=embed)


@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    embed = discord.Embed(title=f'{member}', description=f'{member.status}', color=0x00ff00)
    embed.add_field(name='ID', value=f'{member.id}', inline=False)
    embed.add_field(name='Nickname', value=f'{member.nick}', inline=False)
    embed.add_field(name='Joined at', value=f'{member.joined_at}', inline=False)
    embed.add_field(name='Created at', value=f'{member.created_at}', inline=False)
    embed.add_field(name='Roles', value=f'{member.roles}', inline=False)
    embed.add_field(name='Avatar', value=f'{member.avatar_url}', inline=False)
    await ctx.reply(embed=embed)


# @bot.command()
# async def run(ctx, *, code: str = None):
#     print(ctx.author,Owner)
#     if not str(ctx.author) == str(Owner):
#         await ctx.reply('You are not the owner of this bot!')
#         return
#     if not code:
#       embed=discord.Embed(title="خطا",description="منو سرکار گذاشتی یا خودتو که کامند میزنی ولی دستور نمیدی؟",color=0xFF0000)
#       embed.set_image(url="https://cdn.thingiverse.com/assets/83/5c/96/ee/81/featured_preview_Crm4_G3uns8_1.jpg")
#       await ctx.reply(embed)
#       return

#     str_obj = io.StringIO() #Retrieves a stream of data
#     try:
#       with contextlib.redirect_stdout(str_obj):
#         exec(code)
#       output=str_obj.getvalue()  
#     except Exception as error:
#       output=f"ارور داد :( :\n{error}"
#     embed=discord.Embed(title="ران شد :)",description=f"بیا اینم نتیجه:\n```python\n{output}```")
#     await ctx.reply(embed=embed)

@bot.command()
async def run(ctx, *, cmd):
    """Run input.
    Input is interpreted as newline seperated statements.
    Its just like Python shell,It runs your code and after running it returns the outputs created
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    ```
    print("5")
    ```
    It also supports await expressions.So you can manage your server with ease.
    """
    if str(ctx.author) != str(Owner):
        await ctx.reply('You are not the owner of this bot!')
        return
    env = {
        'bot': bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    #make possible to use await expressions
    executable_code = f'async def __ex(ctx):\n{textwrap.indent(cmd, "  ")}'
    StrObj = io.StringIO()
    exec(executable_code, env)
    try:
        with contextlib.redirect_stdout(StrObj):
            await eval(f'__ex(ctx)', env)
        result = StrObj.getvalue()
        if result == "python":result = "Nothing(There`s no output)"
        embed=discord.Embed(title="ران شد :)",description=f"بیا اینم نتیجه:\n```python\n{result}```")
        await ctx.reply(embed=embed)
    except Exception as error:
        embed=discord.Embed(title="خطا",description=f"{error}",color=0xFF0000)
        await ctx.reply(embed=embed)
@bot.command()
async def link2discord(ctx, *, link):
    async with ctx.typing():
        r = requests.get(link, stream=True)
        file_name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
        while os.path.exists(os.path.join(os.getcwd(),file_name)):
            file_name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
        if int(r.headers.get('content-length', 0)) > 1048576:
            embed=discord.Embed(title="خطا",description="داداش بزرگه\nبا وازلین هم رد نمیشه از فیلتر دیسکورد",color=0xFF0000)
            await ctx.reply(embed=embed)
            return 
        if r.status_code == 200:
            with open("tescct.mp4", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            embed=discord.Embed(title="خطا",description=f"داش لینکت یا من یا یه چیزی ایراد داشته تو شبکه\nحوصله ندارم خودت یه نگاه بنداز:\n```{requests.text}```",color=0xFF0000)
            await ctx.reply(embed=embed)
            return
        await ctx.send(file=discord.File('tescct.mp4'))
        os.remove(os.path.join(os.getcwd(),file_name))

        









alive()
bot.run(os.getenv('TOKEN'))