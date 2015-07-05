#########################
# Written By: Chad Clough
#########################

import textblob
from textblob import TextBlob
from collections import Counter
import math
import corpus
import logging
import string
import re
    
def length_score(sentence):
    '''
        Scores the length of a sentence based upon elite yelp reviews
        
        Args:
            sentence: The sentence to calculate the lengthScore of

        Returns:
            float; The score of the sentence in the range [0, 1] where 1 is
                optimal
    '''
    optimalLength = 15 #15.4 actual
    variance = 24.8
    
    length = len(sentence.split(' '))
    
    #e^-((len-15)^2/24.8)
    return gaussian(math.fabs(length-optimalLength), variance) 
    
def remove_punc(sentence):
    return sentence.translate(string.maketrans("", ""), string.punctuation)
    
def name_score(sentence, name):
    '''
        Scores the relevance of a sentence to the name of the product/service

        Args:
            sentence: The sentence to calculate the nameScore of
            name: The name of the good/service

        Returns:
            float; The score of the sentence in the range [0, 1] where 1 is
                optimal
    '''
    if name in sentence:
        return 1;

    partsOfName = name.split(' ')
    length = len(partsOfName)

    numParts = 0
    for word in partsOfName:
        if word in sentence:
            numParts += 1

    if numParts == length:
        #Give less weight to sentences that don't explicitly say the name
        return (numParts - 0.5) / float(length); 
    elif numParts > 0:
        return numParts / float(length);

    return 0;


def gaussian(x, variance):
    return math.exp(-(x**2/variance))

def get_words(text):
    return re.findall(r"[\w']+", text.lower())

def tf(document):
    '''
        Generates a Term Frequency dictionary with the 
    '''
    words = get_words(document)
    
    #count the terms
    tf_dict = Counter(word for word in words)
    tf_dict = {a: b for a, b in tf_dict.most_common()}
    
    #normalize the dictionary
    for key in tf_dict:
        tf_dict[key] = tf_dict[key] / float(len(words))
        
    return tf_dict

def idf(term):
    '''
        Finds the pre-calculated Inverse Document Frequency value of
        a term.
        
        Args:
            term: The term we're looking to find the idf of
            
        Returns:
            float; The pre-calculated idf value of term. If term is
                not found then it will return the default idf score
    '''
    try:
        return corpus.corpus[term]
    except KeyError:
        return corpus.corpus['']; #term not found
    


def tfidf(document):
    '''
        Creates a dictionary of terms with tfidf scores
        
        Args:
            document: The document to be analysed 
    '''
    tfidf_dict = tf(document)

    for key in tfidf_dict:
        tfidf_dict[key] = tfidf_dict[key] * idf(key)
    
    return tfidf_dict;
 
def rel_score(tfidf_dict, sentence):
    score = 0.0;
    #use textblob instead
    words = get_words(sentence)
    for word in words:
        try:
            score = score + tfidf_dict[word]
        except:
            try:
                logging.warning('Term not found in tfidf dict: {}'.format(word))
            except:
                logging.warning('Term not found in tfidf dict')
            
    score = score / len(words)
    
    return score;
    
#TODO: Create main function to go from start to finish   
   
if __name__ == '__main__':
    s =  '''
        STOP. Before you walk into this shop thinking that you're going to walk 
        away with a lovely cup of cappuccino, walk back over to Hanover to the 
        Thinking Cup or Caffe Vittoria because they sell coffee...beans. Coffee
        beans, not the drink. 

        Upon walking into the store, your nostrils are flooded with the wonderful 
        aroma of coffee beans & teas adorned all around the store. That's right 
        folks, not just coffee, but loose leaf tea too! The prices are so affordable 
        that you might feel like tipping them extra money because you feel bad for
        practically stealing from them. Coffee, candy, loose leaf tea, spices, & 
        Sriracha, this place is a spice collector's dream. Various types of flour 
        are carried here & are so reasonable that I might have to come back with my
        dorky grocery cart on wheels to wheel away 2 oz of every spice they have! 
        From paprika to oregano to curry to chamomile to amaretto coffee, they've 
        got tons of items. Beyonce wrote "Crazy in Love" about Polcari's, not about
        Jay-Z. 

        Whether you need a gift for your sister, mother, father, brother, aunt, uncle,
        cousin, boyfriend/girlfriend, spouse, daughter, son, WHOMEVER, just stop by 
        here. Only a spoiled snob wouldn't appreciate the kind gesture of delicious 
        coffee beans or loose leaf tea. Yeah, I could get you an iPad for your 
        birthday, or I could buy you diabetes in the form of candy & antioxidants 
        in the form of coffee & tea, sooooo what's it gonna be? I pick the things 
        that make you less cranky in the morning.
    '''
    s2 = """From paprika to oregano to curry to chamomile to amaretto coffee, they've 
        got tons of items."""
    s3 = """My spouse carried a lovely iPad to this place."""
    s = s.lower()
    s2 = s2.lower()
    s3 = s3.lower()
    dict = tfidf(s)
    #dict = sorted(dict.items(), key=lambda x: x[1])
    print rel_score(dict, s2)
    print rel_score(dict, s3)