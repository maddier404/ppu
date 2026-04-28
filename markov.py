import random as rnd
class MarkovBot:
    def __init__(self, corpus_indices, idx_to_word, word_to_idx, vocab):
        self.corpus = corpus_indices
        self.idx_to_word = idx_to_word
        self.word_to_idx = word_to_idx
        self.vocab = vocab
        self.vocab_set = set(vocab)
        self.trigram = {}
        self.bigram = {}
        self.build_models()
    def build_models(self):
        for i in range(len(self.corpus) - 1):
            w1 = self.corpus[i]
            w2 = self.corpus[i + 1]
            self.bigram.setdefault(w1, []).append(w2)
        for i in range(len(self.corpus) - 2):
            w1 = self.corpus[i]
            w2 = self.corpus[i + 1]
            w3 = self.corpus[i + 2]
            self.trigram.setdefault((w1, w2), []).append(w3)
    def stutter(self, word):
        if len(word) < 2:
            return word
        return f"{word[0]}-{word}"
    def next_word(self, w1, w2):
        key = (self.word_to_idx[w1], self.word_to_idx[w2])
        if key in self.trigram:
            return self.idx_to_word[rnd.choice(self.trigram[key])]
        if self.word_to_idx[w2] in self.bigram:
            return self.idx_to_word[rnd.choice(self.bigram[self.word_to_idx[w2]])]
        return rnd.choice(self.vocab)
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
                result.append(self.stutter(clean))
            else:
                result.append(clean)
        text = " ".join(result)
        if not text.endswith((".", "!", "?")):
            text += rnd.choices([".", "!", "?"], weights=[3, 1, 1])[0]
        words = text.split()
        new_words = []
        for i, w in enumerate(words):
            if i > 2 and rnd.random() < 0.08:
                new_words.append(w + ",")
            else:
                new_words.append(w)
        text = " ".join(new_words)
        if len(result) > 12:
            text += "."
        return text
    def reply(self, message_text):
        words = message_text.lower().split()
        prompt_words = [w for w in words if w in self.vocab_set]
        if len(prompt_words) >= 2:
            w1 = rnd.choice(prompt_words)
            w2 = rnd.choice(prompt_words)
        else:
            w1, w2 = rnd.choice(self.vocab), rnd.choice(self.vocab)
        return self.generate(w1, w2, length=rnd.randint(7, 20), prompt_words=prompt_words)
