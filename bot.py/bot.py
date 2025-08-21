import discord  # type: ignore[reportMissingImports]
from discord import app_commands  # type: ignore[reportMissingImports]
import tracemalloc
import os
import asyncio
import time
import google.generativeai as genai  # type: ignore[reportMissingImports]
import requests
import io
import base64
from dotenv import load_dotenv  # type: ignore[reportMissingImports]
from help_embed import get_help_embed

load_dotenv()
# Fix Windows asyncio shutdown noise ("Event loop is closed")
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
token = os.getenv("TOKEN")
# Configure Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

client = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(client)

welcome_channels = {}
bot_settings = {}  # Store bot settings per server

prefix = "&"

# Keep track of the last time a command was used
last_command_time = None

# AI chat function (Gemini REST API - v1beta generateContent)
async def get_ai_response(prompt, guild_id=None):
    try:
        # Get server-specific settings or use defaults
        if guild_id and guild_id in bot_settings:
            settings = bot_settings[guild_id]
            model = settings.get("ai_model", "gemini-2.0-flash")
            temperature = settings.get("ai_temperature", 0.7)
            max_tokens = settings.get("ai_max_tokens", 500)
            persona = settings.get(
                "ai_persona",
                "Talk like a casual, rowdy friend: cheeky, energetic, a bit teasing; use light slang and occasional emojis. Keep it short and helpful. No profanity, slurs, NSFW, harassment, hate, or personal attacks. Follow Discord rules."
            )
        else:
            model = "gemini-2.0-flash"
            temperature = 0.7
            max_tokens = 500
            persona = "Talk like a casual, rowdy friend: cheeky, energetic, a bit teasing; use light slang and occasional emojis. Keep it short and helpful. No profanity, slurs, NSFW, harassment, hate, or personal attacks. Follow Discord rules."
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "GEMINI_API_KEY is not set."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": api_key,
        }
        payload = {
            "systemInstruction": {
                "parts": [{"text": persona}]
            },
            "contents": [
                {"parts": [{"text": str(prompt)}]}
            ],
            "generationConfig": {
                "temperature": float(temperature),
                "maxOutputTokens": int(max_tokens),
            },
        }

        http_resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if http_resp.status_code != 200:
            return f"Gemini API error: {http_resp.status_code} {http_resp.text}"
        data = http_resp.json()
        # Extract first candidate text
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return str(data)
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

