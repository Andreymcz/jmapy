from chemspipy import ChemSpider
from bs4 import BeautifulSoup
import requests

# Chemspi web api utilities
class ChemspiWebDB:
    def __init__(self, api_key):
        self.chemspider_web_api = ChemSpider(api_key)
         # Chemspider search functions
            
    # search compounds that matches name, mass criteria. Return list of matching csid's and a list of warnings
    def find_compound_ids_by_name_mass(self, target_compound_name, target_compound_mass = 0, equal_mass_tolerance_percent = 0.001):
        
        if not target_compound_name.isnumeric():
            print("non-numeric")
            http_ids = http_find_compound_ids_by_name_mass(target_compound_name, target_compound_mass, equal_mass_tolerance_percent)
            if len(http_ids) > 0:
                return http_ids
        
        print("Searching compound by name using web API")
        TOLERATED_ERROR = target_compound_mass * equal_mass_tolerance_percent

        warnings = []
        compound_csids = []
        
        # search compound by name
        found_compounds = self.chemspider_web_api.search(target_compound_name)
        found_compounds.wait()
        print(found_compounds)

        if not found_compounds.success():
            warnings.append("Compound search failed")
            warnings.append(found_compounds.message)
            warnings.append(found_compounds.exception)            
            return compound_csids, warnings

        if found_compounds.count == 0:
            warnings.append("Compound Not found in chemspider web search")

        #print("sucess")
        for result in found_compounds :
            try:
                #print("Result: ")
                #print("ID: ", result.record_id)
                #print("Molecular Formula: ", result.molecular_formula)
                #print("Monoisotopic Mass: ", result.monoisotopic_mass)
                if target_compound_mass > 0 and abs(result.monoisotopic_mass - target_compound_mass) > TOLERATED_ERROR :
                    #print("Mass too diferent, skipping")                    
                    continue # mass too diferent from target, continue search

                compound_csids.append(result.record_id)
            except KeyError:
                warnings.append("Compound csID(" + str(result.record_id) + ") missing needed info")


        return compound_csids
    
    def find_external_references(self, compound_csid, search_databases):
        # search for external references from known databases
        warnings = []
        results = dict()
        for db in search_databases:
            results[db] = []
        
        external_refs = self.chemspider_web_api.get_external_references(compound_csid, search_databases)

        if len(external_refs) == 0 :
            warnings.append("No external references found")

        #print("External References: ", external_refs)
        for ref in external_refs :
            #print("External Source: ", ref['source'], " ID: ", ref['externalId'])
            db_name = ref['source']
            db_comp_id = ref['externalId']
            results[db_name].append(db_comp_id)
        
        return results, warnings
    def find_compound_by_id(self, csid):
        return http_find_compound_by_id(csid)

from dataclasses import dataclass    
@dataclass
class ChemspiCompoundInfo:
        csid: int = -1
        name: str = ""
        molecular_formula: str = ""
        monoisotopic_mass: float = 0.0
        iupac_name: str = "NOT FOUND"
            

def __http_req(address):
    print("Waiting for http request: ", address, "...", end='')
    for i in range(100):
        try:
            r = requests.get(address, timeout=10)
            print("Done");
            return BeautifulSoup(r.text, 'html.parser')
        except requests.exceptions.Timeout:
            print("Timeout, Trying again ...")
            
def __search_compound_by_name(name):
    addr = 'http://www.chemspider.com/Search.aspx?q=' + name
    return __http_req(addr)
    
def __search_compound_by_id(id):
    addr = 'http://www.chemspider.com/Chemical-Structure.' + str(id) + ".html";
    return __http_req(addr)
            
