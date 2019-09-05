import json
import re
import sys

filepath = sys.argv[1]
with open(filepath,'r', encoding='utf-8') as f:
    fcontent = f.read()

newcontent = str(fcontent)
cites = fcontent.split("\href{https://www.zotero.org/}")[1:-2]
errorcount=0
successcount=0
for cite in cites:
    try:
        original_cite = cite
        groups = re.search(r"(ITEM\s*CSL\\_CITATION\s*\\{)(.*)(\\})", cite, re.MULTILINE | re.DOTALL).groups()
        jsons = groups[1]

        to_json = "{" + jsons.replace("\n","").replace("{[}", "[").replace("{]}", "]").replace("\{", "{").replace("\}", "}").replace("\\", "") + "}"

        jsond = json.loads(to_json)

        citekeys = ""
        for item in jsond["citationItems"]:
            itemdata = item["itemData"]
            lastname = itemdata["author"][0]["family"] if "author" in itemdata else ""
            year = itemdata["issued"]["date-parts"][0][0] if "issued" in itemdata else ""
            title = itemdata["title"].split(" ")

            if title[0].lower() in ['a', 'the', 'in', 'of']:
                first_word_title = title[1]
            else:
                first_word_title = title[0]

            citekeys += lastname+year+first_word_title + ","

        citekeys = "\cite{"+citekeys[:-1]+"}"

        cite = cite.replace("[", "{[}").replace("]","{]}").replace("{","\{").replace("}","\}").replace("","\\")

        #newcontent = newcontent.replace(r"ITEM\s*CSL\\_CITATION\s*" + jsons, citekeys)
        #newcontent = newcontent.replace(jsons, citekeys).replace("\href{https://www.zotero.org/}"+groups[0],"").replace(groups[2],"").replace("\href{https://www.zotero.org/}{","")
        newcontent = newcontent.replace(jsons, citekeys)
        successcount += 1
    except:
        errorcount+=1
        print("BEGIN ERROR\n" + str(cite))
        print("END ERROR")
        pass


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




