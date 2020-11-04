from math import *
from heapq import *
from collections import *
import xml.etree.cElementTree as et
import os
import time
import re
import sys
import nltk
import pickle
import operator

wiki_path=sys.argv[1]
index_path=sys.argv[2]

start = time.time()

print(len(sys.argv))
print(sys.argv[1])
print(sys.argv[2])

stemmer = nltk.stem.SnowballStemmer('english')

stopword = {}  #stores all the stopwords

indexes={}
indexes['t']=defaultdict(list) #titles
#indexes['b']=defaultdict(list) text(body)
indexes['c']=defaultdict(list) #category
indexes['i']=defaultdict(list) #infobox

file_count = 0
pages_per_file = 50000
page_count = 0


output_files=list()    #stores pointers to output files
title_pos=list()  #stores position of title words
word_pos=dict()    #stores position of words


xmlFile = wiki_path
content = iter(et.iterparse(xmlFile,events=("start","end")))   #iterable content for xml file
title_tags = open(index_path+"/title_tags.txt","w+")
stem_word_dict=dict()  #maps word to stem word

#arr = ['t','i','b','c']

arr = ['t','i','c']

# RE to remove urls
re_url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.DOTALL)

# RE to remove tags & css
re_tag = re.compile(r'{\|(.*?)\|}',re.DOTALL)

# Regular Expression to remove {{cite **}} or {{vcite **}}
re_cite = re.compile(r'{{v?cite(.*?)}}',re.DOTALL)

# Regular Expression to remove [[file:]]
re_file = re.compile(r'\[\[file:(.*?)\]\]',re.DOTALL)

# pattern to get only alphnumeric text
re_text = re.compile("[^a-zA-Z0-9]")


re_x={'c':"\[\[Category:(.*?)\]\]",'i':"{{Infobox((.|\n)*?)}}"}


#re_cat = "\[\[Category:(.*?)\]\]"

#re_info = "{{Infobox((.|\n)*?)}}"
#stores all the stop words in a dictionary
def stop_func():
    reg = re.compile("\"|,| ")
    file = open("stop_words.txt","r")
    words = file.read()
    words = re.split(reg,words)
    for word in words:
        if word:
            stopword[word]=True


# stems the given word and maintains the dictionary
def preprocess_word(word):
    global stem_word_dict
    word = word.strip().lower()
    if word not in stem_word_dict:
        stem_word = stemmer.stem(word)
        stem_word_dict[word] = stem_word
    else:
        stem_word = stem_word_dict[word]
    return stem_word


#removes urls,tags,citations,files from given text
def clean_text(text):
    text = re_url.sub('',text)
    text = re_tag.sub('',text)
    text = re_cite.sub('',text)
    text = re_file.sub('',text)
    return text


def maintain_helper(text,x,word_map):
    text = re.split(re_text, text)
    for t in text:
        t = preprocess_word(t)
        if t and len(t) > 2 and t not in stopword:
            if t not in word_map[x]:
                word_map[x][t] = 1
            else:
                word_map[x][t] += 1

def maintain(text,word_map,x):
    try:
        tempword = re.findall(re_x[x],text)
        #if x=='i':
         #   print("something")
        if tempword:
            for temp in tempword:
                if x=='c':
                    maintain_helper(temp,x,word_map)
                elif x=='i':
                    for word in temp:
                        maintain_helper(word,x,word_map)

    except:
        pass

def maintain2(text,word_map,x):
    try:
        #if x == 'b':
            #text = re.split(re_text, text.lower())
        if x == 't':
            title_pos.append(title_tags.tell())
            title_string = text
            title_tags.write(title_string+"\n")
            text = re.split(re_text,text)
        for word in text:
            if word:
                if word not in stem_word_dict:
                    stem_word = stemmer.stem(word)
                    stem_word_dict[word] = stem_word
                else:
                    stem_word = stem_word_dict[word]
                word = stem_word
                if word not in stopword and len(word)>2:
                    if word not in word_map[x]:
                        word_map[x][word] = 1
                    else:
                        word_map[x][word] += 1
    except:
        pass


def to_index(word_map,id):
    for x in arr:
        #print(x," ",len(word_map[x]))
        for word in word_map[x]:
            s = id + ":"
            s = s + str(word_map[x][word])
            indexes[x][word].append(s)


