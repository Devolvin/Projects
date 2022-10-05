import nltk
import string
import math
import html


def calculate_tfidf(posts: list, q):
    def tokenize(text):
        punct = string.punctuation
        stopwords = nltk.corpus.stopwords.words("english")
        word_list = nltk.word_tokenize(text.lower())
        word_list = [word for word in word_list if
                     not all(letter in punct for letter in word) and word not in stopwords]
        return word_list

    def compute_idf(texts_dict):
        frequency_dict = dict()
        idf_dict = dict()

        for text in texts_dict:
            for word in set(texts_dict[text]):
                if word not in frequency_dict.keys():
                    frequency_dict[word] = 1
                else:
                    frequency_dict[word] += 1

        for word in frequency_dict:
            idf_dict[word] = math.log(len(texts_dict) / frequency_dict[word]) + 1

        return idf_dict

    def top_post(query, posts_words, idfs):

        tfidfs = dict()

        for post in posts_words:
            tfidfs[post] = 0
            for query_word in query:
                tf = posts_words[post].count(query_word)
                if tf:
                    tfidfs[post] += tf * idfs[query_word]

        return max(tfidfs, key=lambda key: tfidfs[key])

    def top_sentence(query, sentences, idfs):

        match_measure = dict()
        for sentence in sentences:
            match_measure[sentence] = [0, 0]
            count = 0
            length = len(sentences[sentence])
            for word in query:
                if word in sentences[sentence]:
                    match_measure[sentence][0] += idfs[word]
                    count += 1
            match_measure[sentence][1] = count / length

        return list(max((match_measure.items()), key=lambda x: (x[1][0], x[1][1])))

    post_dict = {
        post: html.unescape(post.body) for post in posts
    }

    post_words = dict()
    for post in posts:
        tokens = tokenize(html.unescape(post.body))
        post_words[post] = tokens

    post_idfs = compute_idf(post_words)

    query = set(tokenize(html.unescape(q)))

    searched_post = top_post(query, post_words, post_idfs)

    sentences = dict()
    for passage in post_dict[searched_post].split("\n"):
        for sentence in nltk.sent_tokenize(passage):
            tokens = tokenize(sentence)
            if tokens:
                sentences[sentence] = tokens

    idfs = compute_idf(sentences)

    searched_sentence = top_sentence(query, sentences, idfs)
    return [searched_post, searched_sentence]