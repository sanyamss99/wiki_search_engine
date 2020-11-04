import operator
import time
import sys
import gc
import os
import re
import sys
import pickle
import base64
import nltk
import json


def read_file(testfile):
    with open(testfile,'r') as file:
        queries = file.readlines()
    return queries

def write_file(outputs, path_to_output):
    with open(path_to_output,'w') as file:
        for output in outputs:
            for line in output:
                file.write(line.strip()+'\n')
            file.write('\n')


def mapping(field):
    field = field.lower()

    if field == "title":
        return 't'
    elif field == "infobox":
        return 'i'
    elif field == "category":
        return 'c'
    else:
        return field





def search(path_to_index):
    stemmer = nltk.stem.SnowballStemmer('english')
    stop_words = {}
    reg = re.compile("\"|,| ")
    #file_path = "C:\Users\hp\wiki_search_engine\project\stop_words.txt"
    stop_file = open(r"C:\Users\hp\Desktop\wiki_search_engine\project\stop_words.txt", "r")
    content = stop_file.read()
    content = re.split(reg,content)
    for word in content:
        if word:
            stop_words[word]=True

    title_tags = open(path_to_index+"/title_tags.txt",'r')
    title_position = pickle.load(open(r"C:\Users\hp\Desktop\wiki_search_engine\project\index\title_positions.pickle", "rb"))
    word_position = pickle.load(open(r"C:\Users\hp\Desktop\wiki_search_engine\project\index\word_postions.pickle", "rb"))


    field_map = {"t" : 0, "i" : 1, "c" : 2}
    field_chars = {"t","i","c"}

    files = []

    for x in field_chars:
        file = path_to_index + "/" + x + ".txt"
        fp = open(file,"r")
        files.append(fp)

    while(1):
        query = input()
        start = time.time()
        result = []
        documents = dict()
        query_words = list()

        if ":" in query:
            query_bag = query.split(" ")
            t_result = list()
            flag = 0
            for q in query_bag:
                field_query = q.split(":")
                field = field_query[0]
                query = field_query[1]
                field = mapping(field)
                query_words = query.split()
                for word in query_words:
                    word = stemmer.stem(word)
                    if word in word_position and field in word_position[word]:
                        position = word_position[word][field]
                        files[field_map[field]].seek(position)
                        intersection = list()
                        s = files[field_map[field]].readline()[:-1]
                        if "," in s:
                            items = s.split(",")
                            for item in items :
                                doc_score = item.split(":")
                                doc_id = doc_score[0]
                                score = doc_score[1]
                                tt = 1
                                if doc_id in documents:
                                    documents[doc_id] = documents[doc_id] + float(score)
                                else:
                                    documents[doc_id] = float(score)
                        else:
                            doc_score = item.split(":")
                            doc_id = doc_score[0]
                            score = doc_score[1]
                            tt = 1
                            union_list = list()
                            if doc_id in documents:
                                documents[doc_id] = documents[doc_id] + float(score)
                            else:
                                documents[doc_id] = float(score)
        else:
            query_bag = query.split()
            length = len(query_bag)
            for i in range(length):
                query_bag[i] = stemmer.stem(query_bag[i])

            for word in query_bag:
                if word not in stop_words and word in word_position:
                    query_words.append(word)

            for word in query_words:
                docs = list()
                flag = 0
                positions = word_position[word]
                for field in positions.keys():
                    position = positions[field]
                    intersection = list()
                    files[field_map[field]].seek(position)
                    s = files[field_map[field]].readline()[:-1]
                    if "," in s:
                        #print(s)
                        items = s.split(",")
                        #print(items)
                        for item in items:
                            #print(item)
                            ind = item.find(":")
                            #doc_score = item[:ind]
                            doc_id = item[:ind]
                            #print(doc_score)
                            score = item[ind+1:]
                            tt = 1
                            if doc_id in documents:
                                documents[doc_id] = documents[doc_id] + float(score)
                            else:
                                documents[doc_id] = float(score)
                    else:
                        doc_score = item.split(":")
                        doc_id = doc_score[0]
                        score = doc_score[1]
                        tt = 1
                        union_list = list()
                        if doc_id in documents:
                            documents[doc_id] = documents[doc_id] + float(score)
                        else:
                            documents[doc_id] = float(score)


        documents = sorted(documents.items(),key = operator.itemgetter(1), reverse = True)
        count = 1
        end = time.time()
        print("Response Time :  " + str(end-start) + "s\n")
        for document in documents:
            position = title_position[int(document[0])-1]
            title_tags.seek(position)
            title = title_tags.readline()[:-1]
            result.append(title)
            print(title)
            count += 1
            if count>10:
                break



def main():
    path_to_index = sys.argv[1]
    search(path_to_index)




if __name__ == '__main__':
        main()