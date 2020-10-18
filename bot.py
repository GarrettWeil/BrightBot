import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import json

global classID
classID = ""

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

@client.command()
async def quizzes (ctx): #unimplemented sections stay out until the user authentication process is completed. For now, uses a temp JSON file
    if classID == "":
        await ctx.send('Initialize the class ID first!')
    else:  
        # response = requests.get('https://purdue.brightspace.com/d2l/api/le/1.0/' + classID + '/content/toc')
        # if response.status_code != '200':
        #     await ctx.send('Error ' + response.status_code + ': Could not find the class, please check your class ID!')
        # else:
        await ctx.send('Formatting remaining quizzes...')
        #    if response.string == "":
        #        await ctx.send('No quizzes!')
        #    else:
        with open('quizzes.json') as data_file: # add two indents
            data = json.load(data_file)
        fullResponse = ""
        for quiz in data["Objects"]:
            tLoc = quiz["DueDate"].index('T') # used to identify position of 'T' to split up the date and time in the DueDate returned value
            dueDate = quiz["DueDate"][:tLoc] + ' ' + quiz["DueDate"][tLoc + 1:tLoc + 9] + ' UTC' # 8 more as time format is XX:XX:XX
            responseString = quiz["Name"] + ': ' + quiz["Description"]["Text"]["Text"] + 'Due: ' + dueDate
            fullResponse = fullResponse + responseString + '\n\n'
        await ctx.send(fullResponse)
    
f = open("token.txt", mode='r')
f = f.readlines()[0]
#add your bot's token to the file called token.txt before running 

client.run(f)
