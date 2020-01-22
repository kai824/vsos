Run network_drawing.py for main code, written in python 3.

Libraries needed:
matplotlib
planarity
networkx (to go with planarity)
nltk

To setup nltk after downloading, run:
import nltk
nltk.download('all')

Usage:

First, input the name of text file (story). By default, it assumes encoding of text file to be utf-8. If not, please amend it on line 9. 

It will take a few minutes to generate list of characters, depending on length of text file. When done, combine the characters which seem to refer to the same character.

A sample input is as follows:(Or you could copy the input from input.txt)

0 8 11 14 31
Hercule Poirot
1 20 23
Mr. Jack Renauld
5 7
Mrs. Renauld
12 28
Marthe Daubreuil
4 46
Madame Daubreuil
17 39
Jeanne Beroldy
3
M. Hautet
end

Afterwards, try to find a sharp drop in the graph, and count the number of characters before the drop, which is used by the programme. Note that the characters are 0-indexed.
