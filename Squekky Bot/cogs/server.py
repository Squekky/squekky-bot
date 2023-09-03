import discord
from discord.ext import commands


class Server(commands.Cog):
    """ Send messages when a user joins or leaves a server """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['si'])
    async def serverinfo(self, ctx):
        """ Send the statistics for the current server """
        guild = ctx.guild
        embed = discord.Embed(title=f"[{guild.name} Statistics]", color=0xff8aef)
        embed.set_thumbnail(url=f"{guild.icon_url}")
        embed.add_field(name="Members", value=f"{guild.member_count}", inline=False)
        embed.add_field(name="Roles", value=f"{len(guild.roles)}", inline=True)
        embed.add_field(name="Emojis", value=f"{len(guild.emojis)}", inline=True)
        embed.add_field(name="Server Owner", value=f"{guild.owner.mention}", inline=False)
        embed.add_field(name="Creation Date", value=f"{str(guild.created_at)[0:10]}", inline=False)
        embed.add_field(name="Channels", value=f"Text Channels: {len(guild.text_channels)}"
                        f"\nVoice Channels: {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="Boosts", value=f"{guild.premium_subscription_count}", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=['rc'])
    async def rolecheck(self, ctx, role: discord.Role = None):
        """ Check how many users have a given role """
        if role is None:
            embed = discord.Embed(
                title="Please include a valid role ID.",
                description="Use `-roleid (role name)` to fine the ID of a role.",
                color=0x800000
            )
            await ctx.send(embed=embed)
        else:
            users = len(role.members)  # Member count
            role_name = role.name
            if users == 1:
                embed = discord.Embed(
                    title=f"There is 1 user with the `{role_name}` role.",
                    color=0x00CBE6
                )
            else:
                embed = discord.Embed(
                    title=f"There are {users} users with the `{role_name}` role.",
                    color=0x00CBE6
                )
            await ctx.send(embed=embed)

    @commands.command()
    async def roleid(self, ctx, *role_name: str):
        role_name = ' '.join(role_name)
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                embed = discord.Embed(
                    title=f"The ID for {role.name} is `{role.id}`.",
                    description=f"Use `-rolecheck {role.id}` to see how many users have that role.",
                    color=0x00CBE6
                )
                await ctx.send(embed=embed)
                return
        embed = discord.Embed(
            title="Please include a valid role name.",
            color=0x800000
        )
        await ctx.send(embed=embed)

    @rolecheck.error
    async def rolecheck_error(self, ctx, error):
        if isinstance(error, commands.RoleNotFound):
            embed = discord.Embed(
                title="Please include a valid role ID.",
                description="Use `-roleid (role name)` to find the ID of a role.",
                color=0x800000
            )
            await ctx.send(embed=embed)
            error.error_handled = True


async def setup(bot):
    await bot.add_cog(Server(bot))
