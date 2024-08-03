# main script for bot
import os
import discord
import controller
from dotenv import load_dotenv
from dataset_tools.retrieve_msg_history import retrieve

load_dotenv()
TOKEN = os.getenv('TEKTIM_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')

# lock for interactions: turn on when interacting with another server please :)
lock = False

#print(TOKEN)
intents=discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

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
    if(message.content.lower() == 'owo' or message.content.lower()=='uwu' and not lock):
        await message.channel.send('<:erm:1267111273275854908>')

    # admin: exception handling example
    elif (message.content.strip() == 'raise-exception' and message.author.strip() == 'tigm'):
        raise discord.DiscordException
    
    # admin: retrieve messages for dataset
    elif (message.content.strip() == 'retrieve-content' and message.author.strip() == 'tigm'):
        # bot response
        response = 'Affirmative: retrieving message history of this channel'
        await message.channel.send(response)

        # retrieve all messages: need to call retrieve_msg_history.py for this
        channel = 'temp'
        server = 'temp'
        retrieve(channel, server)
    
    # if some random message is seen respond to it here
    elif not message.attachments and not lock:
        print('\nAuthor: ', message.author)
        print('Message: ', message.content)
        response = controller.generate_response(message.content)
        await message.channel.send(response)

    # if an attachment is seen, send the attachments to 
    elif not lock:
        emoji = controller.generate_react_on_media(message.attachments)
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