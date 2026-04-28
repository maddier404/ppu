from flask import Flask
from threading import Thread
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

import numpy as np
import random as rnd
from pathlib import Path
# Sample dataset: A small text corpus
file_path=Path('corpus.txt')
corpus = file_path.read_text()
# tokenize corpus
words = corpus.lower().split()
# vocab creation
vocab = list(set(words))
vocab_size = len(vocab)
#print(f"Vocabulary: {vocab}")
#print(f"Vocabulary size: {vocab_size}")
word_to_idx = {word: idx for idx, word in enumerate(vocab)}
idx_to_word = {idx: word for word, idx in word_to_idx.items()}
# convert words in corpus to index
corpus_indices = [word_to_idx[word] for word in words]
# init bigram counts matrix. no, trigram
trigram_counts = {}
# count occurrences of each bigram in corpus
for i in range(len(corpus_indices) - 2):
    w1 = corpus_indices[i]
    w2 = corpus_indices[i + 1]
    w3 = corpus_indices[i + 2]
    key = (w1, w2)
    if key not in trigram_counts:
        trigram_counts[key] = {}
    trigram_counts[key][w3] = trigram_counts[key].get(w3, 0) + 1
trigram_probs = {}
for key, next_words in trigram_counts.items():
    total = sum(next_words.values()) + 0.01 * len(vocab)
    trigram_probs[key] = {
        word: (count + 0.01) / total
        for word, count in next_words.items()
    }
# normalize counts to get probabilities
#trigram_probabilities = trigram_counts / trigram_counts.sum(axis=2, keepdims=True)
#print("Bigrams probabilities matrix: ", bigram_probabilities)
def predict_next_word(w1, w2):
    key = (word_to_idx[w1], word_to_idx[w2])
    if key not in trigram_probs:
        return rnd.choice(vocab)
    next_words = trigram_probs[key]
    words = list(next_words.keys())
    probs = list(next_words.values())
    next_idx = np.random.choice(words, p=probs)
    return idx_to_word[next_idx]
# Test the model with a word
#current_word = "ai"
#next_word = predict_next_word(current_word, bigram_probabilities)
#print(f"Given '{current_word}', the model predicts '{next_word}'.")
def generate_sentence(w1, w2, length=5):
    sentence = [w1, w2]
    current_w1, current_w2 = w1, w2
    for _ in range(length):
        next_word = predict_next_word(current_w1, current_w2)
        sentence.append(next_word)
        current_w1 = current_w2
        current_w2 = next_word
    return ' '.join(sentence)
# for i in range(1):
    # generated_sentence=generate_sentence("maddie", bigram_probabilities, length=length)
    # print(generated_sentence)
# ==============================================================
# ==============================================================
# ==============================================================
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
#bot = discord.Client(intents=discord.Intents.default())
# event listener
@bot.event
async def on_ready():
    guild_count = 0
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
        guild_count = guild_count + 1
    print("ppu is in " + str(guild_count) + "guilds")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.lower() == "ppu" and not message.content.startswith("!"):
        await message.channel.send(f"that's me!")
    await bot.process_commands(message)
@bot.command(name="ppu")
async def ppu(ctx):
    await ctx.send(f"ppu latency: {round(bot.latency * 1000)}ms")
@bot.command(name="specs")
async def specs(ctx):
    await ctx.send(f"ppu specs: \nclock speed: 1hz\nsilliness: off the freacking charts")
@bot.command(name="speak")
async def speak(ctx):
    w1 = rnd.choice(vocab)
    w2 = rnd.choice(vocab)
    length = rnd.randint(7, 20)
    generated_sentence = generate_sentence(w1, w2, length=length)
    await ctx.send(generated_sentence)
@bot.command(name="pronouns")
async def pronouns(ctx):
    await ctx.send("my pronouns are it/she! i'm bot!")
#@bot.command(name="corpus")
#async def corpus(ctx):
#    await ctx.send(file_path.read_text())
# ==============================================================
bot.remove_command("help")
@bot.command(name="help")
async def help(ctx):
    await ctx.send("help\nprefix is !\ncommands:\n-help\n-corpus\n-ppu\n-specs\n-speak\n-pronouns")
# ==============================================================
# ==============================================================
# ==============================================================
keep_alive()
bot.run(DISCORD_TOKEN)
