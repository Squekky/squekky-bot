import discord
import random
from discord.ext import commands


class Chainbreaker(commands.Cog):
    """ Breaks Chains """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, ctx):
        """ Break chat chains of 3 or more messages """
        message = ctx.content
        channel = ctx.channel
        user_id = str(ctx.author.id)
        channel_id = str(ctx.channel.id)
        guild_id = str(ctx.guild.id)
        disabled = [280345822435213312, 282641718359097344]  # Disable in s-rank and leaderboards
        disabled_guilds = [815768615269040148]  # Disable in Isaiah's server
        if ctx.channel.id in disabled or ctx.guild.id in disabled_guilds:  # Disable in s-rank and leaderboards
            return
        data = await self.bot.pg_con.fetch("SELECT * FROM messages WHERE channel_id = $1", channel_id)
        messages = [message['message_content'] for message in data]  # Get a list of past messages in that channel
        users = [message['user_id'] for message in data]
        if len(ctx.attachments) > 0:  # Add filenames to the message to break image chains
            for file in ctx.attachments:
                if file.filename != 'unknown.png':
                    message += file.filename
        for mention in ctx.mentions:  # Make sure mention chains are broken
            message = message.replace(f'!{mention.id}', f'{mention.id}')
        if ctx.author.bot or message == '':  # Delete the channel messages from the database when a bot sends a message
            await self.bot.pg_con.execute("DELETE FROM messages WHERE channel_id = $1", channel_id)
            return
        elif user_id in users:  # Prevent breaking chains when a user spams the same message
            await self.bot.pg_con.execute("DELETE FROM messages WHERE channel_id = $1", channel_id)
            await self.bot.pg_con.execute("INSERT INTO messages (channel_id, user_id, message_content) "
                                          "VALUES ($1, $2, $3)", channel_id, user_id, message)
        elif message in messages:
            if len(messages) >= 2:  # Break the chain if it is 3 or more messages
                broken = await self.bot.pg_con.fetch("SELECT chains_broken FROM broken")  # Get broken chains
                broken = broken[0]['chains_broken']
                embed = discord.Embed(
                    title="No chains!",
                    color=0x76E3FE
                )
                embed.set_footer(text=f"Chains Broken: {random.randint(0, 1000)}")
                await self.bot.pg_con.execute("DELETE FROM messages WHERE channel_id = $1", channel_id)  # Remove
                # messages in the channel from the database
                await self.bot.pg_con.execute("UPDATE broken SET chains_broken = $1", broken + 1)
                # Update broken chains
                try:
                    await channel.send(embed=embed)
                except:
                    print(f'ERROR: {channel}')
                return
            else:  # Add the message to the database if it's the same
                await self.bot.pg_con.execute("INSERT INTO messages (channel_id, user_id, message_content) "
                                              "VALUES ($1, $2, $3)", channel_id, user_id, message)
        else:  # Delete the messages and add the message to the database if it's a new message
            await self.bot.pg_con.execute("DELETE FROM messages WHERE channel_id = $1", channel_id)
            await self.bot.pg_con.execute("INSERT INTO messages (channel_id, user_id, message_content) "
                                          "VALUES ($1, $2, $3)", channel_id, user_id, message)

    @commands.command()
    @commands.is_owner()
    async def chains(self, ctx):
        broken = await self.bot.pg_con.fetch("SELECT chains_broken FROM broken")  # Get broken chains
        broken = broken[0]['chains_broken']
        embed = discord.Embed(
            title=f"Total Chains Broken: {broken}",
            color=0x76E3FE
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Chainbreaker(bot))
