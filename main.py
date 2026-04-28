from corpus import load_corpus
from markov import MarkovBot
from bot import create_bot
from web import keep_alive
from config import DISCORD_TOKEN, COMMAND_PREFIX
corpus_indices, vocab, word_to_idx, idx_to_word, corpus_ok = load_corpus()
markov = MarkovBot(corpus_indices, idx_to_word, word_to_idx, vocab)
bot = create_bot(markov, DISCORD_TOKEN, COMMAND_PREFIX, keep_alive)
print("Starting bot...")
print("Corpus OK:", corpus_ok)
keep_alive()
bot.run(DISCORD_TOKEN)
