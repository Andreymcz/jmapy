def remove_duplicated_entries(compounds_table):
    
    NAME_COL = 'Name'
    AREA_COL = 'Area (Max.)'
    RT_COL = 'RT [min]'
    
    # Map column_name -> column_index
    column_index = dict()
    index = 0
    for c in compounds_table.columns:        
        column_index[c] = index
        index +=1    

    # sort by name and Area in descending order
    sort_columns = [NAME_COL, AREA_COL , RT_COL]
    #print("########### Sorting data by #############")
    compounds_table.sort_values(by=sort_columns, inplace=True, ascending=False)

    # Get first result for each compound
    last_compound_name = None
    name_index = column_index[NAME_COL]
    for row_index, row_data in compounds_table.iterrows() :
        if last_compound_name == None or last_compound_name != row_data[name_index]:
            last_compound_name = row_data[name_index]
            #print("Selected unique compound: ", row_data[name_index], "(", row_data[column_index['Area (Max.)']], ")")
            continue
        #print("Discarded compound: ", row_data[name_index], "(", row_data[column_index['Area (Max.)']], ")")
        compounds_table.drop(index=row_index, inplace = True)

    #print("########## Done filtering Duplicate compounds.... ###########")
    # sort by Name, ascending
    compounds_table.sort_index(inplace=True)
    
    return compounds_table
    
def parse_generated_CSID(csid):
    if type(csid) is str:
        csids = []
        try:
            for sid in csid.split(';'):
                if len(sid) > 0:
                    csids.append(int(sid))
        except ValueError:
            return []
        return csids
    else:
        return [csid] # assume int
