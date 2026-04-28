import discord
from discord.ext import commands
from corpus import vocab
def create_bot(markov, token, prefix, keep_alive):
    bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())
    user_memory = {}
    latency_history = []
    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}")
        print(f"In {len(bot.guilds)} guilds")
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        user_memory[message.author.id] = message.content.lower()
        if message.content.lower() == "ppu" and not message.content.startswith(prefix):
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
        await ctx.send("ppu specs:\nclock speed: 1hz\nsilliness: off the freacking charts")
    @bot.command(name="speak")
    async def speak(ctx):
        response = markov.reply(ctx.message.content)
        await ctx.send(response)
    @bot.command(name="pronouns")
    async def pronouns(ctx):
        await ctx.send("my pronouns are it/she! i'm bot!")
    @bot.command(name="vlist")
    async def vlist(ctx):
        await ctx.send("my vocabulary is:\n", vocab)
    @bot.command(name="vlength")
    async def vlength(ctx):
        await ctx.send(f"my vocabulary is {len(vocab)} words long")
    bot.remove_command("help")
    @bot.command(name="help")
    async def help_cmd(ctx):
        await ctx.send(
            "help\nprefix is !\ncommands:\n-help\n-diag\n-specs\n-speak\n-pronouns\n=vocab=\n-vlist\n-vlength"
        )
    return bot
