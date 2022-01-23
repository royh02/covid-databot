import discord
from discord.ext import commands
import requests
import json
import io
from random import seed
from random import random
from decouple import config
from matplotlib import pyplot as plt
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, ConciseDateFormatter, date2num

# establish bot connection
TOKEN = config("TOKEN")

bot = commands.Bot(command_prefix='covid ')

seed(4)
# get ISO 2-digit country codes from JSON
country_codes_raw = json.load(open("iso_country_codes.json"))
name_code_pair = {}
for c in country_codes_raw:
    name_code_pair[c['Name']] = c['Code']

# for covid fun
infected = []

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(activity=discord.Activity(name="\"covid help\""))



@bot.event
async def on_message(message):
    msg = message.content.lower()
    if "drip" in msg:
        await message.add_reaction("<:drip:805220338068881420>")
    if message.author == bot.user:
        return
    else:
        await bot.process_commands(message)

    # Perhaps a future custom help update

    # if message.content == 'covid help':
    #     help_msg = discord.Embed(
    #         title = 'Useful Commands',
    #         description = '(Prefix `covid`)\n Here are some cool commands you can use to get some good COVID data',
    #         colour = discord.Colour.red()            
    #     )
    #     help_msg.set_footer(text='Data from: https://about-corona.net/')
    #     help_msg.add_field(name='Command',
    #                         value='help\n'+
    #                               'stats <country>\n'+
    #                               'has_covid <name>\n'+
    #                               'miracle_cure',
    #                         inline=True)
    #     help_msg.add_field(name='Description',
    #                         value='This command\n'+
    #                               'Gets stats for <country>\n'+
    #                               'Tests <name> for COVID-19\n'+
    #                               'Gets rid of all active COVID-19 cases', 
    #                         inline=True)
    #     await message.channel.send(embed=help_msg)

    if message.content.startswith('covid avatar'):
        if message.mentions.__len__() > 0:
            for user in message.mentions:
                await message.channel.send(user.avatar_url)

    if message.content.startswith('covid rate'):
        rated = " ".join(message.content.split()[2:])
        result = (sum([ord(rated[i]) * 9 * (i+1)
                       for i in range(len(rated))]) * 42 // 69) % 11
        emoji = "👍" if result >= 5 else "👎"
        emb = discord.Embed(
            description=f"I rate ***{rated}*** a **{result}/10** {emoji}",
            colour=discord.Colour.red()
        )
        await message.channel.send(embed=emb)


@bot.command(
    help = "Lists all the countries with statistics",
    brief = "List of countries"
)
async def country_list(ctx):
    country_list_raw = list(name_code_pair.keys())[:10]
    country_list_str = ''
    for c in country_list_raw:
        country_list_str += c + '\n'
    lst_embed = discord.Embed(
        title='Country List',
        description='Here is a list of countries that work with this bot',
        colour=discord.Colour.red()
    )
    lst_embed.add_field(name='Names', value=country_list_str)
    await ctx.send(embed=lst_embed)


@bot.command(
    help = "Get stats for requested countries, including total cases and deaths",
    brief = "Get stats for requested country"
)
async def stats(ctx, *args):
    req_country = " ".join([country.title() for country in args])
    r = requests.get('https://corona-api.com/countries/{0}'.format(
                     name_code_pair[req_country]))
    json_data = json.loads(r.text)['data']
    latest_confirmed = json_data['latest_data']['confirmed']
    latest_deaths = json_data['latest_data']['deaths']

    # Process graph
    dates = date2num([day['date'] for day in json_data['timeline']])
    confirmed = [day['confirmed'] for day in json_data['timeline']]
    deaths = [day['deaths'] for day in json_data['timeline']]

    plt.style.use('dark_background')
    fig, ax = plt.subplots()

    plt.plot_date(dates, confirmed, color='#47a0ff',
                  linestyle='-', marker='', linewidth=4,
                  ydate=False, xdate=True)
    loc = AutoDateLocator()
    formatter = ConciseDateFormatter(loc)

    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)

    ax.yaxis.grid()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    locs, _ = plt.yticks()
    ylabels = []
    for l in locs:
        lab = str(int(l)).replace('000000000', '000M').replace('00000000', '00M').replace(
            '0000000', '0M').replace('000000', 'M').replace('00000', '00K').replace('0000', '0K').replace('000', 'K')
        if not ('K' in lab or 'M' in lab):
            lab = "{:,}".format(int(lab))
        ylabels.append(lab)
    plt.yticks(locs, ylabels)
    plt.ylim(bottom=0)

    plt.savefig("images/stats.png", transparent=True)
    plt.close(fig)

    with open('images/stats.png', 'rb') as f:
        file = io.BytesIO(f.read())

    image = discord.File(file, filename='stats.png')

    embed = discord.Embed(
        title=req_country,
        description=f'Some stats for {req_country}',
        colour=discord.Colour.red()
    )
    embed.set_thumbnail(
        url=f'https://flagcdn.com/h240/{name_code_pair[req_country].lower()}.png')
    embed.set_footer(text='Data from: https://about-corona.net/')
    embed.add_field(name='Total Cases Confirmed', value="{:,}".format(latest_confirmed))
    embed.add_field(name='Total Deaths Confirmed', value="{:,}".format(latest_deaths))
    embed.set_image(url='attachment://stats.png')

    await ctx.send(embed=embed, file=image)


@bot.command(
    help = "Tests person for COVID-19. If you are infected, you will remain like that until you use a miracle_cure",
    brief = "Tests person for COVID-19"
)
async def has_covid(ctx, *args):
    global infected
    i = random()
    patient = "**"+ " ".join(args) + "**"
    confirmed = patient in infected
    print(i)
    print(infected)
    if i > 0.5 or confirmed:
        bot_msg = patient + ' has the coronavirus! Quarantine this fella fast!'
        if not confirmed:
            infected.append(patient)
    else:
        bot_msg = patient + ' has dodged a bullet! The lab results say negative for COVID-19!'
    await ctx.send(bot_msg)


@bot.command(
    help = "Cures all today_confirmed of COVID-19 for the has_covid game",
    brief = "Cures all infected"
)
async def miracle_cure(ctx):
    infected = []
    await ctx.send("All today_confirmed of covid has been cured...for now")


bot.run(TOKEN)
