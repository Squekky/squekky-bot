import string
import discord
import asyncio
import json
import random
import time
from discord.ext import commands


class Flags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.user)  # Prevent user from having more than 1 ongoing game
    @commands.cooldown(1, 60, commands.BucketType.user)  # 60-second cooldown
    async def flags(self, ctx, mode=None):
        channel = ctx.channel
        if mode is None:  # Check if mode is not provided
            await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
            self.flags.reset_cooldown(ctx)
            return

        with open("./files/flags/categories.json", "r") as file:
            mode = mode.lower()
            try:
                flag_names = dict(json.load(file))[mode]
            except KeyError:
                await ctx.invoke(self.bot.get_command(f'help {ctx.command}'))
                self.flags.reset_cooldown(ctx)
                return
            fold = f"{mode}/"

        random.shuffle(flag_names)

        def flag_embed(color, description=None):
            accuracy = round(((score / guessed) * 100), 2) if guessed > 0 else 0
            embed = discord.Embed(
                title=f"Score: {score}/{guessed} [{accuracy}%]",
                description=description,
                colour=color
            )
            embed.set_footer(text="Type 'exit' to end the game")
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            return embed

        async def game_over(color):
            accuracy = round(((score / len(flag_names)) * 100), 2) if guessed > 0 else 0
            end_time = time.perf_counter()
            timer = round((end_time - start_time), 2)

            if mode == 'countries':
                uid = str(ctx.author.id)
                user = await self.bot.pg_con.fetchrow("SELECT * FROM flags WHERE user_id = $1", uid)
                if not user:  # Create new user
                    await self.bot.pg_con.execute("INSERT INTO flags (user_id, accuracy, time) VALUES ($1, $2, $3)",
                                                  uid, accuracy, timer)
                else:
                    if accuracy > user['accuracy'] or \
                            (accuracy == user['accuracy'] and timer < user['time']):
                        await self.bot.pg_con.execute("UPDATE flags SET accuracy = $1, time = $2 WHERE user_id = $3",
                                                      accuracy, timer, uid)

            embed = discord.Embed(
                title=f"Final Score: {score}/{len(flag_names)} [{accuracy}%] [{timer}s]",
                colour=color
            )
            embed.set_footer(text=f"mode: {mode}")
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            return embed

        def rmv_punc(text):
            return text.translate(str.maketrans('', '', string.punctuation))

        def check(new_guess):  # Make sure the response is in the same channel from the same user
            return new_guess.channel == channel and new_guess.author == ctx.author

        score = 0
        guessed = 0

        start_time = time.perf_counter()
        flag_image = rmv_punc(flag_names[0].lower().replace(" ", "")) + ".png"
        full_flag_image = fold + flag_image
        flag_file = discord.File(f"./files/flags/{full_flag_image}", filename="flag.png")
        embed = flag_embed(0xD780FF)
        embed.set_thumbnail(url=f"attachment://flag.png")
        current_game = await ctx.send(file=flag_file, embed=embed)
        for flag in flag_names:
            current_flag = rmv_punc(flag.lower().replace(" ", ""))
            accepted_names = []
            with open("./files/flags/categories.json", "r") as file:
                try:
                    accepted_names = list(json.load(file)["Alternate Names"][flag])
                except KeyError:
                    pass
            accepted_names.append(current_flag)
            guessed += 1
            try:  # Continue to prompt the user for guesses until they quit or finish the game
                guess = await self.bot.wait_for("message", timeout=60.0, check=check)
                while guess.content[0] == "*":  # Check if the user is commenting out their guess
                    guess = await self.bot.wait_for("message", timeout=60.0, check=check)
                response = rmv_punc(guess.content)
            except asyncio.TimeoutError:  # End the game if the user doesn't respond for a minute
                guessed -= 1
                await ctx.send(embed=await game_over(0xFF6675))
                self.flags.reset_cooldown(ctx)
                break
            if response.upper() == 'EXIT':  # Break the loop and end the game if the user types "exit"
                guessed -= 1
                await ctx.send(embed=await game_over(0x66FFCC))
                break
            elif rmv_punc(response.lower().replace(" ", "")) in accepted_names:
                score += 1
                embed = flag_embed(0x14CB10)
            else:
                embed = flag_embed(0xFF6675, description=f"The previous flag was {flag}")
            try:
                flag_image = rmv_punc(flag_names[flag_names.index(flag) + 1].lower().replace(" ", "")) + ".png"
                full_flag_image = fold + flag_image
            except IndexError:
                await ctx.send(embed=await game_over(0x66FFCC))
                self.flags.reset_cooldown(ctx)
                break
                # Game over
            flag_file = discord.File(f"./files/flags/{full_flag_image}", filename="flag.png")
            embed.set_thumbnail(url=f"attachment://flag.png")
            if guessed % 10 == 0:
                current_game = await ctx.send(file=flag_file, embed=embed)
            else:
                await current_game.edit(attachments=[flag_file], embed=embed)


async def setup(bot):
    await bot.add_cog(Flags(bot))
