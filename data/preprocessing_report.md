# CE49X Final Project - Task 2: Text Preprocessing Report

## Preprocessing Summary

- **Total Articles Processed:** 1155
- **Preprocessing Steps:**
  1. Tokenization
  2. Normalization (lowercasing, punctuation removal)
  3. Stopword Removal
  4. Lemmatization (where applicable)
  5. N-gram Extraction

---

## Top 20 Most Frequent Words (Excluding Stopwords)

| Rank | Word | Frequency |
|------|------|-----------|
| 1 | market | 598 |
| 2 | data | 451 |
| 3 | 2025 | 451 |
| 4 | highlights | 413 |
| 5 | technology | 395 |
| 6 | discusses | 394 |
| 7 | importance | 392 |
| 8 | industry | 359 |
| 9 | growth | 337 |
| 10 | global | 329 |
| 11 | new | 307 |
| 12 | billion | 299 |
| 13 | significant | 298 |
| 14 | intelligence | 280 |
| 15 | energy | 248 |
| 16 | 2026 | 243 |
| 17 | development | 234 |
| 18 | infrastructure | 226 |
| 19 | future | 225 |
| 20 | technologies | 222 |

---

## Top 20 Bi-grams

| Rank | Bigram | Frequency |
|------|--------|-----------|
| 1 | artificial intelligence | 203 |
| 2 | data center | 97 |
| 3 | usd billion | 96 |
| 4 | data centers | 93 |
| 5 | highlights importance | 79 |
| 6 | dec 2025 | 79 |
| 7 | market size | 75 |
| 8 | machine learning | 60 |
| 9 | 2025 globe | 58 |
| 10 | globe newswire | 58 |
| 11 | emphasizing importance | 55 |
| 12 | supply chain | 52 |
| 13 | real time | 51 |
| 14 | signifies significant | 49 |
| 15 | emphasizes importance | 48 |
| 16 | market projected | 47 |
| 17 | deep learning | 45 |
| 18 | shift towards | 44 |
| 19 | decision making | 42 |
| 20 | technological advancements | 42 |

---

## Notes

- Stopwords removed: Common English stopwords (the, a, an, and, or, etc.) and domain-specific noise words (article, read, more, click, etc.)
- Words with length <= 2 characters were excluded
- Bigrams are consecutive word pairs in the processed text
- All text was normalized to lowercase before processing

---

**Generated:** Task 2 - Text Preprocessing & NLP
**Course:** CE49X - Introduction to Data Science for Civil Engineering
