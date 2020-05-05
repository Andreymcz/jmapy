# chemspi Local DB Class
import pandas as pd
from chemspipy import ChemSpider
class ChemspiLocalDB:
    compound_name_column_label = 'Name'
    def __init__(self, filename):
        self.database = pd.read_excel(filename)
        self.db_names = self.database.loc[:,self.compound_name_column_label].copy().str.lower().sort_values()
    
    def find_compounds_by_name_mass(self, compound_name, compound_mass, equal_mass_tolerance_percent = 0.001):
        TOLERATED_ERROR = compound_mass * equal_mass_tolerance_percent
        
        compound_name = compound_name.lower()
        search_name_idx = self.db_names.searchsorted(compound_name)
        
        while search_name_idx < self.db_names.shape[0]:
            db_row = self.db_names.index[search_name_idx]
            db_entry = self.database.iloc[db_row]
            #print("Candidate: ",db_entry.Name.lower(), " ", db_entry['Molecular Weight'])
            if db_entry.Name.lower() != compound_name:
                return None
            else:
                # check mass                
                if compound_mass > 0 and abs(db_entry['Molecular Weight'] - compound_mass) < TOLERATED_ERROR:
                    return db_entry
            
            search_name_idx += 1
        
    
        if (search_name_idx < self.db_names.shape[0]):
            db_row = self.db_names.index[search_name_idx]
            db_entry = self.database.iloc[db_row]
            return db_entry
        
        return None

# end class
