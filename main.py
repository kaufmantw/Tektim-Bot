# main script for bot
import os
import discord
import controller
from dotenv import load_dotenv
import tensorflow as tf

load_dotenv()
TOKEN = os.getenv('TEKTIM_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')

#print(TOKEN)
intents=discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

#grab the model
img_model = tf.keras.models.load_model('data/models/raw/resnet.keras')

# event handling
@client.event
async def on_ready():
    # locate the server that is in your env variable
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

# bot response for user joining server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send('nyuck')

# bot response for messages
@client.event
async def on_message(message):
    # ignore message sent by itself
    if message.author == client.user:
        return

    # respond with emoji at this cringe behavior
    if(message.content.lower() == 'owo' or message.content.lower()=='uwu'):
        await message.channel.send('<:erm:1267111273275854908>')

    # admin: exception handling example
    elif (message.content.strip() == 'raise-exception' and message.author.strip() == 'tigm'):
        raise discord.DiscordException
    
    # if tektim is pinged, respond to the message
    if message.content != "" and client.user in message.mentions:
        print('\nAuthor: ', message.author)
        print('Message: ', message.content)

        # filter the mention out of the original message
        mention_format = f"<@{client.user.id}>"
        msg = message.content.replace(mention_format, "")

        # create and return a response
        response = controller.generate_response(msg)
        await message.channel.send(response)

    # if an attachment is seen, send the attachments to 
    if message.attachments:
        emoji = controller.generate_react_on_media(message.attachments, img_model)
        if emoji != '':
            await message.add_reaction(emoji)


# error-handling. Gets sent to err.log
@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

client.run(TOKEN)