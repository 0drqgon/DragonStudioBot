import os
import json
import discord
import asyncio
from discord.utils import get
from discord.ext import commands


CONFIG_PATH = 'settings.json'

if not os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as config_file:
        config_file.write('{"token": ""}')

with open('settings.json', 'r') as token_file:
    data = json.load(token_file)
TOKEN = data.get('token', None)

GUILD = '1073348814573928468'
EMOJI_BELL = '🔔'
EMOJI_GIVEAWAY = '🎉'
ROLE_BELL_ID = 1073682987482366014
ROLE_GIVEAWAY_ID = 1073683339841638410

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix="!")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.presences = True
intents.typing = True
intents.integrations = True
intents.webhooks = True
intents.invites = True
intents.voice_states = True
intents.dm_messages = True
intents.dm_reactions = True
intents.dm_typing = True
intents.guild_messages = True
intents.guild_reactions = True
intents.guild_typing = True

client = commands.Bot(intents=intents, command_prefix="!")


@client.event
async def on_ready():
    guild = get(client.guilds, name=GUILD)
    print(f'{client.user} has connected to Discord!')


@client.command()
async def ticket(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(
        title="Support Ticket",
        description="Click the button below to open a support ticket.",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed, view=TicketButtonView())

class TicketButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(TicketButton())

class TicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Open Ticket",
            style=discord.ButtonStyle.green,
            custom_id="open_ticket",
            emoji="🎫"
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.channel:
            return await interaction.response.send_message(
                "This button cannot be used in a direct message.",
                ephemeral=True
            )

        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
        category = discord.utils.get(guild.categories, name='Tickets')
        channel = await category.create_text_channel(
            name=f'ticket-{interaction.user.display_name}',
            overwrites=overwrites
        )
        await channel.send(f"{interaction.user.mention} Welcome!")
        embed = discord.Embed(
            title=f"Support Ticket - {interaction.user.display_name}",
            description="Please describe your issue. Support will be with you shortly.",
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=CloseButtonView())
        await interaction.response.send_message(
            content=f"You have successfully opened a ticket in {channel.mention}.",
            ephemeral=True
        )

class CloseButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(CloseButton())

class CloseButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Close Ticket",
            style=discord.ButtonStyle.red,
            custom_id="close_ticket",
            emoji="🔒"
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.channel:
            return await interaction.response.send_message(
                "This button cannot be used in a direct message.",
                ephemeral=True
            )
        
        # Rename the channel to "closed"
        await interaction.channel.edit(name=f"closed-{interaction.user.display_name}")
        
        # Remove the user's permissions to view the channel
        overwrites = interaction.channel.overwrites
        overwrites[interaction.user] = discord.PermissionOverwrite(read_messages=False)
        await interaction.channel.edit(overwrites=overwrites)
        
        await interaction.response.send_message(
            content=f"{interaction.user.mention}, your ticket has been closed.",
            ephemeral=True
        )



# Reaction Role function
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