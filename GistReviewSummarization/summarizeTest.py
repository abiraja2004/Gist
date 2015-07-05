#############################
# Written By: Justin Lovinger
#############################

import textblob
import math
import re
import yelpreviewscraper

from optimal import genalg
from optimal import gahelpers

NUM_KEY_POINTS = 3
LINE_ENDERS = r'\.\n\!\?'

def text_to_sentences(text):
    """Convert a block of text into individual sentences."""
    #use regular expression to extract sentences
    #a sentence starts with a non-whitespace, non-line-ender character
    #continues with any number of non-line-ender characters
    #then ends with a line-ender character
    sentences = re.findall(r'[^\s{0}][^{0}]*[{0}]'.format(LINE_ENDERS), text)
    return sentences

def get_sentiments(text):
    """Get the overall sentiment of a block of text, and the sentiment of every sentence"""
    blob = textblob.TextBlob(text)

    overall_sentiment = blob.sentiment.polarity

    sentence_dataset = []
    for sentence in text_to_sentences(text):
        sentence_blob = textblob.TextBlob(sentence)

        data_point = {'sentence': sentence}
        data_point['sentiment'] = sentence_blob.sentiment.polarity #get sentiment with textblob
        data_point['sentiment_magnitude'] = math.fabs(data_point['sentiment']) #absolute value of sentiment

        sentence_dataset.append(data_point)

    return overall_sentiment, sentence_dataset

def cull_sentences(sentence_dataset):
    """Remove sentences with poor attributes, and return the new dataset.

    The origional dataset is unmodified.
    """
    culled_dataset = []
    #iterate over every data point in the dataset
    #add data points that pass all requirements to the culled dataset
    for data_point in sentence_dataset:
        if data_point['sentiment_magnitude'] > 0.2:
            culled_dataset.append(data_point)
    return culled_dataset

def optimize_keypoints(sentence_dataset, overall_sentiment):
    """Given a dataset of sentences, return the N sentences that best describe the product."""

    dataset_length = len(sentence_dataset)
    #determine the size of 1/Nth of the chromosome
    #len = 2^b
    binary_index_size = int(math.ceil(math.log(dataset_length, 2)))

    chromosome_size = binary_index_size*NUM_KEY_POINTS
    def decode_chromosome(chromosome):
        """Turn a binary chromosome into indexes for the dataset."""
        #NOTE: this encoding may be problematic with large datasets
        #because there will be a large number of invalid indexes
        indexes = []
        #for every chunk in the chromosome of size "binary_index_size"
        for i in range(0, chromosome_size, binary_index_size):
            #take a chunk from the chromosome of size "binary_index_size", starting at i
            #turn the chunk into an int, and add it as an index
            indexes.append(gahelpers.binary_to_int(chromosome[i:i+binary_index_size], 0))
        return indexes

    def get_fitness(chromosome):
        """Determine the fitness of some potential key points."""
        indexes = decode_chromosome(chromosome)
        #if any index is invalid or repeated
        #return a very low fitness
        for i in range(len(indexes)):
            #if index is out of range
            if indexes[i] > dataset_length-1:
                return 0.000001
            #if index is repeated
            if indexes[i] in indexes[i+1:]:
                return 0.000001

        #get the potential key points from the dataset
        key_points = [sentence_dataset[index] for index in indexes]

        total_sentiment = sum([key_point['sentiment'] for key_point in key_points])
        sentiment_magnitude = sum([key_point['sentiment_magnitude'] for key_point in key_points])

        #calculate fitness
        #fitness if a function of how close the sum of fitness is to the overall fitness
        #and the magnitude of the sentiments
        sentiment_closeness = 1.0/(((overall_sentiment-total_sentiment)**2)+1)
        fitness = sentiment_closeness*10+sentiment_magnitude

        return fitness

    #optimize to find the best key points
    optimizer = genalg.GenAlg(get_fitness, chromosome_size)
    optimizer.logging = False #disble output logging to avoid spamming the console, enable for debugging
    best_chromosome = optimizer.run_genalg()

    #return the key points
    indexes = decode_chromosome(best_chromosome)
    return [sentence_dataset[index] for index in indexes]


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


if __name__ == '__main__':
    text = yelpreviewscraper.get_reviews('http://www.yelp.com/biz/slainte-irish-pub-new-bedford')

    sentences = text_to_sentences(text)
    for sentence in sentences:
        print sentence
        print '-----------------------'

    overall_sentiment, sentence_dataset = get_sentiments(text)
    #write_output(sentence_dataset, overall_sentiment)

    culled_dataset = cull_sentences(sentence_dataset)
    #write_output(culled_dataset, output_file_name = 'culled_sentiments.txt')

    key_points = optimize_keypoints(culled_dataset, overall_sentiment)
    print key_points
    for key_point in key_points:
        print key_point['sentence']