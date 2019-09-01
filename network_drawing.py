import planarity
import matplotlib.pyplot as plt
import networkx as nx
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#The following section sets up NLTk. Can be removed after first run
nltk.download('punkt')
nltk.download('vader_lexicon')
nltk.download('averaged_perceptron_tagger')

sia = SentimentIntensityAnalyzer()
filename=input('File name of text, with file extension:')
a = open(filename, 'r',encoding='utf-8')#change encoding here if needed
f = a.read()
a.close()
f2 = f.split('\n\n')  # split by paragraph
i = 0
dialogue = False
while i < len(f2):

    # checking for blank paragraphs, when more than 4 newlines

    if f2[i] == '':
        del f2[i]
        continue
    if f2[i][0] == '\n':  # newline paragraphs, if odd number of newlines
        f2[i] = (f2[i])[1:]
    i += 1


def subset(a, b):  # used in subset checking

    # checks if a is a subset of b

    cur_it = 0
    for y in b:
        if a[cur_it].lower() == y.lower():
            cur_it += 1
            if cur_it == len(a):
                return True
    return False


def checkgender(agent):  # used in replacing hes and shes
    if agent.split()[0].lower() in ['ms.','miss','mrs','mrs.','mademoiselle','madam']:
        return 'F'
    if agent.split()[0].lower() in ['mr.','mr','sir','monsieur']:
        return 'M'
    if agent.split()[0] in [
        'mr.',
        'mrs.',
        'ms.',
        'monsieur',
        'mademoiselle',
        'elder',
        'brother',
        'papa',
        'miss',
        'mr',
        'mrs',
        'sir',
        'don',
        ]:
        if agent.split()[1][-1] == 'a' or agent.split()[1][-1] == 'e' \
            or agent.split()[1][-1] == 'i':
            return 'F'
    else:
        if agent.split()[0][-1] == 'a' or agent.split()[0][-1] == 'e' \
            or agent.split()[0][-1] == 'i':
            return 'F'
    return 'M'


sentences = []

# sentences=sent_tokenize(f)

for x in f2:  # iterating through the paragraphs
    sentences += sent_tokenize(x)  # add the sentences from a paragraph
    sentences.append('\n\n')  # to help us distinguish between paragraphs

