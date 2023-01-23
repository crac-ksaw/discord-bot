import discord 
import tracemalloc
import os
import asyncio
import time
from dotenv import load_dotenv
from help_embed import get_help_embed

load_dotenv()
token = os.getenv("TOKEN")

client = discord.Client(intents=discord.Intents.all())

welcome_channels = {}

prefix = "&"

# Keep track of the last time a command was used
last_command_time = None

async def update_presence(client):
    global last_command_time
    while True:
        if last_command_time is None:
            # The bot is idle
            await client.change_presence(status=discord.Status.idle,
            activity = discord.Activity(type=discord.ActivityType.playing, name = "Dynamically"))
        else:
            current_time = time.time()
            if current_time - last_command_time > 120:
                # No one has used a command in the last 2 minutes
                last_command_time = None
                await client.change_presence(status=discord.Status.idle,
                activity = discord.Activity(type=discord.ActivityType.playing, name = "Dynamically"))
            else:
                await client.change_presence(status=discord.Status.online,
                activity = discord.Activity(type=discord.ActivityType.listening, name = "help"))
        await asyncio.sleep(1)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")
    # Start the presence update loop
    client.loop.create_task(update_presence(client))

@client.event
async def on_message(message):
    global last_command_time
    if message.content.startswith(prefix):
        command = message.content[len(prefix):]

        # Set welcome channel command
        if command.startswith("setwelcomechannel"):
            # Check if the user is an admin
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You have to be an admin to set the welcome channel.")
                return
            # Set the welcome channel for the current server
            welcome_channels[message.guild.id] = message.channel
            await message.channel.send(f"Welcome channel set to {message.channel.name}.")

        # Get welcome channel command
        if command.startswith("getwelcomechannel"):
            # Check if the welcome channel has been set for the current server
            welcome_channel = welcome_channels.get(message.guild.id)
            if welcome_channel is None:
                await message.channel.send("Welcome channel is not set.")
            else:
                await message.channel.send(f"Welcome channel is set to {welcome_channel.name}.")
        if command.startswith("hello"):
            await message.channel.send("Hii!")
        if command.startswith("mf"):
            await message.reply("latom!",mention_author=True)
        if command.startswith("help"):
            embed = await get_help_embed(message.author)
            await message.channel.send(embed=embed)
        #update the last command time
        last_command_time = time.time()

@client.event
async def on_member_join(member):
    # Get the welcome channel for the server the user is joining
    welcome_channel = welcome_channels.get(member.guild.id)
    # Send the welcome message
    if welcome_channel:
        embed = discord.Embed(title="Welcome!", description=f"Ara ara! {member.mention}, welcome to **{member.guild.name}**! Hope you find Peace here.", color=0xfc30ff)
        embed.set_image(url= 'https://cdn.discordapp.com/attachments/998612463492812822/1063409897871511602/welcome.png')
        embed.set_thumbnail(url= member.avatar)
        embed.set_footer(text=f"{member.name} joined!") #icon_url= member.avatar
        await welcome_channel.send(embed=embed)

tracemalloc.start()
client.run(token)
