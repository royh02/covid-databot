import discord
import requests
import json
import os
from random import seed
from random import random
from dotenv import load_dotenv
from decouple import config

# establish client connection
TOKEN = config("TOKEN")
print(TOKEN)

client = discord.Client()
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


@client.event
async def on_message(message):
    if message.content == 'covid help':
        help_msg = discord.Embed(
            title = 'Useful Commands',
            description = '(Prefix `covid`)\n Here are some cool commands you can use to get some good COVID data',
            colour = discord.Colour.red()            
        )
        help_msg.set_footer(text='Data from: https://about-corona.net/')
        help_msg.add_field(name='Command',
                            value='help\n'+
                                  'stats total_cases <country>\n'+
                                  'stats total_deaths <country>',
                            inline=True)
        help_msg.add_field(name='Description',
                            value='This command\n'+
                                  'Gets total confirmed cases in <country>\n'+
                                  'Gets total confiremd deaths in <country>', 
                            inline=True)
        await message.channel.send(embed=help_msg)

    if message.content == 'covid country_list':
        await message.channel.send("to be implemented soon in embed mode")
    if message.content.startswith('covid stats'):
        req_country = message.content.split()[2]
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

client.run(TOKEN)
