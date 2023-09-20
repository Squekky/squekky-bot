import discord
from discord.ext import commands

# Embed Color Palette:
# Mute User - 0xEE6D17
# Unmute User - 0x17EE69
# Error - 0xFFCD42


class Moderation(commands.Cog):
    """ Moderation commands used for the bot """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['mute'])
    @commands.has_permissions(administrator=True)  # Requires administrator permission
    async def kill(self, ctx, user: discord.Member):
        """ Indefinitely mute a given user if they are not already muted """
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            role = await ctx.guild.create_role(name="Muted",
                                               permissions=discord.Permissions(send_messages=False),
                                               color=0x000001)
        killed = user.mention
        embed = discord.Embed(
            color=0xEE6D17
        )
        if role not in user.roles:  # Check to make sure the user isn't muted
            embed.add_field(name="User Killed", value=f"Rest in peace {killed}.", inline=False)
            await user.add_roles(role)
        else:  # Let the administrator know if the user is already muted
            embed.add_field(name="User Already Dead", value=f"{killed} is already dead, stop it!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['unmute'])
    @commands.has_permissions(administrator=True)  # Requires Administrator permission
    async def revive(self, ctx, user: discord.Member):
        """ Unmute a given user if they are muted """
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        killed = user.mention
        embed = discord.Embed(
            color=0x17EE69
        )
        if role in user.roles:  # Check to make sure the user is muted
            embed.add_field(name="User Revived", value=f"Welcome back, {killed}!", inline=False)
            await user.remove_roles(role)
        else:  # Let the administrator know if the user is already unmuted
            embed.add_field(name="User Alive", value=f"{killed} is already alive.", inline=False)
        await ctx.send(embed=embed)

    @kill.error
    async def kill_error(self, ctx, error):
        """ Let the user know when the command returns an error after being executed and log the error """
        if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            embed = discord.Embed(
                title="Please include a valid user ID or mention.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True
        elif not isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                color=0xFFCD42
            )
            embed.add_field(name="Something went wrong!", value="Your weapon malfunctioned! [Check logs]", inline=False)
            await ctx.send(embed=embed)
            print(error)

    @revive.error
    async def revive_error(self, ctx, error):
        """ Let the user know when the command returns an error after being executed and log the error """
        if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            embed = discord.Embed(
                title="Please include a valid user ID or mention.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True
        elif not isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                color=0xFFCD42
            )
            embed.add_field(name="Something went wrong!", value="Your weapon malfunctioned! [Check logs]", inline=False)
            await ctx.send(embed=embed)
            print(error)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji == '🖕':
            await reaction.message.clear_reaction('🖕')

    @commands.Cog.listener()
    async def on_message(self, message):
        if '🖕' in message.content:
            await message.delete()


async def setup(bot):
    await bot.add_cog(Moderation(bot))
