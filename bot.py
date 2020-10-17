import discord
from discord.ext import commands

client = commands.Bot(command_prefix="!")

@client.event
async def on_ready():
    print("Ready!")
    
client.run("RcJg1EuXvsp51ClRSttYLpGqx_Isoxms")
