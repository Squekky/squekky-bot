import discord
import random
import math
from discord.ext import commands

# Embed Color Palette
# Help - 0xA600FF
# Info - 0xC800FF


async def get_help(command):
    embed = discord.Embed(
        title=f"{command}",
        color=0xB800FF
    )
    return embed


async def hangman_stats_help(category):
    embed = await get_help(f"stats {category} [user]")
    embed.add_field(name=f"Show your {category} stats from hangman, or another user's, including total correct "
                         f"guesses and most collected {category}",
                    value="Accepts both user IDs and mentions\n\n"
                          f"**Example:** -stats {category} 489560386886959115")
    return embed


async def hangman_help(category):
    embed = await get_help(f"{category} [page]")
    embed.add_field(name=f"Show your collected and missing {category}",
                    value=f"Use `-hangman {category}` to collect {category}\n"
                          "Add `-orderd` or `-ordera` to your command to order by "
                          "most or least collected respectively.\n\n"
                          "**Cooldown:** 1 second\n"
                          f"**Example:** -{category} {random.randint(2, 3)}")
    return embed


class Help(commands.Cog):
    # Provide statistics for the server #
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['cmds', 'commands'])
    async def help(self, ctx):
        embed = discord.Embed(
            title="Prefix: `-`\n"
                  "Use `-help [command/subcommand]` for more help on a given command",
            color=0xA600FF
        )
        general = ["`help`", "`ping`"]
        info = ["`serverinfo`", "`rolecheck`", "`roleid`"]
        games = ["`hangman`", "`flags`", "`yahtzee`", "`roll`", "`wordle`", "`nerdle`"]
        stats = ["`disasters`", "`countries`", "`capitals`", "`states`", "`teams`", "`companies`", "`games`", "`stats`",
                 "`leaderboard`", "`leaderboards`"]
        math = ["`prime`", "`factorial`", "`fibonacci`"]
        time = ["`time`", "`times`", "`timezones`"]
        music = ["`lyrics`", "`songs`", "`artists`"]
        # other = ["`ghost`", "`opt`"]
        # moderation = ["`kill`", "`revive`"]
        embed.add_field(name="General", value=f"{', '.join(general)}", inline=False)
        embed.add_field(name="Info", value=f"{', '.join(info)}", inline=False)
        embed.add_field(name="Games", value=f"{', '.join(games)}", inline=False)
        embed.add_field(name="Stats", value=f"{', '.join(stats)}", inline=False)
        embed.add_field(name="Math", value=f"{', '.join(math)}", inline=False)
        embed.add_field(name="Time", value=f"{', '.join(time)}", inline=False)
        embed.add_field(name="Music", value=f"{', '.join(music)}", inline=False)
        # embed.add_field(name="Other", value=f"{', '.join(other)}", inline=False)
        # embed.add_field(name="Moderation", value=f"{', '.join(moderation)}", inline=False)
        embed.set_author(name=f"Squekky Bot Commands", icon_url=f"{self.bot.user.avatar}")
        await ctx.send(embed=embed)

    @help.command(name='help', aliases=['cmds, commands'])
    async def help_help(self, ctx):
        # HELP HELP #
        embed = await get_help("help [command/subcommand]")
        embed.add_field(name="Provide a list of commands or more information on a given command",
                        value="**Aliases:** cmds, commands\n"
                              "**Example:** -help roll")
        await ctx.send(embed=embed)

    @help.command(name='ping')
    async def help_ping(self, ctx):
        """ PING HELP """
        embed = await get_help("ping")
        embed.add_field(name="Check how long the bot takes to respond",
                        value="**Cooldown:** 5 seconds\n"
                              "**Example:** -ping")
        await ctx.send(embed=embed)

    @help.command(name='serverinfo', aliases=['si'])
    async def help_serverinfo(self, ctx):
        """ SERVERINFO HELP """
        embed = await get_help("serverinfo")
        embed.add_field(name="Provide detailed information about the server",
                        value="**Aliases:** si\n"
                              "**Example:** -serverinfo")
        await ctx.send(embed=embed)

    @help.command(name='rolecheck', aliases=['rc'])
    async def help_rolecheck(self, ctx):
        """ SERVERINFO HELP """
        embed = await get_help("rolecheck (roleID)")
        embed.add_field(name="Check how many users have a given role",
                        value="Accepts both role IDs and names. Names are case-sensitive.\n\n"
                              "**Aliases:** rc\n"
                              "**Example:** -rolecheck 774168309704294400")
        await ctx.send(embed=embed)

    @help.command(name='roleid')
    async def help_roleid(self, ctx):
        """ SERVERINFO HELP """
        embed = await get_help("roleid (role name)")
        embed.add_field(name="Get the ID of a role.",
                        value="**Example:** -roleid s-rank")
        await ctx.send(embed=embed)

    @help.command(name='hangman')
    async def help_hangman(self, ctx):
        """ HANGMAN HELP """
        embed = await get_help("hangman (disasters/games/countries/capitals/states/teams/companies/words)")
        embed.add_field(name="Play a game of hangman with a random disaster, video game, country, capital, "
                             "state, sports team, company, or word",
                        value="Include `*` before your message during a game to avoid it being counted as a guess.\n\n"
                              "**Cooldown:** 60 seconds\n"
                              "**Example:** -hangman disasters")
        await ctx.send(embed=embed)

    @help.command(name='flags')
    async def help_flags(self, ctx):
        """ HANGMAN HELP """
        embed = await get_help("flags (countries/territories/usa)")
        embed.add_field(name="Play a quiz through a series of flags while trying to guess each one correctly",
                        value="\n"
                              "**Cooldown:** 60 seconds\n"
                              "**Example:** -flags countries")
        await ctx.send(embed=embed)

    @help.command(name='disasters')
    async def help_disasters(self, ctx):
        """ DISASTERS HELP """
        await ctx.send(embed=await hangman_help("disasters"))

    @help.command(name='games')
    async def help_games(self, ctx):
        """ GAMES HELP """
        await ctx.send(embed=await hangman_help("games"))

    @help.command(name='countries')
    async def help_countries(self, ctx):
        """ COUNTRIES HELP """
        await ctx.send(embed=await hangman_help("countries"))

    @help.command(name='capitals')
    async def help_capitals(self, ctx):
        """ CAPITALS HELP """
        await ctx.send(embed=await hangman_help("capitals"))

    @help.command(name='states')
    async def help_states(self, ctx):
        """ STATES HELP """
        await ctx.send(embed=await hangman_help("states"))

    @help.command(name='teams')
    async def help_teams(self, ctx):
        """ TEAMS HELP """
        await ctx.send(embed=await hangman_help("teams"))

    @help.command(name='companies')
    async def help_companies(self, ctx):
        """ COMPANIES HELP """
        await ctx.send(embed=await hangman_help("companies"))

    @help.command(name='data')
    async def help_data(self, ctx):
        """ DATA HELP """
        embed = await get_help("data (disasters/games/countries/states/teams/companies)")
        embed.add_field(name="Get data regarding a specific hangman category",
                        value="**Permissions:** Owner only\n"
                              "**Example:** -data games")
        await ctx.send(embed=embed)

    @help.command(name='yahtzee')
    async def help_yahtzee(self, ctx):
        """ YAHTZEE HELP """
        embed = await get_help("yahtzee")
        embed.add_field(name="Play a game of Yahtzee!",
                        value="**Cooldown:** 30 second\n"
                              "**Example:** -yahtzee")
        await ctx.send(embed=embed)

    @help.command(name='roll')
    async def help_roll(self, ctx):
        """ ROLL HELP """
        embed = await get_help("roll (number of dice) (guess)")
        embed.add_field(name="Guess the sum of a number of dice (Maximum 36 dice)",
                        value="**Cooldown:** 5 seconds\n"
                              "**Example:** -roll 5 18")
        await ctx.send(embed=embed)

    @help.group(name='wordle', invoke_without_command=True)
    async def help_wordle(self, ctx):
        """ WORDLE HELP """
        embed = await get_help("wordle")
        embed.add_field(name="Play a game of Wordle.\n"
                             "https://www.nytimes.com/games/wordle/",
                        value="**Example:** -wordle")
        await ctx.send(embed=embed)

    @help.group(name='nerdle', invoke_without_command=True)
    async def help_nerdle(self, ctx):
        """ NERDE HELP """
        embed = await get_help("nerdle")
        embed.add_field(name="Play a game of Nerdle.\n"
                             "https://nerdlegame.com/",
                        value="**Example:** -nerdle")
        await ctx.send(embed=embed)

    @help.group(name="stats", invoke_without_command=True)
    async def help_stats(self, ctx):
        """ STATS HELP """
        embed = await get_help("stats (category) [user]")
        embed.add_field(name="Show a given user's statistics in a given category",
                        value="Use `-stats` to see the list of categories.\n"
                              "Accepts both user IDs and mentions\n\n"
                              "**Example:** -stats dice 489560386886959115")
        await ctx.send(embed=embed)

    @help_stats.command(name='dice')
    async def help_stats_dice(self, ctx):
        """ STATS DICE HELP """
        embed = await get_help("stats dice [user]")
        embed.add_field(name="Show your dice rolling statistics, or another user's, "
                             "including total rolls, highest score, and highest correct guess",
                        value="Accepts both user IDs and mentions\n\n"
                              "**Example:** -stats dice 489560386886959115")
        await ctx.send(embed=embed)

    @help_stats.command(name='yahtzee')
    async def help_stats_yahtzee(self, ctx):
        """ STATS YAHTZEE HELP """
        embed = await get_help("stats yahtzee [user]")
        embed.add_field(name="Show your yahtzee stats, or another user's, including highest score",
                        value="Accepts both user IDs and mentions\n\n"
                              "**Example:** -stats yahtzee 489560386886959115")
        await ctx.send(embed=embed)

    @help_stats.command(name='disasters')
    async def help_stats_disasters(self, ctx):
        """ STATS DISASTERS HELP """
        await ctx.send(embed=await hangman_stats_help("disasters"))

    @help_stats.command(name='games')
    async def help_stats_games(self, ctx):
        """ STATS GAMES HELP """
        await ctx.send(embed=await hangman_stats_help("games"))

    @help_stats.command(name='countries')
    async def help_stats_countries(self, ctx):
        """ STATS COUNTRIES HELP """
        await ctx.send(embed=await hangman_stats_help("countries"))

    @help_stats.command(name='capitals')
    async def help_stats_capitals(self, ctx):
        """ STATS CAPITALS HELP """
        await ctx.send(embed=await hangman_stats_help("capitals"))

    @help_stats.command(name='states')
    async def help_stats_states(self, ctx):
        """ STATS STATES HELP """
        await ctx.send(embed=await hangman_stats_help("states"))

    @help_stats.command(name='companies')
    async def help_stats_companies(self, ctx):
        """ STATS COMPANIES HELP """
        await ctx.send(embed=await hangman_stats_help("companies"))

    @help.group(name="leaderboard", invoke_without_command=True, aliases=['lb'])
    async def help_leaderboard(self, ctx):
        """ LEADERBOARD HELP """
        embed = await get_help("leaderboard (category) [page]")
        embed.add_field(name="Show the leaderboard in a given category; Pages optional",
                        value="Use `-leaderboards` to see the list of available leaderboards\n\n"
                              "**Aliases:** lb\n"
                              "**Example:** -leaderboard score 3")
        await ctx.send(embed=embed)

    @help.command(name='leaderboards', aliases=['lbs'])
    async def help_leaderboards(self, ctx):
        """ LEADERBOARDS HELP """
        embed = await get_help("leaderboards")
        embed.add_field(name="Provide a list of leaderboard categories\n",
                        value="**Aliases:** lbs\n"
                              "**Example:** -leaderboards")
        await ctx.send(embed=embed)

    @help.command(name='prime')
    async def help_prime(self, ctx):
        """ PRIME HELP """
        embed = await get_help("prime (number)")
        embed.add_field(name="Check if a number between 0 and 1 quintillion is prime",
                        value="A prime number is a number that has only two factors, 1 and itself\n\n"
                              "**Example:** -prime 27")
        await ctx.send(embed=embed)

    @help.command(name='factorial', aliases=['fac'])
    async def help_factorial(self, ctx):
        """ FACTORIAL HELP """
        embed = await get_help("factorial (number)")
        embed.add_field(name="Calculate the factorial of a number between 0 and 100,000",
                        value="The factorial of a number is that number multiplied by "
                              "every integer between 1 and itself\n"
                              "For example, 4 factorial is 4\*3\*2\*1 = 24\n\n"
                              "**Aliases:** fac\n"
                              "**Example:** -factorial 6")
        await ctx.send(embed=embed)

    @help.command(name='fibonacci', aliases=['fib'])
    async def help_fibonacci(self, ctx):
        """ FIBONACCI HELP """
        embed = await get_help("fibonacci (number)")
        embed.add_field(name="Calculate the given term of the Fibonacci Sequence (Maximum 1,000,000)",
                        value="The Fibonacci Sequence is a sequence in which each number "
                              "is the sum of the previous two numbers\n"
                              "0, 1, 1, 2, 3, 5, 8, 13, 21...\n\n"
                              "**Aliases:** fib\n"
                              "**Example:** -fibonacci 16")
        await ctx.send(embed=embed)

    @help.command(name='time')
    async def help_time(self, ctx):
        """ TIME HELP """
        embed = await get_help("time (timezone)")
        embed.add_field(name="Get the current time in a given timezone",
                        value="Use `-timezones` to see the list of available timezones\n\n"
                              "**Example:** -time est")
        await ctx.send(embed=embed)

    @help.command(name='times')
    async def help_times(self, ctx):
        """ TIMES HELP """
        embed = await get_help("times")
        embed.add_field(name="Get the current time in all available timezones",
                        value="**Example:** -timezones")
        await ctx.send(embed=embed)

    @help.command(name='timezones', aliases=['tzs'])
    async def help_timezones(self, ctx):
        """ TIMEZONES HELP """
        embed = await get_help("timezones")
        embed.add_field(name="Provide a list of available timezones",
                        value="**Aliases:** tzs\n"
                              "**Example:** -timezones")
        await ctx.send(embed=embed)

    @help.command(name='lyrics', aliases=['sing'])
    async def help_lyrics(self, ctx):
        """ LYRICS HELP """
        embed = await get_help("lyrics (song)")
        embed.add_field(name="Messages you the lyrics to a given song",
                        value="Use `-songs` to see the list of available songs\n\n"
                              "**Aliases:** sing\n"
                              "**Cooldown:** 10 seconds\n"
                              "**Example:** -lyrics 7 rings")
        await ctx.send(embed=embed)

    @help.command(name='songs')
    async def help_songs(self, ctx):
        """ SONGS HELP """
        embed = await get_help("songs (artist)")
        embed.add_field(name="Messages you the list of available songs by a given artist",
                        value="Use `-artists` to see the list of available artists\n\n"
                              "**Cooldown:** 1 minute\n"
                              "**Example:** -songs ariana grande")
        await ctx.send(embed=embed)

    @help.command(name='artists')
    async def help_artists(self, ctx):
        """ ARTISTS HELP """
        embed = await get_help("artists")
        embed.add_field(name="Messages you the list of available artists",
                        value="**Example:** -artists")
        await ctx.send(embed=embed)

    '''
    @help.command(name='ghost')
    async def help_ghost(self, ctx):
        """ GHOST HELP """
        embed = await get_help("ghost (user)")
        embed.add_field(name="Ghost ping a user if they aren\'t opted out",
                        value="Accepts both user IDs and mentions\n"
                              "Disabled in Fanmade\n\n"
                              "**Cooldown:** 30 seconds\n"
                              "**Example:** -ghost 489560386886959115")
        await ctx.send(embed=embed)

    @help.command(name='opt')
    async def help_opt(self, ctx):
        """ OPT HELP """
        embed = await get_help("opt (in/out)")
        embed.add_field(name="Opt in or out of being able to be ghost pinged by other users",
                        value="You cannot ghost ping others if you are opted out\n"
                              "Disabled in Fanmade\n\n"
                              "**Cooldown:** 1 minute\n"
                              "**Example:** -opt out")
        await ctx.send(embed=embed)

    @help.command(name='kill', aliases=['mute'])
    async def help_kill(self, ctx):
        """ KILL HELP """
        embed = await get_help("kill (user)")
        embed.add_field(name="Indefinitely mute a given user",
                        value="Accepts both user IDs and mentions\n\n"
                              "**Permissions:** Administrator only\n"
                              "**Aliases:** mute\n"
                              "**Example:** -kill 489560386886959115")
        await ctx.send(embed=embed)

    @help.command(name='revive', aliases=['unmute'])
    async def help_revive(self, ctx):
        """ REVIVE HELP """
        embed = await get_help("revive (user)")
        embed.add_field(name="Unmute a given user",
                        value="Accepts both user IDs and mentions\n\n"
                              "**Permissions:** Administrator only\n"
                              "**Aliases:** unmute\n"
                              "**Example:** -revive 489560386886959115")
        await ctx.send(embed=embed)
    '''

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(error, 'error_handled'):
            return
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CommandOnCooldown):
            minutes = math.floor(error.retry_after / 60)  # Calculate minutes left
            seconds = round(error.retry_after % 60, 2)  # Calculate seconds left
            time = f"{minutes} minutes, {seconds} seconds"
            if minutes == 1:
                time = f"1 minute, {seconds} seconds"
            elif minutes == 0:
                time = f"{seconds} seconds"
            embed = discord.Embed(
                title=f"*{ctx.command}* is on cooldown.",
                description=f"Try again in `{time}`.",
                color=0x800000
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.NotOwner):
            print(f"[{ctx.command}] {ctx.author} attempted to use an owner-only command.")
        elif isinstance(error, commands.MissingPermissions):
            print(f"[{ctx.command}] {ctx.author} does not have the required permissions.\n"
                  f"Permission: {error.args[0]}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            ctx.command.reset_cooldown(ctx)
        else:
            print(f"[{ctx.command}] {error.args[0]}")
            print(error.args)


async def setup(bot):
    await bot.add_cog(Help(bot))
