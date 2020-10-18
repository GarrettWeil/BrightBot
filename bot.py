import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import json
import boilerkey

intents = discord.Intents.default()
intents.members = True


global classID
classID = ""

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print("Ready!")

@client.event
async def on_member_join(member):
    print("New Member " + member.mention)
    await member.create_dm()
    await member.dm_channel.send("Test!")

@client.command()
async def helloworld(ctx):
    await ctx.send("This works!")
    #await boilerkey.main()

@client.command()
async def setclassID(ctx,*,inputID):
    classID = inputID
    await ctx.send('Class ID was set to ' + classID)

@client.command()
async def classID(ctx):
    await ctx.send('Current class ID is ' + classID)
    
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Make sure that you fill all required inputs!")
    
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
        global quizList
        # response = requests.get('https://purdue.brightspace.com/d2l/api/le/1.0/' + classID + '/content/toc')
        # if response.status_code == '404':
        #     await ctx.send('Error 404: Could not find the class, please check your class ID!')
        # elif response.status_code == '403':
        #     await ctx.send('Error 403: Invalid permissions! Make sure you logged in!')
        # else:
        await ctx.send('Formatting remaining quizzes...')
        #    if response.string == "":
        #        await ctx.send('No quizzes!')
        #    else:
        with open('quizzes2.json') as data_file:
            data = json.load(data_file)

        fullResponse = ""

        for quiz in data["Objects"]:
            tLoc = quiz["DueDate"].index('T') # used to identify position of 'T' to split up the date and time in the DueDate returned value
            dueDate = quiz["DueDate"][:tLoc] + ' ' + quiz["DueDate"][tLoc + 1:tLoc + 9] + ' UTC' # 8 more as time format is XX:XX:XX
            print(dueDate)
            quizList.append([quiz["Name"], quiz["Description"]["Text"]["Text"], dueDate, False])
        # y1, m1, d1 = [int(i) for i in datetime.utcnow().strftime('%Y-%m-%d').split("-")]
        todayDate = datetime.utcnow()
        tempQuizList = []
        for quiz in quizList: # cleaning out quizzes that are already done
            y2, m2, d2 = [int(i) for i in quiz[2][:quiz[2].index(' ')].split("-")]
            hour2, min2, sec2 = [int(i) for i in quiz[2][quiz[2].index(' ') + 1:quiz[2].index(' ') + 9].split(":")]
            quizDate = datetime(y2,m2,d2,hour2,min2,sec2)
            if (quizDate < todayDate):
                print (quiz[0])
                continue
            else:
                tempQuizList.append(quiz)
                timeUntilDeadline = quizDate - todayDate
                if ((timeUntilDeadline / timedelta(days=1)) <= 7):
                    quiz[3] = True #mark priority
            fullResponse = fullResponse + quiz[0] + ': ' + quiz[1] + '\n' + quiz[2] + ' UTC.\nWithin 7 days: ' + str(quiz[3]) + "\n\n"
        quizList = tempQuizList        
        if(fullResponse == ""):
            fullResponse = 'No quizzes!'
        await ctx.send(fullResponse)

f = open("token.txt", mode='r')
f = f.readlines()[0]
#add your bot's token to the file called token.txt before running

client.run(f)
