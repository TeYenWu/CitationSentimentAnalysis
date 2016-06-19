# Run with -> python find_cite.py [outputFile] [CiteNumber] [PdfPath]

import re
import sys
import subprocess
import os.path
import SyntaxTree;
# from SyntaxTree import main
# Please not include ".txt".
outFileName = sys.argv[1]
citeNum = sys.argv[2]
pdfPath = sys.argv[3]


if not os.path.exists("./tmp/" + outFileName + '.txt'):
    subprocess.call(['./pdfminer-master/tools/pdf2txt.py', "-o", "./tmp/" + outFileName + '.txt', pdfPath])

with open('./tmp/' + outFileName + '.txt', 'r') as files:
    paper=files.read()

snumb = citeNum
mod_snumb = '[^0-9]' + snumb + '[^0-9]'  #regular expression
pronounsAnotations = [" these ","These ","Their "," their ","Such ", " such ", "This method", "this method",  snumb]



cite_location = []
for cites in re.finditer('\[(.*?)\]', paper):
    if re.search(mod_snumb,paper[cites.start():cites.end()]):
        # print paper[cites.start():cites.start()+3] + '\n'
        cite_location.append(cites.start())

nn_location = [nn.start() for nn in re.finditer('\. *\n', paper)]
# print nn_location
cite_prg = []
sentence_list = []
if len(cite_location) > 0:
    cite_index = 0
    for cite in xrange(len(nn_location)):
        if cite_index < len(cite_location) and\
                        nn_location[cite] > cite_location[cite_index]:
            cite_start = (nn_location[cite-1] if cite-1 >= 0 else 0)
            # cite_start = (cite_location[cite_index]
            cite_end = nn_location[cite]
            cite_prg.append((cite_start,cite_end))
            cite_index += 1
            while cite_index < len(cite_location) and\
                    nn_location[cite] > cite_location[cite_index]:
                cite_index += 1
    for prg in cite_prg:
        # print paper[prg[0]:prg[1]]
        for sentence in paper[prg[0]:prg[1]].split('. '):
            # print sentence
            for anotation in pronounsAnotations:
                if anotation in sentence:
                    sentence =  sentence.replace('-','')
                    sentence =  sentence.replace('\n',' ')

                    # res = sentence.split(',')
                    sentence_list.append(sentence);
                    break;
    fullOutfileName = os.path.join("sentence-citenum", outFileName + '_' + citeNum + '.txt')
    with open(fullOutfileName, 'w') as outputFile: 
        for sentence in sentence_list:
            outputFile.write(sentence+'\n');
    absOutfileName = os.path.abspath(fullOutfileName)
    SyntaxTree.main(absOutfileName, sentence_list)

            
else:
    print 'no citation number in txt'



    # print sentence
    
#print cite_prg  #output paragraph tuple(start,end) in paper.txt