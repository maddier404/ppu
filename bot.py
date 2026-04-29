import discord
from discord.ext import commands
from discord.ui import Button, View
import random as rnd
import corpus
import psutil
import platform
import os
def create_bot(markov, token, prefix, keep_alive):
    corpus_indices, vocab, word_to_idx, idx_to_word, corpus_exists = corpus.load_corpus()
    if not corpus_exists:
        raise FileNotFoundError("Corpus file 'corpus.txt' not found!")
    bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
    user_memory = {}
    latency_history = []
    async def paginate_vocabulary(ctx, vocab_list, page=1):
        words_per_page = 25
        start_index = (page - 1) * words_per_page
        end_index = page * words_per_page
        current_page_words = vocab_list[start_index:end_index]
        embed = discord.Embed(title="Vocabulary List", color=discord.Color.blue())
        embed.add_field(name=f"Page {page}", value="\n".join(current_page_words), inline=False)
        buttons = View()
        if page > 1:
            prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="prev_page")
            async def prev_callback(interaction):
                await paginate_vocabulary(interaction, vocab_list, page - 1)
                await interaction.response.edit_message(embed=embed, view=buttons)
            prev_button.callback = prev_callback
            buttons.add_item(prev_button)
        if end_index < len(vocab_list):
            next_button = Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next_page")
            async def next_callback(interaction):
                await paginate_vocabulary(interaction, vocab_list, page + 1)
                await interaction.response.edit_message(embed=embed, view=buttons)
            next_button.callback = next_callback
            buttons.add_item(next_button)
        await ctx.send(embed=embed, view=buttons)
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        print(f"In {len(bot.guilds)} guilds")
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        user_memory[message.author.id] = message.content.lower()
        greet = message.content.lower()
        greetcheck = greet.split()
        print(f"{greetcheck}")
        if "ppu" in greetcheck and not message.content.startswith(prefix):
            await message.channel.send("that's me!")
        await bot.process_commands(message)
    @bot.command(name="ppu")
    async def ppu(ctx):
        start = discord.utils.utcnow()
        msg = await ctx.send("measuring...")
        end = discord.utils.utcnow()
        ws_latency = round(bot.latency * 1000)
        rtt = (end - start).total_seconds() * 1000
        latency_history.append(rtt)
        if len(latency_history) > 50:
            latency_history.pop(0)
        avg = sum(latency_history) / len(latency_history)
        jitter = max(latency_history) - min(latency_history)
        await msg.edit(content=(
            f"ppu diagnostics\n"
            f"ws latency: {ws_latency}ms\n"
            f"rtt: {round(rtt)}ms\n"
            f"avg rtt: {round(avg)}ms\n"
            f"jitter: {round(jitter)}ms"
        ))
    @bot.command(name="specs")
    async def specs(ctx):
        # cpu info
        cpu_cores = psutil.cpu_count(logical=True)
        cpu_percent = psutil.cpu_percent(interval=1)
        # mem info
        mem = psutil.virtual_memory()
        total_mem = round(mem.total/(1024 ** 2))
        used_mem = round(mem.used/(1024 ** 2))
        # disk info
        disk = psutil.disk_usage("/")
        total_disk = round(disk.total/(1024 ** 3), 2)
        used_disk = round(disk.used/(1024 ** 3), 2)
        # system info and such
        system = platform.system()
        release = platform.release()
        python_version = platform.python_version()
            # send the thing 
        await ctx.send(
            f"ppu specs (container)\n"
            f"os: {system} {release}\n"
            f"python: {python_version}\n"
            f"cpu cores: {cpu_cores}\n"
            f"cpu usage: {cpu_percent}%\n"
            f"ram: {used_mem}MB / {total_mem}MB\n"
            f"disk: {used_disk}GB / {total_disk}GB"
        )
    @bot.command(name="speak")
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def speak(ctx):
        response = markov.reply(ctx.message.content)
        await ctx.send(response)
    @bot.command(name="pronouns")
    async def pronouns(ctx):
        await ctx.send("my pronouns are it/she! i'm bot!")
    @bot.command(name="vlist")
    async def vlist(ctx):
        await paginate_vocabulary(ctx, vocab, page=1)
    @bot.command(name="vlength")
    async def vlength(ctx):
        vocab_length = len(vocab)
        await ctx.send(f"my vocabulary is {vocab_length} words long")
    bot.remove_command("help")
    @bot.command(name="help")
    async def help_cmd(ctx):
        await ctx.send(
            "help\nprefix is !\ncommands:\n-help\n-diag\n-specs\n-speak\n-pronouns\n-vocab=\n-vlist\n-vlength"
        )
    return bot
