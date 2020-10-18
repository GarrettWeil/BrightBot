import discord
from discord.ext.commands import Bot
from discord.ext import commands
import asyncio
import json
import boilerkey
import requests
import os
from lxml import etree

intents = discord.Intents.default()
intents.members = True

PURDUE_LOGIN_URL = "https://www.purdue.edu/apps/account/cas/login"
BS_SAML_AUTH = "https://purdue.brightspace.com/d2l/lp/auth/saml/initiate-login?entityId=https://idp.purdue.edu/idp/shibboleth"
BS_BASE = "https://purdue.brightspace.com"

quizList = []
classID = ""

client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print("Ready!")


@client.event
async def on_member_join(member):

    CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + member.display_name + "_config.json"
    COUNTER_PATH = os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + member.display_name + "_counter.json"

    if not os.path.isfile(CONFIG_PATH) or not os.path.isfile(COUNTER_PATH):
        await member.create_dm()
        await member.dm_channel.send("""
        Welcome """ + member.display_name + """! Please complete this brief
        process to authorize BrightBot to access your information
        """)

        await boilerkey.askForInfo(client, member)


def getSession(member):

    username = boilerkey.getConfig(member)
    username = username["username"]
    password = boilerkey.generatePassword(member)
    session = create_purdue_cas_session(username, password)
    brightspace_auth(session)
    return session


def create_purdue_cas_session(username: str, password: str) -> requests.Session:
    session = requests.Session()

    res = session.get(PURDUE_LOGIN_URL)
    res.raise_for_status()

    tree = etree.HTML(res.text)
    lt = tree.xpath('//*[@name="lt"]/@value')[0]

    res = session.post(
        PURDUE_LOGIN_URL,
        data={
            "username": username,
            "password": password,
            "lt": lt,
            "execution": "e1s1",
            "_eventId": "submit",
            "submit": "Login",
        },
    )
    res.raise_for_status()
    assert res.status_code == 200

    return session


def brightspace_auth(session: requests.Session) -> None:
    res = session.get(BS_SAML_AUTH)
    res.raise_for_status()

    tree = etree.HTML(res.text)
    res = session.post(
        tree.xpath("//form/@action")[0],
        data={"SAMLResponse": tree.xpath('//input[@name="SAMLResponse"]/@value')[0]},
    )


def create_bs_session(username: str, password: str) -> requests.Session:
    session = create_purdue_cas_session(username, password)
    brightspace_auth(session)
    return session


@client.command()
async def helloworld(ctx):
    print("This works!")
    await ctx.send("This works!")


@client.command()
async def setclassID(ctx,*,inputID):
    global classID
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
        print("test2")
        print(ctx.author)
        memberName = str(ctx.author)[:len(str(ctx.author))-5]
        print ('starting session')
        s =  getSession(ctx)
        print ('created session object')
        response = s.get('https://purdue.brightspace.com/d2l/api/le/1.0/' + classID + '/content/toc')
        print ('session started')
        if response.status_code == '404':
            await ctx.send('Error 404: Could not find the class, please check your class ID!')
        elif response.status_code == '403':
            await ctx.send('Error 403: Invalid permissions! Make sure you logged in!')
        else:
            await ctx.send('Formatting remaining quizzes...')
            if response.text == "":
               await ctx.send('No quizzes!')
            else:
                print("We're here now")
                data = response.json()

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
