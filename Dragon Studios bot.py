import discord
from discord.utils import get
from discord.ext import commands

TOKEN = 'MTA4NDE5NDgzNjA3NDIwNTI4NQ.Gv0Quq.RhcLDVKlP1Xf6ubVa2aXC-tzhDVS6NpfAWhIoY'
GUILD = '1073348814573928468'
EMOJI_BELL = '🔔'
EMOJI_GIVEAWAY = '🎉'
ROLE_BELL_ID = 1073682987482366014
ROLE_GIVEAWAY_ID = 1073683339841638410

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix="!")


@client.event
async def on_ready():
    guild = get(client.guilds, name=GUILD)
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == EMOJI_BELL:
        guild = client.get_guild(payload.guild_id)
        role = guild.get_role(ROLE_BELL_ID)
        await payload.member.add_roles(role)
    elif payload.emoji.name == EMOJI_GIVEAWAY:
        guild = client.get_guild(payload.guild_id)
        role = guild.get_role(ROLE_GIVEAWAY_ID)
        await payload.member.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name == EMOJI_BELL:
        guild = client.get_guild(payload.guild_id)
        role = guild.get_role(ROLE_BELL_ID)
        member = await guild.fetch_member(payload.user_id)
        if role.id in [_role.id for _role in member.roles]:
            await member.remove_roles(role)
    elif payload.emoji.name == EMOJI_GIVEAWAY:
        guild = client.get_guild(payload.guild_id)
        role = guild.get_role(ROLE_GIVEAWAY_ID)
        member = await guild.fetch_member(payload.user_id)
        if role.id in [_role.id for _role in member.roles]:
            await member.remove_roles(role)


@client.command()
async def generate(ctx):
    if ctx.message.content == "!generate":
        embed = discord.Embed()
        embed.colour = discord.Colour(0xE2340F)
        embed.description = "To get roles related to different pings in this discord, check the emoji related to the role!\n" \
                            "\n" \
                            "\n" \
                            "Announcements: :bell:\n" \
                            "\n" \
                            "Giveaways: :tada:"
        message = await ctx.send(embed=embed)
        await message.add_reaction(EMOJI_BELL)
        await message.add_reaction(EMOJI_GIVEAWAY)


client.run(token=TOKEN)
