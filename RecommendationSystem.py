
# coding: utf-8

# In[1]:

from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import urllib.request
import zipfile

def download_data():
    """ DONE. Download and unzip data.
    """
    url = 'https://www.dropbox.com/s/h9ubx22ftdkyvd5/ml-latest-small.zip?dl=1'
    urllib.request.urlretrieve(url, 'ml-latest-small.zip')
    zfile = zipfile.ZipFile('ml-latest-small.zip')
    zfile.extractall()
    zfile.close()


def tokenize_string(my_string):
    """ DONE. You should use this in your tokenize function.
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    Append a new column to the movies DataFrame with header 'tokens'.
    This will contain a list of strings, one per token, extracted
    from the 'genre' field of each movie. Use the tokenize_string method above.
    Note: you may modify the movies parameter directly; no need to make
    a new copy.
    Params:
      movies...The movies DataFrame
    Returns:
      The movies DataFrame, augmented to include a new column called 'tokens'.
    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    ###TODO
    pass

    token = []
    for g in movies["genres"]:
        token.append(tokenize_string(g))
    movies['tokens'] = pd.Series(np.array(token), movies.index)
    return movies




def featurize(movies):
    """
    Append a new column to the movies DataFrame with header 'features'.
    Each row will contain a csr_matrix of shape (1, num_features). Each
    entry in this matrix will contain the tf-idf value of the term, as
    defined in class:
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document (movie)
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents (movies)
    df(i) is the number of unique documents containing term i
    Params:
      movies...The movies DataFrame
    Returns:
      A tuple containing:
      - The movies DataFrame, which has been modified to include a column named 'features'.
      - The vocab, a dict from term to int. Make sure the vocab is sorted alphabetically as in a2 (e.g., {'aardvark': 0, 'boy': 1, ...})
    """
    ###TODO
    pass
    
    f_list = list(defaultdict(lambda: 0))
    f_freq = defaultdict(lambda: 0)
    
    for tks in movies['tokens']:
        tkset = set(tks)
        for e in tkset:     
            f_freq[e] += 1
        f_dict = defaultdict(lambda: 0)
        for tk in tks:      
            f_dict[tk] += 1
        f_list.append(f_dict)


    allfeatures = sorted(f_freq)
    vocab = dict((k, allfeatures.index(k)) for k in allfeatures)

    feature_csr_matrix_list = []

    N = movies.shape[0]
    for i in range(N):
        doc_feat = f_list[i]
        maxk = doc_feat[max(doc_feat, key = doc_feat.get)]
        row = []
        col = []
        data = []
        for k in doc_feat:
            if k  in vocab:
                row.append(0)
                col.append(vocab[k])
                tfidf = doc_feat[k] / maxk * np.log(N / f_freq[k])
                data.append(tfidf)
        doc_csr_matrix = csr_matrix((data, (row, col)), shape = (1, len(vocab)))
        feature_csr_matrix_list.append(doc_csr_matrix)

    movies['features'] = pd.Series(feature_csr_matrix_list, movies.index)

    return movies, vocab



def train_test_split(ratings):
    """DONE.
    Returns a random split of the ratings matrix into a training and testing set.
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]


def cosine_sim(a, b):
    """
    Compute the cosine similarity between two 1-d csr_matrices.
    Each matrix represents the tf-idf feature vector of a movie.
    Params:
      a...A csr_matrix with shape (1, number_features)
      b...A csr_matrix with shape (1, number_features)
    Returns:
      The cosine similarity, defined as: dot(a, b) / ||a|| * ||b||
      where ||a|| indicates the Euclidean norm (aka L2 norm) of vector a.
    """
    ###TODO
    pass

    n = np.dot(a.toarray(),b.toarray().T)
    d =np.linalg.norm(a.toarray()) * np.linalg.norm(b.toarray())
    return n[0][0]/d






def make_predictions(movies, ratings_train, ratings_test):
    """
    Using the ratings in ratings_train, predict the ratings for each
    row in ratings_test.
    To predict the rating of user u for movie i: Compute the weighted average
    rating for every other movie that u has rated.  Restrict this weighted
    average to movies that have a positive cosine similarity with movie
    i. The weight for movie m corresponds to the cosine similarity between m
    and i.
    If there are no other movies with positive cosine similarity to use in the
    prediction, use the mean rating of the target user in ratings_train as the
    prediction.
    Params:
      movies..........The movies DataFrame.
      ratings_train...The subset of ratings used for making predictions. These are the "historical" data.
      ratings_test....The subset of ratings that need to predicted. These are the "future" data.
    Returns:
      A numpy array containing one predicted rating for each element of ratings_test.
    """
    ###TODO
    pass

    predicted = []
    ratings = []
    for index, row in ratings_test.iterrows():
        m_id = row['movieId']
        u_id = row['userId']
        sum_sim = 0.
        weighted_rating = 0.
        feature = movies.loc[movies.movieId == m_id].squeeze()['features']
        other_movies = ratings_train.loc[ratings_train.userId == u_id]
        all_neg = True
        for u_index, u_row in other_movies.iterrows():
            c_sim = cosine_sim(feature, movies.loc[movies.movieId == u_row['movieId']].squeeze()['features'])
            if c_sim > 0:
                weighted_rating += c_sim * u_row['rating']
                sum_sim += c_sim
                all_neg = False
        if all_neg == True:
            ratings.append(other_movies['rating'].mean())
        else:
            ratings.append(weighted_rating / sum_sim)

    return np.array(ratings)


def mean_absolute_error(predictions, ratings_test):
    """DONE.
    Return the mean absolute error of the predictions.
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()


def main():
    download_data()
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test)
    print('error=%f' % mean_absolute_error(predictions, ratings_test))
    print(predictions[:10])


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:



