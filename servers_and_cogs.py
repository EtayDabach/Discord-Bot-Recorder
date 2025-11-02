import discord
import os
import re
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

def get_discord_servers():
    prefix = "SERVER_"
    all_discord_servers = [discord.Object(id=value) for key, value in os.environ.items() if re.match(f"^{prefix}\d", key)] # only for single digit server names, e.g: SERVER_# 
    return all_discord_servers


def get_all_cogs():
    cog_names = []
    for filename in os.listdir("./cogs"):
        if filename.endswith("cogfile.py"):
            cog_names.append(filename[:-3]) # Appends only the file name without .py

    return cog_names


# print(get_discord_servers())


# print(os.environ.items())   
