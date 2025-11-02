import asyncio
import discord
import logging
import re
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
from servers_and_cogs import get_discord_servers, get_all_cogs


# Load environment variables
load_dotenv()

# Get all the discord servers ids and all cog files names.
guilds_list = get_discord_servers()
cogs_list = get_all_cogs()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        # Forward all arguments, and keyword-only arguments to commands.Bot
        super().__init__(*args, **kwargs)

    async def on_ready(self)-> None:
        all_guilds = []
        for guild in self.guilds:
            all_guilds.append(guild)
        print(f"Logged on as {self.user} in {all_guilds}!")
        print("All set!")

        # NOT RECOMMENDED, NEED TO BE CHANGED
        # try:
        #     for guild in guilds_list:
        #         synced = await self.tree.sync(guild=guild)
        #         print(f'Synced {len(synced)} commands to guild {guild}')

        # except Exception as e:
        #     print(f'Error syncing commands: {e}')
    
    # async def setup_hook(self):
    #     try:
    #         for guild in guilds_list:
    #             synced = await self.tree.sync(guild=guild)
    #             print(f'Synced {len(synced)} commands to guild {guild}')

    #     except Exception as e:
    #         print(f'Error syncing commands: {e}')
        


intents = discord.Intents.all()
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
discord.utils.setup_logging(handler=handler, level=logging.INFO)

bot = CustomBot(command_prefix="!", intents=intents)

# Must be a prefix command (will not appear in slash commands, use commands.Context instead of discord.Interaction).
@bot.command(name="sync", description="Admin only. Sync the commands", guilds=guilds_list)
@commands.is_owner()
async def sync(ctx: commands.Context) -> None: # ctx:commands.Context
    print(f"foo")
    try:
        if ctx.author.id == int(ADMIN_ID): ## str to int
            guild = ctx.guild
            synced = await bot.tree.sync(guild=guild) # interaction.guild
            embed = discord.Embed(title=f"Synced {len(synced)} commands to this guild", color=discord.Color.dark_teal())
            await ctx.send(embed=embed)
            print(f"Synced {len(synced)} commands to {ctx.guild.name}")
        else:
            embed = discord.Embed(title=f"You must be the Admin to use this command!", color=discord.Color.dark_teal())
            await ctx.send(embed=embed)
    except Exception as e:
        print(e)



# Test slash commands
@bot.tree.command(name="hello", description="Says hello!", guilds=guilds_list) # checker
async def hello(interaction: discord.Interaction) -> None:
    embed = discord.Embed(title=f"Hi {interaction.user.display_name}!", color=discord.Color.dark_teal())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="diceroll", description="Rolls a dice", guilds=guilds_list)
@app_commands.describe(sides="The number of sides of the dice")
async def roll(interaction: discord.Interaction, sides: int = 6) -> None:
    result = random.randint(1, sides)
    embed = discord.Embed(title=f"You rolled a {result}!", color=discord.Color.dark_teal())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ping", description="Pings the bot", guilds=guilds_list)
async def ping(interaction: discord.Interaction) -> None:
    embed = discord.Embed(title=f"Pong!", color=discord.Color.dark_teal())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="coinflip", description="Flips a coin", guilds=guilds_list)
async def coinflip(interaction: discord.Interaction) -> None:
    result = random.choice(["Heads", "Tails"])
    embed = discord.Embed(title=f"You flipped a {result}!", color=discord.Color.dark_teal())
    await interaction.response.send_message(embed=embed)


# Main initialization
async def main():
    async with bot:
        try:
            print("Loading cogs...")
            for cogfile in cogs_list:
                await bot.load_extension(f"cogs.{cogfile}")
            print(f"{len(cogs_list)} Cogs are synced!")
        except Exception as e:
            print(e)
        await bot.start(BOT_TOKEN, reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())