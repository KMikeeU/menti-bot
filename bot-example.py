import menti_bot

mentid = input("Menti ID: ")

menti = menti_bot.Menti(mentid)

am = int(input("Amount of Bots (1 Thread per bot): "))

bots = [menti_bot.MentiClient(menti) for i in range(am)]

bot = menti_bot.MentiBot(menti, bots)
bot.identify()
bot.loop()