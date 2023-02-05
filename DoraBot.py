import os
import sys
import discord
from discord.ext import commands
import random
from discord import FFmpegPCMAudio
import math
import youtube_dl
import asyncio
from keep_alive import keep_alive 
from recommender.api import Recommender # A Python client for the Spotify Recommendations

intents = discord.Intents.default()
intents.members = True

global loop
loop = False

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

queues = {}

def check_queue(ctx, id):
  if queues [id] != []:
    voice = ctx.guild.voice_client
    source = queues[id].pop(0)
    player = voice.play(source)
client = commands.Bot(command_prefix = 'ig.', Intents=intents)

loop = False

snipe_message_author = {}
snipe_message_content = {}

@client.event
async def on_message_delete(message):
     snipe_message_author[message.channel.id] = message.author
     snipe_message_content[message.channel.id] = message.content
     await asyncio.sleep(60)
     del snipe_message_author[message.channel.id]
     del snipe_message_content[message.channel.id]

@client.event
async def on_ready():
  await client.change_presence(status=discord.Status.online, activity=discord.Game('ig.help'))
  print('Bot is ready to roll.')

@client.command(name='ping', help='check bot latency')
async def ping(ctx):
  embed = discord.Embed(color=0xfd6a02)
  embed.add_field(name="Bot latency",
                    value=f'🏓 Pong! {round(client.latency * 1000)}ms',
                    inline=True)
  await ctx.send(embed=embed)

@client.command(name = 'snipe', help='Snipes a recently deleted message.')
@commands.has_permissions(manage_messages=True)
async def snipe(ctx):
   channel = ctx.channel
   try:
      em = discord.Embed(name = f"Last deleted message in #{channel.name}", description = snipe_message_content[channel.id], color=0xfd6a02)
      em.set_footer(text = f"This message was sent by {snipe_message_author[channel.id]}")
      await ctx.send(embed = em)
    
   except:
      await ctx.send(f"There are no recently deleted messages in #{channel.name}")

@client.command(aliases=['die'], help='It kills the bot.(Not literally.)')
async def kill(ctx):
  responses_1 = ["Noo you killed me.",
  "Why, what did I do wrong to deserve this.",
  "*Dies silently.*",
  "Haha killing me is not that easy",
  "One Piece is real \n *dies*",
  "My time has come but it was good time in this bot world." ]
  await ctx.send(f'{random.choice(responses_1)}')

@client.command(aliases=['question', 'ask'], help = 'Ask a question to the bot.')
async def questions(ctx, *, question):
  responses = ["It is certain.",

"It is decidedly so.",

"Without a doubt.",

"Yes - definitely.",

"You may rely on it.",

"As I see it, yes.",

"Most likely.",

"Outlook good.",

"Yes.",

"Signs point to yes.",

"Reply hazy, try again.",

"Ask again later.",

"Better not tell you now.",

"Cannot predict now.",

"Concentrate and ask again.",

"Don't count on it.",

"My reply is no.",

"My sources say no.",

"Outlook not so good.",

"Very doubtful."]
  embed = discord.Embed(title=question, description=random.choice(responses), color=0xfd6a02)
  await ctx.send(embed=embed)

@client.command(help='Clear a certain amount of messages.')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
  await ctx.channel.purge(limit=amount) 

@client.command(help='Kicks a member from the server.')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member : discord.Member, *, reason=None):
  await member.kick(reason=reason)
  await ctx.send(f'Kicked {member.mention}')

@client.command(help='Bans a member from the server.')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member : discord.Member, *, reason=None):
  await member.ban(reason=reason)
  await ctx.send(f'Banned {member.mention}')

@client.command(help='Unban a banned member.')
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user
    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'Unbanned {user.mention}')
      return

@client.command(name='credits', help='This command specifies the creator of this bot.')
async def credits(ctx):
   embed = discord.Embed(color=0xfd6a02)
   embed.add_field(name="The creator of this bot is",value=f"**FarhanHaqLabib#5157**",inline=True)
   await ctx.send(embed=embed)
  
  
 
@client.command(name='join', help='This command makes the bot joins a VC.')
async def join(ctx):
  if (ctx.author.voice):
    channel = ctx.message.author.voice.channel
    voice = await channel.connect()
    source = FFmpegPCMAudio('rickroll.mp3')
    player = voice.play(source)
    await ctx.message.add_reaction('✅')
  else:
    await ctx.send("You must be joined in a voice channel to execute this command")      

  

@client.command(name='pause', help='This command pauses an ongoing song.')
async def pause(ctx):
  voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
    await ctx.send("**Paused!**")
  else:
    await ctx.send("There is no audio playing in the voice channel")  



