import discord
import asyncpg
import json
import os
from discord.ext import commands

# Color Palette
# Leaderboards - 0x00CBE6
# Bot Online - 0x34FF1A
# Bot Offline - 0xFE2020
# Load Extension - 0x33FF66
# Unload Extension - 0xFF4242
# Reload Extension - 0xFFE642

intents = discord.Intents.default()
intents.members = True
intents.dm_messages = False


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, command_prefix='-', case_insensitive=True, help_command=None, intents=intents)

    async def close(self):
        print("Bot Offline.")
        channel = bot.get_channel(919315204096016384)
        embed = discord.Embed(
            color=0xFE2020
        )
        embed.add_field(name="Nap time!", value="squekky bot is taking a nap.", inline=False)
        await channel.send(embed=embed)
        await super().close()


bot = Bot()

async def create_db_pool():
    bot.pg_con = await asyncpg.create_pool(database="SQUEKKY_BOT", user="postgres", password=password)

@bot.event
async def on_ready():
    """ Print when the bot is online and send a message in a status channel """
    activity = discord.Game(name="-help")
    await bot.change_presence(activity=activity, status="L")
    print('Bot Online.')
    channel = bot.get_channel(919315204096016384)
    embed = discord.Embed(
        color=0x34FF1A
    )
    embed.add_field(name="Wakey wake!", value="squekky bot is awake!", inline=False)
    await channel.send(embed=embed)


def emb(ext, option):
    """ Create an embed that will be sent when a cog is loaded, unloaded, or reloaded """
    if option == 'Loaded':
        embed = discord.Embed(
            color=0x33FF66
        )
    elif option == 'Unloaded':
        embed = discord.Embed(
            color=0xFF4242
        )
    elif option == 'Reloaded':
        embed = discord.Embed(
            color=0xFFE642
        )
    else:
        embed = discord.Embed(
            color=0x000000
        )
    embed.add_field(name=f"Extension {option}", value=f"{option} {ext}", inline=False)
    return embed


@bot.command()
@commands.is_owner()  # Owner-only command
async def load(ctx, loaded):
    """ Load a cog to avoid restarting the entire program """
    try:
        bot.load_extension("cogs." + loaded)
        await ctx.send(embed=emb(loaded, 'Loaded'))
        print(f"{loaded}.py was loaded.")
    except Exception as error:
        print(f"{loaded}.py cannot be loaded. [{error}]")


@bot.command()
@commands.is_owner()  # Owner-only command
async def unload(ctx, unloaded):
    """ Unload a cog to avoid restarting the entire program """
    try:
        bot.unload_extension("cogs." + unloaded)
        await ctx.send(embed=emb(unloaded, 'Unloaded'))
        print(f"{unloaded}.py was unloaded.")
    except Exception as error:
        print(f"{unloaded}.py cannot be unloaded. [{error}]")


@bot.command()
@commands.is_owner()  # Owner-only command
async def reload(ctx, reloaded):
    """ Reload a cog to avoid restarting the entire program """
    try:
        bot.reload_extension("cogs." + reloaded)
        await ctx.send(embed=emb(reloaded, 'Reloaded'))
        print(f"{reloaded}.py was reloaded.")
    except Exception as error:
        print(f"{reloaded}.py cannot be reloaded. [{error}]")


if __name__ == '__main__':  # Start the bot when the program is run
    with open('config.json', 'r') as file:  # Get the bot token from the JSON file
        configData = json.load(file)
    token = configData["Token"]
    password = configData["Password"]
    for extension in os.listdir('.\\cogs'):  # Load the extensions associated with the bot
        if extension.endswith('.py') and not extension.startswith('_'):
            try:
                bot.load_extension(f"cogs.{extension.replace('.py', '')}")
                print(f"{extension} was loaded.")
            except Exception as error:  # Alert the user of any errors that occur when loading extensions
                print(f"{extension} cannot be loaded. [{error}]")
    bot.loop.run_until_complete(create_db_pool())
    bot.run(token)
