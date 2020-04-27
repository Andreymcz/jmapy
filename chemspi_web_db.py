from chemspipy import ChemSpider
# Chemspi web api utilities
class ChemspiWebDB:
    def __init__(self, api_key):
        self.chemspider_web_api = ChemSpider(api_key)
         # Chemspider search functions
            
    # search compounds that matches name, mass criteria. Return list of matching csid's and a list of warnings
    def find_compounds_by_name_mass(self, target_compound_name, target_compound_mass = 0, equal_mass_tolerance_percent = 0.001):
        TOLERATED_ERROR = target_compound_mass * equal_mass_tolerance_percent

        warnings = []
        compound_csids = []
        
        # search compound by name
        found_compounds = self.chemspider_web_api.search(target_compound_name)
        found_compounds.wait()

        if not found_compounds.success():
            warnings.append("Compound search failed")
            warnings.append(found_compounds.message)
            warnings.append(found_compounds.exception)            
            return compound_csids, warnings

        if found_compounds.count == 0:
            warnings.append("Compound Not found in chemspider web search")

        for result in found_compounds :
            try:
                #print("Result: ")
                #print("ID: ", result.record_id)
                ##print("Molecular Formula: ", result.molecular_formula)
                #print("Monoisotopic Mass: ", result.monoisotopic_mass)
                if target_compound_mass > 0 and abs(result.monoisotopic_mass - target_compound_mass) > TOLERATED_ERROR :
                    #print("Mass too diferent, skipping")                    
                    continue # mass too diferent from target, continue search

                compound_csids.append(result.record_id)
            except KeyError:
                warnings.append("Compound csID(" + str(result.record_id) + ") missing needed info")


        return compound_csids, warnings
    
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
        