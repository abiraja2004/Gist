import optimize
import summarize

import sys
import os

NUM_RUNS = 20

files = ['./summarization/nyajsreviews.txt',
         './summarization/mirasolreviews.txt',
         './summarization/brickreviews.txt']
names = ["Not Your Average Joe's", "Mirasol's Cafe", "Brick Pizzeria Napoletana"]

# Setup the input data for the optimizers
sentiments = []
sentence_sets = []

for file, name in zip(files, names):
    reviews = open(file, 'r').read()
    utf_data = reviews.decode('utf-8')
    overall_sentiment, sentence_dataset = summarize.get_attributes(utf_data, name)

    sentiments.append(overall_sentiment)
    sentence_sets.append(sentence_dataset)

# Get best fitnesses for each algorithm
genalg_best_fitnesses = []
gsa_best_fitnesses = []
pso_best_fitnesses = []

# For each set of reviews
for i in range(len(files)):
    sentiment = sentiments[i]
    sentences = sentence_sets[i]

    genalg_best_fitnesses.append([])
    gsa_best_fitnesses.append([])
    pso_best_fitnesses.append([])

    for j in range(NUM_RUNS):
        print 'File {}, Run {}'.format(i+1, j+1)

        genalg_optimizer = optimize.genalg_optimizer(sentences, sentiment)
        genalg_optimizer.logging = False
        genalg_optimizer.optimize()
        genalg_best_fitnesses[i].append(genalg_optimizer.best_fitness)

        gsa_optimizer = optimize.gsa_optimizer(sentences, sentiment)
        gsa_optimizer.logging = False
        gsa_optimizer.optimize()
        gsa_best_fitnesses[i].append(gsa_optimizer.best_fitness)
    
        pso_optimizer = optimize.pso_optimizer(sentences, sentiment)
        actual_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        _, pso_best_fitness = pso_optimizer()
        sys.stdout = actual_stdout
        pso_best_fitnesses[i].append(1.0/pso_best_fitness)


# Print results
algorithms = ['GenAlg', 'GSA', 'PSO']
products = ['Not Your Average Joes', 'Mirasol\'s Cafe', 'Brick\'s Pizzeria']
fitnesses = [genalg_best_fitnesses, gsa_best_fitnesses, pso_best_fitnesses]

print 
print
for i in range(len(algorithms)):
    print '{} Fitnesses'.format(algorithms[i])
    for j in range(len(products)):
        print '{}: {}'.format(products[j], sum(fitnesses[i][j])/NUM_RUNS)
    print 'Total: {}'.format(sum([sum(p_fitnesses) for p_fitnesses in fitnesses[i]])/(len(files)*NUM_RUNS))
    print