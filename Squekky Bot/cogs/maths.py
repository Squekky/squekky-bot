import discord
import math
from discord.ext import commands

# Embed Color Palette:
# Invalid Input - 0x800000
# Calculation - 0x03C700


class Maths(commands.Cog):
    """ Math Commands """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prime(self, ctx, numInput):
        """ Check if a number is prime if it is less than 1 billion or return its smallest factor """
        try:
            num = int(numInput)
        except ValueError as error:  # Check for invalid inputs
            embed = discord.Embed(
                title=f"Invalid input. Please only use positive integers.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return

        if num < 0:  # Check if the number is negative
            embed = discord.Embed(
                title="Please refrain from using negative numbers.",
                color=0x800000
            )
        elif 0 <= num < 2:  # Check if the number is 0 or 1
            embed = discord.Embed(
                title=f"{numInput} is not prime.",
                color=0x03C700
            )
        elif num % 2 == 0 and num != 2:  # Check if the number is even
            embed = discord.Embed(
                title=f"{numInput} is not prime.",
                description=f"Divisible by 2",
                color=0x03C700
            )
        elif num > 10 ** 18:  # Check if the number is over 1 quintillion
            embed = discord.Embed(
                title="Input a number less than 1 quintillion.",
                color=0x800000
            )
        else:
            async with ctx.typing():  # Let the user know the bot is calculating
                prime = True
                for term in range(2, int(math.sqrt(num)) + 1):
                    if num % term == 0:
                        prime = False
                        break
                if prime:  # Create a custom embed if the number is prime
                    embed = discord.Embed(
                        title=f"{numInput} is prime!",
                        color=0x03C700
                    )
                elif not prime:  # Create a custom embed if the number is not prime
                    embed = discord.Embed(
                        title=f"{numInput} is not prime.",
                        description=f"Divisible by {term}",
                        color=0x03C700
                    )
                else:  # Create a custom embed if the calculation takes too long
                    embed = discord.Embed(
                        title=f"Calculation takes too long! :(",
                        color=0x800000
                    )
        embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
        await ctx.send(embed=embed)

    @commands.command(aliases=['fac'])
    async def factorial(self, ctx, numInput):
        """ Return the value of a given number's factorial """
        try:
            result = int(numInput)
        except ValueError as error:  # Check for invalid inputs
            embed = discord.Embed(
                title=f"Invalid input. Please only use positive integers.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return

        if result < 0:  # Avoid negative numbers
            embed = discord.Embed(
                title="Please refrain from using negative numbers.",
                color=0x800000
            )
        elif result > 100000:  # Prevent the embed from being too long
            embed = discord.Embed(
                title="Input a number less than 100,000.",
                color=0x800000
            )
        else:
            async with ctx.typing():
                for term in range(1, result):
                    result *= term
                if result == 0:  # 0! = 1
                    result = 1
                embed = discord.Embed(
                    title=f"{numInput}!",
                    description=f"{result}",
                    color=0x03C700
                )
        textFile = open('./files/math/largeFactorial.txt', 'w')  # Add the temporary value to a text file
        textFile.write(str(result))
        textFile.close()
        if len(str(result)) > 360:  # Prevent the embed descriptions from being too long
            embed = discord.Embed(
                title=f"{numInput}!",
                description="Value is too large, but here you go!",
                color=0x03C700
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
            raise commands.errors.CommandInvokeError  # Raise an error to send the text file of the output
        else:
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)

    @commands.command(aliases=['fib'])
    async def fibonacci(self, ctx, term):
        """ Return the value of a given term in the Fibonacci Sequence """
        try:
            term = int(term)
        except ValueError as error:  # Check for invalid inputs
            embed = discord.Embed(
                title=f"Invalid input. Please only use positive, nonzero integers.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            return

        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= term % 100 <= 20:  # Add suffixes to the given term
            suffix = 'th'
        else:
            suffix = suffixes.get(term % 100, 'th')
        stringTerm = str(term) + suffix

        first = 0
        second = 1
        output = 1
        if term > 1000000 or term < 1:  # Prevent the input of 0 and negative numbers
            embed = discord.Embed(
                title=f"Please enter a number between 1 and 1 million.",
                color=0x800000
            )
        elif term == 1:
            embed = discord.Embed(
                title=f"1st term of the Fibonacci Sequence",
                description="0",
                color=0x03C700
            )
        else:  # Calculate the provided term if it is not 1
            async with ctx.typing():
                for terms in range(2, term):
                    output = first + second  # Update the current term
                    first = second  # Set the first term to the following term
                    second = output  # Set the second term to the current term
                embed = discord.Embed(
                    title=f"{stringTerm} term of the Fibonacci Sequence",
                    description=f"{output}",
                    color=0x03C700
                )
            textFile = open('./files/math/largeFibonacci.txt', 'w')  # Add the temporary value to a text file
            textFile.write(str(output))
            textFile.close()
        embed.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar}")
        if len(str(output)) > 360:  # Prevent the embed descriptions from being too long
            embed = discord.Embed(
                title=f"{stringTerm} term of the Fibonacci Sequence",
                description="Term is too large, but here you go!",
                color=0x03C700
            )
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)
            raise commands.errors.CommandInvokeError  # Raise an error to send the text file of the output
        else:
            embed.set_author(name=f"{ctx.author}", icon_url=f"{ctx.author.avatar}")
            await ctx.send(embed=embed)

    @prime.error
    async def prime_error(self, ctx, error):
        """ Check for invalid characters """
        if isinstance(error, commands.errors.CommandInvokeError):
            embed = discord.Embed(
                title=f"Invalid input. Please only use positive integers.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True

    @factorial.error
    async def factorial_error(self, ctx, error):
        """ Send the output in a text file if it is longer than 360 characters """
        if isinstance(error, commands.errors.CommandInvokeError):
            new_error = error.original
            if isinstance(new_error, TypeError):
                await ctx.send(file=discord.File('./files/math/largeFactorial.txt'))
                error.error_handled = True
            else:
                print(new_error)

    @fibonacci.error
    async def fibonacci_error(self, ctx, error):
        """ Send the output in a text file if it is longer than 360 characters """
        if isinstance(error, commands.errors.CommandInvokeError):
            new_error = error.original
            if isinstance(new_error, TypeError):
                await ctx.send(file=discord.File('./files/math/largeFibonacci.txt'))
                error.error_handled = True
            else:
                print(error.original)


async def setup(bot):
    await bot.add_cog(Maths(bot))
