# imports
import os
import string
import numpy as np
import random as rnd
from pathlib import Path
from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from dotenv import load_dotenv
# pinger
app = Flask('')
@app.route('/')
def home():
    return "I'm alive"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        t = Thread(target=run)
        t.start()
# get corpus and vocab
file_path = Path('corpus.txt')
corpus = file_path.read_text()
words = corpus.lower().split()
words = [w.strip(string.punctuation) for w in words]
words = [w for w in words if w]
word_to_idx = {word: idx for idx, word in enumerate(vocab)}
idx_to_word = {idx: word for word, idx in word_to_idx.items()}
corpus_indices = [word_to_idx[word] for word in words]
# markov bs i hate classes AAAAAAAAA
class MarkovBot:
    def __init__(self, corpus_indices, idx_to_word, word_to_idx, vocab):
        self.corpus = corpus_indices
        self.idx_to_word = idx_to_word
        self.word_to_idx = word_to_idx
        self.vocab = vocab
        self.trigram = {}
        self.bigram = {}
        self.build_models()
    # read corpus
    def build_models(self):
        for i in range(len(self.corpus) - 1):
            w1 = self.corpus[i]
            w2 = self.corpus[i + 1]
            if w1 not in self.bigram:
                self.bigram[w1] = {}
            self.bigram[w1][w2] = self.bigram[w1].get(w2, 0) + 1
        for i in range(len(self.corpus) - 2):
            w1 = self.corpus[i]
            w2 = self.corpus[i + 1]
            w3 = self.corpus[i + 2]
            key = (w1, w2)
            if key not in self.trigram:
                self.trigram[key] = {}
            self.trigram[key][w3] = self.trigram[key].get(w3, 0) + 1
    # do stuff with corpus i don't remember i kinda got lost in the code and forgot to comment
    def stutter(word):
        if len(word) < 2:
            return word
        first = word[0]
        return f"{first}-{word}"
    def next_word(self, w1, w2):
        key = (self.word_to_idx[w1], self.word_to_idx[w2])
        # trigram
        if key in self.trigram:
            options = self.trigram[key]
            words = list(options.keys())
            probs = list(options.values())
            next_idx = np.random.choice(words, p=np.array(probs) / sum(probs))
            return self.idx_to_word[next_idx]
        # bigram fallback
        if self.word_to_idx[w2] in self.bigram:
            options = self.bigram[self.word_to_idx[w2]]
            words = list(options.keys())
            probs = list(options.values())
            next_idx = np.random.choice(words, p=np.array(probs) / sum(probs))
            return self.idx_to_word[next_idx]
        # random fallback
        return rnd.choice(self.vocab)
    # make the text
    def generate(self, w1, w2, length=10, prompt_words=None):
        sentence = [w1, w2]
        for _ in range(length):
            nxt = self.next_word(w1, w2)
            if prompt_words and rnd.random() < 0.2:
                nxt = rnd.choice(prompt_words)
            sentence.append(nxt)
            w1, w2 = w2, nxt
        result = []
        for w in sentence:
            clean = w.strip(".,!?")
            if rnd.random() < 0.015:
                result.append(stutter(clean))
            else:
                result.append(clean)
        sentence = " ".join(result)
        # always end sentence properly
        if not sentence.endswith((".", "!", "?")):
            sentence += rnd.choice([".", ".", ".", "!", "?"])
        words = sentence.split()
        new_words = []
        for i, w in enumerate(words):
            if i > 2 and rnd.random() < 0.08:
                new_words.append(w + ",")
            else:
                new_words.append(w)
        sentence = " ".join(new_words)
        if len(result) > 12:
            sentence += "."
        return sentence    
# this is called when the command is used. ex !speak hi how are you
    def reply(self, message_text):
        words = message_text.lower().split()
        prompt_words = [w for w in words if w in self.vocab]
        if len(prompt_words) >= 2:
            weights = [words.count(w) for w in prompt_words]
            w1 = rnd.choices(prompt_words, weights=weights)[0]
            w2 = rnd.choices(prompt_words, weights=weights)[0]
        else:
            w1, w2 = rnd.choice(self.vocab), rnd.choice(self.vocab)
        return self.generate(w1, w2, length=rnd.randint(7, 20), prompt_words=prompt_words)
markov = MarkovBot(corpus_indices, idx_to_word, word_to_idx, vocab)
user_memory = {}
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"In {len(bot.guilds)} guilds")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    user_memory[message.author.id] = message.content.lower()
    if message.content.lower() == "ppu" and not message.content.startswith("!"):
        await message.channel.send("that's me!")
    await bot.process_commands(message)
@bot.command(name="ppu")
async def ppu(ctx):
    await ctx.send(f"ppu latency: {round(bot.latency * 1000)}ms")
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
# ===
bot.remove_command("help")
@bot.command(name="help")
async def help(ctx):
    await ctx.send("help\nprefix is !\ncommands:\n-help\n-corpus\n-ppu\n-specs\n-speak\n-pronouns")
# ===
try:
    keep_alive()
    bot.run(DISCORD_TOKEN)
except Exception as e:
    print("CRASH:", e)
