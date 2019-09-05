import json
import re
import sys
from unidecode import unidecode
import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter
import os
from bibtexparser.bparser import BibTexParser
from difflib import SequenceMatcher


def intext_citations(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        fcontent = f.read()

    fcontent = fcontent.replace("textbackslash\"", "")

    newcontent = str(fcontent)
    cites = fcontent.split("\href{https://www.zotero.org/}")[1:-2]
    errorcount=0
    successcount=0
    to_json = None
    for cite in cites:
        try:
            #print(cite.encode("utf-8"))
            #original_cite = cite
            search = re.search(r"(ITEM\s*CSL\\_CITATION\s*\\{)(.*)(csl-citation.json)", cite, re.MULTILINE | re.DOTALL)
            try:
                groups = search.groups()
            except:
                continue

            jsons = groups[1]
            to_json = "{" + jsons.replace("\n"," ").replace("{[}", "[").replace("{]}", "]").replace("\{", "{").replace("\}", "}").replace("\\", "")
            to_json += "csl-citation.json\"}"
            jsond = json.loads(to_json)

            citekeys = ""
            for item in jsond["citationItems"]:

                itemdata = item["itemData"]
                lastname, year, title = "", "", ""
                try:
                    lastname = itemdata["author"][0]["family"] if "author" in itemdata else ""
                except:
                    pass
                try:
                    year = itemdata["issued"]["date-parts"][0][0] if "issued" in itemdata else ""
                except:
                    pass
                try:
                    title = itemdata["title"].split(" ")
                except:
                    pass

                if title[0].lower() in ['a', 'the', 'an']:
                    first_word_title = title[1]
                else:
                    first_word_title = title[0]

                citekeys += lastname+year+first_word_title + ","
                citekeys = citekeys.replace(" ", "")

            citekeys = "\cite{"+unidecode(citekeys[:-1])+"}"


            cite = cite.replace("[", "{[}").replace("]","{]}").replace("{","\{").replace("}","\}").replace("","\\")

            newcontent = newcontent.replace(jsons, citekeys)
            successcount += 1

            #print("Sucess ^^^:  ")
        except Exception as e:
            errorcount+=1
            print("BEGIN ERROR")
            print(to_json)
            print("The error is    >> " + str(e))
            print("END ERROR")
            pass


    newcontent = newcontent.replace("csl-citation.json\"", "")
    newcontent = newcontent.replace("""ZOTERO\_TRANSFER\_DOCUMENT
    
    The Zotero citations in this document have been converted to a format
    that can be safely transferred between word processors. Open this
    document in a supported word processor and press Refresh in the Zotero
    plugin to continue working with the citations.
    """, "")

    newcontent = re.sub(r"(\\href{https://www.zotero.org/}{ITEM\s*CSL\\_CITATION\s*\\{)(.*)(\\}})", r"\2", newcontent)


    print("SUCCESSES " + str(successcount))
    print("ERRORS " + str(errorcount))

    with open(filepath+".with_cites.tex",  'w', encoding='utf-8') as f:
        f.write(newcontent)



def bibfix(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        fcontent = f.read()

    newcontent = unidecode(fcontent)
    newcontent = newcontent.replace("&", "\&").replace("_", "\_")
    bibentries: BibDatabase = bibtexparser.loads(newcontent)

    for comm in bibentries.comments:
        try:
            g = re.search(r"(@[a-z]+{)([A-Za-z0-9\s.:-]+)", comm, re.MULTILINE | re.DOTALL).groups()
            old_key = g[1]
            new_key = old_key.replace(" ", "")
            entry_str = comm.replace(old_key, new_key)
            bibentry:BibDatabase = bibtexparser.loads(entry_str)
            bibentries.entries.extend(bibentry.entries)

        except:
            print(comm)

    bibentries.comments = []

    keys = []
    duplicate_keys = []
    for entry in bibentries.entries:
        if "\_" in entry["ID"]:
            entry["ID"] = entry["ID"].replace("\_", "_")
        key = entry["ID"].lower()
        if key not in keys:
            keys.append(key)
        elif key not in duplicate_keys:
            duplicate_keys.append(key)


    if len(duplicate_keys) > 0:
        print("Duplicate keys: " + str(duplicate_keys))
        
    with open(filepath + ".fixed.bib", 'w') as bibfile:
        bibtexparser.dump(bibentries, bibfile)

filepath = sys.argv[1]
#filepath = "/Users/rfsouza/Dropbox/Doctorate/_Tese/Qualify/bibliography.bib"
_, file_extension = os.path.splitext(filepath)
if file_extension == ".tex":
    intext_citations(filepath)
elif file_extension == ".bib":
    bibfix(filepath)
else:
    print("Extension not recognized")

