import json
import time, sys
from tkinter import *
import itertools
import math
import operator
import _pickle as pickle
import pprint

urlDict = {}
searchDict = {}
corpus_length = 0
idxpath = "invidx.pickle"

def query_result():
    global searchDict
    global corpus_length
    global urlDict

    result_txtarea.delete(1.0,END)
    query = searchbar.get()
    result = search(query, searchDict, corpus_length, urlDict)
    if(result == None or len(result[0]) <= 0):
        result_txtarea.insert(END, "No results found.\n")
        return
    result_txtarea.insert(END, str(result[0]))
    result_label["text"] = str(result[1])

#using this to remove duplicates from result list after cosine similarity calculations
#http://www.howtobuildsoftware.com/index.php/how-do/N5h/python-delete-duplicates-from-list-of-tuples
def unique_preserve_order(seq, key=None):
    if key is None:
        key = lambda elem: elem
    seen = set()
    seen_add = seen.add
    augmented = ((key(x), x) for x in seq)
    return [x for k, x in augmented if not (k in seen or seen_add(k))]

def search(query, searchDict, corpus_length, urlDict):
    query_tfidf = {}
    scores = {}
    url_list = []

    if(not query):
        print("No search terms specified..\n")
        return

    terms = query.split()
    terms = [x if x.isupper() else x.lower() for x in terms]

    search_start_time = time.time()

    #calculating cosine similarity
    for term in terms:
        if(term in searchDict):
            term_count = terms.count(term)
            query_tf = 0
            
            if(term_count != 0):
                query_tf = 1 + math.log(1 + term_count, 10)

            query_tfidf[term] = query_tf * math.log(corpus_length / len(searchDict[term]), 10)

            for j in range(len(searchDict[term])):
                url = urlDict[searchDict[term][j]["doc-id"]]
                if(url in scores):
                    scores[url] += query_tfidf[term] * searchDict[term][j]["tf-idf"]
                else:
                    scores[url] = query_tfidf[term] * searchDict[term][j]["tf-idf"]

            score_len = len(scores)
            
            for d in scores:
                scores[d] = scores[d]/score_len
                url_list.append( (d, scores[d]) )
    
    url_list.sort(key=lambda tup: tup[1], reverse=True)
    final_list = unique_preserve_order(url_list, key=operator.itemgetter(0))
    result_string = "\n\n".join([str(i[0]) for i in final_list[:19]])

    result_sz = len(final_list)
    if(result_sz > 20):
        result_sz = 20

    result_info_string = "Returned " + str(result_sz) + " results(" + str(len(final_list)) + " total results) in " + str((time.time() - search_start_time)) + " seconds.\n"
    return(result_string, result_info_string)

def main():
    global searchDict
    global corpus_length
    global urlDict

    load_start_time = time.time()

    print("Loading index...")
    with open(idxpath, 'rb') as invidx:
        searchDict = pickle.load(invidx)

    corpus_length = len(searchDict)

    f = open("bookkeeping.json", 'r')
    urlDict = json.load(f)

    print(corpus_length)
    print("Index loaded in %s seconds" % (time.time() - load_start_time))

    f.close()

#main GUI loop
if __name__ == "__main__":
    main()
    app = Tk()
    app.configure(background="black")
    frame = Frame(app)
    frame.pack()

    app.geometry('750x600')
    app.title('ICS Search Engine')

    searchbar= Entry(app,width=50, foreground="black")
    searchbar.pack(padx=(50,50), pady=(100,0))

    searchbtn = Button(text="Search", highlightbackground="black", command=query_result)
    searchbtn.pack(padx=(50, 50), pady=(10,20))

    result_txtarea = Text(foreground="white", background="black")
    result_txtarea.pack(padx=(50,50),anchor="s")

    result_label = Label(text="", foreground="white", background="black")
    result_label.pack(anchor="s")
    app.mainloop()