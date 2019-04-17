import discord

client = discord.Client()

authID = "ABCDEFGH..."

# Once successfully logged in
@client.event
async def on_ready():
    print("Logged on as: "+str(client.user))

# Upon receiving a message
@client.event
async def on_message(message):
    # Don't respond to ourselves        
    if message.author == client.user:
        return 0

    elif message.content == "ping":
        await message.channel.send("pong")

    if message.content.startswith("!hello"):
        msg = "Hello "+str(message.author.mention)+"!"
        await message.channel.send(msg)

client.run(authID)
