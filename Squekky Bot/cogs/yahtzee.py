import discord
import asyncio
import random
import uuid
import os
from discord.ext import commands
from PIL import Image


class Yahtzee(commands.Cog):
    """ Play Yahtzee """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def yahtzee(self, ctx):
        uid = str(ctx.author.id)
        categories = {  # Create dictionary for categories that tracks score
            "Ones": '`-`',
            "Twos": '`-`',
            "Threes": '`-`',
            "Fours": '`-`',
            "Fives": '`-`',
            "Sixes": '`-`',
            "3 Of A Kind": '`-`',
            "4 Of A Kind": '`-`',
            "Full House": '`-`',
            "Small Straight": '`-`',
            "Large Straight": '`-`',
            "Yahtzee": '`-`',
            "Chance": '`-`'
        }
        rolled_dice = [0, 0, 0, 0, 0]
        kept_dice = {}

        def check(selection):  # Make sure the response is in the same channel from the same user
            return selection.channel == ctx.channel and selection.author == ctx.author

        turns = 13
        rolls = 3

        def get_score():
            score = 0
            upper_section = 0
            for value in categories.values():  # Calculate base score
                if value != "`-`":
                    score += value
            for upper in list(categories)[:6]:  # Calculate upper section score
                if categories[upper] != "`-`" and categories[upper] <= 30:
                    upper_section += categories[upper]
            if upper_section >= 63:  # Check if upper bonus was earned
                score += 35
            return score

        def yahtzee_bonus(numbers):  # Check if the player has their second yahtzee
            for number in numbers:
                if rolled_dice.count(number) == 5 and categories["Yahtzee"] == 50:
                    return 50
            return 0

        async def play():
            category_list = ''
            for category in categories.keys():
                category_list += f"- `{category}`\n"
            embed = discord.Embed(
                title="Choose where you want to play your dice.",
                description=category_list,
                color=0xFF7300
            )
            embed.set_image(url=f"attachment://{file_name}")
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            play_embed = await ctx.send(embed=embed)
            while True:
                try:
                    played = await self.bot.wait_for("message", timeout=60.0, check=check)
                except asyncio.TimeoutError:  # End the game if the user doesn't respond for a minute
                    embed = discord.Embed(
                        title="Yahtzee",
                        color=0xFF6675
                    )
                    embed.add_field(name="You took too long to respond.", value=f"Your score was: **{score}**",
                                    inline=False)
                    await ctx.send(embed=embed)
                    await on_end()
                    return
                if played.content.title() not in categories:
                    embed = discord.Embed(
                        title=f"Please select a valid category.",
                        description=category_list,
                        color=0x800000
                    )
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                    await play_embed.edit(embed=embed)
                    continue
                elif categories[played.content.title()] != '`-`':
                    embed = discord.Embed(
                        title=f"You already played that category.",
                        description=category_list,
                        color=0x800000
                    )
                    embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                elif played.content.upper() == 'ONES':
                    categories["Ones"] = rolled_dice.count(1) + yahtzee_bonus([1])
                    break
                elif played.content.upper() == 'TWOS':
                    categories["Twos"] = 2 * rolled_dice.count(2) + yahtzee_bonus([2])
                    break
                elif played.content.upper() == 'THREES':
                    categories["Threes"] = 3 * rolled_dice.count(3) + yahtzee_bonus([3])
                    break
                elif played.content.upper() == 'FOURS':
                    categories["Fours"] = 4 * rolled_dice.count(4) + yahtzee_bonus([4])
                    break
                elif played.content.upper() == 'FIVES':
                    categories["Fives"] = 5 * rolled_dice.count(5) + yahtzee_bonus([5])
                    break
                elif played.content.upper() == 'SIXES':
                    categories["Sixes"] = 6 * rolled_dice.count(6) + yahtzee_bonus([6])
                    break
                elif played.content.upper() == '3 OF A KIND':
                    categories["3 Of A Kind"] = 0
                    for dice in rolled_dice:
                        if rolled_dice.count(dice) >= 3:
                            categories["3 Of A Kind"] = sum(rolled_dice) + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                            break
                    break
                elif played.content.upper() == '4 OF A KIND':
                    categories["4 Of A Kind"] = 0
                    for dice in rolled_dice:
                        if rolled_dice.count(dice) >= 4:
                            categories["4 Of A Kind"] = sum(rolled_dice) + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                            break
                    break
                elif played.content.upper() == 'FULL HOUSE':
                    categories["Full House"] = 0 + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                    house_check = -4
                    for dice in [1, 2, 3, 4, 5, 6]:
                        if rolled_dice.count(dice) == 2:
                            house_check += 2
                        elif rolled_dice.count(dice) == 3:
                            house_check += 3
                    if house_check == 1:
                        categories["Full House"] = 25
                    break
                elif played.content.upper() == 'SMALL STRAIGHT':
                    categories["Small Straight"] = 0 + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                    one_to_four = True
                    two_to_five = True
                    three_to_six = True
                    for straight in range(1, 5):
                        if straight not in rolled_dice:
                            one_to_four = False
                    for straight in range(2, 6):
                        if straight not in rolled_dice:
                            two_to_five = False
                    for straight in range(3, 7):
                        if straight not in rolled_dice:
                            three_to_six = False
                    if one_to_four or two_to_five or three_to_six:
                        categories["Small Straight"] = 30
                    break
                elif played.content.upper() == 'LARGE STRAIGHT':
                    categories["Large Straight"] = 0 + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                    one_to_five = True
                    two_to_six = True
                    for straight in range(1, 6):
                        if straight not in rolled_dice:
                            one_to_five = False
                    for straight in range(2, 7):
                        if straight not in rolled_dice:
                            two_to_six = False
                    if one_to_five or two_to_six:
                        categories["Large Straight"] = 40
                    break
                elif played.content.upper() == 'YAHTZEE':
                    categories["Yahtzee"] = 0
                    for number in [1, 2, 3, 4, 5, 6]:
                        if rolled_dice.count(number) == 5:
                            categories["Yahtzee"] = 50
                    break
                elif played.content.upper() == 'CHANCE':
                    categories["Chance"] = sum(rolled_dice) + yahtzee_bonus([1, 2, 3, 4, 5, 6])
                    break
            rolls = 3
            kept_dice = {}
            await play_embed.delete()
            return

        async def on_end():  # Transfer data to database after a game
            score = get_score()
            high = await self.bot.pg_con.fetch("SELECT score FROM yahtzee WHERE user_id = $1", uid)
            if not high:
                await self.bot.pg_con.fetch("INSERT INTO yahtzee (user_id, score) VALUES ($1, $2)", uid, score)
            elif score > high[0]['score']:
                await self.bot.pg_con.execute("UPDATE yahtzee SET score = $1 WHERE user_id = $2", score, uid)
                return True

        while True:
            if turns <= 0:  # Check if the user has finished the game
                score = get_score()
                embed = discord.Embed(
                    title="Yahtzee",
                    description=f"**Final Score:** {score}\n",
                    color=0xFF7300
                )
                for category in categories.keys():
                    embed.add_field(name=category, value=categories[category], inline=True)
                embed.set_thumbnail(url=ctx.author.avatar)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                if await on_end():
                    embed.set_footer(text="New high score!")
                game = await ctx.send(embed=embed)
                await on_end()
                return
            for dice in range(5):  # Reroll and make sure dice are kept
                if str(dice+1) in kept_dice.keys():
                    continue
                else:
                    current_dice = random.randint(1, 6)
                    rolled_dice[dice] = current_dice
            kept_dice = {}
            rolls -= 1
            new_image = Image.new("RGBA", (1280, 256))  # Create a new image for the embed
            for dice in range(5):  # Add the dice images to the new image
                dice_image = Image.open(f".\\files\\dice\\{rolled_dice[dice]}_dice.png").resize((256, 256))
                new_image.paste(dice_image, (dice*256, 0))
            file_name = str(uuid.uuid4()) + ".png"  # Generate a random filename for each roll
            new_image.save(f".\\files\dice\yahtzee\\{file_name}")
            file = discord.File(f".\\files\dice\yahtzee\\{file_name}", filename=file_name)
            score = get_score()
            embed = discord.Embed(
                title="Yahtzee",
                description=f"**Score:** {score}\n"
                            f"**Rolls Left in Turn:** {rolls}\n\n"
                            f"**Options:**\n"
                            f"`roll` to roll again\n"
                            f"`play` to play your dice\n"
                            f"`keep` to select dice to keep then reroll",
                color=0xFF7300
            )
            for category in categories.keys():  # Created embed fields for score in each category
                embed.add_field(name=category, value=categories[category], inline=True)
            embed.set_image(url=f"attachment://{file_name}")
            embed.set_thumbnail(url=ctx.author.avatar)
            embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
            embed.set_footer(text="Type 'exit' to end the game")
            game = await ctx.send(file=file, embed=embed)
            os.remove(f'.\\files\\dice\\yahtzee\\{file_name}')
            if rolls == 0:  # Make the user play a category if they are out of rolls
                embed = discord.Embed()
                stop_check = await play()
                if stop_check:
                    return
                rolls = 3
                turns -= 1
                await game.delete()
                continue
            try:  # Allow the user to choose options throughout the game
                selection = await self.bot.wait_for("message", timeout=60.0, check=check)
                response = selection.content
            except asyncio.TimeoutError:  # End the game if the user doesn't respond for a minute
                embed = discord.Embed(
                    title="Yahtzee",
                    color=0xFF6675
                )
                embed.add_field(name="You took too long to respond.", value=f"Your score was: **{score}**",
                                inline=False)
                await ctx.send(embed=embed)
                await on_end()
                return
            if selection.content.upper() == 'ROLL':  # Reroll
                await game.delete()
                continue
            elif selection.content.upper() == 'PLAY':  # Call play function to determine the category to play
                stop_check = await play()
                if stop_check:
                    return
                rolls = 3
                turns -= 1
                await game.delete()
                continue
            elif selection.content.upper() == 'KEEP':  # Prompt the user to select dice to keep
                embed = discord.Embed(
                    title="Select which dice you would like to keep (1-5).",
                    description="For example, if you want to keep the 1st and 3rd dice, respond with: `13`",
                    color=0xFF7300
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                embed.set_footer(text="Type 'done' finish selecting.")
                kept_embed = await ctx.send(embed=embed)
                while True:
                    try:
                        kept = await self.bot.wait_for("message", timeout=60.0, check=check)
                        keeping = kept.content
                        if kept.content.upper() == 'DONE':  # Reroll once finished
                            await kept_embed.delete()
                            break
                    except asyncio.TimeoutError:  # End the game if the user doesn't respond for a minute
                        embed = discord.Embed(
                            title="Yahtzee",
                            color=0xFF6675
                        )
                        embed.add_field(name="You took too long to respond.", value=f"Your score was: **{score}**",
                                        inline=False)
                        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                        await ctx.send(embed=embed)
                        await on_end()
                        return
                    if keeping.isnumeric():
                        for dice in keeping:
                            if dice in kept_dice:
                                continue
                            elif 0 < int(dice) < 6:
                                kept_dice[dice] = rolled_dice[int(dice) - 1]
                            else:
                                continue
                        kept_text = ''
                        for dice in kept_dice.keys():
                            kept_text += f"- Dice #{dice} - `{kept_dice[dice]}`\n"
                        embed = discord.Embed(
                            title=f"Dice you chose to keep:",
                            description=kept_text,
                            color=0xFF7300
                        )
                        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                        embed.set_footer(text="Type 'done' finish selecting.")
                        await kept_embed.edit(embed=embed)
            elif selection.content.upper().split()[0] == 'KEEP':  # Allow one line to be used to keep dice
                for char in selection.content:
                    if char.isnumeric():
                        if char in kept_dice:
                            continue
                        elif 0 < int(char) < 6:
                            kept_dice[char] = rolled_dice[int(char) - 1]
                        else:
                            continue
            elif selection.content.upper() == 'EXIT':  # End the game
                embed = discord.Embed(
                    title="Yahtzee",
                    color=0xFF6675
                )
                embed.add_field(name="You ended the game.", value=f"Your score was: **{score}**",
                                inline=False)
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.send(embed=embed)
                await on_end()
                return
            else:  # Do nothing if an invalid option is chosen
                rolls += 1
                kept_dice = {'1': '', '2': '', '3': '', '4': '', '5': ''}
                embed = discord.Embed(
                    title=f"Invalid option",
                    description=f"**Options:**\n"
                                f"`roll` to roll again\n"
                                f"`play` to play your dice\n"
                                f"`keep` to select dice to keep then reroll",
                    color=0x800000
                )
                embed.set_author(name=ctx.author, icon_url=ctx.author.avatar)
                await ctx.send(embed=embed)
            await game.delete()


async def setup(bot):
    await bot.add_cog(Yahtzee(bot))
