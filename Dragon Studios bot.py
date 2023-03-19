import os
import json
import logging
import discord
import asyncio
import pytz
import datetime
from discord.utils import get
from discord.ext import commands


class Config:
	def __init__(self):
		self.path = 'settings.json'
		self.data = None
		self.default_settings = {
			"token": "",
			"server_info": {
				"announcement_role_id": None,
				"giveaway_role_id": None,
				"log_channel_id": None,
				"ticket_message_id": None
			}
		}

	def load(self) -> dict:
		exists = self._check_exists()
		if not exists:
			self._generate_defaults()
		self._load_file()
		is_valid = self.is_valid()
		if is_valid:
			return self.data
		return {}

	def _check_exists(self) -> bool:
		if os.path.exists(self.path) and os.path.isfile(self.path):
			return True
		return False

	def _generate_defaults(self) -> None:
		with open(self.path, 'w') as config_file:
			json.dump(self.default_settings, config_file, indent=4)

	def _load_file(self) -> None:
		try:
			with open(self.path, 'r') as config_file:
				self.data = json.load(config_file)
		except json.JSONDecodeError:
			logging.critical("Invalid json found for config file")
			self.data = {}
			logging.info("Force-regenerating config file")
			self._generate_defaults()

	def is_valid(self) -> bool:
		try:
			_data = self.data["token"]
			_server_info = self.data["server_info"]
			return True
		except IndexError:
			logging.critical("Invalid json found for config file")
			self.data = {}
			logging.info("Force-regenerating config file")
			self._generate_defaults()
			self._load_file()
		return False


config = Config().load()
token = config.get('token', None)
if token is None:
	logging.critical("Bot Token Not Found")
	exit(1)

if len(token) == 0:
	logging.critical("Bot Token Not Found")
	exit(1)

GUILD = '1073348814573928468'
EMOJI_BELL = '🔔'
EMOJI_GIVEAWAY = '🎉'
ROLE_BELL_ID = config.get('server_info', {}).get('announcement_role_id', None)
ROLE_GIVEAWAY_ID = config.get('server_info', {}).get('giveaway_role_id', None)
LOGS_CHANNEL_ID = config.get('server_info', {}).get('log_channel_id', None)
TICKET_MESSAGE_ID = config.get('server_info', {}).get('ticket_message_id', None)

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
intents.bans = True

client = commands.Bot(intents=intents, command_prefix="!")


@client.event
async def on_ready():
	guild = get(client.guilds, name=GUILD)
	print(f'{client.user} has connected to Discord!')
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is None:
		print(f"Logs channel with ID {LOGS_CHANNEL_ID} not found.")


@client.event
async def on_member_update(before, after):
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		if before.roles != after.roles:
			added_roles = set(after.roles) - set(before.roles)
			removed_roles = set(before.roles) - set(after.roles)
			embed = discord.Embed(
				description=f":writing_hand:{after.mention} **has been updated.**",
				color=discord.Color.blue(),
			)
			for role in added_roles:
				embed.add_field(name=f"Roles: {role.name} ", value=f":white_check_mark: <@&{role.id}> ", inline=False)
			for role in removed_roles:
				embed.add_field(name=f"Roles: {role.name} ", value=f":no_entry: <@&{role.id}> ", inline=False)
			embed.set_author(name=str(before), icon_url=after.display_avatar)
			embed.set_thumbnail(url=after.display_avatar)
			embed.timestamp = datetime.datetime.now()
			embed.set_footer(text=f"{after.guild.name}")
			await logs_channel.send(embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		if before.channel != after.channel and after.channel is not None:
			embed = discord.Embed(
				description=f"{member.mention} **joined {after.channel.name} voice channel**",
				color=discord.Color.orange()
			)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Server: {member.guild.name}")
			embed.set_author(name=str(member), icon_url=member.display_avatar)
			embed.timestamp = datetime.datetime.now()
			await logs_channel.send(embed=embed)

		if before.channel != after.channel and before.channel is not None:
			embed = discord.Embed(
				description=f"{member.mention} **left {before.channel.name} voice channel**",
				color=discord.Color.orange()
			)
			embed.set_thumbnail(url=member.display_avatar)
			embed.set_footer(text=f"Server: {member.guild.name}")
			embed.set_author(name=str(member), icon_url=member.display_avatar)
			embed.timestamp = datetime.datetime.now()
			await logs_channel.send(embed=embed)


@client.event
async def on_message_edit(before, after):
	if before.author.bot:
		return  # ignore edits by bots
	if before.content == after.content:
		return  # ignore edits that don't change the message content
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		embed = discord.Embed(
			description=f"✏️ **Message sent by {before.author.mention} edited in {before.channel.mention}**",
			color=discord.Color.blue(),
		)
		embed.set_author(name=before.author.display_name, icon_url=after.author.display_avatar)
		embed.add_field(name="Before", value=f"```{before.content}```", inline=False)
		embed.add_field(name="After", value=f"```{after.content}```", inline=False)
		embed.timestamp = datetime.datetime.now()
		embed.set_footer(text=f"{after.guild.name}")
		await logs_channel.send(embed=embed)


@client.event
async def on_message_delete(message):
	if message.author.bot:
		return  # ignore deletions by bots
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		embed = discord.Embed(
			title="Message deleted",
			description=f" 🗑️ **Message sent by {message.author.mention} deleted in {message.channel.mention}**",
			color=discord.Color.red(),
		)
		embed.add_field(name="Content:", value=message.content, inline=False)
		embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar)
		embed.timestamp = datetime.datetime.now()
		embed.set_footer(text=f"{message.guild.name}")
		await logs_channel.send(embed=embed)


