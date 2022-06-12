import discord,os
import pymongo
from discord.ext.commands import Bot
bot = Bot(command_prefix='d.')
Client = pymongo.MongoClient(os.getenv["DB"])
DB = Client.diarybot
Collection = DB.diary
TOKEN = os.environ.get('TOKEN')
Owner = os.getenv('OWNER')
@bot.event
async def on_ready():
    print(f'{bot.user.name} with id: {bot.user.id} is online')
@bot.event
async def on_message(message):
    if message.channel.type != discord.ChannelType.private or str(message.author) != Owner:
        return
    #save message text and if it has image save it and save address of it(diary collection: {text: message.content, image: image_url})
    if message.attachments:
        Collection.diary.insert_one({'text': message.content, 'image': message.attachments[0].url})
    else:
        Collection.diary.insert_one({'text': message.content})
    await message.reply('Message saved!')

    await bot.process_commands(message)
bot.run(TOKEN)
