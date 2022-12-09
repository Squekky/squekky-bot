import discord
import asyncio
import random
import math
import json
import matplotlib.pyplot as plt  # For graph command
from discord.ext import commands

# Embed Color Palette
# Game Started - 0xD780FF
# Correct Guess - 0x14CB10
# Incorrect Guess - 0xCB1010
# Ongoing Game - 0x800000
# Win - 0x66FFCC
# Lose - 0xFF6675
# Data/Statistics - 0x00CBE6

class Hangman(commands.Cog):
    """ Play Hangman """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)  # Prevent user from having more than 1 ongoing game
    @commands.cooldown(1, 60, commands.BucketType.user)  # 10-second cooldown
    async def hangman(self, ctx, user_input=None):
        await asyncio.sleep(0.5)
        channel = ctx.channel
        if user_input is None:  # Check if length is not provided
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            self.hangman.reset_cooldown(ctx)
            return
        elif user_input.title() in ["Disasters", "Games", "Countries", "States", "Teams",
                                    "Companies", "Capitals", "Words"]:
            # Change embed depending on the mode
            user_input = user_input.title()
            if user_input == "Disasters":
                category = "disaster"
            elif user_input == "Games":
                category = "game"
            elif user_input == "Countries":
                category = "country"
            elif user_input == "States":
                category = "state"
            elif user_input == "Teams":
                category = "team"
            elif user_input == "Companies":
                category = "company"
            elif user_input == "Capitals":
                category = "capital"
            elif user_input == "Words":
                category = "word"
            else:
                return
        else:
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            self.hangman.reset_cooldown(ctx)
            return

        with open(".\\files\\hangman\\words.json", 'r') as file:
            words = json.load(file)
        word_count = len(words[user_input]) - 1
        selection = random.randint(0, word_count)
        selected_word = words[user_input][selection]  # Select a random word
        if category == "capital":
            country = f', {words["Countries"][selection]}'
        else:
            country = ''
        if category == "team":
            with open(".\\files\\hangman\\sports_teams.json", 'r') as file:
                sports = json.load(file)
            teams = list(sports.values())
            for item in teams:
                if selected_word in item:
                    sport = f'[{list(sports.keys())[teams.index(item)]}]'
                    break
        else:
            sport = ''
        mystery = ["\_ "] * len(selected_word)  # Create the mystery word
        contains_numbers = False
        for index in range(len(mystery)):
            if selected_word[index] == " ":  # Replace spaces with long dashes
                mystery[index] = "—"
            elif selected_word[index] in "0123456789":
                mystery[index] = "#"
                contains_numbers = True
            elif selected_word[index].lower() not in "abcdefghijklmnopqrstuvwxyz":  # Check if it's not a letter
                mystery[index] = selected_word[index]

        async def on_win(user_id, category):
            embed.add_field(name=f"You guessed the {category}!",
                            value=f"The {category} was: **{selected_word}**{country}",
                            inline=False)
            uid = str(user_id)
            table = user_input.lower()
            if category != "word":
                collection = await self.bot.pg_con.fetch(f"SELECT {table} FROM hangman_{table} "
                                                         f"WHERE user_id = $1 ORDER BY {table} ASC", uid)
                new_collection = []
                for item in range(len(collection)):
                    for thing in collection[item]:
                        new_collection.append(thing)
                if not collection or selected_word not in new_collection:
                    embed.set_footer(text=f"You found a new {category}!")
                    await self.bot.pg_con.execute(f"INSERT INTO hangman_{table} (user_id, {table})"
                                                  f"VALUES ($1, $2)", uid, selected_word)
                elif selected_word in new_collection:
                    total = await self.bot.pg_con.fetch(f"SELECT total FROM hangman_{table} "
                                                        f"WHERE user_id = $1 AND {table} = $2", uid, selected_word)
                    await self.bot.pg_con.execute(f"UPDATE hangman_{table} SET total = $1 "
                                                  f"WHERE user_id = $2 AND {table} = $3",
                                                  total[0]['total'] + 1, uid, selected_word)
            self.hangman.reset_cooldown(ctx)

        def hangman_embed(color, description):
            embed = discord.Embed(
                title=f"Hangman - {user_input.title()} {sport}",
                description=description,
                color=color
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            return embed

        def cheating_embed():
            embed = hangman_embed(0x800000, "")
            embed.add_field(name="No cheating!", value=f"The {category} was: **{selected_word}**{country}",
                            inline=False)
            return embed

        def check(new_guess):  # Make sure the response is in the same channel from the same user
            return new_guess.channel == channel and new_guess.author == ctx.author
        guesses_left = 6
        guessed = []
        letters = ["**A**", "**B**", "**C**", "**D**", "**E**", "**F**", "**G**", "**H**", "**I**", "**J**", "**K**",
                   "**L**", "**M**", "**N**", "**O**", "**P**", "**Q**", "**R**", "**S**", "**T**", "**U**", "**V**",
                   "**W**", "**X**", "**Y**", "**Z**"]
        numbers = ["**0**", "**1**", "**2**", "**3**", "**4**", "**5**", "**6**", "**7**", "**8**", "**9**"]
        embed = hangman_embed(0xD780FF, f"{''.join(mystery)}")
        embed.add_field(name="\nRemaining Guesses", value=f"{guesses_left}", inline=False)
        embed.add_field(name="\nLetters", value=f"{' '.join(letters)}", inline=False)
        if contains_numbers:
            embed.add_field(name="\nNumbers", value=f"{' '.join(numbers)}", inline=False)
        embed.set_footer(text="Type 'exit' to end the game")
        current_game = await ctx.send(embed=embed)
        while guesses_left > 0:
            try:  # Continue to prompt the user for guesses until they are out of guesses
                guess = await self.bot.wait_for("message", timeout=60.0, check=check)
                response = guess.content
            except asyncio.TimeoutError:  # End the game if the user doesn't respond for a minute
                embed = hangman_embed(0xFF6675, "")
                embed.add_field(name="You took too long to respond.",
                                value=f"The {category} was: **{selected_word}**{country}",
                                inline=False)
                await ctx.send(embed=embed)
                return
            if response.upper() == f'-STATS {user_input.upper()}':
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Disasters' and '-DISASTERS' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Games' and '-GAMES' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Countries' and '-COUNTRIES' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Capitals' and '-CAPITALS' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'States' and '-STATES' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Teams' and '-TEAMS' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif user_input == 'Companies' and '-COMPANIES' == response.upper().split()[0]:
                await ctx.send(embed=cheating_embed())
                return
            elif response.upper() == selected_word.upper():  # Check if the user guesses the full word
                embed = hangman_embed(0x66FFCC, "")
                await on_win(ctx.author.id, category)
                await ctx.send(embed=embed)
                return
            elif response.startswith('*'):  # Allow the user to talk without guessing
                continue
            elif response.upper() == 'EXIT':  # Break the loop and end the game if the user types "exit"
                break
            elif len(response) != 1:  # Check if the response is not a letter
                embed = hangman_embed(0x800000, "")
                embed.add_field(name="Incorrect!", value=f"{''.join(mystery)}", inline=False)
                guesses_left -= 1
            elif response.upper() not in guessed and response.lower() in "abcdefghijklmnopqrstuvwxyz0123456789":
                guessed.append(response.upper())  # Add guess to list of guessed letters
                if response.isnumeric():
                    if contains_numbers:
                        numbers[numbers.index(f"**{response}**")] = f"~~{response}~~"  # Cross out guess
                    else:
                        continue
                else:
                    letters[letters.index(f"**{response.upper()}**")] = f"~~{response.upper()}~~"  # Cross out guess
                for appearance in range(selected_word.lower().count(response.lower())):
                    for index in range(len(mystery)):
                        if selected_word[index].lower() == response.lower():  # Check if the response matches any
                            # letter (case-insensitive)
                            mystery[index] = selected_word[index]  # Replace the index in the mystery word with the
                            # letter
                if response in "0123456789" and response in selected_word or response.lower() in selected_word.lower():
                    # Check if the character is in the word
                    embed = hangman_embed(0x14CB10, "")
                    embed.add_field(name="Correct!", value=f"{''.join(mystery)}", inline=False)
                else:
                    embed = hangman_embed(0xCB1010, "")
                    embed.add_field(name="Incorrect!", value=f"{''.join(mystery)}", inline=False)
                    guesses_left -= 1
            elif response.upper() in guessed:  # Check if the user already guessed the letter
                embed = hangman_embed(0xCB1010, "")
                embed.add_field(name="You already guessed that letter!", value=f"{''.join(mystery)}", inline=False)
            else:
                continue
            embed.add_field(name="\nRemaining Guesses", value=f"{guesses_left}", inline=False)
            embed.add_field(name="\nLetters", value=f"{' '.join(letters)}", inline=False)
            if contains_numbers:
                embed.add_field(name="\nNumbers", value=f"{' '.join(numbers)}", inline=False)
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text="Type 'exit' to end the game")
            await current_game.edit(embed=embed)
            if "\_ " not in mystery and "#" not in mystery:  # Check if all the letters have been guessed
                embed = hangman_embed(0x66FFCC, "")
                await on_win(ctx.author.id, category)
                await ctx.send(embed=embed)
                return
        embed = hangman_embed(0xFF6675, "")
        embed.add_field(name=f"You couldn't guess the {category}.",
                        value=f"The {category} was: **{selected_word}**{country}",
                        inline=False)
        await ctx.send(embed=embed)
        if guesses_left == 0:
            self.hangman.reset_cooldown(ctx)
        return

    async def get_collection(self, user, channel, collection, page, extra):
        uid = str(user.id)
        keys_per_page = 21
        if page == '-orderd':
            page = 1 if extra is None else int(extra)
            extra = '-orderd'
        elif page == '-ordera':
            page = 1 if extra is None else int(extra)
            extra = '-ordera'
        elif page is None:  # Set the page to 1 if not provided
            page = 1
        elif page.isnumeric():  # Check if the page is a number
            page = int(page)
        else:
            return
        with open(".\\files\\hangman\\words.json", 'r') as file:
            words = json.load(file)
        collection_list = words[collection]
        max_pages = (len(collection_list) - 1) // keys_per_page + 1
        if page > max_pages or page <= 0:  # Prevent users from going over page limit
            embed = discord.Embed(
                title=f"Invalid page. Maximum pages: {max_pages}",
                color=0x800000
            )
            await channel.send(embed=embed)
            return
        missing = sorted(words[collection])
        category = collection.lower()
        user_collected = await self.bot.pg_con.fetch(f"SELECT {category} FROM hangman_{category} WHERE user_id = $1"
                                                     f"ORDER BY {category} ASC", uid)
        totals = await self.bot.pg_con.fetch(f"SELECT total FROM hangman_{category} WHERE user_id = $1 "
                                             f"ORDER BY {category} ASC", uid)
        totals_dict = {user_collected[item][category]: totals[item]['total'] for item in range(len(user_collected))}
        for item in collection_list:
            if item not in totals_dict.keys():
                totals_dict[item] = 0
        if extra == '-orderd':
            collection_list = sorted(collection_list, key=totals_dict.get, reverse=True)
        elif extra == '-ordera':
            collection_list = sorted(collection_list, key=totals_dict.get, reverse=False)
        else:
            collection_list = sorted(collection_list)
        collected = []
        for item in range(len(user_collected)):
            for thing in user_collected[item]:
                collected.append(thing)
        for item in collected:  # Update missing_countries to remove collected countries
            if item in missing:
                missing.remove(item)
        starting_index = (page - 1) * keys_per_page
        keys_left = len(collection_list) - (page - 1) * keys_per_page
        if collection == "Disasters":
            title = "Disaster"
        elif collection == "Games":
            title = "Game"
        elif collection == "Countries":
            title = "Country"
        elif collection == "Capitals":
            title = "Capital"
        elif collection == "States":
            title = "State"
        elif collection == "Teams":
            title = "Team"
        elif collection == "Companies":
            title = "Company"
        else:
            return
        embed = discord.Embed(
            title=f"{title} Collection",
            description=f"You've collected **{len(collected)}/{len(collection_list)}** {category}!\n"
                        f"Guess {category} correctly in `-hangman {category}` to collect them.",
            color=0x00CBE6
        )
        for index in range(min(keys_per_page, keys_left)):
            item = collection_list[starting_index + index]
            if item in collected:
                count = totals_dict[item]
                embed.add_field(name=f":white_check_mark: {item}", value=f"{count} collected.", inline=True)
            if item in missing:
                embed.add_field(name=f"<:red_x:1005926523372585021> {item}", value="Missing.", inline=True)
        embed.set_footer(text=f"Page {page}/{max_pages}")
        embed.set_author(name=f"{user}", icon_url=f"{user.avatar_url}")
        await channel.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def disasters(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Disasters", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def games(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Games", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def countries(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Countries", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def capitals(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Capitals", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def states(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "States", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def teams(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Teams", page, order)

    @commands.command()
    @commands.cooldown(1, 1, commands.BucketType.user)  # 1-second cooldown
    async def companies(self, ctx, page=None, order=None):
        user = ctx.author
        await self.get_collection(user, ctx.channel, "Companies", page, order)

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def data(self, ctx, category):
        if category.title() not in ["Disasters", "Games", "Countries", "States", "Teams", "Companies"]:  # Make sure
            # it is a category
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            return
        category = category.lower()
        with open(".\\files\\hangman\\words.json") as file:
            words = json.load(file)
        words = words[category.title()]
        frequency = {}
        total_points = 0
        for word in words:
            total_count = 0
            totals = await self.bot.pg_con.fetch(f"SELECT total FROM hangman_{category} WHERE {category} = $1", word)
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
        mean = round(total_value / total_points, 2)
        middle = round((total_points + 1) / 2, 2)
        if middle % 1 == 0:
            median = item_list[int(middle) - 1]
        else:  # If the median is in between two, check if they are the same
            median_one = item_list[math.floor(middle) - 1]
            median_two = item_list[math.ceil(middle) - 1]
            if median_two == median_one:  # If they are the same
                median = median_one
            else:  # Include both if they are different
                median = f"{median_one}, {median_two}"
        if len(most) > 10:
            most = f"{len(most)} different {category}"
        else:
            most = ', '.join(most)
        if len(least) > 10:
            least = f"{len(least)} different {category}"
        else:
            least = ', '.join(least)
        embed = discord.Embed(
            title=f"Hangman {category.title()} Data",
            color=0x00CBE6
        )
        embed.add_field(name="Mean", value=f"{mean}", inline=False)
        embed.add_field(name="Median", value=f"{median}", inline=False)
        embed.add_field(name=f"Most Frequent [{most_amount}]", value=f"{most}", inline=False)
        embed.add_field(name=f"Least Frequent [{least_amount}]", value=f"{least}", inline=False)
        embed.set_footer(text=f"From {total_points} data points")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def graph(self, ctx, category):
        if category.title() not in ["Disasters", "Games", "Countries", "States", "Teams", "Companies"]:  # Make sure
            # it is a category
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            return
        category = category.lower()
        with open(".\\files\\hangman\\words.json", 'r') as file:
            words = json.load(file)[category.title()]
        frequency = {}
        data_points = 0;
        for word in words:
            total_count = 0
            totals = await self.bot.pg_con.fetch(f"SELECT total FROM hangman_{category} WHERE {category} = $1", word)
            for total in totals:
                total_count += total['total']
            frequency[word] = total_count
            data_points += total_count
        words = list(frequency.keys())
        amounts = list(frequency.values())

        fig, ax = plt.subplots(figsize=(25, 37.5))

        ax.barh(words, amounts, height=0.8, color=['dodgerblue', 'deepskyblue'], align='center', edgecolor='white', linewidth=1)
        ax.xaxis.set_tick_params(pad=1)
        ax.yaxis.set_tick_params(pad=1)
        ax.grid(b=True, color='grey',
                linestyle='-.', linewidth=0.5,
                alpha=0.2)
        ax.invert_yaxis()
        for i in ax.patches:
            plt.text(i.get_width() + 0.1, i.get_y() + 0.7,
                     str(round((i.get_width()), 2)),
                     fontsize=1440*math.pow(len(frequency), -0.95), fontweight='bold',
                     color='grey')
        ax.set_title(f'Hangman {category.title()} Frequency - {data_points} data points',
                     loc='left', fontsize=35)
        plt.margins(y=0.001)
        plt.yticks(fontsize=1390*math.pow(len(frequency), -0.95))
        plt.savefig(".\\files\\graph.png", bbox_inches='tight')
        plt.close(fig)
        file = discord.File(".\\files\\graph.png")
        await ctx.send(file=file)
        return

    @commands.command()
    @commands.is_owner()
    async def recover(self, ctx, country, *users):
        for user in users:
            uid = user.strip('<@!>')
            await self.bot.pg_con.execute(f"INSERT INTO hangman_countries (user_id, countries) "
                                          f"VALUES ($1, $2)", uid, country.title())
        user_list = []
        for user in users:
            user_list.append(f"<@{user}>")
        embed = discord.Embed(
            title=f"Recovered {country.title()} for:",
            description=f"{', '.join(user_list)}",
            color=0x000001
        )
        await ctx.send(embed=embed)

    @hangman.error
    async def hangman_error(self, ctx, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            embed = discord.Embed(
                title="You already have a game ongoing.",
                color=0x800000
            )
            embed.set_footer(text="Type 'exit' to end the game")
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=embed)
            error.error_handled = True


def setup(bot):
    bot.add_cog(Hangman(bot))
