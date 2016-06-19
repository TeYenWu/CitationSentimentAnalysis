from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet
from textblob import TextBlob
# from nltk.stem.snowball import SnowballStemmer

#=============================================
# JSON
#=============================================
def recursivePrintJson(d):
    for k, v in d.iteritems():
        # print k, v
        # print "{0} : {1}".format(k, v)
        if isinstance(v, dict):
            recursive(v)
            print "{0} : {1}".format(k, v)

#=============================================
# Sentiwordnet
#=============================================
pennToWordnetPartOfSpeech = {'JJ' : [wordnet.ADJ, wordnet.ADJ_SAT], 'JJR' : [wordnet.ADJ, wordnet.ADJ_SAT],
                             'JJS': [wordnet.ADJ, wordnet.ADJ_SAT], 'NN' : [wordnet.NOUN],
                             'NNS': [wordnet.NOUN], 'NNP':[wordnet.NOUN], 'NNPS':[wordnet.NOUN],
                             'RB': [wordnet.ADV], 'RBR' : [wordnet.ADV], 'RBS' : [wordnet.ADV],
                             'VB': [wordnet.VERB], 'VBD': [wordnet.VERB], 'VBG': [wordnet.VERB],
                             'VBN': [wordnet.VERB], 'VBP': [wordnet.VERB], 'VBZ': [wordnet.VERB]}

def getWordAvgPosNegScore(word, **kwargs):
    posScore = 0
    negScore = 0
    numOfMatchNames = 0
    partOfSpeech = kwargs.get('partOfSpeech', None)
    try:
        sentiWords = list(swn.senti_synsets(word.split('.')[0]))
        for sentiWord in sentiWords:
            sentiWordName = sentiWord.synset.name().split('.')
            if sentiWordName[0] not in word.lower():
                continue
            numOfMatchNames += 1
            if partOfSpeech not in pennToWordnetPartOfSpeech:
               posScore += sentiWord.pos_score()
               negScore += sentiWord.neg_score()
            elif sentiWordName[1] in pennToWordnetPartOfSpeech[partOfSpeech]:
               posScore += sentiWord.pos_score()
               negScore += sentiWord.neg_score()   

        posScore /= numOfMatchNames
        negScore /= numOfMatchNames        
    except Exception, e:
        # print e
        pass
    return (posScore, negScore)

#=============================================
# negation
#=============================================
negationSet = {"not", "never", "neither", "nor", "no"}

#=============================================
# textblob
#=============================================
def getAvgPosNegScoreByTextBlob(sentence, **kwargs):
    blob = TextBlob(sentence)
    if blob.sentiment.polarity >= 0.0:
        return (blob.sentiment.polarity, 0.0)
    else:
        return (0.0, -blob.sentiment.polarity)


#=============================================
# Stemmer
#=============================================

# stemmer = SnowballStemmer("english")
# def stem(word):
#    return stemmer.stem(word)
# plurals = ['caresses', 'flies', 'dies', 'mules', 'denied',
#            'died', 'agreed', 'owned', 'humbled', 'sized',
#            'meeting', 'stating', 'siezing', 'itemization',
#            'sensational', 'traditional', 'reference', 'colonizer',
#            'plotted']
# singles = [stemmer.stem(plural) for plural in plurals]
# print(' '.join(singles))  # doctest: +NORMALIZE_WHITESPACE