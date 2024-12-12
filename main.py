# main script for bot
import os
import discord
import controller
from dotenv import load_dotenv
import tensorflow as tf

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('TEKTIM_TOKEN')
GUILD = os.getenv('DISCORD_SERVER')

#print(TOKEN)
intents=discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#grab the model
img_model = tf.keras.models.load_model('data/models/raw/resnet.keras')
dog_model = tf.keras.models.load_model('data/models/raw/dogcat.keras')

# event handling
@bot.event
async def on_ready():
    # locate the server that is in your env variable
    guild = discord.utils.get(bot.guilds, name=GUILD)

    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

'''
# bot response for user joining server
@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send('nyuck')
'''
# bot response for messages in general
# this section should be used for natural bot interaction
@bot.event
async def on_message(message):
    await bot.process_commands(message)

    # ignore message sent by itself
    if message.author == bot.user:
        return

    # respond with emoji at this cringe behavior
    if(message.content.lower() == 'owo' or message.content.lower()=='uwu'):
        await message.channel.send('<:erm:1267111273275854908>')

    # admin: exception handling example
    elif (message.content.strip() == 'raise-exception' and message.author.strip() == 'tigm'):
        raise discord.DiscordException
    
    if isinstance(message.channel, discord.DMChannel) or (message.content != "" and bot.user in message.mentions):
        print('\nAuthor: ', message.author)
        print('Message: ', message.content)

        # filter the mention out of the original message
        mention_format = f"<@{bot.user.id}>"
        msg = message.content.replace(mention_format, "")

        # create and return a response
        response = controller.generate_response(msg)
        await message.channel.send(response)

    # if an attachment is seen, send the attachments to 
    if message.attachments:
        emoji = controller.generate_react_on_media(message.attachments, img_model)
        if emoji != '':
            await message.add_reaction(emoji)

# section for specific commands
# this section should be used for direct bot interaction
@bot.command(name='av', help='Shows the full discord picture of the user')
async def show_avatar(ctx, member: discord.Member = None):
    # If no member is mentioned, default to the author
    member = member or ctx.author

    # Get the user's profile picture URL
    profile_url = member.avatar.url if member.avatar else member.default_avatar.url

    # Create an embed with the profile picture
    embed = discord.Embed(
        title=f"{member.name}"
    )
    embed.set_image(url=profile_url)
    await ctx.send(embed=embed)

@bot.command(name='dog', help='Whether you are big dawg or not')
async def big_dog(ctx, member: discord.Member = None):
    member = member or ctx.author
    avatar = member.avatar if member.avatar else member.default_avatar

    # get response
    response = controller.check_dogness(avatar, dog_model)
    await ctx.send(response)

# error-handling. Gets sent to err.log
@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

bot.run(TOKEN)