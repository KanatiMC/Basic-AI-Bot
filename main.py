import discord
from discord.ext import commands
import openai
import os
import json

def get_prefix(bot, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]
bot = commands.Bot(command_prefix = (get_prefix), intents=discord.Intents.all())
openai.api_key = os.getenv("OpenAIKey")

@bot.event
async def on_ready():
	print(f"Logged In As: {bot.user.name}#{bot.user.discriminator} | {bot.user.id}")
	response = openai.Completion.create(
  model="text-davinci-002",
  prompt="give me a short random quote",
  temperature=0.7,
  max_tokens=3500,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
	)
	await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{str(response['choices'][0]['text'])} | !help"))

@bot.command()
async def ai(ctx, *, question):
	global lastAIPrompt
	global lastAIId
	response = openai.Completion.create(
  model="text-davinci-002",
  prompt=question,
  temperature=0.7,
  max_tokens=3500,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
	)
	a = await ctx.reply(response['choices'][0]['text'])
	lastAIPrompt = question
	lastAIId = a.id
	await a.add_reaction(u"\U0001F504")

@bot.command()
async def ping(ctx):
  await ctx.send(f"My Ping Is Approximately {round(bot.latency * 1000)} ms.")

@bot.command()
async def invite(ctx):
	embed=discord.Embed(title="My Invite Link", url="https://discord.com/api/oauth2/authorize?client_id=1027404239871426610&permissions=10240&scope=bot")
	await ctx.reply(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def prefix(ctx, prefix):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes[str(ctx.guild.id)] = prefix

	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

	await ctx.reply(f'Prefix Is Now: {prefix}')

@bot.event
async def on_guild_join(guild):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes[str(guild.id)] = '!'

	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

@bot.event
async def on_guild_remove(guild):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes.pop(str(guild.id))

	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

@bot.event
async def on_message(message):
	if bot.user.mentioned_in(message):
		await message.channel.send(f"My prefix is {prefix_check(message.guild)}")
	await bot.process_commands(message)

def prefix_check(guild):
	if guild == None:
		return "!"
	try:
		with open('prefixes.json', 'r') as f:
			prefixes = json.load(f)
		p = prefixes[str(guild.id)]
	except:
		p = "!"

	return p

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.ConversionError):
		embed=discord.Embed(title="Error!", description=error,color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.MissingRequiredArgument):
		embed=discord.Embed(title="Error!", description=f"Missing Required Arguments: `{error.param}`",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.BadArgument):
		embed=discord.Embed(title="Error!", description=error,color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.ArgumentParsingError):
		embed=discord.Embed(title="Error!", description=error,color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.PrivateMessageOnly):
		embed=discord.Embed(title="Error!", description=error,color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.NoPrivateMessage):
		embed=discord.Embed(title="Error!", description=error,color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.MissingPermissions):
		perms = ", ".join(f"`{perm.replace('_', ' ').title()}`" for perm in error.missing_perms)
		embed=discord.Embed(title="Error!", description=f"You're missing the permissions: {perms}",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.BotMissingPermissions):
		perms = ", ".join(f"`{perm.replace('_', ' ').title()}`" for perm in error.missing_perms)
		embed=discord.Embed(title="Error!", description=f"I'm missing the permissions: {perms}",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.DisabledCommand):
		embed=discord.Embed(title="Error!", description=f"{ctx.command.qualified_name}` Is Actively Disabled",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.MaxConcurrencyReached):
		embed=discord.Embed(title="Error!", description=f"`{ctx.command.qualified_name}` Can Only Be Used {error.number} Command At A Time Under {str(error.per)}",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)
	elif isinstance(error, commands.CommandNotFound):
		embed = discord.Embed(title="Command Not Found!",description=f"That Command Doesn't Exist, Type `{prefix_check(ctx.guild)}help` To See All Commands",color=ctx.author.top_role.color)
		await ctx.reply(embed=embed)
		print(error)

@bot.event
async def on_raw_reaction_add(payload):
	global lastAIPrompt
	global lastAIId
	guild = bot.get_guild(payload.guild_id)
	channel = guild.get_channel(payload.channel_id)
	user = await bot.fetch_user(payload.member.id)
	if payload.member.id != bot.user.id and str(payload.emoji) == u"\U0001F504" and payload.message_id == lastAIId:
		msg = await channel.fetch_message(lastAIId)
		response = openai.Completion.create(
		model="text-davinci-002",
		prompt=lastAIPrompt,
		temperature=0.7,
		max_tokens=3500,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
		)
	await msg.edit(content=response['choices'][0]['text'])
	try:
		await msg.remove_reaction(payload.emoji, user)
	except:
		await channel.send("Missing The Permission: `manage_messages`\n This Would Allow Me To Remove The User's Reaction, Allowing Them To Regenerate The AI With The Prompt Given.")


bot.run(os.getenv("token"))