async def generate_image(prompt, guild_id=None):
    try:
        # Stable Diffusion via Stability AI REST API (single fixed model)
        engine = "stable-diffusion-xl-1024-v1-0"
        stability_key = os.getenv("STABILITY_API_KEY")
        if not stability_key:
            return (False, "STABILITY_API_KEY is not set.")
        url = f"https://api.stability.ai/v1/generation/{engine}/text-to-image"
        headers = {
            "Authorization": f"Bearer {stability_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "text_prompts": [{"text": str(prompt)}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }
        http_resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if http_resp.status_code != 200:
            return (False, f"Stability API error: {http_resp.status_code} {http_resp.text}")
        data = http_resp.json()
        artifacts = data.get("artifacts", [])
        if not artifacts:
            return (False, str(data))
        b64 = artifacts[0].get("base64")
        if not b64:
            return (False, "No image data returned.")
        image_bytes = base64.b64decode(b64)
        return (True, image_bytes)
    except Exception as e:
        return (False, f"Sorry, I couldn't generate an image: {str(e)}")

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
    # Sync slash commands
    try:
        # 1) For each guild: wipe existing guild-specific commands so only global remain
        for guild in client.guilds:
            gobj = discord.Object(id=guild.id)
            try:
                existing_guild_cmds = await tree.fetch_commands(guild=gobj)
                if existing_guild_cmds:
                    for cmd in existing_guild_cmds:
                        try:
                            await tree.delete_command(cmd.id, guild=gobj)
                        except Exception:
                            pass
            except Exception:
                pass
            # Ensure guild has no per-guild commands
            await tree.sync(guild=gobj)
        # 2) Register only GLOBAL commands to avoid duplicates
        synced = await tree.sync()
        print(f"Slash commands globally synced: {len(synced)} commands. Guilds cleaned: {len(client.guilds)}")
    except Exception as e:
        print(f"Failed to sync slash commands: {e}")

@tree.command(name="ask", description="Ask the AI assistant anything")
@app_commands.describe(question="Your question for the AI")
async def slash_ask(interaction: discord.Interaction, question: str):
    # Show the thinking indicator
    await interaction.response.defer(thinking=True)
    reply = await get_ai_response(question, interaction.guild.id if interaction.guild else None)
    if not reply:
        reply = "Sorry, I couldn't generate a response."
    if len(reply) > 2000:
        for i in range(0, len(reply), 1990):
            await interaction.followup.send(reply[i:i+1990])
    else:
        await interaction.followup.send(reply)

@tree.command(name="imagine", description="Generate an image from a prompt")
@app_commands.describe(prompt="Describe the image you want")
async def slash_imagine(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    ok, result = await generate_image(prompt, interaction.guild.id if interaction.guild else None)
    if not ok:
        await interaction.followup.send(str(result))
    else:
        file = discord.File(io.BytesIO(result), filename="image.png")
        await interaction.followup.send(file=file)

@tree.command(name="hello", description="Say hi")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hii!")

@tree.command(name="mf", description="Replies 'latom!'")
async def slash_mf(interaction: discord.Interaction):
    await interaction.response.send_message("latom!")

@tree.command(name="setwelcomechannel", description="Set the welcome channel (Admin only)")
@app_commands.describe(channel="Channel to send welcome messages in")
async def slash_setwelcome(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:  # type: ignore[attr-defined]
        await interaction.response.send_message("You have to be an admin to set the welcome channel.", ephemeral=True)
        return
    welcome_channels[interaction.guild.id] = channel  # type: ignore[union-attr]
    await interaction.response.send_message(f"Welcome channel set to {channel.mention}.")

@tree.command(name="getwelcomechannel", description="Show the current welcome channel")
async def slash_getwelcome(interaction: discord.Interaction):
    channel = welcome_channels.get(interaction.guild.id if interaction.guild else 0)
    if channel is None:
        await interaction.response.send_message("Welcome channel is not set.")
    else:
        await interaction.response.send_message(f"Welcome channel is set to {channel.mention}.")

@tree.command(name="settings", description="View current bot settings (Admin only)")
async def slash_settings(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:  # type: ignore[attr-defined]
        await interaction.response.send_message("You have to be an admin to view bot settings.", ephemeral=True)
        return
    if interaction.guild and interaction.guild.id in bot_settings:
        settings = bot_settings[interaction.guild.id]
        embed = discord.Embed(title="Bot Settings", description=f"Current settings for **{interaction.guild.name}**", color=0x00ff00)
        embed.add_field(name="Prefix", value=f"`{settings.get('prefix', '&')}`", inline=True)
        embed.add_field(name="AI Model", value=f"`{settings.get('ai_model', 'gemini-1.5-flash')}`", inline=True)
        embed.add_field(name="AI Temperature", value=f"`{settings.get('ai_temperature', 0.7)}`", inline=True)
        embed.add_field(name="AI Max Tokens", value=f"`{settings.get('ai_max_tokens', 500)}`", inline=True)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("No custom settings found. Using default settings.")

@tree.command(name="help", description="Show available commands")
async def slash_help(interaction: discord.Interaction):
    embed = await get_help_embed(interaction.user)
    await interaction.response.send_message(embed=embed)

@client.event
async def on_guild_join(guild: discord.Guild):
    # Ensure slash commands appear immediately when the bot joins a new guild
    try:
        await tree.sync(guild=guild)
        print(f"Slash commands synced to new guild: {guild.id}")
    except Exception as e:
        print(f"Failed syncing to new guild {guild.id}: {e}")

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
        if command.startswith("imagine"):
            img_prompt = command[len("imagine"):].strip()
            if not img_prompt:
                await message.channel.send("Please provide a prompt! Usage: `&imagine your prompt`")
                return
            async with message.channel.typing():
                ok, result = await generate_image(img_prompt, message.guild.id if message.guild else None)
                if not ok:
                    await message.channel.send(str(result))
                else:
                    file = discord.File(io.BytesIO(result), filename="image.png")
                    await message.channel.send(file=file)
        
        # AI chat command
        if command.startswith("ask"):
            # Extract the question from the command
            question = command[4:].strip()  # Remove "ask " from the beginning
            if not question:
                await message.channel.send("Please provide a question! Usage: `&ask your question here`")
                return
            
            # Show typing indicator while processing
            async with message.channel.typing():
                response = await get_ai_response(question, message.guild.id)
                # Send only the AI's reply without any prefix or the asked question
                if not response:
                    response = "Sorry, I couldn't generate a response."
                # Discord message limit is 2000 characters; chunk if needed
                if len(response) > 2000:
                    for i in range(0, len(response), 1990):
                        await message.channel.send(response[i:i+1990])
                else:
                    await message.channel.send(response)
        
        # Set command for bot configuration
        if command.startswith("set"):
            # Check if the user is an admin
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You have to be an admin to change bot settings.")
                return
            
            # Parse the set command
            set_args = command[4:].strip().split()  # Remove "set " and split arguments
            if len(set_args) < 2:
                await message.channel.send("Usage: `&set <option> <value>`\nAvailable options: `prefix`, `ai_model`, `ai_temperature`, `ai_max_tokens`, `ai_persona`")
                return
            
            option = set_args[0].lower()
            value = " ".join(set_args[1:])
            
            # Initialize settings for this server if not exists
            if message.guild.id not in bot_settings:
                bot_settings[message.guild.id] = {
                    "prefix": "&",
                    "ai_model": "gemini-2.0-flash",
                    "ai_temperature": 0.7,
                    "ai_max_tokens": 500
                }
            
            # Handle different setting options
            if option == "prefix":
                if len(value) > 3:
                    await message.channel.send("Prefix must be 3 characters or less.")
                    return
                bot_settings[message.guild.id]["prefix"] = value
                await message.channel.send(f"Bot prefix set to: `{value}`")
                
            elif option == "ai_model":
                valid_models = [
                    "gemini-2.0-flash",
                    "gemini-2.0-pro",
                ]
                if value not in valid_models:
                    await message.channel.send(f"Invalid AI model. Available models: {', '.join(valid_models)}")
                    return
                bot_settings[message.guild.id]["ai_model"] = value
                await message.channel.send(f"AI model set to: `{value}`")
                
            elif option == "ai_temperature":
                try:
                    temp = float(value)
                    if temp < 0 or temp > 2:
                        await message.channel.send("Temperature must be between 0 and 2.")
                        return
                    bot_settings[message.guild.id]["ai_temperature"] = temp
                    await message.channel.send(f"AI temperature set to: `{temp}`")
                except ValueError:
                    await message.channel.send("Temperature must be a number between 0 and 2.")
                    
            elif option == "ai_max_tokens":
                try:
                    tokens = int(value)
                    if tokens < 50 or tokens > 2000:
                        await message.channel.send("Max tokens must be between 50 and 2000.")
                        return
                    bot_settings[message.guild.id]["ai_max_tokens"] = tokens
                    await message.channel.send(f"AI max tokens set to: `{tokens}`")
                except ValueError:
                    await message.channel.send("Max tokens must be a number between 50 and 2000.")
            
            elif option == "ai_persona":
                if len(value) > 800:
                    await message.channel.send("Persona is too long (max 800 characters).")
                    return
                bot_settings[message.guild.id]["ai_persona"] = value
                await message.channel.send("AI persona updated.")
                    
            elif option in ("image_model", "image_provider"):
                await message.channel.send("Image generation is fixed to Stability SDXL; no image settings to change.")

            else:
                await message.channel.send("Unknown setting. Available options: `prefix`, `ai_model`, `ai_temperature`, `ai_max_tokens`")
        
        # View settings command
        if command.startswith("settings"):
            # Check if the user is an admin
            if not message.author.guild_permissions.administrator:
                await message.channel.send("You have to be an admin to view bot settings.")
                return
            
            # Get current settings for this server
            if message.guild.id in bot_settings:
                settings = bot_settings[message.guild.id]
                embed = discord.Embed(title="Bot Settings", description=f"Current settings for **{message.guild.name}**", color=0x00ff00)
                embed.add_field(name="Prefix", value=f"`{settings.get('prefix', '&')}`", inline=True)
                embed.add_field(name="AI Model", value=f"`{settings.get('ai_model', 'gemini-2.0-flash')}`", inline=True)
                embed.add_field(name="AI Temperature", value=f"`{settings.get('ai_temperature', 0.7)}`", inline=True)
                embed.add_field(name="AI Max Tokens", value=f"`{settings.get('ai_max_tokens', 500)}`", inline=True)
                persona_preview_full = settings.get('ai_persona', '')
                persona_preview = (persona_preview_full[:80] + '…') if len(persona_preview_full) > 80 else (persona_preview_full or 'default rowdy persona')
                embed.add_field(name="AI Persona", value=f"`{persona_preview}`", inline=False)
                # Image settings are fixed to Stability SDXL
                embed.set_footer(text=f"Requested by {message.author.name}", icon_url=message.author.avatar)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send("No custom settings found. Using default settings.")
        
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
