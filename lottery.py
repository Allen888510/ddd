import discord 
from discord.ext import commands
import json
import datetime
import requests
import random
from discord import Client

 
no_one_win = 0.3
with open('setting.json', 'r', encoding='utf8') as jfile:
    filedata = json.load(jfile)

def update_data(jdata):
    update = requests.put(filedata['json_url'],
        json = jdata
    )
    response = requests.get(filedata['json_url'])
    jdata = response.json()


bot = commands.Bot(command_prefix='>')
@bot.event
async def on_ready():
    print('bot is online')

@bot.command()
async def ping(ctx):
    await ctx.send(F'{bot.latency*1000} (ms)')



@bot.command()
async def helpp(ctx):
    embed=discord.Embed(title="Help")
    embed.add_field(name=">save {money}", value="花多少錢", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    response = requests.get(filedata["json_url"])
    jdata = response.json()

    if (F'{ctx.message.author.id}saving' not in jdata):
        jdata[F'{ctx.message.author.id}saving'] = "50000"
    else:
        jdata[F'{ctx.message.author.id}saving'] = str(int(jdata[F'{ctx.message.author.id}saving']) + 1000)

    money = jdata[F'{ctx.message.author.id}saving']
    embed=discord.Embed(title="簽到成功")
    embed.add_field(name=F'{ctx.message.author.name}', value=F'You have {money} dollars', inline=False)
    await ctx.send(embed=embed)
    update_data(jdata)

@bot.command()
async def gambling(ctx, cost):
    if (cost.isdigit() == False):
        await ctx.send('It\'s not a number')
        return
    response = requests.get(filedata['json_url'])
    jdata = response.json()

    if (F'{ctx.message.author.id}saving' not in jdata):#判斷是否有戶頭
        await ctx.send('你還沒有戶頭')
        return
    saving = jdata[F'{ctx.message.author.id}saving']

    if (int(cost) > int(saving)):#判斷戶頭的錢夠不夠
        await ctx.send('你的存款不夠了')
        return

    jdata[F'{ctx.message.author.id}saving'] = str(int(jdata[F'{ctx.message.author.id}saving']) - int(cost))#戶頭扣款
    win_or_lose = [True, False]
    embed = '0'
    if (random.choice(win_or_lose)):
        jdata[F'{ctx.message.author.id}saving'] = str((int(cost))*2 + int(jdata[F'{ctx.message.author.id}saving']))
        embed=discord.Embed(title="你贏了")
    else:
        embed=discord.Embed(title="你輸了")
    saving = jdata[F'{ctx.message.author.id}saving']
    embed.add_field(name=ctx.message.author.name + "的戶頭現在有", value=F'{saving}元', inline=False)
    await ctx.send(embed=embed)
    update_data(jdata)



@bot.command()
async def lottery(ctx, i):
    if (i.isdigit() == False):#j判斷是否為數字
        await ctx.send('It\'s not a number')
        return
    i = int(i)

    response = requests.get(filedata['json_url'])
    jdata = response.json()
    
    cost = 100 * i
    if (F'{ctx.message.author.id}saving' not in jdata):#判斷是否有戶頭
        await ctx.send('你還沒有戶頭')
        return
    if (cost > int(jdata[F'{ctx.message.author.id}saving'])):
        await ctx.send('你的存款不夠了')
        return
    if (int(jdata['total_lottery'])+i >100):
        await ctx.send('超出樂透最大數量')
        return 
    jdata[F'{ctx.message.author.id}saving'] = str(int(jdata[F'{ctx.message.author.id}saving']) - cost)#戶頭扣款
    jdata['accumulated_money'] = str(int(jdata['accumulated_money']) + i*100)#累計金錢
    jdata['total_lottery'] = str(int(jdata['total_lottery']) + i)
    total_money = jdata['accumulated_money']

    
    participants = jdata['player'] #將字典(參加者)內容讀入
    if (F'{ctx.message.author.id}' not in participants):
        participants[F'{ctx.message.author.id}'] = str(i)
        jdata['player'] = participants
        # jdata['player2'].update{F'{ctx.message.author.id}', str(i)}
    else:
        participants[F'{ctx.message.author.id}'] = str(int(jdata['player'][F'{ctx.message.author.id}']) + i)
        jdata['player'] = participants
    total_bought = jdata['player'][F'{ctx.message.author.id}']

    embed=discord.Embed(title="購買成功")
    embed.add_field(name=F"你在這期共買了{total_bought}張", value=F"累計獎金{total_money}元", inline=False)
    await ctx.send(embed=embed)
    # await ctx.send(total_money)#change into embed(購買成功)
    # await ctx.send(F'You have bought {total_bought} lottery')  #embed

    #到了100要開始抽獎

    if (int(jdata['total_lottery']) == 100):
        await ctx.send('開始抽獎')
        lottery_box = [False for i in range(1000)]
        # for i in lottery_box
        now = 0
        for key in jdata['player']:
            t = int(jdata['player'][key])
            guy_id = int(key)
            guy = await bot.fetch_user(guy_id)
            for j in range(now, 7*t+now):
                lottery_box[j] = key
                
            now = 7*t+now + 1
            await ctx.send(guy.mention)        
        winner_id = random.choice(lottery_box)
        if (winner_id == False):
            embed=discord.Embed(title="無人得獎", description="累計獎金" + jdata['accumulated_money'] + "元將留到下一期。")
            await ctx.send(embed=embed)
        else:
            jdata[F'{winner_id}saving'] = str(int(jdata[F'{winner_id}saving']) + int(jdata['accumulated_money']))
            winner = await bot.fetch_user(int(winner_id))
            jdata['accumulated_money'] = '0'
            embed=discord.Embed(title='恭喜'+winner.name + '得獎', description=winner.name + '戶頭現有' + jdata[winner_id + 'saving'] + '元')
            await ctx.send(embed=embed)
        participants = {}
        jdata['player'] = participants
        jdata['total_lottery'] = '0'

    update_data(jdata)

@bot.command()
async def check(ctx):
    response = requests.get(filedata['json_url'])
    jdata = response.json()
    
    sold = jdata['total_lottery']
    total_money = jdata['accumulated_money']
    embed=discord.Embed(title=F"本期樂透共賣出{sold}張", description=F"再賣出{str(100-int(sold))}張即開獎")
    embed.add_field(name=F"累計獎金{total_money}元", value="流局機率30%,一張100元" ,inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def profile(ctx):
    response = requests.get(filedata['json_url'])
    jdata = response.json()
    name = ctx.message.author.name
    if (F'{ctx.message.author.id}saving' not in jdata):#判斷是否有戶頭
        await ctx.send(F'{name},你還沒有戶頭')
        return
    money = jdata[F'{ctx.message.author.id}saving'] 
    if (F'{ctx.message.author.id}' not in jdata['player']):
        embed=discord.Embed(title=F'{name},你現在有{money} dollars')
    else:
        lottery_num = jdata['player'][F'{ctx.message.author.id}']
        embed=discord.Embed(title=F'{name},你現在有{money} dollars', description=F"以及{lottery_num}張樂透")
    await ctx.send(embed=embed)

# @bot.command()
# async def test(ctx):
    # response = requests.get(filedata['json_url'])
    # jdata = response.json()
    # participants = jdata['player']
    # await ctx.send(jdata['player'])
    # for key in jdata['player']:
    #     await ctx.send(jdata['player'][key])

    # print(type(ctx.message.author.id))
    # await ctx.send(ctx.message.author.id)
    # await ctx.send(ctx.message.author.name) 
    # user = await client.fetch_user(id1)
    # user = ctx.message.guild.get_member(id1)
    # user = await bot.fetch_user(518735323707211827)
    # print(ctx.message.author)
    # print(type(ctx.message.author))
    # print(user.name)
    # print(ctx.message.author.id)
    # k = 'name'
    # await ctx.send(k + 'hii', )

bot.run(filedata["token"]) #TOKEN 在剛剛 Discord Developer 那邊「BOT」頁面裡面

