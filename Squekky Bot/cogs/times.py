import discord
import time
import pytz
import json
import re
from discord.ext import commands
from datetime import datetime


# Embed Color Palette
# Times - 0xE67A00
# Timezone List - 0xF7B21D
# Invalid Input - 0xC20000


class Times(commands.Cog):
    """ Convert the current time into a variety of timezones """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def time(self, ctx, timezone):
        """ Send an embed containing the current time in a provided timezone """
        timezone = timezone.upper()
        path = "./files/times/"
        with open('./files/times/time_calc.json', 'r') as file:
            tz_dict = dict(json.load(file))
        try:
            name = tz_dict[timezone][0]
            tz = pytz.timezone(tz_dict[timezone][1])
        except KeyError:
            embed = discord.Embed(
                title="Invalid timezone",
                description="Use `-timezones` for a list of available timezones.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        now = datetime.now(tz)  # Get current time
        current_time = now.strftime("%I:%M %p, %B %d").lstrip('0')  # Format the current time into a string
        if current_time[-2] == "0":
            current_time = current_time[:-2] + current_time[-1]
        embed = discord.Embed(
            title=f"Current time in {name}",
            description=f"{current_time}",
            color=0xE67A00
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def timefor(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        with open("./files/times/user_times.json", "r") as file:
            user_times = json.load(file)
        try:
            tz = pytz.timezone(user_times["Times"][str(user.id)])
        except KeyError:
            embed = discord.Embed(
                title="No timezone set",
                description=f"{user} hasn't set their timezone",
                color=0x800000
            )
            embed.set_footer(text="set your timezone using \"-timezoneset\"")
            await ctx.send(embed=embed)
            return
        now = datetime.now(tz)
        current_time = now.strftime("%I:%M %p, %B %d").lstrip('0')
        if current_time[-2] == "0":
            current_time = current_time[:-2] + current_time[-1]
        embed = discord.Embed(
            title=f"Current time for {user}",
            description=f"{current_time}",
            color=0xE67A00
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['tzset'])
    async def timezoneset(self, ctx, timezone):
        user = str(ctx.author.id)
        if timezone.upper() == "NONE":
            with open("./files/times/user_times.json", "r") as file:
                user_times = json.load(file)
            user_times["Times"].pop(user)
            with open("./files/times/user_times.json", "w") as file:
                json.dump(user_times, file)
            embed = discord.Embed(
                title=f"Successfully removed timezone",
                color=0x14CB10
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
            return

        if not re.search("(GMT|UTC)(\+([0-9]$|1[0-4]$)|-([0-9]$|1[0-2]$))", timezone.upper()):
            embed = discord.Embed(
                title="Invalid timezone",
                description="That timezone is either invalid or currently unavailable.\n"
                            "Make sure to use GMT/UTC offsets, for example GMT-4",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        timezone = timezone.upper().replace("UTC", "GMT")

        with open("./files/times/user_times.json", "r") as file:
            user_times = json.load(file)
        try:
            user_timezone = user_times["Timezones"][timezone]
        except KeyError:
            embed = discord.Embed(
                title="Invalid timezone",
                description="That timezone is either invalid or currently unavailable.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return

        user_times["Times"][user] = user_timezone
        with open("./files/times/user_times.json", "w") as file:
            json.dump(user_times, file)

        embed = discord.Embed(
            title=f"Timezone set successfully",
            description=f"Your timezone has been set to {timezone}.",
            color=0x14CB10
        )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=embed)

    @commands.command()
    async def times(self, ctx, *continents):
        """ Send an embed containing the current time in different timezones """
        tz_dict = {'Australia Eastern Standard Time [AEST]': pytz.timezone('Australia/Canberra'),
                   'Australia Central Standard Time [ACST]': pytz.timezone('Australia/Adelaide'),
                   'Australia Western Standard Time [AWST]': pytz.timezone('Australia/Perth'),
                   'Indochina Time [ICT]': pytz.timezone('Asia/Phnom_Penh'),
                   'Indian Standard Time [IST]': pytz.timezone('Asia/Kolkata'),
                   'Central European Time [CET]': pytz.timezone('CET'),
                   'Greenwich Mean Time [GMT]': pytz.timezone('GMT'),
                   'Brasilia Time [BRT]': pytz.timezone('Brazil/East'),
                   'Eastern Standard Time [EST]': pytz.timezone('US/Eastern'),
                   'Central Standard Time [CST]': pytz.timezone('US/Central'),
                   'Mountain Standard Time [MST]': pytz.timezone('US/Mountain'),
                   'Pacific Standard Time [PST]': pytz.timezone('US/Pacific'),
                   'Hawaiian Standard Time [HST]': pytz.timezone('US/Hawaii')}
        embed = discord.Embed(
            title=f"Current time in different timezones",
            color=0xE67A00
        )
        for tz in tz_dict:  # Add a new field to the embed for each timezone
            current_time = datetime.now(tz_dict[tz]).strftime("%I:%M %p, %b %d").lstrip('0')  # Format the current
            # time into a string and remove leading zeros
            if current_time[-2] == "0":
                current_time = current_time[:-2] + current_time[-1]
            embed.add_field(name=f"{tz}", value=f"{current_time}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['tzs'])
    async def timezones(self, ctx):
        """ Provide a list of applicable timezones for -time command """
        embed = discord.Embed(
            title=f"List of Available Timezones",
            description="AEST - Australia Eastern Standard Time\n"
                        "ACST - Australia Central Standard Time\n"
                        "AWST - Australia Western Standard Time\n"
                        "ICT - Indochina Time\n"
                        "IST - Indian Standard Time\n"
                        "CET - Central European Time\n"
                        "GMT - Greenwich Mean Time\n"
                        "BRT - Brasilia Time\n"
                        "EST - Eastern Standard Time\n"
                        "CST - Central Standard Time\n"
                        "MST - Mountain Standard Time\n"
                        "PST - Pacific Standard Time\n"
                        "HST - Hawaiian Standard Time", color=0xF7B21D)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)  # 5-second cooldown
    async def ping(self, ctx):
        """ Show how long the bot takes to respond in milliseconds """
        user = str(ctx.author.id)
        start_time = time.perf_counter()
        message = await ctx.send("Ping...")
        end_time = time.perf_counter()
        ping = round((end_time - start_time) * 1000)  # Calculate ping and convert to milliseconds
        if ping <= 150:  # Bright green
            embed = discord.Embed(
                title=f"Pong! Took {ping} ms",
                color=0x00E004
            )
        elif ping <= 250:  # Green
            embed = discord.Embed(
                title=f"Pong! Took {ping} ms",
                color=0x5AE000
            )
        elif ping <= 400:  # Lime green
            embed = discord.Embed(
                title=f"Pong! Took {ping} ms",
                color=0x99E000
            )
        elif ping <= 600:  # Orange
            embed = discord.Embed(
                title=f"Pong! Took {ping} ms",
                color=0xE0B000
            )
        else:  # Red
            embed = discord.Embed(
                title=f"Pong! Took {ping} ms",
                color=0xE00F00
            )
        embed.set_footer(text=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
        await message.edit(content=None, embed=embed)

    @time.error
    async def time_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Invalid timezone",
                description="Use `-timezones` for a list of available timezones.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True

    @ping.error
    async def ping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):  # Prevent ping from being increased by cooldown messages
            error.error_handled = True
            return


async def setup(bot):
    await bot.add_cog(Times(bot))
