import discord
import json
from discord.ext import commands

# Embed Color Palette
# Ghost - 0x7FFF5C


class Ghost(commands.Cog):
    """ Enables users the ability to ghost ping or opt in/out of being ghost pinged """
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)  # 30-second cooldown
    async def ghost(self, ctx, user: discord.Member):
        """ Ghost ping a user if they are not opted out and if the author is not opted out """
        if ctx.guild.id == 278099400285356033:  # Blacklist command in fanmade
            return
        else:
            pinger = ctx.message.author.id
            with open('./files/opted/opted_out.json', 'r') as file:
                optedout = json.load(file)
            if pinger in optedout:  # Prevent users that are opted out from ghost pinging others
                embed = discord.Embed(
                    title="You don\'t have permission to ghost ping",
                    description="**Reason:** Opted out",
                    color=0x800000
                )
                await ctx.send(embed=embed)
            else:
                if user.id not in optedout:  # Make sure the user is not opted out before ghost pinging
                    pinged = await self.bot.fetch_user(user.id)
                    await ctx.message.delete()
                    print(f'{ctx.message.author} ghost pinged {pinged}')
                else:
                    embed = discord.Embed(
                        title="Sorry, that user has opted out of ghost pings.",
                        color=0x800000
                    )
                    await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def opt(self, ctx):
        if ctx.guild.id == 278099400285356033:  # Blacklist command in fanmade
            return
        embed = discord.Embed(
            title="Please include a valid option.",
            description="Options: in, out",
            color=0x800000
        )
        await ctx.send(embed=embed)

    @opt.command(name='in')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1-minute cooldown
    async def opt_in(self, ctx):
        if ctx.guild.id == 278099400285356033:  # Blacklist command in fanmade
            return
        """ Allow the user to be ghost pinged """
        user = ctx.message.author.id
        with open('./files/opted/opted_out.json', 'r') as file:
            optedout = json.load(file)
        if user in optedout:  # Check that the user isn't already opted in
            optedout.remove(user)
            await ctx.send('Successfully opted into ghost pings.')
            print(f'{ctx.message.author} opted into ghost pings')
        else:
            await ctx.send('Already opted in.')
        with open('./files/opted/opted_out.json', 'w') as file:
            json.dump(optedout, file)

    @opt.command(name='out')
    @commands.cooldown(1, 60, commands.BucketType.user)  # 1-minute cooldown
    async def opt_out(self, ctx):
        if ctx.guild.id == 278099400285356033:  # Blacklist command in fanmade
            return
        """ Prevent the user from being ghost pinged """
        user = ctx.message.author.id
        with open('./files/opted/opted_out.json', 'r') as file:
            optedout = json.load(file)
        if user not in optedout:  # Check that the user isn't already opted out
            optedout.append(user)
            await ctx.send('Successfully opted out of ghost pings.')
            print(f'{ctx.message.author} opted out of ghost pings')
        else:
            await ctx.send('Already opted out.')
        with open('./files/opted/opted_out.json', 'w') as file:
            json.dump(optedout, file)

    @commands.command()
    @commands.is_owner()  # Owner-only command
    async def optedout(self, ctx):
        """ Print the list of users currently opted out """
        losers = ''
        with open('./files/opted/opted_out.json', 'r') as file:
            users = json.load(file)
        for user in users:
            username = self.bot.get_user(user)
            losers += f'{username.name}\n'
        embed = discord.Embed(
            title="Loser List",
            description=f"{losers}",
            color=0x7FFF5C
        )
        await ctx.send(embed=embed)

    @ghost.error
    async def ghost_error(self, ctx, error):
        if ctx.guild.id == 278099400285356033:  # Blacklist command in fanmade
            error.error_handled = True
            return
        if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            embed = discord.Embed(
                title="Please include a valid user ID or mention.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True


async def setup(bot):
    await bot.add_cog(Ghost(bot))
