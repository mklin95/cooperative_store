# 合作社
import discord, asyncio, os
from discord.ext import commands, tasks
import keep_alive
import sqlite3
import datetime

itemname = ["O", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "Q", "L"]
itemcost = [0, 10, 10, 12, 15, 16, 18, 23, 23, 25, 32, 35, 25]
itemtype = ["其他東西", "狗骨頭", "脆麵", "巧菲斯", "點心麵(小)", "衛生紙", "洋芋片", "維力", 
            "張君雅(大包)", "張君雅(炸雞)", "小泡芙", "阿Q", "來一客"]

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='.', intents=intents)


@client.event
async def on_ready():
  change_status.start()
  print(f"目前登入身份 --> {client.user}")


@client.event
async def on_message(message):
  s = message.content
  s = s.upper()
  pid = message.author.id
  tz = datetime.timezone(datetime.timedelta(hours=8))
  now = str(datetime.datetime.now(tz))
  now = now.replace("+08:00", "")
  conn = sqlite3.connect("test.db")
  c = conn.cursor()
  x = s.split()
  tv = 0

  if s == "Q":
    await message.channel.send("座號/餘額/消費額")
    c.execute("SELECT seatnum, money, cons FROM member order by SeatNum")
    result = c.fetchall()
    tv = 1
    for i in result:
      await message.channel.send(str(i[0]) + " / " + str(i[1]) + " / " + str(i[2]))

  if pid == my_discord_id and (x[0] == 'A' or x[0] == 'S' or x[0] == 'C'):  #me
    person = int(x[1])
    do = "SELECT seatnum, money, cons, id FROM member where seatnum = " + str(person)
    c.execute(do)
    result = c.fetchall()
    money = result[0][1]
    cons = result[0][2]
    id = result[0][3]
    exetrade = ""

    if x[0] == 'A' or x[0] == 'S':
      count = abs(int(x[2]))

      if x[0] == 'A':
        money = money - count
        tv = 1
        exetrade = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(-count) + ", \"提款\"" + ", " + str(person) + ");"

      elif x[0] == 'S':
        money = money + count
        tv = 1
        exetrade = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(count) + ", \"存錢\"" + ", " + str(person) + ");"

    elif x[0] == 'C':
      itempos = -1
      count = 0
      if x[2].isdigit() == 0:
        for i in range(len(itemname)):
          if str(x[2]) == str(itemname[i]):
            itempos = i
            break
        count = int(itemcost[itempos])
        if itempos != -1:
          money -= count
          cons += count
          tv = 1
        elif itempos == -1:
          await message.channel.send("啊你是要買甚麼啊")

      elif x[2].isdigit():
        count = int(x[2])
        money -= count
        cons += count
        itempos = 0
        tv = 1

      if tv == 1:
        exetrade = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(-count) + ", " + "\"買" + str(itemtype[itempos]) + "\", " + str(person) + ");"

    c.execute(exetrade)
    exemoney = "UPDATE member SET money = " + str(money) + ", cons = " + str(cons) + " WHERE seatnum = " + str(person)
    c.execute(exemoney)

    await message.channel.send("座號/餘額/消費額")
    await message.channel.send(
        str(person) + " / " + str(money) + " / " + str(cons))
    if money < 0:
      await message.channel.send("<@" + str(id) + ">" + "乙己你還欠我" + str(abs(money)) + "個錢哩")

  elif pid == my_discord_id and x[0] == 'T':
    xt = s.split()
    person1 = int(xt[1])
    person2 = int(xt[3])
    count = abs(int(xt[4]))

    do1 = "SELECT seatnum, money, cons, id FROM member where seatnum = " + str(person1)
    c.execute(do1)
    result1 = c.fetchall()
    money1 = result1[0][1]
    cons1 = result1[0][2]
    id1 = result1[0][3]
    money1 -= count

    do2 = "SELECT seatnum, money, cons, id FROM member where seatnum = " + str(person2)
    c.execute(do2)
    result2 = c.fetchall()
    money2 = result2[0][1]
    cons2 = result2[0][2]
    id2 = result2[0][3]
    money2 += count

    exetrade1 = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(-count) + ", \"轉帳(to " + str(person2) + ")\", " + str(person1) + ");"
    c.execute(exetrade1)
    exetrade2 = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(count) + ", \"轉帳(from " + str(person1) + ")\", " + str(person2) + ");"
    c.execute(exetrade2)
    tv = 1

    after1 = "UPDATE member SET money = " + str(money1) + " WHERE seatnum = " + str(person1)
    after2 = "UPDATE member SET money = " + str(money2) + " WHERE seatnum = " + str(person2)
    c.execute(after1)
    c.execute(after2)

    await message.channel.send("座號/餘額/消費額")
    await message.channel.send(
        str(person1) + " / " + str(money1) + " / " + str(cons1))
    await message.channel.send(
        str(person2) + " / " + str(money2) + " / " + str(cons2))
    if money1 < 0:
      await message.channel.send("<@" + str(id1) + ">" + "乙己你還欠我" + str(abs(money1)) + "個錢哩")
    if money2 < 0:
      await message.channel.send("<@" + str(id2) + ">" + "乙己你還欠我" + str(abs(money2)) + "個錢哩")

  elif pid == my_discord_id and x[0] == "ALL":
    exesearch = "SELECT TID, trader, time, amount, type FROM trade where trader = " + str(x[1])
    c.execute(exesearch)
    sresult = c.fetchall()
    tv = 1
    await message.channel.send("ID/座號/時間/金額/消費類型")
    for i in sresult:
      await message.channel.send(i)

  elif pid != my_discord_id and pid != 1118896563322896476:  #others
    findnum = "SELECT seatnum, money, cons FROM member where id = \"" + str(pid) + "\""
    c.execute(findnum)
    result1 = c.fetchall()
    person1 = result1[0][0]
    money1 = result1[0][1]
    cons1 = result1[0][2]

    if x[0] == 'S':
      await message.channel.send("這裡充滿了發財的空氣\n||還想幫自己存錢啊爛貨||")
      tv = 1

    elif x[0] == 'C':
      itempos = -1
      count = 0
      if x[1].isdigit() == 0:
        for i in range(len(itemname)):
          if str(x[1]) == str(itemname[i]):
            itempos = i
            break

        count = int(itemcost[itempos])
        if itempos != -1:
          money1 -= count
          cons1 += count
          tv = 1
        elif itempos == -1:
          await message.channel.send("啊你是要買甚麼啊")

      elif x[1].isdigit():
        count = int(x[1])
        money1 -= count
        cons1 += count
        itempos = 0
        tv = 1

      if tv == 1:
        exetrade = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(-count) + ", " + "\"買" + str(itemtype[itempos]) + "\", " + str(person1) + ");"
        c.execute(exetrade)

      exemoney = "UPDATE member SET money = " + str(money1) + ", cons = " + str(cons1) + " WHERE seatnum = " + str(person1)
      c.execute(exemoney)

      await message.channel.send("座號/餘額/消費額")
      await message.channel.send(str(person1) + " / " + str(money1) + " / " + str(cons1))
      if money1 < 0:
        await message.channel.send("<@" + str(pid) + ">" + "乙己你還欠我" + str(abs(money1)) + "個錢哩")

    elif x[0] == 'T':

      person2 = int(x[1])
      count = abs(int(x[2]))
      money1 -= count

      do2 = "SELECT seatnum, money, cons, id FROM member where seatnum = " + str(person2)
      c.execute(do2)
      result2 = c.fetchall()
      money2 = result2[0][1]
      cons2 = result2[0][2]
      id2 = result2[0][3]
      money2 += count

      exetrade1 = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(-count) + ", \"轉帳(to " + str(person2) + ")\", " + str(person1) + ");"
      c.execute(exetrade1)
      exetrade2 = "insert into trade(time, amount, type, trader) values ('" + str(now) + "', " + str(count) + ", \"轉帳(from " + str(person1) + ")\", " + str(person2) + ");"
      c.execute(exetrade2)
      tv = 1

      after1 = "UPDATE member SET money = " + str(money1) + " WHERE seatnum = " + str(person1)
      after2 = "UPDATE member SET money = " + str(money2) + " WHERE seatnum = " + str(person2)
      c.execute(after1)
      c.execute(after2)

      await message.channel.send("座號/餘額/消費額")
      await message.channel.send(str(person1) + " / " + str(money1) + " / " + str(cons1))
      await message.channel.send(str(person2) + " / " + str(money2) + " / " + str(cons2))
      if money1 < 0:
        await message.channel.send("<@" + str(pid) + ">" + "乙己你還欠我" + str(abs(money1)) + "個錢哩")
      if money2 < 0:
        await message.channel.send("<@" + str(id2) + ">" + "乙己你還欠我" + str(abs(money2)) + "個錢哩")

    elif s == "ALL":
      exesearch = "SELECT time, amount, type FROM trade where trader = " + str(person1)
      c.execute(exesearch)
      sresult = c.fetchall()
      tv = 1
      await message.channel.send("時間/金額/消費類型")
      for i in sresult:
        await message.channel.send(i)

  conn.commit()
  conn.close()

  if s == "?" or s == "？":
    hr = open("help.txt", "r")
    helptxt = (hr.readlines())
    for i in helptxt:
      await message.channel.send(i)


keep_alive.keep_alive()
client.run(os.getenv("key")) # bot token
