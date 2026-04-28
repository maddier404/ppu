import random as rnd
import config
import numpy as np
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
    def next_candidates(self, w1, w2, k=5):
        return list({self.next_word(w1, w2) for _ in range(k)})
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
        # convert to fast sampling tables
        for k, v in self.bigram.items():
            items = list(v.keys())
            weights = list(v.values())
            self.bigram[k] = (items, weights)
        for k, v in self.trigram.items():
            items = list(v.keys())
            weights = list(v.values())
            self.trigram[k] = (items, weights)
    def stutter(self, word):
        if len(word) < 2:
            return word
        return f"{word[0]}-{word}"
    def sample(self, table):
        items, weights = table
        return rnd.choices(items, weights=weights, k=1)[0]
    def next_word(self, w1, w2):
        key = (self.word_to_idx[w1], self.word_to_idx[w2])
        if key in self.trigram:
            return self.idx_to_word[
                self.sample(self.trigram[key])
            ]
        if self.word_to_idx[w2] in self.bigram:
            return self.idx_to_word[
                self.sample(self.bigram[self.word_to_idx[w2]])
            ]
        return rnd.choice(self.vocab)
    def score(self, prev, candidate, recent, prompt_words, topic_strength):
        score = 0
        # penalize repetition
        if candidate == prev:
            score -= 5
        # penalize repeating recent words
        if candidate in recent:
            score -= 2
        # small bonus for common English words (from vocab frequency proxy)
        if candidate in self.vocab_set:
            score += 1
        if candidate in prompt_words:
            score += 3 * topic_strength
        # mild preference for shorter words (keeps flow less noisy)
        score += max(0, 5 - len(candidate)) * 0.05
        return score
    def generate(self, w1, w2, length=10, prompt_words=None):
        sentence = [w1, w2]
        recent = []
        for step in range(length):
            topic_strength = (1.0 - step / length) ** 2
            candidates = self.next_candidates(w1, w2, k=8)
            scores = [self.score(w2, c, recent, prompt_words, topic_strength) for c in candidates]
            # stabilize scores so negatives don't explode
            max_s = max(scores)
            exp_scores = np.exp(np.array(scores) - max_s)
            # convert to probabilities
            probs = exp_scores / exp_scores.sum() if exp_scores.sum() != 0 else np.ones(len(exp_scores)) / len(exp_scores)
            nxt = rnd.choices(candidates, weights=probs, k=1)[0]
            candidates = self.next_candidates(w1, w2, k=8)
            weights = []
            for c in candidates:
                base = self.score(w2, c, recent, prompt_words)
                if c in prompt_words:
                    base += 2
                weights.append(base)
            sentence.append(nxt)
            recent.append(nxt)
            if len(recent) > 5:
                recent.pop(0)
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
        prompt_words = [w for w in words if w in self.vocab_set and w not in STOPWORDS]
        if len(prompt_words) >= 2:
            pairs = [(words[i], words[i+1]) for i in range(len(words)-1)
                if words[i] in self.vocab_set and words[i+1] in self.vocab_set]
        if pairs:
            w1, w2 = rnd.choice(pairs)
        else:
            w1 = rnd.choice(config.STARTERS)
            w2 = rnd.choice(self.vocab)
        return self.generate(
            w1,
            w2,
            length=rnd.randint(7, 20),
            prompt_words=prompt_words
        )
