#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
გაფართოებული სიტყვების გენერატორი (make_expanded_wordlist.py)
---------------------------------------------------------------
საწყისი_ფაილი:  words.txt  (ერთი სიტყვა თითო ხაზზე, UTF-8)
საბოლოო_ფაილი: wordlist.txt (ერთი ვარიანტი თითო ხაზზე)

ფუნქციები:
- აერთიანებს სიტყვებს ყველა შესაძლო თანმიმდევრობით (სიგრძე MIN_K..MAX_K, ნაგულისხმევია 2..10)
- თითოეული სიტყვისთვის ქმნის სხვადასხვა ვარიანტებს:
    ორიგინალი, პატარა, დიდი
- თითოეულ კომბინაციას უმატებს პრეფიქსებსა და სუფიქსებს (მაგ. რიცხვებს)
- აქვს უსაფრთხოების ზღვარი (MAX_ENTRIES), რომ ფაილი ძალიან დიდი არ გამოვიდეს
- ტერმინალში აჩვენებს პროგრესს
"""

from itertools import permutations, product, islice
import sys
import math
from typing import List

# --------------------------
# პარამეტრები (შეცვალე სურვილისამებრ)
# --------------------------
INPUT_FILE = "words.txt" # პარამეტრები (შეცვალე სურვილისამებრ)
OUTPUT_FILE = "wordlist.txt" # შედეგის ფაილი

MIN_K = 2    # მინიმალური სიტყვების რაოდენობა ერთ კომბინაციაში
MAX_K = 10   # მაქსიმალური რაოდენობა (გაითვალისწინე: რაც მეტია, მით უფრო იზრდება კომბინაციები)
CASE_OPTIONS = ["original", "lower", "upper", "capitalize"]

# ციფრები ან ტექსტი დასაწყისში და ბოლოში
PREFIXES = ["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]      # რაც გინდა ის შეიყვანე
SUFFIXES = ["", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# მაქსიმალური ხაზების რაოდენობა (უსაფრთხოების ლიმიტი)
# თუ გინდა შეუზღუდავი გენერაცია → დააყენე None
MAX_ENTRIES = 10000000


# --------------------------
# დამხმარე ფუნქციები
# --------------------------
def read_words(path: str) -> List[str]:
    """წაიკითხავს სიტყვებს ფაილიდან"""
    with open(path, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]
    return words


def case_variants_for_word(w: str):
    """აბრუნებს ერთი სიტყვის სხვადასხვა ასო-ფორმატებს"""
    variants = []
    for mode in CASE_OPTIONS:
        if mode == "original":
            variants.append(w)
        elif mode == "lower":
            variants.append(w.lower())
        elif mode == "upper":
            variants.append(w.upper())
        elif mode == "capitalize":
            variants.append(w.capitalize())
    # ვშლით დუბლიკატებს
    unique = []
    for v in variants:
        if v not in unique:
            unique.append(v)
    return unique


def estimate_total_entries(n_words: int, min_k: int, max_k: int, case_opts_len: int, n_prefix: int, n_suffix: int):
    """დაანგარიშებს სავარაუდო საერთო რაოდენობას"""
    total = 0
    for k in range(min_k, min(max_k, n_words) + 1):
        perm_count = math.perm(n_words, k) if hasattr(math, "perm") else math.factorial(n_words) // math.factorial(n_words - k)
        case_mul = (case_opts_len ** k)
        total += perm_count * case_mul * n_prefix * n_suffix
    return total


# --------------------------
# მთავარი ფუნქცია
# --------------------------
def main():
    words = read_words(INPUT_FILE)
    n = len(words)
    if n == 0:
        print(f"ფაილში {INPUT_FILE} სიტყვები ვერ მოიძებნა.")
        sys.exit(1)
    print(f"ჩაიტვირთა {n} სიტყვა ფაილიდან: {INPUT_FILE}")

    # შევამოწმოთ პარამეტრები
    if MIN_K < 1 or MAX_K < MIN_K:
        print("MIN_K ან MAX_K მნიშვნელობები არასწორია.")
        sys.exit(1)

    # წინასწარ შევქმნათ თითო სიტყვის ვარიანტები
    per_word_cases = {w: case_variants_for_word(w) for w in words}
    case_opts_len = len(CASE_OPTIONS)

    estimated = estimate_total_entries(n, MIN_K, MAX_K, case_opts_len, len(PREFIXES), len(SUFFIXES))
    print("სავარაუდო საერთო კომბინაციები:", estimated)
    if MAX_ENTRIES is not None and estimated > MAX_ENTRIES:
        print(f"გაფრთხილება: სავარაუდო რაოდენობა ({estimated}) აჭარბებს ლიმიტს ({MAX_ENTRIES}).")
        print("გენერაცია შეწყდება MAX_ENTRIES მიღწევის შემდეგ.")
    else:
        print("სავარაუდო რაოდენობა ლიმიტშია ან ლიმიტი გამორთულია.")

    written = 0
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for k in range(MIN_K, min(MAX_K, n) + 1):
            print(f"ვქმნი {k}-სიტყვიან კომბინაციებს...")
            for perm in permutations(words, k):
                variant_lists = [per_word_cases[w] for w in perm]
                for case_combo in product(*variant_lists):
                    base = "".join(case_combo)
                    for pref in PREFIXES:
                        for suf in SUFFIXES:
                            final = f"{pref}{base}{suf}"
                            out.write(final + "\n")
                            written += 1
                            if MAX_ENTRIES is not None and written >= MAX_ENTRIES:
                                print(f"მიღწეულია ლიმიტი ({MAX_ENTRIES}). გენერაცია დასრულდა.")
                                print(f"ჯამში ჩაწერილია {written} ხაზი ფაილში: {OUTPUT_FILE}")
                                return
            print(f"{k}-სიტყვიანი კომბინაციები დასრულდა. ჯამში ჩაწერილია: {written}")
    print(f"დასრულდა! სულ ჩაწერილია {written} ხაზი ფაილში: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()