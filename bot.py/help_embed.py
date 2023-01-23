import discord

async def get_help_embed(member):
    embed = discord.Embed(title="Help", description="List of commands:", color=0x3091ff)
    embed.add_field(name="&setwelcomechannel", value="Sets the welcome channel for the current server", inline=False)
    embed.add_field(name="&getwelcomechannel", value="Gets the welcome channel for the current server", inline=False)
    embed.add_field(name="&hello", value="Says Hii!", inline=False)
    embed.add_field(name="&mf", value= " Replies latom!", inline=False)
    #embed.set_thumbnail(url= member.guild.avator)
    embed.set_image(url= "https://cdn.discordapp.com/attachments/998612463492812822/1067016016485416990/maxresdefault.jpg")
    embed.set_footer(text= f"Requested by {member.name}", icon_url = member.avatar)
    return embed