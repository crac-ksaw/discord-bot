import discord  # type: ignore[reportMissingImports]

async def get_help_embed(member):
    embed = discord.Embed(title="Help", description="List of commands:", color=0x3091ff)
    embed.add_field(name="&setwelcomechannel", value="Sets the welcome channel for the current server", inline=False)
    embed.add_field(name="&getwelcomechannel", value="Gets the welcome channel for the current server", inline=False)
    embed.add_field(name="&hello", value="Says Hii!", inline=False)
    embed.add_field(name="&mf", value= " Replies latom!", inline=False)
    embed.add_field(name="&ask [question]", value="Ask the AI assistant anything!", inline=False)
    embed.add_field(name="&set ai_persona [text]", value="Change AI personality (Admin)", inline=False)
    embed.add_field(name="&imagine [prompt]", value="Generate an image from text (Stability SDXL).", inline=False)
    embed.add_field(name="&set [option] [value]", value="Configure bot settings (Admin only)", inline=False)
    embed.add_field(name="&settings", value="View current bot settings (Admin only)", inline=False)
    #embed.set_thumbnail(url= member.guild.avator)
    embed.set_image(url= "https://cdn.discordapp.com/attachments/998612463492812822/1067016016485416990/maxresdefault.jpg")
    embed.set_footer(text= f"Requested by {member.name}", icon_url = member.avatar)
    return embed