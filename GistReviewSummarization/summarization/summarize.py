#############################
# Written By: Justin Lovinger, 
#             Chad Clough
#############################

import textblob
import math
import re

import optimize

from relevance import relevance

LINE_ENDERS = r'\.\n\!\?'

def text_to_sentences(text):
    """Convert a block of text into individual sentences.

    >>> text_to_sentences("sentence1. sentence2. sentence3.")
    ['sentence1.', 'sentence2.', 'sentence3.']
    """
    #use regular expression to extract sentences
    #a sentence starts with a non-whitespace, non-line-ender character
    #continues with any number of non-line-ender characters
    #then ends with a line-ender character
    sentences = re.findall(r'[^\s{0}][^{0}]*[{0}]'.format(LINE_ENDERS), text) 
    return sentences

def add_sentiment(data_point, **kwargs):
    sentence_blob = textblob.TextBlob(data_point['sentence'])

    # Get sentiment with textblob
    data_point['sentiment'] = sentence_blob.sentiment.polarity 
    # Absolute value of sentiment
    data_point['sentiment_magnitude'] = math.fabs(data_point['sentiment'])

def cull_sentiment(data_point, min_sentiment=0.2):
    return (data_point['sentiment_magnitude'] < min_sentiment)

def add_name_score(data_point, **kwargs):
    # Function expects "name" keyword
    data_point['name_score'] = relevance.name_score(data_point['sentence'], kwargs['name'])

def add_relevance_score(data_point, **kwargs):
    # Function expects "tfidf_dict" keyword
    data_point['relevance'] = relevance.rel_score(kwargs['tfidf_dict'], data_point['sentence'])

def add_length_score(data_point, **kwargs):
    data_point['length_score'] = relevance.length_score(data_point['sentence'])

def cull_length_score(data_point, min_length=0.007):
    return data_point['length_score'] < min_length

# Each function represents one or more attributes for a sentence data point
attribute_funcs = [
                   {'get': add_length_score, 'cull': cull_length_score},
                   {'get': add_sentiment, 'cull': cull_sentiment},
                   {'get': add_name_score},
                   {'get': add_relevance_score},
                   ]

def get_attributes(text, name):
    """Get and cull on attributes for every sentence
    
    Args:
        text: Every review for a product in a single string.

    Returns:
        float; The overall sentiment of the product.
        list; A list of dictionaries that contains sentences and their features.
    """
    blob = textblob.TextBlob(text)

    overall_sentiment = blob.sentiment.polarity

    #go through every sentence in a block of text
    #and extract features from the sentences
    #store sentences and features in a list of dictionaries
    sentence_dataset = []
    tfidf_dict = relevance.tfidf(text)
    
    for sentence in text_to_sentences(text):
        data_point = {'sentence': sentence}
        # Add and cull attributes using our attribute function list
        for attribute_func in attribute_funcs:
            # First add the attribute directly to the dict
            attribute_func['get'](data_point, name=name, tfidf_dict=tfidf_dict)
            # Then attempt to cull
            try:
                # Cull functions return True when they cull, False when they don't
                culled = attribute_func['cull'](data_point)
            except KeyError: # Not all attributes have a cull function
                culled = False
            if culled:
                # No need to keep calculating attributes
                break
        if not culled:
            # Sentence made it through all the cull steps
            sentence_dataset.append(data_point)

    return overall_sentiment, sentence_dataset

def write_output(sentence_dataset, overall_sentiment=None, output_file_name='sentiments.txt'):
    """Write output to local hardrive.

    This will not function on a server.
    """
    output_file = open(output_file_name, 'w')

    if overall_sentiment != None:
        output_file.write('Overall Sentiment: {}\n'.format(overall_sentiment))
    for data_point in sentence_dataset:
        output_file.write('{} ({})\n'.format(data_point['sentence'], data_point['sentiment']))

    output_file.close()


def get_keypoints(text, name):
    """Process a set of reviews and return key points.

    This is a helper function that calls the primary functions of this module.
    """

    overall_sentiment, sentence_dataset = get_attributes(text, name)
    key_points_dicts = optimize.optimize_keypoints(sentence_dataset, overall_sentiment)
    key_points = [key_point_dict['sentence'] for key_point_dict in key_points_dicts]
    return key_points

if __name__ == '__main__':
    import pprint

    text = u"""
    Gary Danko is a 5 star experience. 

    Fantastic service and amazing food. My wife and I each did the 5-course pri fix tasting menu and it was plenty of food maybe too much. The whole experience takes about 3 hours. Make reservations months in advance. All the accolades for Gary Danko, they are deserved. Probably the best fine dining restaurant in San Francisco.

    Had the best dinner with my nine year old daughter. We had the tasting menu and every dish was perfection. I highly reccomend the lobster dish, the bass, the beef tenderloin and the rissoto. For dessert the butter cake is Insanely good! 
    One of the highlights of the entire trip. The staff and server Juan Carlos could not have been better. Made our evening just perfect.

    Brought my bf here for his birthday. We had 5 courses for $111 per person (wine not included but good thing we aren't drinkers). Any 5 dishes you choose (stack 'em or mix and match choosing from appetizers, main courses and desserts. ALL of the dishes that were served were excellent in flavor and their portion size is great. Perfectly prepared and they have great service. Oh and you HAVE to try their chocolate souffle.

    This is the only few Michelin star restaurants in SF that are open on Monday. Came here for my partner 50th Birthday celebration. Great location and friendly/classy services that suits the stuffy neighborhood.

    So, they were informed that its a Birthday celebration. They asked us to order our individual dessert, then they came with another "birthday" dessert... Yes, we have 3 plates of dessert, WTH? Just didnt make sense...

    In short, Gary Danko is stuck in the 1990's with traditional, uninspired cuisine!
    """
    
    sentences = text_to_sentences(text)
    for sentence in sentences:
        print sentence
        print '-----------------------'

    overall_sentiment, sentence_dataset = get_attributes(text, "Gary Danko")
    print overall_sentiment
    pprint.pprint(sentence_dataset)
    #write_output(sentence_dataset, overall_sentiment)

    key_points = optimize.optimize_keypoints(sentence_dataset, overall_sentiment, 
                                             algorithm=optimize.genalg_keypoints)
    print key_points
    for key_point in key_points:
        print key_point['sentence'] 
