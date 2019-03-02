#
import discord
import os
import asyncio
import traceback

from keep_alive import keep_alive
import asyncer

client = discord.Client()
devids = [
  '487258918465306634',#My account
  '448207898884177924',#Badvillian's account
  '449654439490355231',#Eaz's account
  '527937324865290260',#My alt account
]
item = {}
db = {}
db2 = {}
storagechannel = None
logchannel = None

async def load_db():
  global db,db2
  data = {}
  async for m in client.logs_from(storagechannel,limit = float('inf')):
    tx = m.content
    if tx.startswith('`') and ':' in tx:
      i = tx.index(':')
      id = int(tx[1:i])
      co = tx[i+1:-1]
      data[id] = co
    elif tx=='`DB BOUND`' and data:
      break
  if data=={}:
    db = {}
    return
  if max(data.keys())+1 != len(data):
    await reply('db has missing chunks',channel = logchannel)
    return
  tex = ''
  for x in range(len(data)):
    tex += data[x]
  db = eval(tex)
  db2 = eval(tex)#keep an original copy
async def save_db():
  await client.send_message(storagechannel,'`DB BOUND`')
  global db,db2
  data = repr(db)
  try:
    assert eval(data)==db#sanity check
  except SytaxError:
    await client.send_message(logchannel,'db-save err: db repr syntaxerror')
  except AssertionError:
    await client.send_message(logchannel,'db-save err: db repr doesn\'t eval to db')
  db2 = eval(data)
  i = 0
  cl = 1997
  chunkid = 0
  while i<len(data):
    try:
      chunk = data[i:i+cl]
      await client.send_message(storagechannel,'`%s:%s`'%(chunkid,chunk))
    except discord.errors.HTTPException:
        
      cl -= 1
    else:
      i += 2000
      cl = 1997
      chunkid += 1
async def clear_old_dbs():
  reached_olds = False
  async for msg in client.logs_from(storagechannel,limit = float('inf')):
    if not reached_olds:
      if msg.content=="`DB BOUND`":
        reached_olds = True
    else:
      await client.delete_message(msg)

@client.event
async def on_ready():
  global storagechannel,logchannel
  print('im in!')
  print('name: %s'%client.user.name)
  print('id: %s'%client.user.id)
  storagechannel = client.get_channel('541801748545798148')
  logchannel = client.get_channel('541801776836247562')
  await load_db()

msgs = 0

@client.event
async def on_message(message):
  global msgs
  if message.author !=  client.user:

    content = message.content
    splitContent = content.split(" ")
    channel = message.channel
    server = message.server
    if content=='spam':
        await client.send_message(channel, "Spam")
    elif content.lower().startswith('faq!'):#main command prefix
      cmd = content[4:]
      ##PUT MAIN COMMANDS HERE##
      if cmd=='':
        await client.send_message(channel,'**Help**\n Currently, there is no help to be displayed. I appologise for the inconvience.')
      elif cmd.startswith('add '):
          args = cmd[4:].split('|')
          #
          assert len(args)==3#this should eventually complain to the user 
          itemName = args[0]
          item[itemName] = {'desc':args[1],'link':args[2]}#but wait serverName is the first one.


          if server.id not in db:
              db[server] = item
          server = server.id
          db[server] = item 
          print(server)
          #db[server.id] = {serverId:itemName}
          #db=={server:{itemname:{itemdesc,itemlink}}}
          await client.send_message(channel, db)
    elif content.lower().startswith('db!') and message.author.id in devids:
      #these commands only work for devs
      cmd = content[3:]
      if cmd.startswith('eval '):
        val = eval(cmd[5:])
        await client.send_message(channel,"`%s`"%val)
      elif cmd=='killall':
        exit()
      #
      elif cmd=='reload':
        await load_db()
      elif cmd=='query':
        await client.send_message(channel,'`%r`'%db)
      elif cmd=='write':
        await save_db()
      elif cmd=='clear':
        await clear_old_dbs()
      elif cmd.startswith('store:'):
        m = cmd[6:]
        db[m] = 0
        await save_db()
      elif cmd.startswith('show '):
        try:
          await client.send_message(channel, db[cmd[5:]])
        except:
          await client.send_message(channel, db[str(cmd[5:])]
     #if message.author.id not in devids:
        #await client.send_message(channel, "You do not have the sufficent permissions")
  msgs+=1
  if msgs !=  1:
    print("%s Messages have been sent"%msgs)
  else:
    print("1 message has been sent")
  #important stuff here, obviously
  #NO At the begining lol
  #nope right here
  #lol I thought you said "import stuff here, obviously" derp

@client.event
async def on_error(event,message=None):
    print('err in %s'%event)
    traceback.print_exc()

token = os.getenv('DISCORD_BOT_SECRET')
if not token:
  print('no .env token!')
  input('press enter for non-bot tests')
  asyncer.start_waiter(asyncer._main)
else:
  keep_alive()
  #asyncio.ensure_future(asyncer.corowaiter())
  client.run(token)
