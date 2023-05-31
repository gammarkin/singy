import discord
import yt_dlp as youtube_dl

from discord.ext import commands

song_queue = {}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='-', intents=intents)

commands = """
commands:
-join
-leave
-play
-search
-queue
-skip
"""

bot.remove_command('help')


@bot.command()
async def help(ctx):
    await ctx.send(commands)


async def check_queue(ctx):
    print(song_queue)
    await play_song(ctx, ctx.message.content.split(" ")[1])


async def search_song(amount, song, get_url=False):
    info = await bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(f"ytsearch{amount}:{song}", download=False, ie_key="YoutubeSearch"))
    if len(info["entries"]) == 0:
        return None

    return [entry["webpage_url"] for entry in info["entries"]] if get_url else info


async def play_song(ctx, song):
    url = youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(
        song, download=False)["url"]
    ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
        url)))
    ctx.voice_client.source.volume = 0.5


@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        return await ctx.send("You are not connected to a voice channel, please connect to the channel you want the bot to join.")

    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

    await ctx.author.voice.channel.connect()


@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        return await ctx.voice_client.disconnect()

    await ctx.send("I am not connected to a voice channel.")


@bot.command()
async def play(ctx, *, song=None):
    if song is None:
        return await ctx.send("You must include a song to play.")

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    # handle song where song isn't url
    if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
        await ctx.send("Searching for song, this may take a few seconds.")

        result = await search_song(1, song, get_url=True)

        if result is None:
            return await ctx.send("Sorry, I could not find the given song, try using my search command.")

        song = result[0]

    else:  # handle song where song is url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):
            return await ctx.send("Sorry, I could not understand the given url, make sure it is a valid youtube url.")

        # check if url is valid
        try:
            url = youtube_dl.YoutubeDL({"format": "bestaudio", "quiet": True}).extract_info(
                song, download=False)["url"]

            return ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
                url)))

        except Exception as e:
            print(e)
            return await ctx.send("Sorry, I could not access the given url, make sure it is valid.")

    await play_song(ctx, song)
    await ctx.send(f"Now playing: {song}")


@bot.command()
async def search(ctx, *, song=None):
    if song is None:
        return await ctx.send("You forgot to include a song to search for.")

    await ctx.send("Searching for song, this may take a few seconds.")

    info = await search_song(5, song)

    embed = discord.Embed(
        title=f"Results for '{song}':", description="*You can use these URL's to play an exact song if the one you want isn't the first result.*\n", colour=discord.Colour.red())

    amount = 0
    for entry in info["entries"]:
        embed.description += f"[{entry['title']}]({entry['webpage_url']})\n"
        amount += 1

    embed.set_footer(text=f"Displaying the first {amount} results.")
    await ctx.send(embed=embed)


@bot.command()
async def queue(ctx):  # display the current guilds queue
    if len(song_queue[ctx.guild.id]) == 0:
        return await ctx.send("There are currently no songs in the queue.")

    embed = discord.Embed(
        title="Song Queue", description="", colour=discord.Colour.dark_gold())
    i = 1
    for url in song_queue[ctx.guild.id]:
        embed.description += f"{i}) {url}\n"

        i += 1

    embed.set_footer(text="Thanks for using me!")
    await ctx.send(embed=embed)


@bot.command()
async def skip(ctx):
    if ctx.voice_client is None:
        return await ctx.send("I am not playing any song.")

    if ctx.author.voice is None:
        return await ctx.send("You are not connected to any voice channel.")

    if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
        return await ctx.send("I am not currently playing any songs for you.")

    return ctx.voice_client.stop()


@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_paused():
        return await ctx.send("I am already paused.")

    ctx.voice_client.pause()
    await ctx.send("The current song has been paused.")


@bot.command()
async def resume(ctx):
    if ctx.voice_client is None:
        return await ctx.send("I am not connected to a voice channel.")

    if not ctx.voice_client.is_paused():
        return await ctx.send("I am already playing a song.")

    ctx.voice_client.resume()
    await ctx.send("The current song has been resumed.")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


bot.run('MTExMzI1NDU1NTUxNDMyMzAyNg.G-vmFg.eTDo4LM7sO7tkspxFtss28UzhtdsKkAxn_KfeQ')
