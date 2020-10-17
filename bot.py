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


@client.command()
async def test(ctx,*,message):
    await ctx.send(message)


f = open("token.txt", mode='r')
f = f.readlines()[0]
#add your bot's token to the file called token.txt before running 

client.run(f)
