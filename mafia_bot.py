import discord
import os
import query
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv("TOKEN")

mafia_bot = commands.Bot("!")


@mafia_bot.event
async def on_ready():
    print("Ready")


# Command for getting a list of all setups
@mafia_bot.command()
async def setups(ctx):
    await ctx.send(query.query_setups())


# Command for getting setup info
@mafia_bot.command()
async def setup(ctx, name: str = "default", version: float = -1.0):
    await ctx.send(query.query_setup(name, version))


# Command for getting setup documentation
@mafia_bot.command(name="setup-doc")
async def setup_doc(ctx, name: str = "default", version: float = -1.0):
    msg, filename = query.query_setup_doc(name, version)

    if filename is not None:
        await ctx.send(content=msg, file=discord.File(filename))
    else:
        await ctx.send(msg)


# Command for changing the default setup
@mafia_bot.command(name="default-setup")
async def default_setup(ctx, name: str, version: float):
    if ctx.guild is not None:
        await ctx.send(query.set_default_setup(name, version))
    else:
        await ctx.send(query.create_multiline_block("[ERROR] Command must be run within a server"))


# Command for getting role info
@mafia_bot.command()
async def role(ctx, name: str, setup_name: str = "default", setup_version: float = -1.0):
    await ctx.send(query.query_role(" ".join([s[0].upper() + s[1:].lower() for s in name.split(" ")]), setup_name, setup_version))


# Command for getting role clarifications
@mafia_bot.command()
async def clarification(ctx, name: str, setup_name: str = "default", setup_version: float = -1.0):
    await ctx.send(query.query_clarification())


mafia_bot.run(TOKEN)
