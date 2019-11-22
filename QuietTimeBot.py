import importlib

import discord
# import TownOfSalem        # Coming soon!
# import random             # Once TownOfSalem is completed
from auth import get_authID # Get the auth ID
authID = get_authID()

# Some libraries required for OAuth2 with Google Docs
import asyncio
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# TODO: Switch quiet time on once it reaches 4pm
import datetime

client = discord.Client()

quiettime = False                   # Whether it's quiet time
qt_messages = 0                     # TODO: Make Quiet Time Bot respond less subtly the more people talk during quiet time
summoned = False                    # Whether someone's tagged it recently

# Remove all punctuation and capitalisation from a message.
def remove_punctuation(message):
    return message.lower().replace("?","").replace(u"\U0001F686","x").replace(u"\U0001F6F3","x").replace(u"\U0001F6A2","x").replace("!","").replace(".","").split()

async def ship(message):
    try:
        names = { # In the format
                  # Discord ID: first name
                  # Not necessarily in order, but associates Discord IDs to people's names
                  1: 'Alice',
                  2: 'Charles',
                  3: 'Bob',
                  4: 'Daniel',
                  5: 'Ethan',
                  6: 'Felix',
                  7: 'Garrett' }

        # Get the name of the person who shipped the two people together
        shipper = names[message.author.id]

        # Replace all words 
        words = remove_punctuation(message.content)
        i = words.index("x")
        ship = sorted([words[i-1], words[i+1]])

        # List of all first names, in lowercase, in order
        names = ["alice", "bob", "charles", "daniel", "ethan", "felix", "garrett"]

        # Set the indexes of the first and the second person in the list
        person1 = names.index(ship[0])
        person2 = names.index(ship[1])

        # Prevent a person from being shipped with themselves
        if person1 == person2:
            return 0

        print(shipper+" ships "+words[i-1]+" x "+words[i+1]+"!")

        # Write to the Google Sheets spreadsheet
        cells = "Ships!" + chr(person1+66) + str(person2+2)

        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        SPREADSHEET_ID = "(Insert spreadsheet ID here)"

        creds = None

        # The file token.pickle stores the access and refresh tokens, and is created
        # automatically when the authorization flow completes for the first time
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
        
        content = value.get('values', [])

        # Append a list 
        try:
            if shipper not in content[0][0]:
                content = content[0][0] + ", " + shipper

            else:
                content = content[0][0]
        except:
            content = shipper

        to_add = { 'range': cells, 'majorDimension': 'ROWS', 'values': [[content]] }

        sheet.values().update(valueInputOption='USER_ENTERED', body=to_add, spreadsheetId=SPREADSHEET_ID, range=cells).execute()

    except Exception as e:
        print(e)

async def QuietTime(message, messages):
    global qt_messages
    qt_messages = messages

    # Announce that it's quiet time when it starts
    if qt_messages == 0:
        await message.channel.send("Quiet time!")

    # Keep track of the number of 
    qt_messages += 1

    # If it's quiet time, police car react messages that have been sent
    await message.add_reaction(u"\U0001F693")
    await message.add_reaction(u"\U0001F694")

# Summon Quiet Time Bot if @Quiet Time Bot is used
# This may be useful if someone wants to interact with Quiet Time Bot
async def Summon(message):
    global summoned
    msg = "I was summoned."
    await message.channel.send(msg)
    summoned = True
    await asyncio.sleep(10)

    # If nobody asks Quiet Time Bot a question for a while, this
    # should expire after 20 seconds
    if summoned:
        await message.channel.send("Who summoned me?")
        await asyncio.sleep(10)
        if summoned:
            summoned = False
            await message.channel.send("I've un-summoned myself.")

# Events once successfully logged in
@client.event
async def on_ready():
    print("Logged in as: "+str(client.user))

# Events upon receiving a message
@client.event
async def on_message(message):
    global summoned, quiettime, qt_messages

    # Don't respond to ourselves
    if message.author == client.user:
        return 0

    # If Quiet Time Bot is asked a question, it will respond 'no'
    # TODO: Add new features here to make it answer questions more appropriately
    if message.content[::-1][0] == "?" and summoned == True:
        summoned = False
        await message.channel.send("No.")

    # Switch quiet time on or off if mentioned by a user; otherwise react to itself being tagged
    if client.user.mentioned_in(message):
        # Don't react if someone used @everyone or @here
        if "everyone" in message.content.lower() or "here" in message.content.lower():
            return 0

        if "off" in message.content.lower():
            print("Quiet time turned off!")
            quiettime = False
            qt_messages = 0

        elif "on" in message.content.lower():
            print("Quiet time turned on!")
            quiettime = True

        else:
            await Summon(message)

    if quiettime:
        await QuietTime(message, qt_messages)

    # Ship two people together if an x is used in between them,
    # in the style "Alice x Bob". A ship emoji can also be used
    if " x " in message.content.lower() or "\U0001F686" in message.content or "\U0001F6F3" in message.content or "\U0001F6A2" in message.content:
        await ship(message)

client.run(authID)
