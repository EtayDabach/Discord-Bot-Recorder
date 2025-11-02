import asyncio
import discord
from discord.ext import commands, voice_recv
from discord import app_commands
import os
from dotenv import load_dotenv
from servers_and_cogs import get_discord_servers

# Load environment variables.
load_dotenv()

# Get all the discord servers ids.
guilds_list = get_discord_servers()

class RecordingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.sinks: dict[int, voice_recv.FFmpegSink] = {}


    @app_commands.command(name="join", description="Joins the voice channel you are in.")
    async def join(self, interaction: discord.Interaction):
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice:
            try:
                channel = interaction.user.voice.channel
                voice = await channel.connect(cls=voice_recv.VoiceRecvClient)
            except AttributeError as e:
                print(f"join AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to a voice channel!", description="Please connect to a voice channel first before using this command.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
            except discord.errors.ClientException as e: # If the bot is already connected to voice channel.
                print(f"join ClientException: {e}")
                embed = discord.Embed(title="I'm already in the voice channel...", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
            except Exception as e:
                print(f"join Error: {e}")
            
            print(f"From join: {voice} in {interaction.guild.name}.")
            hi_tts_filepath = "./command_audio/hi_tts_jessica.mp3"
            source = discord.FFmpegPCMAudio(source=hi_tts_filepath)
            voice.play(source)
            while voice.is_playing():
                await asyncio.sleep(0.1)

            embed = discord.Embed(title=f"Joined channel: {channel.name}", color=discord.Color.dark_teal())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="I'm already in the voice channel...")
            await interaction.response.send_message(embed=embed)
 
        # else:
        #     embed = discord.Embed(title="You are not in a voice channel!", description="Please connect to a voice channel first before using this command.", color=discord.Color.dark_teal())
        #     await interaction.response.send_message(embed=embed)


    @app_commands.command(name="record", description="Starts recording audio in the current voice channel.")
    @app_commands.describe(encoding="The encoding to use for the audio file. Can be 'wav', 'mp3', or 'pcm'.")
    async def record(self, interaction: discord.Interaction, encoding: str = 'mp3'):
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        print(f"From record: {voice}")
        if not voice:
            try:
                voice = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
            except AttributeError as e:
                print(f"record AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to a voice channel!", description="Please connect to a voice channel first before using this command.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
            except discord.errors.ClientException as e: # If the bot is already connected to voice channel.
                print(f"record ClientException: {e}")
                pass
            except Exception as e:
                print(f"record Error: {e}")
                embed = discord.Embed(title="Something went wrong...", description="Please ask the admin to check the logs for more details.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)

        # Make sure the user is in the voice channel before start recording.
        if voice.is_connected(): 
            try: # Try to get user info.
                user = interaction.user.display_name
                user_voice_channel = interaction.user.voice.channel.id
            except AttributeError as e:
                print(f"record AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to the voice channel!", description="Please connect to the voice channel first before using this command.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)

        if voice.is_connected() and not (user_voice_channel == voice.channel.id):
            embed = discord.Embed(title="You are not in the same voice channel as me!", description="Please connect to the same voice channel as me before using this command.", color=discord.Color.dark_teal())
            return await interaction.response.send_message(embed=embed)

        print(f"Start recording with {voice} in {interaction.guild.name}")


        try:
            if self.sinks[interaction.guild.id]:
                embed = discord.Embed(title=f"I'm already recording...", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
        except KeyError: # Should not be a problem because the sink will be created after this.
            pass
        except Exception as e:
            print(f"record Sink Error: {e}")


        if encoding not in ['wav', 'mp3', 'pcm']:
            embed = discord.Embed(title="Invalid encoding. Please use 'wav', 'mp3', or 'pcm'.", color=discord.Color.dark_teal())
            return await interaction.response.send_message(embed=embed)
        
        if not os.path.exists("./audio"):
            os.makedirs("./audio")
        
        start_tts_filepath = "./command_audio/start_recording_tts_jessica.mp3"
        source = discord.FFmpegPCMAudio(source=start_tts_filepath)
        voice.play(source)
        while voice.is_playing():
            await asyncio.sleep(0.4)

        sink_filename = f"./audio/{user}-recording-{interaction.guild.name}-{interaction.created_at.now().strftime("%d-%m-%Y_%H%M%S")}.{encoding}"
        print(f"sink_filename: {sink_filename}")
        sink = voice_recv.FFmpegSink(filename=sink_filename)
        voice.listen(sink)
        self.sinks[interaction.guild.id] = sink

        embed = discord.Embed(title=f"{user} started recording. The audio will be saved as a .{encoding} file.", description="Spill the tea...", color=discord.Color.dark_teal())
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="stop", description="Stops the recording and saves the audio.")
    async def stop(self, interaction: discord.Interaction):
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice:
            try:
                embed = discord.Embed(title="I'm not in the voice channel...", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
            except AttributeError as e:
                print(f"stop AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to the voice channel!", description="Please connect to the voice channel first before using this command.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
        
        if voice.is_connected(): 
            try:
                user = interaction.user.display_name
                user_voice_channel = interaction.user.voice.channel.id
            except AttributeError as e:
                print(f"record AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to the voice channel!", description="Please connect to the voice channel first before using this command.", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)

        if voice.is_connected() and not (user_voice_channel == voice.channel.id):
            embed = discord.Embed(title="You are not in the same voice channel as me!", description="Please connect to the same voice channel as me before using this command.", color=discord.Color.dark_teal())
            return await interaction.response.send_message(embed=embed)
        

        try:
            sink = self.sinks[interaction.guild.id]
        except KeyError:
            embed = discord.Embed(title="I'm not recording right now...", color=discord.Color.dark_teal())
            return await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            embed = discord.Embed(title="Something went wrong, I can't find the recording sink.", description="Please ask the admin to check the logs for more details.", color=discord.Color.dark_teal())
            return await interaction.response.send_message(embed=embed)
        
        # Defer the interaction as processing might take longer than 3 seconds.
        await interaction.response.defer()
         
        # await voice.disconnect()
        voice.stop_listening()
        
        # Wait for the sink to finish processing.
        await asyncio.sleep(1)

        stop_tts_filepath = "./command_audio/recording_stopped_tts_jessica.mp3"
        source = discord.FFmpegPCMAudio(source=stop_tts_filepath)
        voice.play(source)
        while voice.is_playing():
            await asyncio.sleep(0.5)
        
        # Finalize the file.
        filename = sink.filename
        print(f"filename: {filename}")
        sink.cleanup()
        
        try:
            embed = discord.Embed(title=f"{user} stopped the recording. Here is the audio file:", description="Beep boop.", color=discord.Color.dark_teal())
            await interaction.followup.send(embed=embed, file=discord.File(filename))
        except discord.errors.NotFound as e:
            print(f"stop NotFound: {e}")
            embed = discord.Embed(title=f"{user} stopped the recording.", description="But I was unable to find the audio file.", color=discord.Color.dark_teal())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"stop Error: {e}")
            embed = discord.Embed(title=f"{user} stopped the recording.", description="But I was unable to upload the audio file, it might be too large. Please ask the admin to check the logs for more details.", color=discord.Color.dark_teal())
            await interaction.followup.send(embed=embed)
        del self.sinks[interaction.guild.id]
        # os.remove(filename) # If you don't want to keep the audio files.


    @app_commands.command(name="leave", description="Leaves the voice channel.")
    async def leave(self, interaction: discord.Interaction):
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice:
            try:
                embed = discord.Embed(title="I'm not in a voice channel...", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)
            except AttributeError as e:
                print(f"stop AttributeError: {e}")
                embed = discord.Embed(title="You are not connected to the voice channel!", description="Please connect to the voice channel first before using this command", color=discord.Color.dark_teal())
                return await interaction.response.send_message(embed=embed)

        else:
            if voice.is_connected(): 
                try:
                    user = interaction.user.display_name
                    user_voice_channel = interaction.user.voice.channel.id
                except AttributeError as e:
                    print(f"record AttributeError: {e}")
                    embed = discord.Embed(title="You are not connected to the voice channel!", description="Please connect to the voice channel first before using this command.", color=discord.Color.dark_teal())
                    return await interaction.response.send_message(embed=embed)

                if voice.is_connected() and not (user_voice_channel == voice.channel.id):
                    embed = discord.Embed(title="You are not in the same voice channel as me.", description="Please connect to the same voice channel as me before using this command", color=discord.Color.dark_teal())
                    return await interaction.response.send_message(embed=embed)
            
            print(f"From leave: {voice} left {interaction.guild.name}.")
            bye_tts_filepath = "./command_audio/bye_tts_jessica.mp3"
            source = discord.FFmpegPCMAudio(source=bye_tts_filepath)
            voice.play(source)
            while voice.is_playing():
                await asyncio.sleep(0.4)
        
            await voice.disconnect()
            embed = discord.Embed(title="Bye!", color=discord.Color.dark_teal())
            await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RecordingCog(bot), guilds=guilds_list)

