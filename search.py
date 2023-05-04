from whoosh.fields import Schema, TEXT, ID
from whoosh import index, writing
from peer_config import *
from whoosh.qparser import QueryParser, MultifieldParser
import os.path, glob, json
from utils import fields

     
schema = Schema(name=TEXT(stored=True), registeredNumber=ID(stored=True), issuedDate=TEXT(stored=True), stream=TEXT(stored=True), degree=TEXT(stored=True), institution=TEXT(stored=True), hash=TEXT(stored=True))

if not index.exists_in(SEARCHINDEX):
    certchain_search_index = index.create_in(SEARCHINDEX, schema)
else:
    certchain_search_index = index.open_dir(SEARCHINDEX)

def reset_and_create_new_index():
    certchain_search_index_writer = writing.AsyncWriter(certchain_search_index)
    if os.path.exists(CHAINDATA_DIR):
        for filepath in glob.glob(os.path.join(CHAINDATA_DIR, '*.json')):
            with open(filepath, 'r') as block_file:
                try:
                    block_data = json.load(block_file)
                    certchain_search_index_writer.add_document(name=block_data['data']['name'],registeredNumber=block_data['data']['registeredNumber'], issuedDate=block_data['data']['issuedDate'], stream=block_data['data']['stream'], degree=block_data['data']['degree'], institution=block_data['data']['institution'], hash=block_data['hash'])
                except Exception as e:
                    print(e)
                    return False
        certchain_search_index_writer.commit(mergetype=writing.CLEAR)
        return True
    else:
        print("Chain Not Found in Filesystem")
        return False
 
def add_document_to_index(data,hash):
    writer = certchain_search_index.writer()
    try:
        writer.add_document(name=data['name'],registeredNumber=data['registeredNumber'], issuedDate=data['issuedDate'], stream=data['stream'], degree=data['degree'], institution=data['institution'], hash=hash)
        writer.commit()
        return True
    except Exception as e:
        print(e)
        writer.cancel()
        return False
        

def search_field(field, query_term):
    results = []
    with certchain_search_index.searcher() as searcher:
        query = QueryParser(field, certchain_search_index.schema).parse(query_term)
        query_results = searcher.search(query)
        for r in query_results:
            results.append(dict(r.items()))
    return results

def search_all_fields(query_term):
    results = []
    with certchain_search_index.searcher() as searcher:
        query = MultifieldParser(fields, certchain_search_index.schema).parse(query_term)
        query_results = searcher.search(query)
        for r in query_results:
            results.append(dict(r.items()))
    return results
     