"""Dictionary-driven rack solver; no factorial permutation generation."""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import re

DICTIONARY = Path(__file__).with_name('wordlist.txt')


def normalize_rack(value):
    if not isinstance(value, str): raise ValueError('Rack must be text')
    raw = re.sub(r'\s+', '', value)
    if not re.fullmatch(r'[A-Za-z?]{3,12}', raw) or raw.count('?') > 2:
        raise ValueError('Use 3–12 A–Z letters, with at most two ? blank tiles')
    return raw.upper()


@lru_cache(maxsize=1)
def dictionary_index():
    words = {w.strip().upper() for w in DICTIONARY.read_text(encoding='utf-8').splitlines() if re.fullmatch('[A-Za-z]+', w.strip())}
    return tuple((word, Counter(word)) for word in sorted(words, key=lambda w: (-len(w), w)))


def find_anagrams(rack, minimum_length=3, exact=False):
    rack = normalize_rack(rack)
    if not isinstance(minimum_length, int) or minimum_length < 1:
        raise ValueError('Minimum length must be positive')
    available, blanks = Counter(rack), rack.count('?')
    return [word for word, counts in dictionary_index() if minimum_length <= len(word) <= len(rack)
            and (not exact or len(word) == len(rack))
            and sum(max(0, count-available[letter]) for letter, count in counts.items()) <= blanks]


def anagrams(word):
    word = str(word).strip().upper()
    if not re.fullmatch('[A-Z]{1,12}', word): raise ValueError('Use an A–Z word')
    target = Counter(word)
    return {candidate for candidate, counts in dictionary_index() if counts == target}


def tile_indices(rack, word):
    rack = normalize_rack(rack)
    word = str(word).upper()
    if not re.fullmatch('[A-Z]+', word): raise ValueError('Word must contain A–Z letters')
    positions = defaultdict(list)
    for index, letter in enumerate(rack): positions[letter].append(index)
    result = []
    for letter in word:
        choices = positions[letter] or positions['?']
        if not choices: raise ValueError('Word cannot be formed from this rack')
        result.append(choices.pop(0))
    return result