@client.event
async def on_member_join(member):
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		account_age = datetime.datetime.now(pytz.utc) - member.created_at
		account_age_str = format_timedelta(account_age)
		creation_time_str = member.created_at.strftime("%d/%m/%Y %I:%M %p")
		embed = discord.Embed(
			description=f"{member.mention}**joined the server.**\n" \
			            f":timer: **Age of account:**\n`{creation_time_str}`\n**{account_age_str}**\n" \
			            "\n",
			color=0x00ff00
		)
	embed.set_thumbnail(url=member.display_avatar)
	embed.set_footer(text=f"Server: {member.guild.name}")
	embed.set_author(name=str(member), icon_url=member.display_avatar)
	embed.timestamp = datetime.datetime.now()
	await logs_channel.send(embed=embed)


def format_timedelta(td):
	total_seconds = int(td.total_seconds())
	years, remainder = divmod(total_seconds, 60 * 60 * 24 * 365)
	months, remainder = divmod(remainder, 60 * 60 * 24 * 30)
	days, remainder = divmod(remainder, 60 * 60 * 24)
	if years > 0:
		return f"{years} year{'s' if years != 1 else ''}"
	elif months > 0:
		return f"{months} month{'s' if months != 1 else ''}"
	else:
		return f"{days} day{'s' if days != 1 else ''}"


@client.event
async def on_member_unban(guild, user):
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
			if entry.target == user:
				embed = discord.Embed(
					description=f"{user.mention} **was unbanned from the server**\n**Reason:** {entry.reason}",
					color=discord.Color.green()
				)
				embed.set_thumbnail(url=user.display_avatar)
				embed.set_footer(text=f"Server: {guild.name}")
				embed.set_author(name=str(user), icon_url=user.display_avatar)
				embed.timestamp = datetime.datetime.now()
				await logs_channel.send(embed=embed)
				break


@client.event
async def on_member_remove(member):
	logs_channel = client.get_channel(LOGS_CHANNEL_ID)
	if logs_channel is not None:
		async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
			if entry.target == member:
				embed = discord.Embed(
					description=f"{member.mention} **was kicked from the server**\n**Reason:** {entry.reason}",
					color=discord.Color.red()
				)
				embed.set_thumbnail(url=member.display_avatar)
				embed.set_footer(text=f"Server: {member.guild.name}")
				embed.set_author(name=str(member), icon_url=member.display_avatar)
				embed.timestamp = datetime.datetime.now()
				await logs_channel.send(embed=embed)
				break
		else:
			async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
				if entry.target == member:
					if entry.before.roles != entry.after.roles:
						return
					else:
						embed = discord.Embed(
							description=f"{member.mention} **was banned from the server**\n**Reason:** {entry.reason}",
							color=discord.Color.red()
						)
						embed.set_thumbnail(url=member.display_avatar)
						embed.set_footer(text=f"Server: {member.guild.name}")
						embed.set_author(name=str(member), icon_url=member.display_avatar)
						embed.timestamp = datetime.datetime.now()
						await logs_channel.send(embed=embed)
						break
			else:
				embed = discord.Embed(
					description=f"{member.mention} **left the server**",
					color=discord.Color.red()
				)
				embed.set_thumbnail(url=member.display_avatar)
				embed.set_footer(text=f"Server: {member.guild.name}")
				embed.set_author(name=str(member), icon_url=member.display_avatar)
				embed.timestamp = datetime.datetime.now()
				await logs_channel.send(embed=embed)


# Ticket System
 # Load the stored ticket message ID (if available)
TICKET_MESSAGE_ID_FILE = 'settings.json'
if os.path.exists(TICKET_MESSAGE_ID_FILE):
    with open(TICKET_MESSAGE_ID_FILE, 'r') as f:
        TICKET_MESSAGE_ID = json.load(f)
else:
    TICKET_MESSAGE_ID = None

@client.command()
async def ticket(ctx):
    await ctx.channel.purge(limit=1)
    if TICKET_MESSAGE_ID is not None:
        # Use the stored message ID
        message = await ctx.channel.fetch_message(TICKET_MESSAGE_ID)
    else:
        # Create a new message and store its ID
        embed = discord.Embed(
            title="Support Ticket",
            description="Click the button below to open a support ticket.",
            color=discord.Color.blue()
        )
        message = await ctx.send(embed=embed, view=TicketButtonView())
        TICKET_MESSAGE_ID = message.id
        with open(TICKET_MESSAGE_ID_FILE, 'w') as f:
            json.dump(TICKET_MESSAGE_ID, f)


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


client.run(token=token)
