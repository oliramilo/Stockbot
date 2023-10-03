import os
import json

import discord
from discord.ext import commands

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

try:
    # Get the bot token from the config.json file
    with open('config.json', 'r') as file:
        config = json.load(file)
        token = config['token']
except:
    print('The config.json file does not exist or is not formatted correctly. Please add/edit the config.json file and try again.')
    exit()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('Bot is ready to use!')
    
    # Set rich presence (custom status)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="Looking at stocks"))


@bot.event
async def on_guild_join(guild):
    welcome_message = f"I just joined {guild.name}. It's time to make money!!!."

    embed = discord.Embed(title="Stock analysis bot", description="Created by Oli Ramilo.", color=0x3498db)
    embed.add_field(name="Tutorial", value="Commands for stock bot", inline=False)
    embed.add_field(name="!sh <stock_symbol> <period>", value="Displays a graph of the stock price over the specified period", inline=False)
    embed.add_field(name="!ss <stock_symbol>", value="Displays information about the stock", inline=False)
    embed.add_field(name="!msh <stock_symbol1> <stock_symbol2> <period>", value="Displays a graph of the stock price over the specified period for two stocks", inline=False)
    embed.add_field(name="Version Beta 1.0", value="I was just created today so chill if I don't work properly man jeez.", inline=False)
    embed.add_field(name='Code repository', value='[Click Here](https://github.com/oliramilo)', inline=False)
    
    with open('stonks.jpg', 'rb') as file:
        stonk_image = discord.File(file)
        embed.set_image(url='attachment://stonks.jpg')
        # Find a text channel to send the welcome message
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(welcome_message)
                await channel.send(embed=embed, file=stonk_image)
                break

#display help menu for stock commands
@bot.command(name='shelp')
async def stock_search(ctx):
    embed = discord.Embed(title="Stock Bot Help", description="I analyse stock only for now.\nCommands for Stock Bot.", color=0x3498db)
    
    embed.add_field(name="Stock History", value="Usage: !sh <stock_symbol> <period>\nDisplays a graph of the stock price over the specified period.", inline=False)
    embed.add_field(name="Stock Search", value="Usage: !ss <stock_symbol>\nDisplays information about the stock.", inline=False)
    embed.add_field(name="Multiple Stock search ", value="Usage: !msh <stock_symbol1> <stock_symbol2> <period>\nDisplays a graph of the stock price over the specified period for two stocks.", inline=False)
    embed.add_field(name="Version Beta 1.0", value="I was just created today on 03/10/2023 so chill if I don't work properly man jeez.", inline=False)
    with open('stonks.jpg', 'rb') as file:
        stonk_image = discord.File(file)
        embed.set_image(url='attachment://stonks.jpg')
        await ctx.send(embed=embed, file=stonk_image)

#List stock for stock exchange provided
@bot.command(name='ss')
async def embed_stock_info(ctx,arg1):
    print(arg1)
    try:
        stock = yf.Ticker(arg1)
        stock_info = stock.info
        embed = discord.Embed(title=stock_info.get('shortName', 'Stock Info'), color=0x3498db)  # You can set the color and title as desired
        embed.add_field(name="Stock Symbol", value=stock_info['symbol'])
        embed.add_field(name="Stock Name", value=stock_info.get('longName', 'N/A'))
        embed.add_field(name="Exchange", value=stock_info['exchange'])
        embed.add_field(name="Currency", value=stock_info['currency'])
        embed.add_field(name="Sector", value=stock_info.get('sector', 'N/A'))
        embed.add_field(name="Industry", value=stock_info.get('industry', 'N/A'))
        embed.add_field(name="Country", value=stock_info.get('country', 'N/A'))
        embed.add_field(name="Current price", value=stock_info.get('currentPrice', 'N/A'))
        embed.set_thumbnail(url=stock_info.get('logo_url', 'https://example.com/default_logo.png'))  # Default logo URL if not available
        await ctx.send(embed=embed)
    except:
        await ctx.send("Provide a valid ticker symbol i.e AAPL (Apple).")

