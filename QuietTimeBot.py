import discord

client = discord.Client()

quiettime = True
qt_messages = 0
summoned = False

authID = "ABCDEFGH..."

# Once successfully logged in
@client.event
async def on_ready():
    print("Logged on as: "+str(client.user))

# Upon receiving a message
@client.event
async def on_message(message):
    global summoned

    if quiettime:
         await message.add_reaction(u"\U0001F693")
         await message.add_reaction(u"\U0001F694")
    
    # Don't respond to ourselves
    if message.author == client.user:
        return 0

    if message.content[::-1][0] == "?" and summoned == True:
        msg = "No."
        await message.channel.send(msg)

    if client.user.mentioned_in(message):
        msg = "I was summoned."
        await message.channel.send(msg)
        summoned = True

client.run(authID)
