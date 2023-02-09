import discord
from discord.ext import commands
class Notebook (commands.Cog):
    def __init__ (self, owner, db):
        self.db = db
        self.OWNER = owner
    @commands.Cog.listener('on_message')
    async def Save(self, message):
        if message.channel.type == discord.ChannelType.private and message.author.id == self.OWNER:
            if message.attachments:
                self.db.insert_one({'text': message.content, 'attachments': [attach.url for attach in message.attachments]})
            else:
                self.db.insert_one({'text': message.content})
            await message.reply('Message saved!')

