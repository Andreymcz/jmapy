import compound_analisis_utils as utils

def search_metabolite_info_by_id(hmdb_id, info_titles):
    request_result = utils.__http_req('https://hmdb.ca/metabolites/' + hmdb_id)
    info_values = {value: "" for value in info_titles}
    for title in info_titles:
        th = request_result.find("th", string=title)
        if(th != None):
            info_values[title] = th.next_sibling.get_text().strip()

    return info_values

def search_metabolites_by_name(metabolite_name):
    search_result = utils.__http_req("https://hmdb.ca/unearth/q?utf8=%E2%9C%93&query=\"" +metabolite_name + "\"&searcher=metabolites")
    ids = []
    for link in search_result.find_all('div', class_="result-link"):
        ids.append(link.a.get_text())
    return ids

def search_metabolites_by_name_mass(metabolite_name, metabolite_mass,  equal_mass_tolerance_percent = 0.001):
    TOLERATED_ERROR = metabolite_mass * equal_mass_tolerance_percent
    #if target_compound_mass > 0 and abs(c.monoisotopic_mass - target_compound_mass) > TOLERATED_ERROR : discard
    result_ids = []
    for metabolite_id in search_metabolites_by_name(metabolite_name):
        try:
            info = search_metabolite_info_by_id(metabolite_id, ["Monoisotopic Molecular Weight"])
            mono_mass = float(info["Monoisotopic Molecular Weight"])
            if metabolite_mass > 0 and abs(mono_mass - metabolite_mass) > TOLERATED_ERROR :
                continue
            result_ids.append(metabolite_id)
        except ValueError:
            print("ValueError for metabolite", metabolite_name)
        
    return result_ids