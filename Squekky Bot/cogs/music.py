import math
import os
import discord
from discord.ext import commands

# Embed Color Palette:
# User DMed - 0x16C533
# Song List - 0xF21CEB
# Successful Suggestion - 0x04E000
# Blacklisted User - 0x1F1F1F

class Music(commands.Cog):
    """ Print the lyrics from any available Ariana Grande song in the current channel """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['sing'])
    @commands.cooldown(1, 10, commands.BucketType.user)  # 15-second cooldown
    async def lyrics(self, ctx, *songies):
        """ Message you the lyrics to a given song """
        if songies == ():
            embed = discord.Embed(
                title="Invalid song",
                description="Use `-artists` for a list of available artists.\n"
                            "Then, use `-song (artist)` for a list of available songs by that artist.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            self.lyrics.reset_cooldown(ctx)
            return
        name = "_".join(songies).lower()
        user = ctx.message.author
        try:
            for subdir, dirs, songs in os.walk('.\\files\\songs\\'):
                for song in songs:
                    if song[:-4] == name:
                        with open(f'{subdir}\\{song}', 'r') as file:
                            lyrics = file.read()
        except FileNotFoundError:
            embed = discord.Embed(
                title=f"Please provide an available song, {ctx.message.author.name}.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        if len(lyrics) > 2000:
            lyrics = lyrics.splitlines()
            for message in range(math.ceil(len(lyrics) / 40)):  # Send multiple messages if the song
                # is too long
                partial = '\n'.join(lyrics[40*message:40*message + 40])
                await user.send(f'{partial}\n')
        else:
            await user.send(lyrics)
        embed = discord.Embed(
            title="Check your DMs!",
            color=0x16C533
        )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=embed)
        print(f'{user} played a song [{name.replace("_", " ")}]')

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1-minute cooldown
    async def songs(self, ctx, *artist):
        """ Message you the list of currently available songs by a given artist """
        if artist == ():
            embed = discord.Embed(
                title="Invalid artist",
                description="Use `-artists` for a list of available artists.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            self.songs.reset_cooldown(ctx)
            return
        user = ctx.author  # Get the user to send them the direct message
        artist = ' '.join(artist).title()
        page = 1
        embed = discord.Embed(
            title=f"List of available songs\nPage {page}",
            color=0xF21CEB
        )
        try:
            for song in os.listdir(f".\\files\\songs\\{artist}"):
                if song.endswith('.txt'):  # Avoid other files
                    song = song[:-4].replace('_', ' ')  # Remove underscores and .txt
                    if len(embed.fields) > 23:  # Send multiple pages
                        page += 1
                        await user.send(embed=embed)
                        embed = discord.Embed(
                            title=f"List of available songs\nPage {page}",
                            color=0xF21CEB
                        )
                    if len(embed.fields) % 3 > 1:  # Make the design of the embed cleaner by adjusting the placement
                        embed.add_field(name=song, value=f"-sing {song}", inline=False)
                    else:
                        embed.add_field(name=song, value=f"-sing {song}", inline=True)
            await user.send(embed=embed)
            embed = discord.Embed(
                title="Check your DMs!",
                color=0x16C533
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
        except FileNotFoundError:
            embed = discord.Embed(
                title="Invalid artist",
                description="Use `-artists` for a list of available artists.",
                color=0x800000
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def artists(self, ctx):
        """ Messages you the list of available artists """
        embed = discord.Embed(
            title="Available Artists",
            color=0xF21CEB
        )
        for artist in os.listdir('.\\files\\songs\\'):
            embed.add_field(name=artist, value=f"-songs {artist}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def join(self, ctx):
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command()
    @commands.is_owner()
    async def getsongs(self, ctx):
        channel = self.bot.get_channel(506322330352615434)
        messages = await channel.history(limit=None).flatten()
        with open(".\\files\\louis.txt", 'a') as file:
            for message in messages:
                for word in message.content.split():
                    if "spotify.com" in word:
                        try:
                            file.write(f"{word}\n")
                        except UnicodeEncodeError:
                            print(f"Error: {message.jump_url}")
                            continue
        print("Done")

    @lyrics.error
    async def lyrics_error(self, ctx, error):
        """ Let the user know if they aren't able to be messaged """
        if isinstance(error, commands.errors.CommandInvokeError):
            embed = discord.Embed(
                title=f"I don't have permission to message you, {ctx.message.author.name}.",
                color=0x800000
            )
            await ctx.send(embed=embed)

    @songs.error
    async def songs_error(self, ctx, error):
        """ Let the user know if they aren't able to be messaged """
        if isinstance(error, commands.errors.CommandInvokeError):
            embed = discord.Embed(
                title=f"I don't have permission to message you, {ctx.message.author.name}.",
                color=0x800000
            )
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Music(bot))