#display stock graph for stock provided
@bot.command(name='msh')
async def embed_stock_graph(ctx, stock_symbol1, stock_symbol2, period):
    interval = '1d'
    if period == 'day':
        interval = '1h'

    if period == 'max':
        await ctx.send("No dude that's too much data for me to handle.")
        return
    try:
        # Create a Ticker object for the specified stock symbols
        plt.clf()
        stock1 = yf.Ticker(stock_symbol1)
        stock2 = yf.Ticker(stock_symbol2)

        stock_info1 = stock1.info
        stock_info2 = stock2.info
        # Get historical data for the two stocks
        stock_data1 = yf.download(stock_symbol1, period=period, interval=interval)
        stock_data2 = yf.download(stock_symbol2, period=period, interval=interval)

        # Create a time series plot
        plt.figure(figsize=(10, 5))
        plt.plot(stock_data1.index, stock_data1['Adj Close'], label=f'{stock_symbol1} Closing Price', color='blue')
        plt.plot(stock_data2.index, stock_data2['Adj Close'], label=f'{stock_symbol2} Closing Price', color='orange')
        plt.title('Stock Closing Prices over the Last 10 Days')
        plt.xlabel(f'Time Period: ({period})', fontsize=8)
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.legend()

        stock_data1['Daily_Return'] = stock_data1['Adj Close'].pct_change()
        volatility1 = stock_data1['Daily_Return'].std()
        start_price1 = stock_data1['Adj Close'].iloc[0]
        end_price1 = stock_data1['Adj Close'].iloc[-1]
        return_rate1 = ((end_price1 - start_price1) / start_price1) * 100

        stock_data2['Daily_Return'] = stock_data1['Adj Close'].pct_change()
        volatility2 = stock_data2['Daily_Return'].std()
        start_price2 = stock_data2['Adj Close'].iloc[0]
        end_price2 = stock_data2['Adj Close'].iloc[-1]
        return_rate2 = ((end_price2 - start_price2) / start_price2) * 100


        symbol1 = stock_info1['symbol']
        symbol2 = stock_info2['symbol']
        # Save the plot as an image file
        plt.savefig('multi_stock_plot.png')

        with open('multi_stock_plot.png', 'rb') as file:
            plot_image = discord.File(file)
            embed = discord.Embed(title=f'{symbol1} vs {symbol2} Time Series Analysis', description='Closing price over the last 10 days', color=0x3498db)
            embed.add_field(name=f'{symbol1} Volatility', value=volatility1)
            embed.add_field(name=f'{symbol1} Total Return', value=return_rate1)
            embed.add_field(name=f'{symbol2} Volatility', value=volatility2)
            embed.add_field(name=f'{symbol2}Total Return', value=return_rate2)
            embed.set_image(url='attachment://multi_stock_plot.png')
            await ctx.send(embed=embed, file=plot_image)

        if os.path.exists('multi_stock_plot.png'):
            os.remove('multi_stock_plot.png')
    except:
        await ctx.send("You entered an invalid stock symbol or time period. Try !msh <stock_symbol1> <stock_symbol2> <period>")


@bot.command(name='sh')
async def embed_stock_graph(ctx, arg1,arg2):
    try: 
        interval = '1d'
        if arg2 == 'day':
            interval = '1h'

        if arg2 == 'max':
            await ctx.send("No dude that's too much data for me to handle.")
            return
        
        plt.clf()
        
        stock_info = yf.Ticker(arg1)
        stock_data = yf.download(arg1, period=arg2, interval=interval)
        stock_data['Daily_Return'] = stock_data['Adj Close'].pct_change()
        volatility = stock_data['Daily_Return'].std()
        start_price = stock_data['Adj Close'].iloc[0]
        end_price = stock_data['Adj Close'].iloc[-1]
        return_rate = ((end_price - start_price) / start_price) * 100

        symbol = stock_info.info['symbol']
        plt.plot(stock_data.index, stock_data['Adj Close'], marker='o', label=f'{symbol} Closing Price')
        plt.title(f'{symbol} Closing Price over the Previous {arg2} (1 Day Interval)')
        plt.xlabel(f'Time Period: ({arg2})', fontsize=8)
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.legend()

        plt.xticks([])
        plt.savefig('stock_plot.png')

        with open('stock_plot.png', 'rb') as file:
            plot_image = discord.File(file)
            embed = discord.Embed(title=f'{symbol} Graph Data', description=f'Closing price over {arg2}', color=0x3498db)
            embed.add_field(name='Volatility', value=volatility)
            embed.add_field(name='Total Return', value=return_rate)
            embed.set_image(url='attachment://stock_plot.png')
            await ctx.send(embed=embed, file=plot_image)
        
        if os.path.exists('stock_plot.png'):
            os.remove('stock_plot.png')
    except:
        await ctx.send("You entered an invalid stock symbol or time period. Try !sh <stock_symbol> <period>")

bot.run(token)
