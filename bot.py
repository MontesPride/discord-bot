import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import time
import youtube_dl
import math

Client = discord.Client()
client = commands.Bot(command_prefix = "!")
client.remove_command("help")

music_players = {}
music_queues = {}

def check_queue(id):
	if music_queues[id] != []:
		player = music_queues[id].pop(0)
		music_players[id] = player
		player.start()
		#print(player.title)
		print("[check_queue] Kolejna piosenka")
	else:
		del music_players[id]
		print("[check_queue] Koniec kolejki")

@client.event
async def on_ready():
    print("Bot is online and connected to Discord!")
"""
@client.event
async def on_command_error(error, ctx):
	await client.send_message(ctx.message.author, "Error! Something went wrong!:robot:")
"""
"""@client.event
async def on_message(message):
"""

@client.command(pass_context = True)
async def love(ctx):
    userID = ctx.message.author.id
    await client.say("<@%s> I love you" % (userID))

@client.command(pass_context = True)
async def ping(ctx):
    userID = ctx.message.author.id
    await client.say("<@%s> Pong!" % (userID))

@client.command(pass_context = True)
async def say(ctx):
    message = ctx.message.content.split(" ")
    await client.say(" ".join(message[1:]))

@client.command(pass_context = True)
async def amIadmin(ctx):
	author = ctx.message.author
	if "486136721243766784" in [role.id for role in author.roles]:
		await client.say("<@%s> You are an admin!" % (author.id))
	else:
		await client.say("<@%s> You are not an admin!" % (author.id))

@client.command(pass_context = True)
async def members(ctx):
    members = ctx.message.server.members
    for member in members:
        print(member.id)

@client.command(pass_context = True)
async def channel(ctx):
	channel = ctx.message.author
	print(help(channel))
	print(help(channel.server))
	print(channel.server.members)

@client.command(pass_context = True)
async def isBotHere(ctx):
    members = ctx.message.author.voice.voice_channel
    if members != None:
	    members = members.voice_members
	    if client.user.id in [member.id for member in members]:
	        await client.say("I am here")
	    else:
	        await client.say("I am not here")
    else:
        await client.say("Enter voice channel to use this command")
"""
@client.command(pass_context = True)
async def is_ready(ctx):
	print(is_bot_ready)
	if is_bot_ready == True:
		await client.say("<@%s> I am fired up and ready to serve!" % (ctx.message.author.id)) 
	else:
		await client.say("<@%s> Give me a second" % (ctx.message.author.id))       
"""
#MUSIC PLAYER

@client.command(pass_context = True)
async def join(ctx):
	server = ctx.message.server
	if client.is_voice_connected(server):
		voice_client = client.voice_client_in(server)
		await voice_client.disconnect()
	channel = ctx.message.author.voice.voice_channel
	await client.join_voice_channel(channel)