cnts = []  # stores name, total count, agent count, patient count, list of mentions(in the form [sentence_it, word_it])
addr = ''
for y in range(len(sentences)):
    if sentences[y] == '''\n\n''':  # aka the bookmark between paras
        continue
    sentences[y] = list(sentences[y])

    # since python doesn't allow character assignment
    # have to convert to list to replace newlines and add spacing for the characters

    for x in range(len(sentences[y])):
        if sentences[y][x] == '\n':
            sentences[y][x] = ' '
    for x in range(len(sentences[y]) - 1):
        if sentences[y][x + 1] != ' ' \
            and not (sentences[y][x].isdigit()
                     or sentences[y][x].isalpha()):
            sentences[y][x] = ' ' + sentences[y][x] + ' '
    sentences[y] = ''.join(sentences[y])  # combine tgt from list
    words = word_tokenize(sentences[y])
    words2 = []
    for x in range(len(words)):
        words2.append(words[x].lower())  # for lowercase
    words = nltk.pos_tag(words)
    words2 = nltk.pos_tag(words2)
    # used to help us ensure that word is not adjective verb when lowercase. Not really important, as user can rename characters anyway.
    
    i = 0
    while i < len(words):
        if words[i][0] == '``':
            dialogue = not dialogue
        if words[i][0].lower() == "and" and words[i][1] == "NNP":
            words[i] = (words[i][0],"CC")
        if len(words[i][0]) > 2 and (words[i][0])[-2:] == "'s":
            words[i] = ((words[i][0])[:-2], words[i][1])  # remove 's
        if len(words[i][0]) == 1 and words[i][0].lower() != 'a':
            words[i] = (words[i][0], 'NULL')  # weird one-character
        if len(words2[i][0]) == 1 and words2[i][0].lower() != 'a' \
            and words2[i][0].lower() != 'i':
            words2[i] = (words2[i][0], 'NULL')  # do the same in words2
        if words[i][1] == 'NNP':  # change all to lowercase except first one, so stuff like SHERLOCK doesn't appear
            t = list(words[i][0].lower())
            t[0] = t[0].upper()
            words[i] = (''.join(t), 'NNP')
            if (words2[i][1])[:2] == 'VB':
                words[i] = (words[i][0], words2[i][1])
            try:
                if words[i + 1][1] == 'NNP' and (words2[i][1])[:2] \
                    == 'JJ':  # check if it could be adj
                    words[i] = (words[i][0], words2[i][1])
            except IndexError:
                pass
        if words[i][1] == 'NNP' and words[i][0].lower() in ['dr', 'dr.'
                ]:
            words[i] = ('Doctor', 'NNP')  # mainly to uniform dr. watson and doctor watson
        if dialogue == False and (words[i][0] == 'I'
                                  or words[i][0].lower() == 'me'):
            #words[i]=('Narrator','NNP')
            pass
        if i == 0:
            i = 1  # no previous word to combine with
            continue

        #combining with previous
        if words[i][0] != 'Narrator' and (not words[i][0].lower() in ['mr.','mrs.','ms.','monsieur','mademoiselle','miss','mr','mrs','sir']) and words[i][1] == 'NNP' \
            and words[i - 1][1] == 'NNP':
            words[i - 1] = (words[i - 1][0] + ' ' + words[i][0], 'NNP')
            words2[i - 1] = (words2[i - 1][0] + ' ' + words2[i][0],
                             'NNP')
            del words[i]
            del words2[i]
        else:
            i += 1
    i = 0
    sentences[y] = words
    for i in range(0, len(words)):  # change to len-1 if check agents

        # using SVO

        if words[i][1] == 'NNP':  # character
            broke = False

            # check for agency

            agent = False
            ii = i
            while ii + 1 < len(words):
                if (words[ii + 1][1])[:2] == 'VB':
                    agent = True
                    break
                elif (words[ii + 1][1])[:2] == 'RB':
                    ii += 1
                else:
                    break

            for x in reversed(range(len(cnts))):

                # check against previous characters, start from last one

                if subset(words[i][0].split(), cnts[x][0].split()) \
                    == True:
                    cnts[x][1] += 1
                    if agent:
                        cnts[x][2] += 1
                        cnts[x][4].append([y, i])
                    else:
                        cnts[x][3] += 1
                    cnts.append(cnts[x])
                    words[i] = (cnts[x][0], words[i][1])
                    del cnts[x]
                    broke = True
                    break
            if broke == False:
                for x in reversed(range(len(cnts))):

                    # check against previous characters, but don't assume that first mention is the "full name"

                    if subset(cnts[x][0].split(), words[i][0].split()) \
                        == True:
                        cnts[x][0] = words[i][0]
                        cnts[x][1] += 1
                        if agent:
                            cnts[x][2] += 1
                            cnts[x][4].append([y, i])
                        else:
                            cnts[x][3] += 1
                        cnts.append(cnts[x])
                        del cnts[x]
                        broke = True
                        break
                if broke == False:
                    if agent:
                        cnts.append([words[i][0], 1, 1, 0, [[y, i]]])
                    else:
                        cnts.append([words[i][0], 1, 0, 1, []])

newfreq = []
a1 = []
a2 = []
for key in cnts:
    newfreq.append([key[1] + key[2] * 2, key[0], key[2] * 3, key[3],
                   key[4]])#total count + extra agency count
newfreq = sorted(newfreq, reverse=True)
print('Format:\nIndex\tName of character\tWeighted Agency count\tPatiency count')
for i in range(min(len(newfreq),100)):#assuming there'll be less than 100 characters

    # print(i,newfreq[i])

    print (i, newfreq[i][1], newfreq[i][2], newfreq[i][3])

    # a1.append(i)
    # a2.append(newfreq[i][0])

print ('Manual disambiguation: Pls combine proper nouns that refer to the same entity.\nInput format:\n<list of iterators for character, such as 0 2 4>\n<New name of character>\nEnd with "end"')  # combine characters
inp = input()
to_remove = []
while inp != 'end':
    i = inp.split()
    i[0] = int(i[0])
    for x in range(1,len(i)):
        i[x]=int(i[x])      
        newfreq[i[0]][0] += newfreq[i[x]][0]
        newfreq[i[0]][2] += newfreq[i[x]][2]
        newfreq[i[0]][3] += newfreq[i[x]][3]
        newfreq[i[0]][4] += newfreq[i[x]][4]
        to_remove.append(i[x])
    newfreq[i[0]][1] = input()#New name
    inp = input()

to_remove = sorted(to_remove, reverse=True)
for x in to_remove:
    del newfreq[x]
