import discord
import random
import math
import json
import uuid
import os
from discord.ext import commands
from PIL import Image


# Embed Color Palette:
# Leaderboards/Statistics - 0x00CBE6
# Invalid Inputs - 0x800000
# Correct Guess - 0x14CB10
# Incorrect Guess - 0xCB1010
# Broken Chain - 0x76E3FE

def no_stats(user, category):
    embed = discord.Embed(
        title=f"{user} has no statistics for `{category}`.",
        color=0x800000
    )
    return embed


class Games(commands.Cog):
    """ Game commands that I made for myself """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def vycheck(self, ctx, channel: discord.TextChannel):
        channel = self.bot.get_channel(channel.id)  # Get the provided channel
        vyriss = self.bot.get_user(121888967435091968)  # Get Vyriss as a user
        checked = 0
        async with ctx.typing():
            messages = await channel.history(limit=None).flatten()  # List of messages in the channel
            for message in messages:  # Iterate through all the messages
                if not message.reactions:  # Continue if the message has no reactions
                    continue
                for reaction in message.reactions:  # Iterate through all reactions if there are any
                    if reaction.emoji == '✅':
                        reacted = await reaction.users().flatten()  # List of users that reacted with checkmark
                        if vyriss in reacted:  # Check that Vyriss has reacted
                            checked += 1
                        break
        embed = discord.Embed(
            title=f"Vyriss has checkmarked {checked} messages in #{channel.name}.",
            color=0x00cbe6
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def suggestionlb(self, ctx, channel: discord.TextChannel):
        channel = self.bot.get_channel(channel.id)  # Get the provided channel
        embed = discord.Embed(
            title=f"Most Upvoted Suggestions",
            color=0x00CBE6
        )
        reactions = {}
        async with ctx.typing():
            messages = await channel.history(limit=None, oldest_first=False).flatten()
            for message in messages:  # Iterate through all the messages
                if not message.reactions:  # Continue if the message has no reactions
                    continue
                for reaction in message.reactions:
                    if reaction.emoji == '👍':  # Add the message and the reaction count to a dictionary if upvoted
                        reactions[f"{message.author}\n{message.jump_url}"] = reaction.count
            sorted_reactions = sorted(reactions, key=reactions.get, reverse=True)  # Sort the dictionary high to low
            for suggestion in sorted_reactions[0:10]:  # Create the leaderboard embed
                placement = sorted_reactions.index(suggestion) + 1  # Calculate which place the suggestion is
                embed.add_field(name=f"{placement}. {suggestion}", value=f"{reactions[suggestion]} 👍", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def reactionlb(self, ctx, channel: discord.TextChannel):
        embed = discord.Embed(
            title=f"Most Reactions in #{channel.name}",
            color=0x00CBE6
        )
        reactions = {}
        async with ctx.typing():
            async for message in channel.history(limit=None, oldest_first=False):  # Iterate through all the messages
                count = 0
                reaction_emoji = ''
                if not message.reactions:  # Ignore if the message has no reactions
                    continue
                for reaction in message.reactions:
                    if reaction.count > count:
                        count = reaction.count
                        reaction_emoji = reaction.emoji
                reactions[f"{message.author}\n{message.jump_url}"] = (reaction_emoji, count)
            sorted_reactions = sorted(reactions.items(), key=lambda react: react[1][1], reverse=True)  # Sort by count
            for message in sorted_reactions[0:10]:  # Create the leaderboard embed
                placement = sorted_reactions.index(message) + 1  # Calculate which place the message is
                user = message[0]
                reaction = message[1][0]
                reaction_count = message[1][1]
                embed.add_field(name=f"{placement}. {user}", value=f"{reaction_count} {reaction}", inline=False)
        await ctx.send(embed=embed)
        await ctx.send("<@!590719451322646548> check completed!")
        with open("./files/messages.json", 'w') as file:
            json.dump(str(sorted_reactions), file)

    @commands.command()
    @commands.is_owner()
    async def purge(self, ctx, user: discord.Member, category: str):
        uid = str(user.id)
        await self.bot.pg_con.execute(f"DELETE FROM {category} WHERE user_id = $1", uid)
        embed = discord.Embed(title=f"Removed {user} from {category} database", color=0x33FF66)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)  # 5-second cooldown
    async def roll(self, ctx, amount, guess):
        """ Guess the sum of a given amount of dice """
        uid = str(ctx.author.id)
        try:  # Try to convert the guess into an integer, send an embed if the value is incorrect
            guess = int(guess)
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="Invalid input. Please only use numbers.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        rolled_dice = []
        dice_images = []
        dice_sum = 0
        for dice in range(amount):  # Roll the provided amount of dice and sum them
            current_dice = random.randint(1, 6)
            rolled_dice.append(str(current_dice))
            dice_images.append('./files/dice/' + rolled_dice[dice] + "_dice.png")
            dice_sum += current_dice
        if guess > 6 * amount or guess < amount:  # Make sure the guess is logical
            embed = discord.Embed(
                title=f"Your guess should be between {amount} and {6 * amount}!",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        elif amount < 1 or amount > 36 and ctx.author.id != 489560386886959115:  # Minimum 1 die, maximum 6 dice
            embed = discord.Embed(
                title="The dice amount should be between 1 and 36!",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        elif dice_sum == guess:  # Create an embed depending on the outcome
            embed = discord.Embed(
                title=f"Spot on! Sum: {dice_sum}",
                description="Congratulations, you win!",
                color=0x14CB10
            )
        else:
            embed = discord.Embed(
                title=f"Not quite... Sum: {dice_sum}",
                description="Guess the sum to win!",
                color=0xCB1010
            )
        file_dimensions = math.sqrt(amount)  # Adjust the dimensions of the file depending on the amount of dice
        combined_dice = Image.new("RGBA", (256 * (math.ceil(file_dimensions)), 256 * (round(file_dimensions))))
        dimensions = math.ceil(file_dimensions)
        squekky = self.bot.get_user(489560386886959115)
        async with ctx.typing():
            for dice in range(amount):
                count = rolled_dice.count(str(dice + 1))
                if count >= 18:
                    await squekky.send(f"{ctx.message.author} rolled {dice + 1} {count} times.\n"
                                       f"{ctx.message.jump_url}")
                dice_image = Image.open(dice_images[dice]).resize((256, 256))
                combined_dice.paste(dice_image, ((dice % dimensions) * 256, math.floor(dice / dimensions) * 256))
        file_name = str(uuid.uuid4()) + ".png"  # Generate a random filename for each roll
        combined_dice.save('./files/dice/rolls/' + file_name)  # Save the image to the dice folder
        file = discord.File('./files/dice/rolls/' + file_name, filename=file_name)
        embed.set_thumbnail(url=f"attachment://{file_name}")
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(file=file, embed=embed)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM dice WHERE user_id = $1", uid)
        if not user:
            await self.bot.pg_con.execute("INSERT INTO dice (user_id) VALUES ($1)", uid)  # Create new user
        user = await self.bot.pg_con.fetchrow("SELECT * FROM dice WHERE user_id = $1", uid)
        await self.bot.pg_con.execute("UPDATE dice SET rolls = $1 WHERE user_id = $2", user['rolls'] + 1, uid)
        # Increase total rolls
        if dice_sum > user['highest_score']:  # Increase highest roll if applicable
            await self.bot.pg_con.execute("UPDATE dice SET highest_score = $1 WHERE user_id = $2", dice_sum, uid)
        if dice_sum == guess and guess > user['highest_guess']:  # Increase highest guess if applicable
            await self.bot.pg_con.execute("UPDATE dice SET highest_guess = $1 WHERE user_id = $2", dice_sum, uid)
        os.remove('./files/dice/rolls/' + file_name)

    async def get_leaderboard(self, leaderboard, category, title, page):
        # await ctx.send(embed=await self.get_leaderboard("dice", "rolls", "Most Dice Rolls", page))
        if page is None:
            page = 1
        elif page.isnumeric():
            page = int(page)
        else:
            return
        keys_per_page = 10
        starting_index = (page - 1) * keys_per_page
        max_pages = (len(leaderboard) - 1) // keys_per_page + 1
        if page > max_pages or page <= 0:
            embed = discord.Embed(
                title=f"Invalid page. Maximum pages: {max_pages}",
                color=0x800000
            )
            return embed
        embed = discord.Embed(
            title=f"{title} Leaderboard",
            color=0x00CBE6
        )
        keys_left = len(leaderboard) - (page - 1) * keys_per_page
        for index in range(min(keys_per_page, keys_left)):
            uid = leaderboard[starting_index + index]
            username = self.bot.get_user(int(uid['user_id']))
            embed.add_field(name=f"{starting_index + index + 1}. {username}",
                            value=f"{uid[category[0]]} {category[1]}", inline=False)
        embed.set_footer(text=f"Page {page}/{max_pages}")
        return embed

    @commands.group(invoke_without_command=True, aliases=['lb'])
    async def leaderboard(self, ctx):
        """ If no leaderboard is provided """
        embed = discord.Embed(
            title="Invalid leaderboard.",
            description="Use `-leaderboards` to see the list of available leaderboards.",
            color=0x800000
        )
        await ctx.send(embed=embed)

    @leaderboard.command(name='rolls', aliases=['r'])
    async def leaderboard_rolls(self, ctx, page=None):
        """ Total Rolls Leaderboard """
        leaderboard = await self.bot.pg_con.fetch("SELECT * from dice ORDER BY rolls DESC, highest_score DESC,"
                                                  "user_id ASC")
        await ctx.send(embed=await self.get_leaderboard(leaderboard, ["rolls", "Rolls"], "Total Rolls", page))

    @leaderboard.command(name='score', aliases=['s'])
    async def leaderboard_score(self, ctx, page=None):
        """ Highest Score Leaderboard """
        leaderboard = await self.bot.pg_con.fetch("SELECT * from dice ORDER BY highest_score DESC, rolls DESC")
        await ctx.send(embed=await self.get_leaderboard(leaderboard, ["highest_score", ""], "Highest Score", page))

    @leaderboard.command(name='guess', aliases=['g'])
    async def leaderboard_guess(self, ctx, page=None):
        """ Highest Guess Leaderboard """
        leaderboard = await self.bot.pg_con.fetch("SELECT * from dice ORDER BY highest_guess DESC, rolls DESC")
        await ctx.send(embed=await self.get_leaderboard(leaderboard, ["highest_guess", ""], "Highest Guess", page))

    @leaderboard.command(name='yahtzee')
    async def leaderboard_yahtzee(self, ctx, page=None):
        """ Highest Yahtzee Score Leaderboard """
        leaderboard = await self.bot.pg_con.fetch("SELECT * from yahtzee ORDER BY score DESC, user_id ASC")
        await ctx.send(embed=await self.get_leaderboard(leaderboard, ["score", ""], "Highest Yahtzee Score", page))

    @commands.command(aliases=['lbs'])
    async def leaderboards(self, ctx):
        """ Provide a list of available leaderboards """
        embed = discord.Embed(
            title="Leaderboard Categories",
            description="**Use `-leaderboard (category)` to see the leaderboard of a category.**\n\n"
                        "**Dice**\n"
                        "`rolls`\n"
                        "`score`\n"
                        "`guess`\n\n"
                        "**Yahtzee**\n"
                        "`yahtzee`",
            color=0x00CBE6
        )
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def stats(self, ctx):
        """ If no category is provided """
        embed = discord.Embed(
            title="Stats Categories",
            description="**Use `-stats (category)` to see your stats in that category.**\n\n"
                        "**Dice**\n"
                        "`dice`\n\n"
                        "**Hangman**\n"
                        "`hangman`\n"
                        "`disasters`\n"
                        "`games`\n"
                        "`countries`\n"
                        "`capitals`\n"
                        "`states`\n"
                        "`teams`\n"
                        "`companies`\n\n"
                        "**Yahtzee**\n"
                        "`yahtzee`",
            color=0x00CBE6
        )
        await ctx.send(embed=embed)

    @stats.command(name='dice')
    async def stats_dice(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        uid = await self.bot.pg_con.fetchrow("SELECT * FROM dice WHERE user_id = $1", str(user.id))
        if not uid:
            await ctx.send(embed=no_stats(user, "dice"))
            return
        uid = await self.bot.pg_con.fetchrow("SELECT * FROM dice WHERE user_id = $1", str(user.id))
        embed = discord.Embed(
            title=f"Dice Rolling Statistics",
            color=0x00CBE6
        )
        embed.set_author(name=f"{user}", icon_url=f"{user.avatar}")
        embed.add_field(name="Total Rolls:", value=f"{uid['rolls']}", inline=False)
        embed.add_field(name="Highest Roll:", value=f"{uid['highest_score']}", inline=False)
        embed.add_field(name="Highest Guess:", value=f"{uid['highest_guess']}", inline=False)
        await ctx.send(embed=embed)

    @stats.command(name='yahtzee')
    async def stats_yahtzee(self, ctx, user: discord.Member = None):
        """ Provide the highest Yahtzee score """
        if user is None:
            user = ctx.author
        uid = await self.bot.pg_con.fetchrow("SELECT * FROM yahtzee WHERE user_id = $1", str(user.id))
        if not uid:
            await ctx.send(embed=no_stats(user, "yahtzee"))
            return
        embed = discord.Embed(
            title=f"Yahtzee Statistics",
            color=0x00CBE6
        )
        embed.set_author(name=f"{user}", icon_url=f"{user.avatar}")
        embed.add_field(name="Highest Score:", value=f"{uid['score']}", inline=False)
        await ctx.send(embed=embed)

    async def get_stats(self, user, category):
        with open("./files/hangman/words.json", 'r') as file:
            words = json.load(file)
        user_collection = await self.bot.pg_con.fetch(f"SELECT * FROM hangman_{category.lower()} WHERE user_id = $1",
                                                      str(user.id))
        total = 0
        for item in user_collection:
            total += item['total']
        collected = f'{len(user_collection)}/{len(words[category])}'
        return {"Total": total, "Collected": collected}

    @stats.command(name='hangman')
    async def stats_hangman(self, ctx, user: discord.Member = None):
        """ Provide general Hangman stats """
        if user is None:
            user = ctx.author
        disasters = await self.get_stats(user, "Disasters")
        games = await self.get_stats(user, "Games")
        countries = await self.get_stats(user, "Countries")
        capitals = await self.get_stats(user, "Capitals")
        states = await self.get_stats(user, "States")
        teams = await self.get_stats(user, "Teams")
        companies = await self.get_stats(user, "Companies")
        embed = discord.Embed(
            title=f"Hangman Statistics",
            color=0x00CBE6
        )
        embed.set_author(name=f"{user}", icon_url=f"{user.avatar}")
        embed.add_field(name="Disasters", value=f"Total: {disasters['Total']}\n"
                                                f"Collected: {disasters['Collected']}\n", inline=False)
        embed.add_field(name="Games", value=f"Total: {games['Total']}\n"
                                            f"Collected: {games['Collected']}\n", inline=False)
        embed.add_field(name="Countries", value=f"Total: {countries['Total']}\n"
                                                f"Collected: {countries['Collected']}\n", inline=False)
        embed.add_field(name="Capitals", value=f"Total: {capitals['Total']}\n"
                                                f"Collected: {capitals['Collected']}\n", inline=False)
        embed.add_field(name="States", value=f"Total: {states['Total']}\n"
                                             f"Collected: {states['Collected']}\n", inline=False)
        embed.add_field(name="Teams", value=f"Total: {teams['Total']}\n"
                                            f"Collected: {teams['Collected']}\n", inline=False)
        embed.add_field(name="Companies", value=f"Total: {companies['Total']}\n"
                                                f"Collected: {companies['Collected']}\n", inline=False)
        await ctx.send(embed=embed)

    async def get_hangman_stats(self, user, channel, category):
        category = category.lower()
        with open("./files/hangman/words.json") as file:
            words = json.load(file)
        words = words[category.title()]
        frequency = {}
        total_points = 0
        for word in words:
            total_count = 0
            totals = await self.bot.pg_con.fetch(f"SELECT total FROM hangman_{category} WHERE {category} = $1 "
                                                 f"AND user_id = $2", word, str(user.id))
            for total in totals:
                total_count += total['total']
            frequency[word] = total_count
            total_points += total_count
        most = []
        least = []
        most_amount = 0
        least_amount = math.inf
        total_value = 0
        item_list = []
        for item in frequency:  # Remove duplicates
            item_list.extend([item]*frequency[item])
            total_value += (list(frequency).index(item) + 1) * frequency[item]
            if frequency[item] > most_amount:  # If it's a new mode amount, reset the list
                most_amount = frequency[item]
                most = [item]
            elif frequency[item] == most_amount:  # If it has the same amount, add it to the list
                most.append(item)
            if frequency[item] < least_amount:  # If it's a new mode amount, reset the list
                least_amount = frequency[item]
                least = [item]
            elif frequency[item] == least_amount:  # If it has the same amount, add it to the list
                least.append(item)
        if most_amount == 0:
            most_amount = 'X'
            most = 'None'
        elif len(most) > 10:
            most = f"{len(most)} different {category}"
        else:
            most = ', '.join(most)
        if least_amount == most_amount:
            least_amount = 0
            least = 'None'
        elif len(least) > 10:
            least = f"{len(least)} different {category}"
        else:
            least = ', '.join(least)
        embed = discord.Embed(
            title=f"Hangman {category.title()} Statistics",
            color=0x00CBE6
        )
        embed.set_author(name=f"{user}", icon_url=f"{user.avatar}")
        embed.add_field(name=f"Total {category.title()}:", value=f"{total_points}", inline=False)
        embed.add_field(name=f"Most Collected [{most_amount}]:", value=f"{most}", inline=False)
        embed.add_field(name=f"Least Collected [{least_amount}]:", value=f"{least}", inline=False)
        await channel.send(embed=embed)

    @stats.command(name='disasters')
    async def stats_disasters(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "disasters")

    @stats.command(name='games')
    async def stats_games(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "games")

    @stats.command(name='countries')
    async def stats_countries(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "countries")

    @stats.command(name='capitals')
    async def stats_capitals(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "capitals")

    @stats.command(name='states')
    async def stats_states(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "states")

    @stats.command(name='teams')
    async def stats_teams(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "teams")

    @stats.command(name='companies')
    async def stats_companies(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        await self.get_hangman_stats(user, ctx.channel, "companies")

    @roll.error
    async def roll_error(self, ctx, error):
        blacklisted = []
        if ctx.author.id in blacklisted:
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Make sure to include the amount of dice to roll and your guess!",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True

    @commands.command()
    @commands.is_owner()
    async def importdata(self, ctx, category):
        with open(f"./files/data/{category}.txt", 'r') as file:
            data = file.read()
        data = data.split("\n")
        for item in data:
            item = item.split("\t")
            uid = item[0]
            if category.lower() == "dice":
                rolls = int(item[1])
                highest_score = int(item[2])
                highest_guess = int(item[3])
                await self.bot.pg_con.execute(f"INSERT INTO dice (user_id, rolls, highest_score, highest_guess)"
                                              f"VALUES ($1, $2, $3, $4)", uid, rolls, highest_score, highest_guess)
            elif category.lower() == "yahtzee":
                score = int(item[1])
                await self.bot.pg_con.execute(f"INSERT INTO yahtzee (user_id, score)"
                                              f"VALUES ($1, $2)", uid, score)
            else:
                word = item[1]
                total = int(item[2])
                await self.bot.pg_con.execute(f"INSERT INTO hangman_{category} (user_id, {category}, total)"
                                              f"VALUES ($1, $2, $3)", uid, word, total)
        print("SUCCESS")


async def setup(bot):
    await bot.add_cog(Games(bot))
