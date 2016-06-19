import json
import sys
import util
import os

class Node:
    #Construction of Node with word, partOfSpeech, dependency, and children
    def __init__(self, word=None, partOfSpeech=None, dependency=None, children=None, parent=None):
        self.word = word
        self.partOfSpeech = partOfSpeech
        self.dependency = dependency

        if children is None:
            self.children = [] 
        else:
            self.children = children

        if parent is None:
            self.parent = None
        else:
            self.parent = parent

        self.posScore = 0.0
        self.negScore = 0.0

        self.accumPosScore = 0.0
        self.accumNegScore = 0.0

    def sentiWordCompute(self, **kwargs):
        evalFn = kwargs.get('evalFn', None)

        self.posScore, self.negScore =  evalFn(self.word, partOfSpeech = self.partOfSpeech)
        if self.word not in util.negationSet:
            self.accumPosScore, self.accumNegScore = self.posScore, self.negScore
        

#Construction of tree through recursion
class SyntaxTree:
    def __init__(self, sentence, jsonData):
        self.sentence = sentence
        self.jsonData = jsonData
        self.root = self.buildTree(jsonData)

    def buildTree(self, ob):
        rootNode = Node()
        rootNode.children = []
        rootNode.parent = None

        for k, v in ob.iteritems():
            kSplit = k.split(' ')
            rootNode.word = kSplit[0]
            rootNode.partOfSpeech = kSplit[1]
            rootNode.dependency = kSplit[2]
            rootNode.children += self.buildNode(v, rootNode)
        return rootNode

    def buildNode(self, ob, parent):
        nodes = []
        for k, v in ob.iteritems():
            kSplit = k.split(' ')
            node1 = Node(kSplit[0], kSplit[1], kSplit[2], None, parent)
            node1.children = []
            nodes.append(node1)
            if len(v) == 0:
                continue
            node1.children += self.buildNode(v, node1)
        return nodes

    def recursivePrintTree(self):
        print '=============================================='
        self.recursivePrintSubTree(self.root)
        print '=============================================='

    def recursivePrintSubTree(self, node, level=0):
        try:
            print '  '*level, node.word, '(', node.posScore, '/', node.negScore, ')', ' ', node.accumPosScore, '/', node.accumNegScore, ' ', node.partOfSpeech, ' ', node.dependency
        except Exception, e:
            print '  '*level, e
        for childNode in node.children:
            level += 1
            self.recursivePrintSubTree(childNode, level)
            level -= 1

    def computeSentiScore(self, **kwargs):
        self.recursivelyComputeSentiNodeScore(self.root, **kwargs)

    def recursivelyComputeSentiNodeScore(self, node, **kwargs):
        for childNode in node.children:
            self.recursivelyComputeSentiNodeScore(childNode, **kwargs)

        evalFn = kwargs.get('evalFn', None)

        if not kwargs.get('computeAccumOnly', False):
            node.sentiWordCompute(evalFn = evalFn)

        self.accumulateChildrenNodeScore(node)
        self.negationScoreHandling(node)

    def accumulateChildrenNodeScore(self, node):
        numOfSentiWords = 0
        for childNode in node.children:
            if childNode.accumPosScore != 0 or childNode.accumNegScore != 0:
                numOfSentiWords += 1
            node.accumPosScore += childNode.accumPosScore
            node.accumNegScore += childNode.accumNegScore
        
        if node.posScore != 0 or node.negScore != 0:
            numOfSentiWords += 1

        try:
            node.accumPosScore /= numOfSentiWords
            node.accumNegScore /= numOfSentiWords
        except Exception, e:
            pass

    def negationScoreHandling(self, node):
        for childNode in node.children:
            if childNode.word in util.negationSet:
                temp = node.accumPosScore
                if childNode.negScore != 0.0:
                    node.accumPosScore = childNode.negScore * node.accumNegScore
                    node.accumNegScore = childNode.negScore * temp
                else:
                    node.accumPosScore = 0.5 * node.accumNegScore
                    node.accumNegScore = 0.5 * temp
                
    def resetScores(self, **kwargs):
        self.recursivelyResetScores(self.root, **kwargs)

    def recursivelyResetScores(self, node, **kwargs):
        for childNode in node.children:
            self.recursivelyResetScores(childNode, **kwargs)
        node.posScore, node.negScore, node.accumPosScore, node.accumNegScore = 0.0, 0.0, 0.0, 0.0

    def getResults(self):
        return {'sentence' : self.sentence, 'polarity' : self.root.accumPosScore - self.root.accumNegScore};

#Building Json object from text file            
def main(absSentenceFilePath, sentenceList):
    os.chdir("models/syntaxnet")
    sentenceFileNameNoExt = os.path.splitext(os.path.basename(absSentenceFilePath))[0]
    sentenceJsonName = sentenceFileNameNoExt + ".json"
    absSentenceJsonName = os.path.join("..", "..", "sentence-citenum-json", sentenceJsonName)
    absResultsJsonName = os.path.join("..","..", "citenum-results-json", sentenceJsonName)

    os.system("cat " + absSentenceFilePath + " | ./syntaxnet/demo.sh -o " + absSentenceJsonName)

    trees = []
    with open(absSentenceJsonName) as infile:
        for i, l in enumerate(infile):
            data = json.loads(l)
            tree = SyntaxTree(sentenceList[i], data)
            # tree.recursivePrintTree()
            tree.computeSentiScore(evalFn = util.getWordAvgPosNegScore)
            tree.recursivePrintTree()
            # tree.resetScores()
            # tree.computeSentiScore(evalFn = util.getAvgPosNegScoreByTextBlob)
            # tree.recursivePrintTree()

            trees.append(tree.getResults())

    with open(absResultsJsonName, "w") as outFile:
        json.dump(trees, outFile)
