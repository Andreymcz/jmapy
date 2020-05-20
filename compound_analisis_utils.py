from bs4 import BeautifulSoup
import requests
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from diskcache import Cache

cache = Cache("cached_data")

def requests_retry_session(
    retries=5,
    backoff_factor=0.3,
    status_forcelist=(429, 500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@cache.memoize(name = "httpreq")
def __cached_http_req(address, sleep_before = 0.5):    
    session = requests_retry_session()    
    while True:
        try:
            time.sleep(sleep_before)            
            response = session.get(
                address, timeout=10
            )
        except Exception as x:
            print( x.__class__.__name__, ', trying again')
            sleep_before += 5
        else:
            print('status=', response.status_code, end = '')                  
            return response.text

def __http_req(address, sleep_before = 0.5):
    t0 = time.time()
    print("Waiting for http request: ", address, "...", end='')
    html = __cached_http_req(address, sleep_before);    
    t1 = time.time()
    print('Done. Took', t1 - t0, 'seconds')
    return BeautifulSoup(html, 'html.parser')
    
    
def remove_duplicated_entries(compounds_table):
    
    NAME_COL = 'Name'
    AREA_COL = 'Area (Max.)'
    RT_COL = 'RT [min]'
        
    # sort by name and Area in descending order
    sort_columns = [NAME_COL, AREA_COL , RT_COL]
    #print("########### Sorting data by #############")
    compounds_table.Name = compounds_table.Name.apply(lambda x: x.lower())
    
    compounds_table.sort_values(by=sort_columns, inplace=True, ascending=False)
    #print(compounds_table.columns)
    # Get first result for each compound
    last_compound_name = None
    for row_index, row_data in compounds_table.iterrows() :
        if last_compound_name == None or last_compound_name != row_data[NAME_COL]:
            last_compound_name = row_data[NAME_COL]
            #print(last_compound_name)
            #print("Selected unique compound: ", row_data[NAME_COL], "(", row_data[column_index[AREA_COL]], ")")
            continue
        #print("Discarded compound: ", row_data[NAME_COL], "(", row_data[column_index[AREA_COL]], ")")
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
    
def CSID_list_to_string(ids):
    csids = ""
    if len(ids) > 1 :
        for csid in ids:
            csids += str(csid) + ";"       
    elif len(ids) == 1 :
        csids = ids[0]
    return csids

def equal_compound_mass(mass1, mass2, equal_mass_tolerance_percent = 0.001):
    TOLERATED_ERROR = mass1 * equal_mass_tolerance_percent
    return mass1 > 0 and abs(mass2 - mass1) < TOLERATED_ERROR