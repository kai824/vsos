Main file is network_drawing.py for main code, written in python 3.

NOTE: the scripts are provided as is and without warranty

Libraries needed:

matplotlib
planarity
networkx (to go with planarity)
nltk


Usage:

1. Input the name of text file (story). By default, it assumes encoding of text file to be utf-8. If not, please amend it on line 9. 

It will take a few minutes to generate list of characters, depending on length of text file. 

2. When done, combine the characters which seem to refer to the same character.

Input format:
<list of indexes that refer to the character>
<Desired name of character>
...
end

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

3. Afterwards, try to find a sharp drop in the graph that will show, and count the number of characters before the drop, which is used by the programme. Note that the characters are 0-indexed.

4. When the programme is done, the output file will be on "network_drawing_output.gexf" and "network_drawing_output_pmfg.gexf"(after running the planar maximally filtered algorithm) in the same directory. Open this file with gephi software to visualise the network. 
