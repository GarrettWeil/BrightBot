import base64
import json
import os
import sys

try:
    import requests
    import pyotp
except ImportError:
    print("This script requires pyotp and requests packages")
    print("Please run 'pip3 install pyotp requests'")
    sys.exit(1)

CONFIG_PATH = os.path.dirname(os.path.realpath(__file__)) + "/config.json"
COUNTER_PATH = os.path.dirname(os.path.realpath(__file__)) + "/counter.json"


def getActivationData(code):
    print("Requesting activation data...")

    HEADERS = {"User-Agent": "okhttp/3.11.0"}

    PARAMS = {
        "app_id": "com.duosecurity.duomobile.app.DMApplication",
        "app_version": "2.3.3",
        "app_build_number": "323206",
        "full_disk_encryption": False,
        "manufacturer": "Google",
        "model": "Pixel",
        "platform": "Android",
        "jailbroken": False,
        "version": "6.0",
        "language": "EN",
        "customer_protocol": 1,
    }

    ENDPOINT = "https://api-1b9bef70.duosecurity.com/push/v2/activation/{}"

    res = requests.post(ENDPOINT.format(code), headers=HEADERS, params=PARAMS)

    if res.json().get("code") == 40403:
        print(
            "Invalid activation code."
            "Please request a new link in BoilerKey settings."
        )
        sys.exit(1)

    if not res.json()["response"]:
        print("Unknown error")
        print(res.json())
        sys.exit(1)


    print(res.json()["response"])
    return res.json()["response"]


def validateLink(link):
    try:
        assert "m-1b9bef70.duosecurity.com" in link
        code = link.split("/")[-1]
        assert len(code) == 20
        return True, code
    except Exception:
        return False, None


def createConfig(member, activationData):
    with open(os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + member.display_name + "_config.json", "w") as f:
        json.dump(activationData, f, indent=2)
    print("Activation data saved!")


def getConfig(member):
    name = str(member.author)[:len(str(member.author))-5]
    with open(os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + name + "_config.json") as f:
        return json.load(f)


def setCounter(member, number):
    name = str(member.author)[:len(str(member.author))-5]
    with open(os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + name + "_counter.json", "w") as f:
        json.dump({"counter": number}, f, indent=2)


def getCounter(member):
    name = str(member.author)[:len(str(member.author))-5]
    with open(os.path.dirname(os.path.realpath(__file__)) + "/userConfigs/" + name + "_counter.json") as f:
        return json.load(f)["counter"]


def generatePassword(member):
    config = getConfig(member)
    counter = getCounter(member)

    hotp = pyotp.HOTP(base64.b32encode(config["hotp_secret"].encode()))

    hotpPassword = hotp.at(counter)

    if config.get("pin"):
        password = "{},{}".format(config.get("pin"), hotpPassword)
    else:
        password = hotpPassword

    setCounter(member, counter + 1)

    return password


async def askForInfo(client, member):
    await member.dm_channel.send("""
1. Please go to the BoilerKey settings (https://purdue.edu/boilerkey)
   and click on 'Set up a new Duo Mobile BoilerKey'
2. Follow the process until you see the qr code
3. Paste the link (https://m-1b9bef70.duosecurity.com/activate/XXXXXXXXXXX)
   under the qr code right here and press Enter""")

    await asyncio.sleep(1)

    valid = False
    while not valid:
        linkObj = await client.wait_for("message")
        link = linkObj.content
        valid, activationCode = validateLink(link)

        if not valid:
            await member.dm_channel.send("Invalid link. Please try again")


    await member.dm_channel.send("4. Please enter your boilerkey username")
    usernameObj = await client.wait_for("message")
    username = usernameObj.content
    user = {"username":username}

    await member.dm_channel.send(
        """5. (Optional) In order to generate full password (pin,XXXXXX),
    script needs your pin. You can leave this empty."""
    )

    pinObj = await client.wait_for("message")
    pin = pinObj.content
    if len(pin) != 4:
        pin = ""
        await member.dm_channel.send("Invalid pin")

    activationData = getActivationData(activationCode)
    activationData = json.dumps(activationData)
    activationData["pin"] = pin
    activationData.update(user)
    createConfig(member, activationData)
    setCounter(member, 0)

    await member.dm_channel.send("You're all set!\nThanks for getting set up.")
