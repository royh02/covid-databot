# web scrape imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

# discord.py import
import discord
#from dotenv import load_dotenv

# establish client connection
TOKEN = 'NzIxMTIwMjQ3NDEwNzIwNzc4.XuP5kA.TdxXBXNOAAiSr92k2Xj3He0oOC8'

client = discord.Client()

base_url = "https://www.worldometers.info/coronavirus/"

# driver + website setup
driver = webdriver.Chrome()
page = driver.get(base_url)
page_sauce = driver.page_source
soup = BeautifulSoup(page_sauce, features="html.parser")

# data lists
country_names = []
total_cases = []
total_deaths = []
active_cases = []

# value scraper
for nation in soup.find_all('tr', {'style': ''}):
    raw_stats = []
    for grid_val in nation.find_all('td'):
        raw_stats.append(grid_val.text)
    if len(raw_stats) == 19:
        country_names.append(raw_stats[1])
        total_cases.append(raw_stats[2])
        total_deaths.append(raw_stats[4])
        active_cases.append(raw_stats[8])

driver.quit()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(msg):
    channel = msg.channel

    """ # check country is valid
    async def check_country(c):
        return c in country_names """

    # don't reply to the bot itself
    if msg.author == client.user:
        return
    if msg.content.startswith("!covid help"):
        bot_msg = 'Hi {0.author.mention}! Here is the command list. This bot is still a WIP, so expect more to be added'.format(msg)
        await channel.send(bot_msg)
        await channel.send('>  !covid help --- Help \n\n  >  !covid stats total_cases <country> --- Current amt of **total cases** '
                           'in <country> \n\n  >  !covid stats deaths <country> --- Current amt of **confirmed deaths** in <country> \n\n'
                           '  >  !covid stats active_cases <country> --- Current amt of **active cases** in <country> \n\n'
                           )

    elif msg.content.startswith("!covid"):
        r_country = msg.content.split()[3:]
        raw_country = []

        # capitalize words cuz ppl are stupid
        for raw in r_country:
            raw_country.append(raw.capitalize())

        country = " ".join(raw_country)
        print(country)
        print(country_names)

        if msg.content.startswith("!covid stats total_cases"):
            if country in country_names:
                cases = str(total_cases[country_names.index(country)])
                bot_msg = ('{0.author.mention} There are currently ' + cases + ' total confirmed cases in ' + country).format(msg)

                # message is sent off!!!
                await channel.send(bot_msg)
            else:
                await channel.send('{0.author.mention}, that was not a valid country! Please check spelling.')

        elif msg.content.startswith("!covid stats active_cases"):
            if country in country_names:
                active = str(active_cases[country_names.index(country)])
                bot_msg = ('{0.author.mention} There are currently ' + active + ' active cases in ' + country).format(msg)

                await channel.send(bot_msg)
            else:
                await channel.send('{0.author.mention}, that was not a valid country! Please check spelling.')

        elif msg.content.startswith("!covid stats deaths"):
            if country in country_names:
                deaths = str(total_deaths[country_names.index(country)])
                bot_msg = ('{0.author.mention} There are currently ' + deaths + ' confirmed deaths in ' + country).format(msg)

                await channel.send(bot_msg)
            else:
                await channel.send('{0.author.mention}, that was not a valid country! Please check spelling.')

client.run(TOKEN)