def write_to_files():
    for x in arr:
        print("writing...")
        file = index_path +"/"+ x +str(file_count) + ".txt"
        outfile = open(file,"w+")
        for word in sorted(indexes[x]):
            post_list = ",".join(indexes[x][word])
            index = word + "-" + post_list
            outfile.write(index+"\n")
        outfile.close()


cnt=1

for event,elem in content:
    cnt+=1
    tag = re.sub(r"{.*}", "", elem.tag)
    if event == "start":
        if tag == "page":
            word_map={'t':{},'b':{},'i':{},'c':{}}
            page_count = page_count + 1
    if event == "end":
        if tag == "text":
            text = clean_text(str(elem.text))
            maintain(text,word_map,'i')
            #print("info finish")
            maintain(text,word_map,'c')
            #maintain2(text,word_map,'b')

        if tag == "title":
            maintain2(str(elem.text),word_map,'t')

        if tag == "page":
            id = str(page_count)
            to_index(word_map,id)

            if page_count % 50000 == 0:
                stem_word_dict = {}

            if page_count % pages_per_file == 0:
                write_to_files()
                for x in arr:
                    indexes[x].clear()
                file_count+=1
        elem.clear()


write_to_files()
file_count+=1

t_file = index_path + "/title_positions.pickle"
file = open(t_file,"wb+")
pickle.dump(title_pos,file)
file.close()


for x in arr:
    print("sorting...")
    heap = []
    flag = True
    input_files = []
    file = index_path + "/" + x + ".txt"
    fp = open(file,"w+")
    output_files.append(fp)
    outfile_index = len(output_files) - 1

    for i in range(file_count):
        file = index_path + "/" + x + str(i) + ".txt"
        if os.stat(file).st_size == 0:
            try:
                del input_files[i]
                os.remove(file)
            except:
                pass
        else:
            fp = open(file,"r")
            input_files.append(fp)

    if len(input_files) == 0:
        flag = False
        break

    for i in range(file_count):
        try:
            s = input_files[i].readline()[:-1]
            heap.append((s,i))
        except:
            pass #flag=False

    heapify(heap)
    i=0

    try:
        while i < file_count:
            s,ind = heappop(heap)
            pos = s.find("-")
            word = s[:pos]
            post_list = s[pos+1:]
            next_line = input_files[ind].readline()[:-1]
            if next_line:
                heappush(heap,(next_line,ind))
            else:
                i+=1

            if i == file_count:
                flag=False
                break

            while i < file_count:
                next_s , next_ind = heappop(heap)
                next_pos = next_s.find("-")
                next_word = next_s[:next_pos]
                next_post_list = next_s[next_pos+1:]
                if next_word == word:
                    post_list = post_list + "," + next_post_list
                    next_new_line = input_files[next_ind].readline()[:-1]
                    if next_new_line:
                        heappush(heap,(next_new_line,next_ind))
                    else:
                        i+=1
                else:
                    heappush(heap,(next_s,next_ind))
                    break

            if word not in word_pos:
                word_pos[word]=dict()

            word_pos[word][x] = output_files[outfile_index].tell()
            postings = post_list.split(",")
            documents = dict()
            idf = log10(page_count/len(postings))

            for post in postings:
                pos = post.find(":")
                id = post[:pos]
                freq = int(post[pos+1:])
                tf = log10(freq)+1
                documents[str(id)] = round(tf*idf,2)

            documents = sorted(documents.items(),key=operator.itemgetter(1), reverse=True)
            top_post_list_result = ""

            for doc in documents:
                top_post_list_result = top_post_list_result + doc[0] + ":" + str(doc[1]) + ","
            top_post_list_result = top_post_list_result[:-1]
            output_files[outfile_index].write(top_post_list_result+"\n")

    except IndexError:
        pass

    output_files[outfile_index].close()

    try:
        for i in range(file_count):
            file = index_path + "/" + x + str(i) + ".txt"
            input_files[i].close()
            os.remove(file)
    except:
        pass

file = open(index_path + "/word_postions.pickle","wb+")
pickle.dump(word_pos,file)
file.close()

end = time.time()
print("Total time taken : " + str(end-start) + " seconds")
