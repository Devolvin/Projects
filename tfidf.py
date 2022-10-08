import nltk
import string
import math
import html


class Tfidf_Calculator():
    def __init__(self,posts):
        self.post_dict = dict()
        self.post_words = dict()
        for post in posts:
            post.body = post.body.replace("\r\n", "")
            if post.body[:3] == "<p>":
                post.body = post.body[3:]
            if post.body[-4:] == "</p>":
                post.body = post.body[:-4]
            self.post_dict[post.id] = html.unescape(post.body)
            self.post_words[post.id] = self.tokenize(html.unescape(post.body))
        self.post_idfs = self.compute_idf(self.post_words)


    def tokenize(self,text):
        punct = string.punctuation
        stopwords = nltk.corpus.stopwords.words("english")
        word_list = nltk.word_tokenize(text.lower())
        word_list = [word for word in word_list if
                     not all(letter in punct for letter in word) and word not in stopwords]
        return word_list

    def compute_idf(self,texts_dict):
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

    def top_post(self,query, posts_words, idfs):

        tfidfs = dict()

        for post in posts_words:
            tfidfs[post] = 0
            for query_word in query:
                tf = posts_words[post].count(query_word)
                if tf:
                    tfidfs[post] += tf * idfs[query_word]

        return max(tfidfs, key=lambda key: tfidfs[key])

    def top_sentence(self, query, sentences, idfs):

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
        # print(match_measure)
        return list(max((match_measure.items()), key=lambda x: (x[1][0], x[1][1])))

    def find_post_and_sentence(self,q):
        query = set(self.tokenize(html.unescape(q)))
        searched_post = self.top_post(query,self.post_words,self.post_idfs)
        sentences = dict()
        for passage in self.post_dict[searched_post].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = self.tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens
        sentence_idfs = self.compute_idf(sentences)
        searched_sentence = self.top_sentence(query, sentences, sentence_idfs)
        return [searched_post, searched_sentence]

    def recalculate_tfidf(self,posts):
        for post in posts:
            post.body = post.body.replace("\r\n", "")
            if post.body[:3] == "<p>":
                post.body = post.body[3:]
            if post.body[-4:] == "</p>":
                post.body = post.body[:-4]
            self.post_dict[post.id] = html.unescape(post.body)
            self.post_words[post.id] = self.tokenize(html.unescape(post.body))
        self.post_idfs = self.compute_idf(self.post_words)