import importlib

import discord
# import TownOfSalem
from auth import get_authID
authID = get_authID()

import asyncio
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import random
import pickle
import datetime

client = discord.Client()

quiettime = False
qt_messages = 0
summoned = False

async def ship(message):
    try:
        names = { 1: "name1",
                  2: "name2",
                  3: "name3" }

        shipper = names[message.author.id]

        words = message.content.lower().replace("?","").replace(u"\U0001F686","x").replace(u"\U0001F6F3","x").replace(u"\U0001F6A2","x").replace("ú","u").replace("Jennifer","Jenny").replace("!","").replace(".","").split()
        i = words.index("x")
        ship = sorted([words[i-1], words[i+1]])

        names = ["name1", "name2", "name3"]

        x = names.index(ship[0])
        y = names.index(ship[1])

        if x == y:
            return 1

        print(shipper+" ships "+words[i-1]+" x "+words[i+1]+"!")

        # Write to the Google Sheets spreadsheet
        cells = "Ships!" + chr(x+66) + str(y+2)

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SPREADSHEET_ID = "1J9Xg3ExmycwnbMCrYwoqs-WeDeLED6yyphq3B4hc6Ms"

        creds = None

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        value = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=cells).execute()

        # This line messed me up big time
        content = value.get('values', [])

        try:
            if shipper not in content[0][0]:
                content = content[0][0] + ", " + shipper

            else:
                content = content[0][0]
        except:
            content = shipper

        to_add = {'range': cells, 'majorDimension': 'ROWS', 'values': [[content]]}

        sheet.values().update(valueInputOption='USER_ENTERED', body=to_add, spreadsheetId=SPREADSHEET_ID, range=cells).execute()

    except Exception as e:
        print(e)

async def predict(message):

    with open('predictions.p', 'rb') as handle:
        predictions = pickle.load(handle)

    words = message.content.lower().replace("?","").replace("\U0001F686","x").replace("\U0001F6F3","x").replace("\U0001F6A2","x").replace("ú","u").replace("!","").replace(".","").split()
    i = words.index("x")
    ship = sorted([words[i-1], words[i+1]])

    names = ["name1", "name2", "name3"] # Replace these with people's names

    x = names.index(ship[0])
    y = names.index(ship[1])

    if x == y:
        return 1

    if (x,y) in predictions[message.author.id]:
        await message.author.send("You've already shipped them before!")
        return 1

    print("An intimacy has been predicted between "+words[i-1]+" x "+words[i+1]+"!")

    # Write to the Google Sheets spreadsheet
    cells = "Predictions!" + chr(x+66) + str(y+2)

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    SPREADSHEET_ID = "..."

    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    value = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=cells).execute()

    # This line messed me up big time
    content = value.get('values', [])

    content = str(int(content[0][0])+1)

    await message.author.send("Great, thanks!")
    predictions[message.author.id].append((x,y))
    pickle.dump(predictions, open("predictions.p", "wb"))

    to_add = {'range': cells, 'majorDimension': 'ROWS', 'values': [[content]]}

    sheet.values().update(valueInputOption='USER_ENTERED', body=to_add, spreadsheetId=SPREADSHEET_ID, range=cells).execute()

async def QuietTime(message, messages):
    global qt_messages
    qt_messages = messages
    if qt_messages == 0:
        await message.channel.send("Quiet time!")

    qt_messages += 1

    await message.add_reaction(u"\U0001F693")
    await message.add_reaction(u"\U0001F694")

async def Summon(message):
    global summoned
    msg = "I was summoned."
    await message.channel.send(msg)
    summoned = True
    await asyncio.sleep(10)

    if summoned:
        await message.channel.send("Who summoned me?")
        await asyncio.sleep(10)
        if summoned:
            summoned = False
            await message.channel.send("I've un-summoned myself.")

# Once successfully logged in
@client.event
async def on_ready():
    print("Logged in as: "+str(client.user))
#    await remind(client)

# Upon receiving a message
@client.event
async def on_message(message):
    global summoned, quiettime, qt_messages

    # Don't respond to ourselves
    if message.author == client.user:
        return 0

    if client.user.mentioned_in(message) or "quiet time bot" in message.content.lower():
        hearts = ["<3", u"\u2764", u"\u2665", "\U0001F499", "\U0001F49A", "\U0001F49B", "\U0001F49C", "aw", "owo", "uwu", "heart"]

        for emoji in hearts:
            if emoji in message.content.lower():
                await message.add_reaction(u"\u2764")
                return 0

    if message.content[::-1][0] == "?" and summoned == True:
        msg = "No."
        summoned = False
        await message.channel.send(msg)

    if client.user.mentioned_in(message):
        if "off" in message.content.lower():
            print("Quiet time turned off!")
            quiettime = False
            qt_messages = 0

        elif "on" in message.content.lower():
            if "everyone" in message.content.lower():
                return 0
            
            print("Quiet time turned on!")
            quiettime = True

        else:
            await Summon(message)

    if quiettime:
        await QuietTime(message, qt_messages)

    # Ship two people together if an x is used
    if " x " in message.content.lower() or "\U0001F686" in message.content or "\U0001F6F3" in message.content or "\U0001F6A2" in message.content:
        if message.content.lower()[0] == "!":
            await predict(message)

        else:
            await ship(message)

client.run(authID)
