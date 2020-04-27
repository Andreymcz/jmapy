# chemspi Local DB Class
import pandas as pd
from chemspipy import ChemSpider
class ChemspiLocalDB:
    compound_name_column_label = 'Name'
    def __init__(self, filename):
        self.database = pd.read_excel(filename)
        self.db_names = self.database.loc[:,self.compound_name_column_label].copy().str.lower().sort_values()
    
    def find_compound_by_name(self, compound_name):
        compound_name = compound_name.lower()
        search_name_idx = self.db_names.searchsorted(compound_name)    
    
        if (search_name_idx < self.db_names.shape[0]):
            db_row = self.db_names.index[search_name_idx]
            db_entry = self.database.iloc[db_row]
            return db_entry
        
        return None

# end class
