from summarization.summarize import *
from summarization import optimize

text = """
Gary Danko is a 5 star experience. 

Fantastic service and amazing food. My wife and I each did the 5-course pri fix tasting menu and it was plenty of food maybe too much. The whole experience takes about 3 hours. Make reservations months in advance. All the accolades for Gary Danko, they are deserved. Probably the best fine dining restaurant in San Francisco.

Had the best dinner with my nine year old daughter. We had the tasting menu and every dish was perfection. I highly reccomend the lobster dish, the bass, the beef tenderloin and the rissoto. For dessert the butter cake is Insanely good! 
One of the highlights of the entire trip. The staff and server Juan Carlos could not have been better. Made our evening just perfect.

Brought my bf here for his birthday. We had 5 courses for $111 per person (wine not included but good thing we aren't drinkers). Any 5 dishes you choose (stack 'em or mix and match choosing from appetizers, main courses and desserts. ALL of the dishes that were served were excellent in flavor and their portion size is great. Perfectly prepared and they have great service. Oh and you HAVE to try their chocolate souffle.

This is the only few Michelin star restaurants in SF that are open on Monday. Came here for my partner 50th Birthday celebration. Great location and friendly/classy services that suits the stuffy neighborhood.

So, they were informed that its a Birthday celebration. They asked us to order our individual dessert, then they came with another "birthday" dessert... Yes, we have 3 plates of dessert, WTH? Just didnt make sense...

In short, Gary Danko is stuck in the 1990's with traditional, uninspired cuisine!
"""

name = 'Gary Danko'

def test_get_sentiments():
    overall_sentiment, sentence_dataset = get_attributes(text, name)
    assert overall_sentiment > 0.0
    for sentence in sentence_dataset:
        # Check for all required keys in each sentence dict
        assert sentence['sentence']
        assert isinstance(sentence['sentiment'], float)
        assert isinstance(sentence['sentiment_magnitude'], float)

def test_cull_sentences():
    overall_sentiment, sentence_dataset = get_attributes(text, name)
    for sentence in sentence_dataset:
        assert sentence['sentiment_magnitude'] >= 0.2
    #culled_sentences2 = cull_sentences(sentence_dataset, 0.5)
    #for sentence in culled_sentences2:
    #    assert sentence['sentiment_magnitude'] > 0.5

def test_get_keypoints():
    key_points = get_keypoints(text, name)
    assert len(key_points) == optimize.NUM_KEY_POINTS