@client.command(name='resume', help='This command resumes a paused song.')
async def resume(ctx):
  voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
  if voice.is_paused():
    voice.resume()
    await ctx.send("**Resumed!**")
  else:
    await ctx.send("There is no audio paused in the voice channel")  


          

@client.command(name='leave', help='This command stops an ongoing song and the bot leaves the vc.')
async def leave(ctx):
  if (ctx.voice_client):
    await ctx.guild.voice_client.disconnect()
    await ctx.send("Successfully disconnected")
  else:
    await ctx.send("I am not in a voice channel")  
 

  
@client.command(name='stop', help='This command stops an ongoing song.')
async def stop(ctx):
  voice = discord.utils.get(client.voice_clients,guild=ctx.guild)
  voice.stop()
  await ctx.send("**Stopped!**") 


@client.command(name='restart', help='restarts the bot')
@commands.is_owner()
async def restart(ctx):
  await ctx.send('**Restarting, Please wait.**')
  os.execv(sys.executable, ['python'] + sys.argv)



def rando(x: int, y: int):
  return random.randint(x, y)

def sqrt(x: float):
  return math.sqrt(x)




@client.command(help = 'generates a random number between 2 given numbers')
async def mathrandom(ctx, x: int, y: int):
  res = rando(x,y)
  await ctx.send(res)

@client.command(help = 'shows the squareroot of a number')
async def mathsqrt(ctx, x: int):
  res = sqrt(x)
  await ctx.send(res)

@client.command(name="whois",help = 'Shows the profile of a user')
async def whois(ctx,user:discord.Member=None):

    if user==None:
        user=ctx.author

    rlist = []
    for role in user.roles:
      if role.name != "@everyone":
        rlist.append(role.mention)

    b = ", ".join(rlist)


    embed = discord.Embed(colour=0xfd6a02,timestamp=ctx.message.created_at)

    embed.set_author(name=f"User Info - {user}"),
    embed.set_thumbnail(url=user.avatar_url),
    embed.set_footer(text=f'Requested by - {ctx.author}',
  icon_url=ctx.author.avatar_url)

    embed.add_field(name='ID:',value=user.id,inline=False)
    embed.add_field(name='Name:',value=user.display_name,inline=False)

    embed.add_field(name='Created at:',value=user.created_at,inline=False)
    embed.add_field(name='Joined at:',value=user.joined_at,inline=False)

  
 
    embed.add_field(name='Bot:',value=user.bot,inline=False)

    embed.add_field(name=f'Roles:({len(rlist)})',value=''.join([b]),inline=False)
    embed.add_field(name='Top Role:',value=user.top_role.mention,inline=False)

    await ctx.send(embed=embed)
  


@client.command(name="avatar",help = 'Shows the avatar of the mentioned user')

async def avatar(ctx, *,  user : discord.Member=None):
  if user == None:
    user = ctx.author

    

  embed = discord.Embed( color = 0xfd6a02)

  embed.set_author(name = f"{user.name}'s Avatar")

  embed.set_image(url = user.avatar_url)

  embed.set_footer(text = f"Requested By : {ctx.author.name}")

  await ctx.send(embed=embed)


@client.command(name="serverinfo",help = 'Shows the guild info')
async def serverinfo(ctx):
    embed=discord.Embed(title="Server Information",color=0xfd6a02)
    embed.add_field(name="Server Name", value=(ctx.message.guild.name), inline=True)
    embed.add_field(name="Roles:", value=len(ctx.message.guild.roles), inline=True)
    embed.add_field(name="Members", value=(ctx.message.guild.member_count))
    embed.add_field(name="Channels", value=len(ctx.message.guild.channels))
    embed.add_field(name="Region", value=(ctx.message.guild.region))
    embed.add_field(name="ID", value=(ctx.message.guild.id))
    embed.add_field(name="Creation Date", value=(ctx.message.guild.created_at.strftime("%b %d, %Y")))
    embed.set_footer(text =  f"Requested By : {ctx.author.name}")
    await ctx.send(embed=embed)

myid = 718046660139286559

@client.command()
async def invite(ctx):
  if ctx.author.id != myid:
    await ctx.send("Command not currently available for public use, wait for the author to make it public. Sorry for the meantime.")

  else:
    await ctx.send("https://discord.com/api/oauth2/authorize?client_id=833547501595262996&permissions=8&scope=bot")

    
@client.command(name="calculate", help ="calculates mathematical problems")
async def calculate(ctx, operation, *nums):

  if operation not in ['+', '-', '*', '/']:
      await ctx.send('Please type a valid operation type.')
  var = f' {operation} '.join(nums)
  await ctx.send(f'{var} = {eval(var)}')

keep_alive()
client.run(os.getenv('TOKEN'))

