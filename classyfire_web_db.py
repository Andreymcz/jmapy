import os
import json
import requests

def main():
    infile = [f for f in os.listdir('.') if f.endswith('.json')][0]
    ids = ['identifier', 'smiles']
    keys = ['kingdom', 'superclass', 'class', 'subclass']
    with open(infile) as f:
        data = json.load(f)
    with open('results.csv', 'a') as out:
        out.write(';'.join(ids + keys) + '\n')
        for e in data['entities']:
            out.write(';'.join([e[k] for k in ids] + [e[k]['name'] for k in keys if e[k] is not None]) + '\n')

def search_smiles():
    url = 'http://classyfire.wishartlab.com/queries'
    ids = ['identifier', 'smiles']
    keys = ['kingdom', 'superclass', 'class', 'subclass']
    with open('results.csv', 'a') as out:
        out.write(';'.join(ids + keys) + '\n')
    with open('smiles.txt') as f:
        for l in f:
            smile = l.strip()
            print(smile)
            #{:label => label, :query_input => input, :query_type => type}.to_json
            params = {'label':'teste', 'query_input':smile, 'query_type':'STRUCTURE'}
            try:
                r = requests.post(url=url, json=params, headers={'Accept':'application/json'})
                data = r.json()
                print(data)
                print(data['id'])
                r = requests.get(url + f"/{data['id']}.json")
                data = r.json()
                print(data['entities'])
                with open('results.csv', 'a') as out:
                    for e in data['entities']:
                        out.write(';'.join([e[k] for k in ids] + [e[k]['name'] for k in keys if e[k] is not None]) + '\n')
            except:
                with open('results.csv', 'a') as out:
                    out.write(smile + '\n')

if __name__ == '__main__':
    search_smiles()
    #main()
