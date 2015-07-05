#########################
# Written By: Chad Clough
#########################

import textblob
from textblob import TextBlob
from collections import Counter
import math
	
#MySQL stopwords with contractions separated
stop_words = set([
    "a", "able", "about", "above", "according", "accordingly", "across", "actually", "after", "afterwards",
    "again", "against", "ai", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although",
    "always", "am", "among", "amongst", "an", "and", "another", "any", "anybody", "anyhow", "anyone", "anything",
    "anyway", "anyways", "anywhere", "apart", "appear", "appreciate", "appropriate", "are", "around", 
    "as", "aside", "ask", "asking", "associated", "at", "available", "away", "awfully", "be", "became", "because",
    "become", "becomes", "becoming", "been", "before", "beforehand", "behind", "being", "believe", "below",
    "beside", "besides", "best", "better", "between", "beyond", "both", "brief", "but", "by", "c'mon", "c", "came",
    "can", "ca", "cannot", "cant", "cause", "causes", "certain", "certainly", "changes", "clearly", "co", 
    "com", "come", "comes", "concerning", "consequently", "consider", "considering", "contain", "containing", 
    "contains", "corresponding", "could", "course", "currently", "definitely", "described", "despite", "did", 
    "different", "do", "does", "doing", "do", "done", "down", "downwards", "during", "each", "edu", "eg", 
    "eight", "either", "else", "elsewhere", "enough", "entirely", "especially", "et", "etc", "even", "ever", 
    "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "far",
    "few", "fifth", "first", "five", "followed", "following", "follows", "for", "former", "formerly", "forth", 
    "four", "from", "further", "furthermore", "get", "gets", "getting", "given", "gives", "go", "goes", "going",
    "gone", "got", "gotten", "greetings", "had", "happens", "hardly", "has", "have", "having", "he", "hello", 
    "help", "hence", "her", "here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", "hi", "him",
    "himself", "his", "hither", "hopefully", "how", "howbeit", "however", "i", "ie", "if", "ignored", "immediate",
    "in", "inasmuch", "inc", "indeed", "indicate", "indicated", "indicates", "inner", "insofar", "instead", 
    "into", "inward", "is", "it", "its", "itself", "just", "keep", "keeps", "kept", "know", "known", "knows", 
    "last", "lately", "later", "latter", "latterly", "least", "less", "lest", "let", "like", "liked", 
    "likely", "little", "look", "looking", "looks", "ltd", "mainly", "many", "may", "maybe", "me", "mean", 
    "meanwhile", "merely", "might", "more", "moreover", "most", "mostly", "much", "must", "my", "myself", "name", 
    "namely", "nd", "near", "nearly", "necessary", "need", "needs", "neither", "never", "nevertheless", 
    "new", "next", "nine", "no", "nobody", "non", "none", "noone", "nor", "normally", "not", "nothing", 
    "novel", "now", "nowhere", "obviously", "of", "off", "often", "oh", "ok", "okay", "old", "on", "once", "one", 
    "ones", "only", "onto", "or", "other", "others", "otherwise", "ought", "our", "ours", 
    "ourselves", "out", "outside", "over", "overall", "own", "particular", "particularly", "per", "perhaps", 
    "placed", "please", "plus", "possible", "presumably", "probably", "provides", "que", "quite", "qv", 
    "rather", "rd", "re", "really", "reasonably", "regarding", "regardless", "regards", "relatively", "respectively", 
    "right", "said", "same", "saw", "say", "saying", "says", "second", "secondly", "see", 
    "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", 
    "serious", "seriously", "seven", "several", "shall", "she", "should", "since", "six", 
    "so", "some", "somebody", "somehow", "someone", "something", "sometime", "sometimes", "somewhat", "somewhere", 
    "soon", "sorry", "specified", "specify", "specifying", "still", "sub", "such", "sup", "sure", 
    "t", "take", "taken", "tell", "tends", "th", "than", "thank", "thanks", "thanx", 
    "that", "thats", "the", "their", "theirs", "them", "themselves", "then", "thence", 
    "there", "thereafter", "thereby", "therefore", "therein", "theres", "thereupon", "these", "they", 
    "think", "third", "this", "thorough", "thoroughly", "those", 
    "though", "three", "through", "throughout", "thru", "thus", "to", "together", "too", "took", 
    "toward", "towards", "tried", "tries", "truly", "try", "trying", "twice", "two", "un", 
    "under", "unfortunately", "unless", "unlikely", "until", "unto", "up", "upon", "us", "use", 
    "used", "useful", "uses", "using", "usually", "value", "various", "very", "via", "viz", 
    "vs", "want", "wants", "was", "way", "we", "welcome", "well", "went", "were", "what", "whatever", "when", 
    "whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", "whereupon", "wherever", 
    "whether", "which", "while", "whither", "who", "whoever", "whole", "whom", "whose", 
    "why", "will", "willing", "wish", "with", "within", "without", "wo", "wonder", "would", 
    "yes", "yet", "you", "your", "yours", "yourself", "yourselves", "zero", "'d", "'m", "'s", "'ll", "n't",  "'re", "'ve"
])    
    
