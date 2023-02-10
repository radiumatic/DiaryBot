import textwrap
import discord,os
from discord.ext import commands
from make_online_bot_server import alive
import io
import contextlib
import requests,json, shutil, random, string, pymongo
from events import Notebook
import yt_dlp
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.environ.get('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='d.', intents=intents)
bot.remove_command('help')

HelpEmbed = discord.Embed(title="راهنما", description="**نکته مهم**\nاین بات تنها در دی ام فردی که هنگام تنظیم بات مشخص شده است کار خواهد کرد و این کامند ها اصل بات نیستند.", color=0x00ff00)
HelpEmbed.add_field(name="d.help", value="نمایش راهنمای بات", inline=False)
HelpEmbed.add_field(name="d.ping", value="میزان تاخیر بات", inline=False)
HelpEmbed.add_field(name="d.avatar", value="نمایش آواتار شما", inline=False)
HelpEmbed.add_field(name="d.serverinfo", value="نمایش اطلاعات سرور", inline=False)
HelpEmbed.add_field(name="d.userinfo", value="نمایش اطلاعات کاربر", inline=False)
HelpEmbed.add_field(name="d.run", value="اجرای کد پایتون دریافتی(تنها مختص صاحب بات)", inline=False)

DBClient = pymongo.MongoClient(os.getenv("DB"))
DB = DBClient.diarybot
Collection = DB.diary.diary
Owner = int(os.getenv('OWNER'))


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


@bot.command()
async def link2discord(ctx, *, args):
    a = args.split(" ")
    async with ctx.typing():
        r = requests.get(a[0], stream=True)
        file_name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
        while os.path.exists(os.path.join(os.getcwd(),f"{file_name}.{a[1]}")):
            file_name = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6))
        if int(r.headers.get('content-length', 0)) > 8388608:
            embed=discord.Embed(title="خطا",description="داداش بزرگه\nبا وازلین هم رد نمیشه از فیلتر دیسکورد",color=0xFF0000)
            await ctx.reply(embed=embed)
            return 
        if r.status_code == 200:
            with open(f"{file_name}.{a[1]}", 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            embed=discord.Embed(title="خطا",description=f"داش لینکت یا من یا یه چیزی ایراد داشته تو شبکه\nحوصله ندارم خودت یه نگاه بنداز:\n```{requests.text}```",color=0xFF0000)
            await ctx.reply(embed=embed)
            return
        await ctx.send(file=discord.File(f"{file_name}.{a[1]}"))
        os.remove(os.path.join(os.getcwd(),f"{file_name}.{a[1]}"))
@bot.command()
async def dlvid(ctx, *urls):
    await ctx.reply("Sure, your videos will soon arrive.")
    file_names = []
    vidprop = {
        'format':'[filesize_approx<=8M]/[filesize<=8M]',
        'outtmpl': '%(id)s.%(ext)s',
        'merge-output-format':'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }
    async with ctx.typing():
        try:
            with yt_dlp.YoutubeDL(vidprop) as ydl:
                for url in urls:
                    info = ydl.extract_info(url, download=True)
                    # Copy info dict and change video extension to audio extension
                    info_with_extension = json.loads(ydl.sanitize_info(info))
                    info_with_extension['ext'] = 'mp4'
                    # Return filename with the correct extension
                    file_names.append(ydl.prepare_filename(info_with_extension))
            for file_name in file_names:
                name=os.path.join(os.getcwd(),file_name)
                await ctx.send(file=discord.File(name))
                os.remove(name)
            await ctx.send("Lemme guess...\n We're finished?")
        except Exception as error:
            embed=discord.Embed(title="Error",description=f"Yeah yeah...\nJust understand this error and do fucking something about it\n```{error}```",color=0xFF0000)
            await ctx.reply(embed=embed)
@bot.command()
async def run(ctx, *, cmd):
    if ctx.author.id != Owner:
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

alive()
bot.add_cog(Notebook(Owner, Collection))
bot.run(os.getenv('TOKEN'))
