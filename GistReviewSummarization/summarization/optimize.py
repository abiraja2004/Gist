import math
import sys
import os

from optimal import genalg
from optimal import gahelpers
from optimal import gsa

import pyswarm

NUM_KEY_POINTS = 3

class NotEnoughSentencesError(Exception):
    pass

def get_fitness(indexes, sentence_dataset, overall_sentiment, minimize=False):
        """Determine the fitness of some potential key points."""
        # If any index is invalid or repeated
        # return a very low fitness
        dataset_length = len(sentence_dataset)
        for i in range(len(indexes)):
            # If index is out of range
            if indexes[i] > dataset_length-1 or indexes[i] < 0:
                if minimize:
                    return 9999999
                return 0.000001
            # If index is repeated
            if indexes[i] in indexes[i+1:]:
                if minimize:
                    return 9999999
                return 0.000001

        # Get the potential key points from the dataset
        key_points = [sentence_dataset[index] for index in indexes]

        # Get avg sentiment and magnitude
        # avg sentiment is normalized so the closeness metric doesn't bias exteme sentiments
        # sentiment_magnitude is normalized, so it isn't given greater weight with more key points
        avg_sentiment = sum([key_point['sentiment'] for key_point in key_points])/NUM_KEY_POINTS
        sentiment_magnitude = sum([key_point['sentiment_magnitude'] for key_point in key_points])/NUM_KEY_POINTS
        magnitude_score = sentiment_magnitude*2 # A little important

        # Calculate sentiment closeness attribute
        # The value ranges from 1.0 to 0.0, 1.0 being the closest
        sentiment_closeness = 1.0/(((overall_sentiment-avg_sentiment)**2)+1)
        closeness_score = sentiment_closeness*15 # Very important

        # Get relevance scores
        name_score = key_point['name_score'] # Not too imporant
        length_score = key_point['length_score'] # Not too important
        rel_score = key_point['relevance']*5 # Also important

        # Calculate fitness
        # Fitness if a function of how close the sum of fitness is to the overall fitness
        # and the magnitude of the sentiments
        fitness = closeness_score+magnitude_score+name_score+length_score+rel_score

        # Minimize for pyswarm, if necessary
        if minimize:
            return 1.0/fitness
        return fitness

def decode_chromosome(chromosome, binary_index_size):
        """Turn a binary chromosome into indexes for the dataset."""
        #NOTE: this encoding may be problematic with large datasets
        #because there will be a large number of invalid indexes
        indexes = []
        #for every chunk in the chromosome of size "binary_index_size"
        for i in range(0, len(chromosome), binary_index_size):
            #take a chunk from the chromosome of size "binary_index_size", starting at i
            #turn the chunk into an int, and add it as an index
            indexes.append(gahelpers.binary_to_int(chromosome[i:i+binary_index_size], 0))
        return indexes

def get_binary_index_size(dataset_length):
    #determine the size of 1/Nth of the chromosome
    #len = 2^b
    return int(math.ceil(math.log(dataset_length, 2)))

def genalg_optimizer(sentence_dataset, overall_sentiment):
    """Optimize using a genetic algorithm"""

    dataset_length = len(sentence_dataset)
    binary_index_size = get_binary_index_size(dataset_length)
    chromosome_size = binary_index_size*NUM_KEY_POINTS

    def genalg_fitness(chromosome, binary_index_size, **kwargs):
        indexes = decode_chromosome(chromosome, binary_index_size)
        return get_fitness(indexes, **kwargs)

    #optimize to find the best key points
    optimizer = genalg.GenAlg(genalg_fitness, chromosome_size, 
                              sentence_dataset=sentence_dataset,
                              overall_sentiment=overall_sentiment,
                              binary_index_size=binary_index_size)
    return optimizer

def genalg_keypoints(sentence_dataset, overall_sentiment):
    optimizer = genalg_optimizer(sentence_dataset, overall_sentiment)

    optimizer.logging = False #disble output logging to avoid spamming the console, enable for debugging
    best_chromosome = optimizer.optimize()

    #return the best indexes
    return decode_chromosome(best_chromosome, 
                             optimizer.additional_parameters['binary_index_size'])

def decode_floats(raw_indexes, ceil=False):
        """Turn a binary chromosome into indexes for the dataset."""
        if ceil:
            return [int(math.ceil(i)) for i in raw_indexes]
        return [int(i) for i in raw_indexes]

def decode_floats_best(raw_indexes):
    decimals = [raw_index-int(raw_index) for raw_index in raw_indexes]
    avg_decimal = sum(decimals)/len(decimals)

    if avg_decimal > 0.5:
        return decode_floats(raw_indexes, True)
    else:
        return decode_floats(raw_indexes, False)

def pso_gsa_fitness(raw_indexes, **kwargs):
    indexes_high = decode_floats(raw_indexes, True)
    indexes_low = decode_floats(raw_indexes, False)

    decimals = [raw_index-int(raw_index) for raw_index in raw_indexes]
    avg_decimal = sum(decimals)/len(decimals)

    high_fitness = avg_decimal*get_fitness(indexes_high, **kwargs)
    low_fitness = (1.0-avg_decimal)*get_fitness(indexes_low, **kwargs)
    return high_fitness+low_fitness

def pso_optimizer(sentence_dataset, overall_sentiment):
    """Return a function that will optimize with pso when called."""
    index_lower_bounds = [0]*NUM_KEY_POINTS
    index_upper_bounds = [len(sentence_dataset)+1]*NUM_KEY_POINTS   

    #optimize to find the best key points
    kwargs = {'sentence_dataset': sentence_dataset, 
              'overall_sentiment': overall_sentiment, 'minimize': True}
    def optimizer():
        return pyswarm.pso(pso_gsa_fitness, index_lower_bounds, index_upper_bounds, 
                                 kwargs=kwargs, swarmsize=20)
    return optimizer

def pso_keypoints(sentence_dataset, overall_sentiment):
    """Optimize using particle swarm optimization."""

    optimizer = pso_optimizer(sentence_dataset, overall_sentiment)
    
    # Supress pyswarm outputs
    actual_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')

    # Optimize
    raw_indexes, _ = optimizer()

    # Re enable print
    sys.stdout = actual_stdout

    #return the key points
    return decode_floats_best(raw_indexes)

def gsa_optimizer(sentence_dataset, overall_sentiment):
    index_lower_bounds = [0]*NUM_KEY_POINTS
    index_upper_bounds = [len(sentence_dataset)+1]*NUM_KEY_POINTS

    #optimize to find the best key points
    optimizer = gsa.GSA(pso_gsa_fitness, NUM_KEY_POINTS, index_lower_bounds, index_upper_bounds,
                        sentence_dataset=sentence_dataset,
                        overall_sentiment=overall_sentiment, minimize=False)
    return optimizer

def gsa_keypoints(sentence_dataset, overall_sentiment):
    """Optimize using gravitational search algorithm."""
    optimizer = gsa_optimizer(sentence_dataset, overall_sentiment)
    optimizer.logging = False
    raw_indexes = optimizer.optimize()

    #return the key points
    return decode_floats_best(raw_indexes)

def optimize_keypoints(sentence_dataset, overall_sentiment, algorithm=genalg_keypoints):
    """Given a dataset of sentences, return the N sentences that best describe the product."""
    
    if len(sentence_dataset) < NUM_KEY_POINTS:
        raise NotEnoughSentencesError("Not enough sentences. {0} sentences in sentence_dataset.".format(len(sentence_dataset)))

    indexes = algorithm(sentence_dataset, overall_sentiment)

    return [sentence_dataset[index] for index in indexes]