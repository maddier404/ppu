import string
import re
from pathlib import Path
def load_corpus(path="corpus.txt"):
    file_path = Path(path)
    corpus = file_path.read_text()
    text = corpus.lower()
    words = text.split()
    words = [w.strip(string.punctuation) for w in words]
    words = [w for w in words if w]
    vocab = list(set(words))
    word_to_idx = {word: idx for idx, word in enumerate(vocab)}
    idx_to_word = {idx: word for word, idx in word_to_idx.items()}
    corpus_indices = [word_to_idx[w] for w in words if w in word_to_idx]
    raw_sentences = re.split(r"[.!?]\s+", text)
    sentences = []
    for s in raw_sentences:
        tokens = [w.strip(string.punctuation) for w in s.split()]
        tokens = [w for w in tokens if w in word_to_idx]
        if len(tokens) >= 2:
            sentences.append(tokens)
    print("CORPUS LOADED", len(corpus_indices))
    print("SENTENCES:", len(sentences))
    return corpus_indices, vocab, word_to_idx, idx_to_word, file_path.exists()