newfreq = sorted(newfreq, reverse=True)  # since combining will affect ordering
print("Format: Index\tName of character\tWeighted frequency count of character in story")
for i in range(min(len(newfreq),100)):
    print (i, newfreq[i][1],newfreq[i][0])
    a1.append(i)
    a2.append(newfreq[i][0])

print("Press enter when ready. A graph will show. Determine the sharp drop, and count the no. of characters before it.\nWhen done, close the graph.")
input()

plt.semilogy(a1,a2,'-o')
plt.axis([0,50,1,a2[0]+50])
plt.ylabel('Weighted of characters')
plt.xlabel('0-indexed rank of characters')
plt.show()

print("Based on graph, how many characters should be taken into account?")

noofchar = int(input())

last_mentioned = []
characters = []
for x in range(noofchar):
    characters.append(newfreq[x][1])
    for y in newfreq[x][4]:  # use the list of mentions found to standardise mentions
        i = y[1] + 1
        while i < len(sentences[y[0]]):
            if subset([sentences[y[0]][i][0]], newfreq[x][1].split()):
                sentences[y[0]][y[1]] = (sentences[y[0]][y[1]][0] + ' '
                        + sentences[y[0]][i][0],
                        sentences[y[0]][y[1]][1])
                sentences[y[0]][i] = ('', '')
            else:
                break
            i += 1
        sentences[y[0]][y[1]] = (newfreq[x][1],sentences[y[0]][y[1]][1])

for y in range(len(sentences)):  # iterate through sentences
    if sentences[y] == '''\n\n''':  # new para
        last_mentioned = []  # stores the characters, with the last one being the last mentioned
        continue
    for x in range(len(sentences[y])):  # iterate through words
        if sentences[y][x][0] in characters:
            last_mentioned.append(sentences[y][x][0])
        elif x + 1 < len(sentences[y]):
            if (sentences[y][x + 1][1])[:2] == 'VB':  # only care if it's agent

                # replacing he's and she's

                if sentences[y][x][0].lower() == 'he':
                    for i in reversed(range(len(last_mentioned))):
                        if checkgender(last_mentioned[i]) == 'M':
                            sentences[y][x] = (last_mentioned[i],
                                    sentences[y][x][1])
                            last_mentioned.append(last_mentioned[i])
                            del last_mentioned[i]
                            break
                elif sentences[y][x][0].lower() == 'she':
                    for i in reversed(range(len(last_mentioned))):
                        if checkgender(last_mentioned[i]) == 'F':
                            sentences[y][x] = (last_mentioned[i],
                                    sentences[y][x][1])
                            last_mentioned.append(last_mentioned[i])
                            del last_mentioned[i]
                            break
el = {}
agent = []
patient = []
sentences.append('''\n\n''')
for y in sentences:
    if y == '''\n\n''':
        continue
    (agent, patient) = ([], [])  # by sentence
    sent = y[0][0]
    for x in range(1, len(y)):
        sent += ' ' + y[x][0]
    ss = sia.polarity_scores(sent)['compound']
    for xx in range(len(y)):
        x = y[xx]
        if x[0] in characters and not x[0] in last_mentioned:
            agentt = False  # stores if it is agent
            ii = xx + 1
            while ii < len(y):
                if (y[ii][1])[:2] == 'VB':
                    agentt = True
                    break
                elif (y[ii][1])[:2] == 'RB':
                    ii += 1
                    continue
                else:
                    break
            if agentt:
                agent.append(x[0])
            else:
                patient.append(x[0])

    for xx in agent:
        for yy in patient:
            if xx == yy:
                continue
            if (xx, yy) in el:
                el[(xx, yy)][0] += 1
                el[(xx, yy)][1] += ss
                el[(xx, yy)][2] += 1
            else:
                el[(xx, yy)] = [1, ss, 1]  # weight,   sum,count(for sent analysis)

f = open('network_drawing_output.gexf', 'w+')
f.write('<?xml version="1.1" encoding="UTF-8"?>\n')
f.write('<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">\n')
f.write('<graph defaultedgetype="directed">\n\n')
f.write("<nodes>\n")
charid={}
for x in range(len(characters)):
    charid[characters[x]]=x
for (xx,yy) in el:
    characters[charid[xx]]=[xx,None]
    characters[charid[yy]]=[yy,None]#marks them as having an edge
for x in range(len(characters)):
    if type(characters[x])==type('Doctor Watson'):#check if it's string. If it still is, it is an island node
        continue
    f.write('<node id="'+str(x)+'" label="'+characters[x][0]+'"/>\n')
