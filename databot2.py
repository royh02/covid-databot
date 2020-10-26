import discord
from discord.ext import commands
import requests
import json
import os
from random import seed
from random import random
from decouple import config

# establish client connection
TOKEN = config("TOKEN")
print(TOKEN)

client = discord.Client()
bot = commands.Bot(command_prefix='covid', description='Hi')
seed(4)
# get ISO 2-digit country codes from JSON
country_codes_raw = json.load(open("iso_country_codes.json"))
name_code_pair = {}
for c in country_codes_raw:
    name_code_pair[c['Name']] = c['Code']

# for covid fun
infected = []

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #await bot.change_presence(activity=discord.Game(name="type \"covid help\""))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'covid help':
        help_msg = discord.Embed(
            title = 'Useful Commands',
            description = '(Prefix `covid`)\n Here are some cool commands you can use to get some good COVID data',
            colour = discord.Colour.red()            
        )
        help_msg.set_footer(text='Data from: https://about-corona.net/')
        help_msg.add_field(name='Command',
                            value='help\n'+
                                  'stats <country>\n'+
                                  'has_covid <name>\n'+
                                  'miracle_cure',
                            inline=True)
        help_msg.add_field(name='Description',
                            value='This command\n'+
                                  'Gets stats for <country>\n'+
                                  'Tests <name> for COVID-19\n'+
                                  'Gets rid of all active COVID-19 cases', 
                            inline=True)
        await message.channel.send(embed=help_msg)

    if message.content == 'covid country_list':
        country_list_raw = list(name_code_pair.keys())[:10]
        country_list_str = ''
        for c in country_list_raw:
            country_list_str += c + '\n'
        lst_embed = discord.Embed(
            title='Country List',
            description='Here is a list of countries that work with this bot',
            colour=discord.Colour.red()
        )
        lst_embed.add_field(name='Names',value=country_list_str)        
        await message.channel.send(embed=lst_embed)

    if message.content.startswith('covid stats'):
        req_country = " ".join([country.title() for country in message.content.split()[2:]])
        r = requests.get('https://corona-api.com/countries/' + name_code_pair[req_country])
        json_data = json.loads(r.text)['data']
        cases = json_data['latest_data']['confirmed']
        deaths = json_data['latest_data']['deaths']
        stats = discord.Embed(
            title=req_country,
            description='Some stats for ' + req_country,
            colour = discord.Colour.red()
        )
        stats.set_thumbnail(
            url='https://www.countryflags.io/{0}/flat/64.png'.format(name_code_pair[req_country]))
        stats.set_footer(text='Data from: https://about-corona.net/')
        stats.add_field(name='Total Cases Confirmed',value=str(cases))
        stats.add_field(name='Total Deaths Confirmed',value=str(deaths))
        
        await message.channel.send(embed=stats)
    
    if message.content.startswith('covid has_covid'):
        global infected
        i = random()
        patient = message.content.split()[2]
        confirmed = patient in infected
        print(i)
        print(infected)
        if i > 0.5 or confirmed:
            bot_msg = (patient + 
                        ' has the coronavirus! Quarantine this fella fast!').format(message)
            if not confirmed:
                infected.append(patient)
        else:
            bot_msg = (patient +
                        ' has dodged a bullet! The lab results say negative for COVID-19!').format(message)
        await message.channel.send(bot_msg)

    if message.content.startswith('covid miracle_cure'):
        infected = []
        await message.channel.send("All cases of covid has been cured...for now hehehehe")

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

client.run(TOKEN)
