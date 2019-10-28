import os, io, re
import os.path as path
import sys
import math
import ujson
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.corpus import stopwords
import time
import pickle

final_dict = {}
walk_dir = "WEBPAGES_RAW"
root_counter = 0
subdir_fc = 0
doc_length = 0
doc_count = 0
curr_doc_count = 0
file_number = 0
stopWords = set(stopwords.words('english'))

# adapted from https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def remove_html(element):
    if element.parent.name in ['style', 'script', 'meta']:
        return False
    if isinstance(element, Comment):
        return False
    return True

# adapted from https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text#1983219
# we utilize BS4 in these functions to grab all visible text from the pages using "html5lib" html parser
def text_from_html(body):
    soup = BeautifulSoup(body, 'html5lib')
    texts = soup.findAll(text=True)
    visible_texts = [x for x in texts if remove_html(x) == True]
    return (u" ".join(t.strip() for t in visible_texts), [v.parent.name for v in visible_texts])

def tokenizeInput( lines ):
    p = re.compile("\\b[\\w]*[a-zA-z]{2,}[\\w]*\\b", re.UNICODE)
    tok_lines = [re.findall(p,s) for s in lines]
    final_list = []
    for i in tok_lines:
        final_list.append( [x if x.isupper() else x.lower() for x in i] )
    return final_list

def countOccurences(lines):
    occ_dict = {}

    for i in range(len(lines)):
        for word in lines[i]:
            if word not in occ_dict:
                occ_dict[word] = 0
            occ_dict[word] += 1

    return occ_dict

walk_dir = os.path.abspath(walk_dir)

start_time = time.time()

# to walk directories, we adapt code from this post
# https://stackoverflow.com/questions/2212643/python-recursive-folder-read
for root, subdirs, files in os.walk(walk_dir):
    subdir_fc = 0
    print(root_counter)
    root_counter += 1

    for filename in files:
        doc_length = 0

        if(filename == "bookkeeping.json" or filename == "bookkeeping.tsv" or filename.startswith(".")):
            continue
        file_path = os.path.join(root, filename)
        
        doc_count += 1
        curr_doc_count += 1
        subdir_fc += 1

        with open(file_path, 'rb') as f:
            f_content = f.read()
        
            html_content = text_from_html(f_content)
            html_content_lines = html_content[0].splitlines()
            html_line = tokenizeInput(html_content_lines)
            html_line = [x for x in html_line if x != None]
            for i in html_line:
                doc_length += len(i)
	
            temp_dict = countOccurences(html_line)

            for i in temp_dict:
                frequency = 0

                if(temp_dict[i] != 0):
                    frequency = 1 + (math.log(temp_dict[i],10))

                if(i not in stopWords):
                    current_doc_id = str(os.path.basename(os.path.dirname(file_path))) + "/" + str(filename)
                    if(i not in final_dict):
                        final_dict[i] = [{"doc-id": current_doc_id, "tf-idf" : frequency, "tag-type" : html_content[1][0]}]
                    else:
                        dup_flag = 0
                        for j in range(len(final_dict[i])):
                            if(current_doc_id in final_dict[i][j]["doc-id"]):
                                dup_flag = 1

                        if(dup_flag == 0):
                            final_dict[i].append({"doc-id": current_doc_id, "tf-idf" : frequency, "tag-type" : html_content[1][0]})
    print("curr_docs-->" + str(curr_doc_count))



#calculating tf-idf with frequency
for term in final_dict:
    for j in range(len(final_dict[term])):
        idf = math.log( float(doc_count) / (len(final_dict[term])), 10)
        tfidf = idf * final_dict[term][j]["tf-idf"]
        final_dict[term][j]["tf-idf"] = tfidf

#pickling dictionary        
with open('invidx.pickle', 'wb') as handle:
    pickle.dump(final_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

# optional code for tag weighting
# for term in final_dict_weighted:
#     for j in range(len(final_dict_weighted[term])):
#         if(final_dict[term][j]["tag-type"] == "title"):
#             final_dict[term][j]["tf-idf"] *= 1.5
#         if(final_dict[term][j]["tag-type"] == "strong"):
#             final_dict[term][j]["tf-idf"] *= 1.3
#         if(final_dict[term][j]["tag-type"] == "b"):
#             final_dict[term][j]["tf-idf"] *= 1.1

# print("final dict size-->" + str(len(final_dict)))
# print("--- %s seconds ---" % (time.time() - start_time))