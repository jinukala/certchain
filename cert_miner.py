import mine, sync, utils
from peer_config import *
from schema import Certificate
from fastapi import FastAPI, Body, Depends
from fastapi.responses import JSONResponse
from search import add_document_to_index
from fastapi.security.api_key import APIKey
import auth

app = FastAPI()

sync.sync(save=False)
local_chain = sync.sync_refresh_local_chain()

if not local_chain.is_valid():
    local_chain = sync.sync_refresh_network_chain(save=True)

@app.get('/download')
async def blockchain():
    blocks = local_chain.block_list_dict()
    return JSONResponse(content=blocks)

@app.post('/broadcasted_block')
def broadcasted_block(broadcasted_block_data: dict = Body()):
    broadcasted_block = utils.generate_block(broadcasted_block_data)
    status = mine.validate_broadcasted_block(broadcasted_block)
    if status:
        add_document_to_index(broadcasted_block.data, broadcasted_block.hash)
    return JSONResponse(content=status)

@app.get('/refresh')
def refresh_chain(api_key: APIKey = Depends(auth.get_api_key)):
    try:
        local_chain.update_chain()
        return JSONResponse(content=True)
    except Exception as e:
        print(e)
        return JSONResponse(content=False)

@app.get('/check')
def check_chain_validity(api_key: APIKey = Depends(auth.get_api_key)):
    if not local_chain.is_valid():
        return JSONResponse(content=False)
    return JSONResponse(content=True)

@app.post('/mine')
def mine_certficate(raw_data: Certificate,api_key: APIKey = Depends(auth.get_api_key)):
    if not local_chain.is_valid():
        return JSONResponse(content="Chain Corrupted")
    data = utils.format_data(raw_data)
    if data is None:
        return JSONResponse(content='Data is InValid Format')
    local_chain.update_chain()
    last_added_block = local_chain.most_recent_block()
    if data==last_added_block.get_data():
        return JSONResponse(content='Duplicate Data')
    gen_cert_block = utils.create_new_block_from_previous(previous_block=last_added_block, data=data, reference_blocks=None)
    new_cert_block = mine.mine_block(gen_cert_block)
    if new_cert_block is None:
        return JSONResponse(content='Failed to Mine Block')
    try:
        utils.generate_pdf_with_data(new_cert_block)
        local_chain.add_block(new_cert_block)
        mine.broadcast_mined_block(new_cert_block)
        local_chain.self_save()
        add_document_to_index(new_cert_block.data, new_cert_block.hash)
        local_chain.update_chain()
        return new_cert_block.get_hash()
    except Exception as e:
        print(e)
        return JSONResponse(content='Failed to Generate Certificate')