def __extract_single_compound(single_request_result):
    compound_info = ChemspiCompoundInfo()
    
    structure_header = single_request_result.find(id = "ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewDetails_rptDetailsView_ctl00_structureHead")    
    details = single_request_result.find(id = "ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewTabDetailsControl_identifiers_ctl_synonymsControl_SynonymsPanel")
    
    #print(details)
    #print(structure_header.prettify())
    # db name
    db_name = structure_header.find(id = "ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewDetails_rptDetailsView_ctl00_WrapTitle")
    compound_info.name = db_name.get_text()
    
    for li in structure_header.find_all('li'):
        if li.span and li.span.has_attr('class') and li.span['class'][0] == "prop_title":
            ptitle = li.span.string
            if ptitle == "Molecular Formula":
                compound_info.molecular_formula = li.contents[1].get_text()
            elif ptitle == "Monoisotopic mass":
                try:
                    compound_info.monoisotopic_mass = float(str(li.contents[1]).split(" ")[0])
                except:
                    compound_info.monoisotopic_mass = 999999999999.0
            elif ptitle == "ChemSpider ID":
                compound_info.csid = int(li.contents[1])

    for syn in details.find_all('div', class_="syn", recursive=False):        
        SYN_REF_TARGET = "[ACD/IUPAC Name]"

        language = syn.find('span', class_='synonym_language')        
        syn_ref = syn.find('span', class_='synonym_ref')
        if syn_ref != None and syn_ref.string.strip() == SYN_REF_TARGET and language == None:
            if syn.strong:
                compound_info.iupac_name = syn.strong.get_text()
            elif syn.find('span', class_='synonym_cn'):
                compound_info.iupac_name = syn.find('span', class_='synonym_cn').get_text()
            else:
                compound_info.iupac_name = "NOT FOUND"
            
    
    return compound_info

def http_find_compounds_by_name_mass(compound_name, target_compound_mass, equal_mass_tolerance_percent = 0.001):
    TOLERATED_ERROR = target_compound_mass * equal_mass_tolerance_percent
    #print(soup.prettify())
    search_result = __search_compound_by_name(compound_name)

    single_result = search_result.find(id = "ctl00_ctl00_ContentSection_ContentPlaceHolder1_RecordViewDetails_rptDetailsView_ctl00_pnlDetailsView")
    table_results = search_result.find(id="ctl00_ctl00_ContentSection_ContentPlaceHolder1_ResultViewControl1_grid_GridView1")

    if single_result :
        c = __extract_single_compound(search_result)
        if target_compound_mass > 0 and abs(c.monoisotopic_mass - target_compound_mass) > TOLERATED_ERROR :
            return []
        return [c]
    elif table_results:
        # filter results by mass, then search from result_id page
        compounds = []
        for td in table_results.find_all('td', class_='search-id-column'):
            id = td.a.string.strip()
            c = __extract_single_compound(__search_compound_by_id(id))
            if target_compound_mass > 0 and abs(c.monoisotopic_mass - target_compound_mass) > TOLERATED_ERROR :
                continue
            compounds.append(c)
        
        return compounds
    else:
        print("no results")
        return []
    
def http_find_compound_ids_by_name_mass(compound_name, target_compound_mass, equal_mass_tolerance_percent = 0.001):
    ids = []
    for c in http_find_compounds_by_name_mass(compound_name, target_compound_mass, equal_mass_tolerance_percent):
        ids.append(c.csid)
    return ids

def http_find_compound_by_id(compound_id):
    return __extract_single_compound(__search_compound_by_id(compound_id))


def http_find_compound_external_sources_ids(compound_id, external_sources_list):
    
    external_sources_ids = dict()
    for es in external_sources_list:
        external_sources_ids[es] = []
        
    request_response = __http_req('http://www.chemspider.com/ibcontent.ashx?csid=' + str(compound_id) + '&type=ds')
    if not request_response.find('table'):
        return external_sources_ids
    
    
    for tr in request_response.table.tbody.find_all('tr'):
        entries = tr.find_all('td')
        es_name = entries[0].a.get_text()
        if es_name in external_sources_ids:
            es_ids =  entries[1]
            for esid in es_ids.find_all('a'):
                external_sources_ids[es_name].append(esid.get_text())
                
    return external_sources_ids
            
        
        
        
    
        