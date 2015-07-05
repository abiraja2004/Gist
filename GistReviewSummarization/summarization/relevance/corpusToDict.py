import argparse
import csv
import math

def idf(total, count):
    return math.log(total/count)

def import_corpus(filepath):
    '''
    
    '''
    corpus = {}
    csvfile = open(filepath, 'rb') 
    try:
        reader = list(csv.reader(csvfile))
        
        for row in reader[1:]:
            # If this is our first time encountering this word
            # initialize it with 0.0
            key = decode(row[0])
            try:
                corpus[key]
            except KeyError:
                corpus[key] = 0.0
               
            # Every other time we see this word, add its count
            try:
                corpus[key] += float(row[3])# / theCount
            except (IndexError, ValueError):
                pass
    finally:
        csvfile.close()

    # Remove all 0 counts
    empty_keys = []
    for key in corpus:
        if corpus[key] == 0.0:
            empty_keys.append(key)
    for key in empty_keys:
        corpus.pop(key)
        
    # Normalize by total
    total = sum([corpus[key] for key in corpus])
    
    for key in corpus:
        corpus[key] = idf(total, corpus[key])
        
    # Add default idf
    corpus[''] = idf(total, 1.0)
    
    print corpus['the']
    print corpus['']
    return corpus

def export_corpus(filepath, corpus):
    '''
    
    '''
    f = open(filepath, 'w')
    try:
        f.write("corpus = {")
        for key, value in corpus.iteritems():
            f.write("\"" + encode(key) + "\" : " + str(value) + ",\n    ")
        f.write("}")
    finally:
        f.close()
    
def encode(text):
    return text.encode('ascii', 'ignore')
    
def decode(text):
    return text.decode('ascii', 'ignore')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='none')
    parser.add_argument('corpus_filepath', type=str)
    parser.add_argument('dict_filepath', type=str)
    args = parser.parse_args()
    
    corpus = import_corpus(args.corpus_filepath)
    export_corpus(args.dict_filepath, corpus)
    print "Done."