f.write('</nodes>\n')
f.write('<edges>\n')
mini = 10
maxi = -10
for (xx, yy) in el:
    mini = min(el[(xx, yy)][1] / el[(xx, yy)][2], mini)
    maxi = max(el[(xx, yy)][1] / el[(xx, yy)][2], maxi)
cnt=0
edge_pairs={}#{(node1, node2) : [max weight,[node 1 to node 2 ss, weight],[node 2 to node 1 ss, weight] ] }
for (xx, yy) in el:
    f.write('<edge id="'+str(cnt)+'" source="'+str(charid[xx])+'" target="'+str(charid[yy])+'" weight="'+str(el[(xx, yy)][0])+'">\n')
    cnt+=1
    ss = el[(xx, yy)][1] / el[(xx, yy)][2]
    ss -= mini
    ss = ss / (maxi - mini) * 2
    ss -= 1
    (r, g, b) = (None, None, None)

    # r
    if ss >= 0:
        r = 0
    else:
        r = -ss * 255

    # g
    if ss <= 0:
        g = (ss + 1) * 255
    else:
        g = (-ss + 1) * 255

    # b
    if ss <= 0:
        b = 0
    else:
        b = ss * 255
    f.write('<viz:color r="'+str(int(r))+'" g="'+str(int(g))+'" b="'+str(int(b))+'"/>\n</edge>\n')

    if (yy,xx) in edge_pairs:
        edge_pairs[(yy,xx)][0]=max(edge_pairs[(yy,xx)][0],el[(xx,yy)][0])
        edge_pairs[(yy,xx)][2]=[ss,el[(xx,yy)][0]]
    else:
        edge_pairs[(xx,yy)]=[el[(xx,yy)][0],[ss,el[(xx,yy)][0]],[None,None]]
f.write('</edges>\n</graph>\n</gexf>\n')
f.close()
sorted_edges=[]
for (xx,yy) in edge_pairs:
    sorted_edges.append(edge_pairs[(xx,yy)]+[(xx,yy)])#weight, edge 1, edge 2, (node1, node2)
sorted_edges=sorted(sorted_edges,reverse=True,key=lambda edge:edge[0])
f=open('network_drawing_output_pmfg.gexf','w+')
f.write('<?xml version="1.1" encoding="UTF-8"?>\n')
f.write('<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">\n')
f.write('<graph defaultedgetype="directed">\n\n')
f.write("<nodes>\n")
for x in range(len(characters)):
    if type(characters[x])==type('Doctor Watson'):
        continue
    f.write('<node id="'+str(x)+'" label="'+characters[x][0]+'"/>\n')
f.write('</nodes>\n')
f.write('<edges>\n')

pmfg = nx.Graph()

cnt=0
removed=False
for edge in sorted_edges:
    pmfg.add_edge(edge[3][0],edge[3][1])
    if planarity.is_planar(pmfg):
        f.write('<edge id="'+str(cnt)+'" source="'+str(charid[edge[3][0]])+'" target="'+str(charid[edge[3][1]])+'" weight="'+str(edge[1][1])+'">\n')
        cnt+=1
        ss=edge[1][0]
        r=max(0,-ss*255)
        g=(1-abs(ss))*255
        b=max(0,ss*255)
        f.write('<viz:color r="'+str(int(r))+'" g="'+str(int(g))+'" b="'+str(int(b))+'"/>\n</edge>\n')
        if edge[2][0]!=None:
            f.write('<edge id="'+str(cnt)+'" source="'+str(charid[edge[3][1]])+'" target="'+str(charid[edge[3][0]])+'" weight="'+str(edge[2][1])+'">\n')
            cnt+=1
            ss=edge[2][0]
            r=max(0,-ss*255)
            g=(1-abs(ss))*255
            b=max(0,ss*255)
            f.write('<viz:color r="'+str(int(r))+'" g="'+str(int(g))+'" b="'+str(int(b))+'"/>\n</edge>\n')
    else:
        pmfg.remove_edge(edge[3][0],edge[3][1])
        removed=True
f.write('</edges>\n</graph>\n</gexf>\n')
f.close()
if removed==False:
    print('FYI the graph itself is already planar. Which means that both graph files will give the same graph')

print('Graph is output as "network_drawing_output.gexf" and "network_drawing_output_pmfg.gexf" for the planar graph. Open them with additional software, such as Gephi.')
