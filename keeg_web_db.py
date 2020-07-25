import compound_analisis_utils as utils
import re
from bs4 import BeautifulSoup, NavigableString

def search_keeg_info_by_id(keeg_id, info_titles):
    request_result = utils.__http_req('https://www.genome.jp/dbget-bin/www_bget?cpd:' + keeg_id)
    info_values = {value: "" for value in info_titles}
    for title in info_titles:
        title_re = re.compile(title)
        
        # From sub tables
        td = request_result.find("td", text=title_re)
        if(td != None): 
            #print(td)
            value = ""
            for child in td.next_sibling.children:
                if isinstance(child, NavigableString):
                    continue
                value += child.get_text() + ";"
            info_values[title] = value
        
        # from main table
        th = request_result.find("th", text=title_re)
        if(th != None): 
            info_values[title] = th.parent.td.get_text().replace('\n', '')
        

    return info_values