def length_score(sentence):
    """Scores the length of a sentence
    
    Args:
        sentence: The sentence to calculate the lengthScore of

    Returns:
        float; The score of the sentence in the range [0, 1] where 1 is
            optimal
    """
    #based upon 40 'elite' yelp reviews
    optimalLength = 15 #15.4 actual
    variance = 24.8
    
    length = len(sentence.split(' '))
    
    return gaussian(math.fabs(length-optimalLength), variance) 
	
def gaussian(x, variance):
    return math.exp(-(x**2/variance))

def name_score(sentence, name):
    """Scores the relevance of a sentence to the name of the product/service

    Args:
        sentence: The sentence to calculate the nameScore of
        name: The name of the good/service

    Returns:
        float; The score of the sentence in the range [0, 1] where 1 is
            optimal
    """
    if name in sentence:
        return 1;

    partsOfName = name.split(' ')
    length = len(partsOfName)

    numParts = 0
    for word in partsOfName:
        if word in sentence:
            numParts += 1

    if numParts == length:
        return (numParts - 0.5) / float(length); #Give less weight to sentences that don't explicitly say the name
    elif numParts > 0:
        return numParts / float(length);

    return 0;


def rel_score(sentence, categories):
    """Scores the relevance of a sentence to the categories of a product/service
    
    Args:
    sentence: The sentence to calculate the catRelScore of
	
    Returns:
        float; The score of the sentence in the range [0, 1] where 1 is
            optimal
    """
    return 0;

def keywords(reviews, numKeywords):
    """Gets the [numKeywords] most frequent words within the reviews for 
    a product/service excluding stop_words
    
    Args:
        reviews: a list of all the reviews for a product/service
        numKeywords: The number of keywords we want to have
        
    Returns:
        list; Contains each of the [numKeywords] keywords
    """
    alltext = ""
    for review in reviews:
        alltext = alltext + review
        
    blob = TextBlob(alltext)
    words = blob.lower().words
    num_words = len(words)
    
    #count the frequency of each word
    counts = Counter(word for word in words if word not in stop_words)
    keywords = {a: b for a, b in counts.most_common(numKeywords)}
    
    #quadratic scaling
    
    for i in keywords:
        keywords[i] = keywords[i] / float(num_words)
        
    return keywords

if __name__ == '__main__':
    #s = ['', 'word'] * 16
    #for numWords in range(2, 31):
    #    s[numWords] = s[numWords-1] + " word"
    #    print "Num words: " + str(len(s[numWords].split(' ')))
    #    print "Score: " + str(length_score(s[numWords])) + "\n"
    #print name_score("asdGary Danko's is great!", "Gary Danko")	
    #print name_score("aosknfddaf wqdwef feGary's is great!", "Gary Danko")
    #print name_score("asdasd Danko's is great!", "Gary Danko")
    #print name_score("Danko's is great Bary Gary!", "Gary Bary Danko")
    #print name_score("This sentence is irrelevant!", "Gary Bary Danko")
    s = list()
    s.append('''
        STOP. Before you walk into this shop thinking that you're going to walk away with a lovely cup 
        of cappuccino, walk back over to Hanover to the Thinking Cup or Caffe Vittoria because they sell 
        coffee...beans. Coffee beans, not the drink. 
        Upon walking into the store, your nostrils are flooded with the wonderful aroma of coffee beans & 
        teas adorned all around the store. That's right folks, not just coffee, but loose leaf tea too! The 
        prices are so affordable that you might feel like tipping them extra money because you feel bad for
        practically stealing from them. Coffee, candy, loose leaf tea, spices, & Sriracha, this place is a
        spice collector's dream. Various types of flour are carried here & are so reasonable that I might 
        have to come back with my dorky grocery cart on wheels to wheel away 2 oz of every spice they have!
        From paprika to oregano to curry to chamomile to amaretto coffee, they've got tons of items. Beyonce
        wrote "Crazy in Love" about Polcari's, not about Jay-Z. 
        Whether you need a gift for your sister, mother, father, brother, aunt, uncle, cousin, boyfriend/girlfriend,
        spouse, daughter, son, WHOMEVER, just stop by here. Only a spoiled snob wouldn't appreciate the kind gesture 
        of delicious coffee beans or loose leaf tea. Yeah, I could get you an iPad for your birthday, or I could
        buy you diabetes in the form of candy & antioxidants in the form of coffee & tea, sooooo what's it gonna 
        be? I pick the things that make you less cranky in the morning.
    ''')
    s.append("""
        review is only about the bulk coffee, which is what i was looking for. 
        coffee beans itself - they LITERALLY poured coffee beans out of downeast coffee bags into their glass containers 
        (which are ~$3 cheaper per pound if you buy it directly from downeast). NOT WORTH IT TO BUY FROM HERE!]\
        -------
        service: 
        girl at the counter couldn't answer any of my questions (e.g. "where is this from? is it light or dark roast?", 
        and had to refer to another staff member (apparently her dad) every time I asked simple questions, which made
         the process twice as long as necessary.
        in general service was meh - we waited for a while and got overlooked for other more familiar customers.
    """)
    print keywords(s, 15)
    