import os
import requests

import discord

GUILD = 'Meager Martini\'s Server 1'
global classID
classID = ""

client = discord.Client()

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    
    print(f'{client.user} connected')
    print(f'{guild.name}(id: {guild.id})')
    

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return
    
    if message.content == '!test':
        await message.channel.send('Testing 1...2...3...')
        
    if '!setClassID' in message.content:
        string = message.content
        if len(string) < 12:
            await message.channel.send('Please put the class ID after the command!')
        else:
            classID = string[string.find('!setClassID') + 12:]
            print(classID)
    
    if message.content == '!schedule':
       # response = requests.get("https://purdue.brightspace.com/d2l/api/lp/1.0/organization/info")
       if classID == "":
           await message.channel.send('Initialize the class ID first!')
       else:  
            response = requests.get("https://purdue.brightspace.com/d2l/api/le/1.0/' + classID + '/content/toc")
            if response.status_code != '200':
                await message.channel.send('Could not find the class, please check your class ID!')
            else:
                await message.channel.send('Formatting schedule...')
        
f = open("token.txt", mode='r')
f = f.readlines()[0]       
    
client.run(f)