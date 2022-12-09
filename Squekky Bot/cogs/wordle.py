import discord
import asyncio
import json
import random
from discord.ext import commands


def get_pattern(length, wrong_spot, guess, answer):
    confirmed_letters = []
    result = []
    letters = {}
    answer_str = list(answer)
    for num in range(length):
        letters[guess[num]] = guess.count(guess[num])
    for num in range(length):
        letter = guess[num]
        if letter == answer[num]:
            result.append('🟩')
            confirmed_letters.append(letter)
            answer_str.remove(letter)
        elif letter not in answer or letters[letter] > answer_str.count(letter):
            result.append('⬛')
        elif letter in answer and answer[num] != letter \
                and confirmed_letters.count(letter) < answer.count(letter) and \
                (letters[letter] <= answer.count(letter) or letters[letter] == 1):
            result.append(wrong_spot)
            confirmed_letters.append(letter)
            answer_str.remove(letter)
        letters[letter] -= 1
    return result


class Wordle(commands.Cog):
    """ Play or check a Wordle """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def wordlecheck(self, ctx, input_word: str):
        with open(".\\files\\wordle\\word_frequency_bot.json") as file:
            frequency = json.load(file)
        with open(".\\files\\wordle\\wordle_words_bot.txt") as file:
            words = [word.strip() for word in file.readlines()]
        word_to_guess = input_word.lower()
        if word_to_guess.upper() == 'RANDOM':
            word_to_guess = words[random.randint(0, len(words))]
        elif len(word_to_guess) != 5 or word_to_guess not in words:
            embed = discord.Embed(
                title="Invalid word.",
                description="Please provide a valid 5 letter word.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return
        guess = "trace"
        tried_words = {}
        async with ctx.typing():
            while True:
                confirmed_letters = []
                if guess == word_to_guess:
                    tried_words[guess] = ['🟩'] * 5
                    break
                result = []
                letters = {}
                for num in range(5):
                    letters[guess[num]] = guess.count(guess[num])
                for num in range(5):
                    letter = guess[num]
                    if letter == word_to_guess[num]:
                        result.append('🟩')
                        confirmed_letters.append(letter)
                    elif letter in word_to_guess and word_to_guess[num] != letter \
                            and confirmed_letters.count(letter) < word_to_guess.count(letter) and \
                            (letters[letter] <= word_to_guess.count(letter) or letters[letter] == 1):
                        result.append('🟨')
                        confirmed_letters.append(letter)
                    else:
                        result.append('⬛')
                    letters[letter] -= 1
                for num in range(5):
                    checking_words = words.copy()
                    letter = guess[num]
                    color = result[num]
                    if color == '🟩':
                        for word in checking_words:
                            if letter != word[num] and word in words:
                                # Remove words without the letter in the given position
                                words.remove(word)
                    elif color == '🟨':
                        for word in checking_words:
                            if (letter not in word or word[num] == letter) and word in words:
                                # Remove words if they:
                                # - Do not have the letter
                                # - Have the letter in the given position
                                words.remove(word)
                    elif color == '⬛':
                        for word in checking_words:
                            if letter in word and word in words:
                                if word[num] == letter or confirmed_letters.count(letter) == 0 \
                                        or (word.count(letter) < confirmed_letters.count(letter)) \
                                        or (guess.count(letter) > confirmed_letters.count(letter)
                                            and word.count(letter) > confirmed_letters.count(letter)):
                                    # Remove words if they:
                                    # - Have the letter in the given spot
                                    # - Contain letter if it's excluded
                                    # - Contain fewer of the letter than the confirmed amount
                                    # - Contain more of a letter than the proven amount
                                    words.remove(word)
                tried_words[guess] = result
                guess = sorted(words, key=frequency.get, reverse=True)[0]  # Get best next guess using word frequency
        embed = discord.Embed(
            title=f"Selected Word: {word_to_guess}",
            color=0x14CB10
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        count = 0
        for word in tried_words:
            count += 1
            embed.add_field(name=f'Guess {count}: {word}', value=f'{" ".join(tried_words[word])}', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 10, commands.BucketType.user)  # 10-second cooldown
    async def wordle(self, ctx):
        with open(".\\files\\wordle\\word_frequency_bot.json") as file:
            frequency = json.load(file)
        with open(".\\files\\wordle\\wordle_words_bot.txt") as file:
            words = [word.strip() for word in file.readlines()]
        word_to_guess = sorted(words, key=frequency.get, reverse=True)[random.randint(0, 2000)]  # Only include the
        # 2500 most frequent words

        def check(guess):
            return guess.author == ctx.author and guess.channel == ctx.channel

        embed = discord.Embed(
            title="Wordle",
            description="Enter your first guess to begin the game!",
            color=0xFF7300
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Type 'exit' to end the game")
        current_game = await ctx.send(embed=embed)
        tried_words = []
        tried_results = []
        turns = 6
        while turns > 0:
            try:
                guess = await self.bot.wait_for("message", timeout=120.0, check=check)
                guess = guess.content.lower()
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="Wordle",
                    color=0xFF6675
                )
                embed.add_field(name="You took too long to respond.", value=f"The word was: **{word_to_guess}**",
                                inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                return
            if guess.upper() == 'EXIT':  # Allow the user to end the game if they wish
                embed = discord.Embed(
                    title="Wordle",
                    color=0xFF6675
                )
                embed.add_field(name="You ended the game.", value=f"The word was: **{word_to_guess}**",
                                inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                return
            elif len(guess) != 5 or guess.lower() not in words:  # Make sure the guess is valid
                continue
            else:
                turns -= 1
                result = get_pattern(5, '🟨', guess, word_to_guess)
                tried_words.append(guess)  # Use lists to track guesses and results to account for duplicates
                tried_results.append(result)
                if guess == word_to_guess:
                    embed = discord.Embed(
                        title=f"Wordle - Winner!",
                        color=0x14CB10
                    )
                    turns = 0
                elif turns == 0:
                    embed = discord.Embed(
                        title=f"Wordle - Better luck next time!",
                        color=0xFF6675
                    )
                    embed.add_field(name="You ran out of turns.", value=f"The word was: **{word_to_guess}**",
                                    inline=False)
                else:
                    embed = discord.Embed(
                        title=f"Wordle - {turns} turns remaining",
                        color=0xFF7300
                    )
                    embed.set_footer(text="Type 'exit' to end the game")
                count = 0
                for word in tried_words:
                    embed.add_field(name=f'Guess {count + 1}: {tried_words[count]}',
                                    value=f'{" ".join(tried_results[count])}', inline=False)
                    count += 1
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await current_game.edit(embed=embed)

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 10, commands.BucketType.user)  # 10-second cooldown
    async def nerdle(self, ctx):
        with open(".\\files\\wordle\\nerdle_equations.json") as f:
            calculations = json.load(f)
        calculation = calculations[random.randint(0, len(calculations) - 1)]
        embed_calc = calculation.replace("*", "\*")

        def check(guess):
            return guess.author == ctx.author and guess.channel == ctx.channel

        embed = discord.Embed(
            title="Nerdle",
            description="Enter your first guess to begin the game!",
            color=0xFF7300
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Type 'exit' to end the game")
        current_game = await ctx.send(embed=embed)
        tried_words = []
        tried_results = []
        turns = 6
        while turns > 0:
            try:
                guess = await self.bot.wait_for("message", timeout=120.0, check=check)
                guess = guess.content.lower()
                eval_guess = guess.replace('=', '==').replace('/', '//')
            except asyncio.TimeoutError:
                embed = discord.Embed(
                    title="Nerdle",
                    color=0xFF6675
                )
                embed.add_field(name="You took too long to respond.", value=f"The calculation was: **{embed_calc}**",
                                inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                return
            if guess.upper() == 'EXIT':  # Allow the user to end the game if they wish
                embed = discord.Embed(
                    title="Nerdle",
                    color=0xFF6675
                )
                embed.add_field(name="You ended the game.", value=f"The calculation was: **{embed_calc}**",
                                inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
                return
            elif len(guess) != 8 or not eval(eval_guess):  # Make sure the guess is valid
                continue
            else:
                turns -= 1
                result = get_pattern(8, '🟪', guess, calculation)
                tried_words.append(guess.replace('*', '\*'))  # Use lists to track guesses and results to account for
                # duplicates
                tried_results.append(result)
                if guess == calculation:
                    embed = discord.Embed(
                        title=f"Nerdle - Winner!",
                        color=0x14CB10
                    )
                    turns = 0
                elif turns == 0:
                    embed = discord.Embed(
                        title=f"Nerdle - Better luck next time!",
                        color=0xFF6675
                    )
                    embed.add_field(name="You ran out of turns.", value=f"The calculation was: **{embed_calc}**",
                                    inline=False)
                else:
                    embed = discord.Embed(
                        title=f"Nerdle - {turns} turns remaining",
                        color=0xFF7300
                    )
                    embed.set_footer(text="Type 'exit' to end the game")
                count = 0
                for word in tried_words:
                    embed.add_field(name=f'Guess {count + 1}: {tried_words[count]}',
                                    value=f'{" ".join(tried_results[count])}', inline=False)
                    count += 1
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await current_game.edit(embed=embed)


def setup(bot):
    bot.add_cog(Wordle(bot))
