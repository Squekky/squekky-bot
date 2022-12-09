import discord
from discord.ext import commands
from pytz import timezone


class Welcome(commands.Cog):
    """ Send messages when a user joins or leaves a server """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """ Send a welcome message in the main channel when a member leaves """
        channels = ['join-log', 'general', 'lobby']
        oldtime = timezone('UTC').localize(member.created_at)  # Convert the time from UTC to Eastern Time
        newtime = oldtime.astimezone(timezone('America/New_York'))
        created = newtime.strftime('%B %d, %Y at %I:%M %p [%Z]')  # Convert the time into a string using datetime format
        if created[-14] == '0':
            created = created[:-14] + created[-13:]
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description=f"{member.mention} joined the server.",
            color=0xff4747
        )
        embed.set_thumbnail(url=f"{member.avatar_url}")
        embed.set_footer(text=f"ID: {member.id}"
                              f"\nAccount Created: {created}")
        if member.guild.id == 760252418541223976:  # Make adjustments for Ambition
            channel = self.bot.get_channel(760252418541223979)
            colors = 760254936906334229
            rules = 760253647752921108
            embed.add_field(name=f"Before you do anything!",
                            value=f"Head to <#{rules}> for the basics and have fun!"
                                  f"\nPick out a custom color in <#{colors}>!", inline=True)
            await channel.send(embed=embed)
            return
        elif member.guild.id == 278099400285356033:  # Blacklist welcome messages in fanmade
            return
        else:
            for channel in member.guild.channels:  # Check for #lobby or #general to send the welcome message
                if channel.name in channels:
                    await channel.send(embed=embed)
                    return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """ Send a goodbye message in the main channel when a member leaves """
        channels = ['join-log', 'general', 'lobby']
        oldtime = timezone('UTC').localize(member.joined_at)  # Convert the time from UTC to Eastern Time
        newtime = oldtime.astimezone(timezone('America/New_York'))
        joined = newtime.strftime('%B %d, %Y at %I:%M %p [%Z]')  # Convert the time into a string using datetime format
        if joined[-14] == '0':
            joined = joined[:-14] + joined[-13:]
        embed = discord.Embed(
            title="Farewell!",
            description=f"{member.mention} left the server.",
            color=0xff4747
        )
        embed.set_thumbnail(url=f"{member.avatar_url}")
        embed.set_footer(text=f"ID: {member.id}"
                              f"\nDate Joined: {joined}")
        if member.guild.id == 760252418541223976:  # Make adjustments for Ambition
            channel = self.bot.get_channel(760252418541223979)
            await channel.send(embed=embed)
            return
        elif member.guild.id == 278099400285356033:  # Blacklist leave messages in fanmade
            return
        else:
            for channel in member.guild.channels:  # Check for #lobby or #general to send the welcome message
                if channel.name in channels:
                    await channel.send(embed=embed)
                    return

def setup(bot):
    bot.add_cog(Welcome(bot))
