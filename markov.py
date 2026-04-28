import random as rnd
import config
import numpy as np
class MarkovBot:
    def __init__(self, corpus, idx_to_word, word_to_idx, vocab):
        self.idx_to_word = idx_to_word
        self.word_to_idx = word_to_idx
        self.vocab = vocab
        self.vocab_set = set(vocab)
        self.tokenized_corpus = [self.word_to_idx[word] for word in corpus if word in self.word_to_idx]
        self.trigram = {}
        self.bigram = {}
        self.build_models()
        self.sentences = self.generate_sentences(self.tokenized_corpus)
    def generate_sentences(self, tokenized_corpus):
        sentences = []
        current_sentence = []
        for idx in tokenized_corpus:
            word = self.idx_to_word[idx]
            if word in {".", "!", "?"}:
                if current_sentence:
                    sentences.append(current_sentence)
                current_sentence = []
            else:
                current_sentence.append(word)
        return sentences
    def next_candidates(self, w1, w2, k=5):
        return list({self.next_word(w1, w2) for _ in range(k)})
    def build_models(self):
        for i in range(len(self.tokenized_corpus) - 1):
            w1 = self.tokenized_corpus[i]
            w2 = self.tokenized_corpus[i + 1]
            if w1 not in self.bigram:
                self.bigram[w1] = {}
            self.bigram[w1][w2] = self.bigram[w1].get(w2, 0) + 1
        for i in range(len(self.tokenized_corpus) - 2):
            w1 = self.tokenized_corpus[i]
            w2 = self.tokenized_corpus[i + 1]
            w3 = self.tokenized_corpus[i + 2]
            key = (w1, w2)
            if key not in self.trigram:
                self.trigram[key] = {}
            self.trigram[key][w3] = self.trigram[key].get(w3, 0) + 1
        for k, v in self.bigram.items():
            items = list(v.keys())
            weights = list(v.values())
            self.bigram[k] = (items, weights)
        for k, v in self.trigram.items():
            items = list(v.keys())
            weights = list(v.values())
            self.trigram[k] = (items, weights)
    def find_relevant_sentence(self, prompt_words):
        if not prompt_words:
            return None
        best_score = 0
        best_sentences = []
        for sent in self.sentences:
            score = self.weighted_overlap(prompt_words, sent)
            if score > best_score:
                best_score = score
                best_sentences = [sent]
            elif score == best_score and score > 0:
                best_sentences.append(sent)
        if best_sentences:
            return rnd.choice(best_sentences)
        return None
    def stutter(self, word):
        if len(word) < 2:
            return word
        return f"{word[0]}-{word}"
    def sample(self, table):
        items, weights = table
        return rnd.choices(items, weights=weights, k=1)[0]
    def next_word(self, w1, w2):
        w1_idx = self.word_to_idx.get(w1, None)
        w2_idx = self.word_to_idx.get(w2, None)
        if w1_idx is None or w2_idx is None:
            return rnd.choice(self.vocab)
        key = (w1_idx, w2_idx)
        if key in self.trigram:
            next_word_idx = self.sample(self.trigram[key])
        elif w2_idx in self.bigram:
            next_word_idx = self.sample(self.bigram[w2_idx])
        else:
            return rnd.choice(self.vocab)
        return self.idx_to_word[next_word_idx]
    def weighted_overlap(self, prompt_words, sentence):
        score = 0
        sentence_set = set(sentence)
        for w in prompt_words:
            if w in sentence_set:
                if w in config.STOPWORDS:
                    score += 0.5
                else:
                    score += 1.8
        return score
    def score(self, prev, candidate, recent, prompt_words, topic_strength):
        score = 0
        if candidate == prev:
            score -= 5
        if candidate in recent:
            score -= 2
        if candidate in self.vocab_set:
            score += 1
        if candidate in prompt_words:
            score += 3 * topic_strength
        score += max(0, 5 - len(candidate)) * 0.05
        return score
    def generate(self, w1, w2, length=10, prompt_words=None):
        sentence = [w1, w2]
        recent = []
        w1_idx = self.word_to_idx.get(w1, None)
        w2_idx = self.word_to_idx.get(w2, None)
        if w1_idx is None or w2_idx is None:
            w1_idx = rnd.choice(list(self.word_to_idx.values()))
            w2_idx = rnd.choice(list(self.word_to_idx.values()))
        for step in range(length):
            topic_strength = (1.0 - step / length) ** 2
            candidates = self.next_candidates(w1, w2, k=8)
            scores = [self.score(w2, c, recent, prompt_words, topic_strength) for c in candidates]
            max_s = max(scores)
            exp_scores = np.exp(np.array(scores) - max_s)
            probs = exp_scores / exp_scores.sum() if exp_scores.sum() != 0 else np.ones(len(exp_scores)) / len(exp_scores)
            nxt_idx = rnd.choices(candidates, weights=probs, k=1)[0]
            sentence.append(self.idx_to_word[nxt_idx])
            recent.append(self.idx_to_word[nxt_idx])
            if len(recent) > 5:
                recent.pop(0)
            w1, w2 = w2, self.idx_to_word[nxt_idx]
            if len(sentence) > 2 and sentence[-1] in {".", "!", "?"}:
                break
        return " ".join(sentence)
    def reply(self, message_text):
        words = message_text.lower().split()
        prompt_words = [w for w in words if w in self.vocab_set and w not in config.STOPWORDS]
        if len(prompt_words) < 3:
            prompt_words = [w for w in words if w in self.vocab_set]
        seed_sentence = self.find_relevant_sentence(prompt_words)
        if seed_sentence:
            i = rnd.randint(0, len(seed_sentence) - 2)
            w1, w2 = seed_sentence[i], seed_sentence[i+1]
        else:
            pairs = [
                (words[i], words[i+1])
                for i in range(len(words) - 1)
                if words[i] in self.vocab_set and words[i+1] in self.vocab_set
            ]
            if pairs:
                w1, w2 = rnd.choice(pairs)
            else:
                w1 = rnd.choice(config.STARTERS)
                w2 = rnd.choice(self.vocab)
        min_length = 3
        max_length = 30
        lengths = list(range(min_length, max_length + 1))
        weights = [max_length - i + min_length for i in lengths]
        return self.generate(
            w1,
            w2,
            length = rnd.choices(lengths, weights=weights, k=1)[0],
            prompt_words=prompt_words
        )

