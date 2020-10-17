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
async def setclassID(ctx,*,inputID):
    classID = inputID
    await ctx.send('Class ID was set to ' + classID)

@client.command()
async def schedule (ctx):
    if classID == "":
        await ctx.send('Initialize the class ID first!')
    else:  
        response = requests.get('https://purdue.brightspace.com/d2l/api/le/1.0/' + classID + '/content/toc')
        if response.status_code != '200':
            await ctx.send('Could not find the class, please check your class ID!')
        else:
            await ctx.send('Formatting schedule...')
    
f = open("token.txt", mode='r')
f = f.readlines()[0]
#add your bot's token to the file called token.txt before running 

client.run(f)
