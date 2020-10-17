import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print("Ready!")

@client.command()
async def helloworld(ctx):
    await ctx.send("This works!")
    
client.run("NzY3MTA2NTM5NDIwMjU0MjYw.X4tFow.DWlZ8pmQG_E5J6G2YenVLiFBoCc")