@client.command(pass_context = True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    if voice_client != None:
    	await voice_client.disconnect()

@client.command(pass_context = True)
async def play(ctx, url):
	members = ctx.message.author.voice.voice_channel
	if members != None:
		server = ctx.message.server

		members = members.voice_members
		if client.user.id not in [member.id for member in members]:
			if client.is_voice_connected(server) and client.voice_client_in(server) != None:
				voice_client = client.voice_client_in(server)
				await voice_client.disconnect()
			channel = ctx.message.author.voice.voice_channel
			await client.join_voice_channel(channel)
		if client.voice_client_in(server) == None:
			channel = ctx.message.author.voice.voice_channel
			await client.join_voice_channel(channel)

		voice_client = client.voice_client_in(server)
		music_player = await voice_client.create_ytdl_player(url, after = lambda : check_queue(server.id))

		if server.id in music_queues:
			music_queues[server.id].append(music_player)
		else:
			music_queues[server.id] = [music_player]

		if server.id not in music_players:
			check_queue(server.id)

		if len(music_queues[server.id]) == 0:
			#await client.say("Let's jam, currently playing: **" + music_player.title + "**")
			await client.say("Let's jam, currently playing: **{}**".format(music_player.title))
		else:
			#await client.say("**" + music_player.title + "** succesfully queued. Position in queue: **" + str(len(music_queues[server.id])) + "**")
			await client.say("**{}** succesfully queued. Position in queue: **{}**".format(music_player.title, len(music_queues[server.id])))
	else:
		await client.say("Enter voice channel to use this command")

@client.command(pass_context = True)
async def pause(ctx):
	server = ctx.message.server
	if server.id in music_players:
		if music_players[server.id].is_playing():
			music_players[server.id].pause()

@client.command(pass_context = True)
async def resume(ctx):
	server = ctx.message.server
	if server.id in music_players:
		music_players[server.id].resume()

@client.command(pass_context = True)
async def skip(ctx):
	server = ctx.message.server
	if server.id in music_players:
		if music_players[server.id].is_playing():
			music_players[server.id].stop()

@client.command(pass_context = True)
async def stop(ctx):
	server = ctx.message.server
	if server.id in music_players:
		if music_players[server.id].is_playing():
			music_queues[server.id].clear()
			music_players[server.id].stop()

@client.command(pass_context = True)
async def volume(ctx, volume):
	try:
		volume = int(volume)
	except ValueError:
		await client.say("Volume must be a number between 0 and 200")
	else:
		if volume >= 0 and volume <= 200:
			volume = volume / 100
			server = ctx.message.server
			if server.id in music_players:
				music_players[server.id].volume = volume
			else:
				await client.say("You must play a song first to use this command")
		else:
			await client.say("Volume must be a number between 0 and 200")

"""@client.command(pass_context = True)
async def queue(ctx, url):
	server = ctx.message.server
	voice_client = client.voice_client_in(server)
	player = await voice_client.create_ytdl_player(url, after = lambda : check_queue(server.id))

	if server.id in music_queues:
		music_queues[server.id].append(player)
	else:
		music_queues[server.id] = [player]
	await client.say("Song succesfully queued")"""

@client.command(pass_context = True)
async def queue(ctx):
	server = ctx.message.server
	song_index = 1

	if server.id in music_players:
		if music_players[server.id].is_playing():
			await client.say("Currently playing: **{}**".format(music_players[server.id].title))
			for song in music_queues[server.id]:
				await client.say("**{}. {}**".format(song_index, song.title))
				song_index = song_index + 1
		else:
			await client.say("Queue is empty")
	else:
		await client.say("Queue is empty")
	

#END OF MUSIC PLAYER

@client.command(pass_context = True)
async def connected(ctx):
	server = ctx.message.server
	if client.is_voice_connected(server):
		voice_client = client.voice_client_in(server)
		help(voice_client)
	channel = ctx.message.author.voice.voice_channel
	print("2\n2\n2\n2")
	help(channel)

@client.command(pass_context = True)
async def give_voice(ctx):
    message = ctx.message.content.split(" ")
    await client.send_message(ctx.message.channel, " ".join(message[1:]), tts=True)

@client.command(pass_context = True)
async def clear(ctx, amount = 100):
	channel = ctx.message.channel
	messages = []
	async for message in client.logs_from(channel, limit = int(amount)):
		messages.append(message)
	await client.delete_messages(messages)
	await client.say("Messages deleted!")

@client.command(pass_context = True)
async def check_id(ctx):
	if client.user.id == "482552054171303937":
		print("kappa")

@client.command(pass_context = True)
async def help(ctx):
	author = ctx.message.author

	help_embed = discord.Embed(
			title = "I am a Bot, I am helping!",
			colour = discord.Colour.blue()
		)

	help_embed.set_author(name = "Help", icon_url = client.user.avatar_url)
	help_embed.set_thumbnail(url = author.avatar_url)
	help_embed.add_field(name = "*Chat controls*", value = "\u200b", inline = False)
	help_embed.add_field(name = "!clear X", value = "Bot will clear X most recent messages", inline = True)
	help_embed.add_field(name = "\u200b", value = "\u200b", inline = True)
	help_embed.add_field(name = "*Audio player commands*", value = "\u200b", inline = False)
	help_embed.add_field(name = "!join", value = "Bot will join your voice channel", inline = True)
	help_embed.add_field(name = "!leave", value = "Bot will leave your voice channel", inline = True)
	help_embed.add_field(name = "!play url", value = "Bot will play audio from the given url and queue extra songs", inline = True)
	help_embed.add_field(name = "!pause", value = "Bot will pause the audio", inline = True)
	help_embed.add_field(name = "!resume", value = "Bot will resume the audio", inline = True)
	help_embed.add_field(name = "!skip", value = "Bot will skip a track", inline = True)
	help_embed.add_field(name = "!volume X", value = "Bot will change the volume [0-200] to X", inline = True)
	help_embed.add_field(name = "!stop", value = "Bot will stop the audio and cancel the queue", inline = True)

	await client.send_message(author, embed = help_embed)
"""
@client.command(pass_context = True)
async def play_test(ctx, url):
	members = ctx.message.author.voice.voice_channel
	if members != None:
		server = ctx.message.server

		members = members.voice_members
		if "482552054171303937" not in [member.id for member in members]:
			if client.is_voice_connected(server):
				voice_client = client.voice_client_in(server)
				await voice_client.disconnect()
			channel = ctx.message.author.voice.voice_channel
			await client.join_voice_channel(channel)

		voice_client = client.voice_client_in(server)
		music_player = await voice_client.create_ytdl_player(url, after = lambda : check_queue(server.id))

		if server.id in music_queues:
			music_queues[server.id].append(music_player)
		else:
			music_queues[server.id] = [music_player]

		if server.id not in music_players:
			check_queue(server.id)

		if len(music_queues[server.id]) == 0:
			await client.say("Let's jam, currently playing your song.")
		else:
			await client.say("Song succesfully queued. Position in queue: " + str(len(music_queues[server.id])))
	else:
		await client.say("Enter voice channel to use this command")
"""
client.run("bot_oath_token")
