import sync, utils
from schema import Search
from dotenv import load_dotenv
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKey
from search import reset_and_create_new_index, fields, search_all_fields, search_field
import auth

app = APIRouter(prefix='/api')

load_dotenv()

block_data = list()
local_chain = sync.sync_refresh_local_chain()
reset_and_create_new_index()

@app.get('/ping')
async def ping():
    return JSONResponse(content=True)


@app.get('/refresh')
def refresh_data(api_key: APIKey = Depends(auth.get_api_key)):
    status = reset_and_create_new_index()
    return JSONResponse(content=status)


@app.post('/validate')
def validate(certPDF: UploadFile = File(...),api_key: APIKey = Depends(auth.get_api_key)):
    if certPDF.filename == '' or certPDF.size < 1:
        return JSONResponse(content='upload a file')
    pdf_data = utils.validate_pdf(certPDF)
    if pdf_data is False:
        return JSONResponse(content='Please Upload a Signed Certificate')
    try:
        local_chain.update_chain()
        pdf_hash = pdf_data.get('data')['hash']
        block = local_chain.find_block_by_hash(pdf_hash)
        check_data = utils.check_data(pdf_data.get('data'), block.data)
        pdf_data['valid'] = check_data
        return JSONResponse(content=pdf_data)
    except Exception as e:
        print(e)
        return JSONResponse(content="Error")


@app.get('/data/{hash}')
async def get_block(hash: str,api_key: APIKey = Depends(auth.get_api_key)):
    local_chain.update_chain()
    if len(hash)!=128:
        return JSONResponse(content="Invalid Hash")
    block = local_chain.find_block_by_hash(hash=hash)
    if block is False:
        return JSONResponse(content="Invalid Hash")
    return JSONResponse(content={"hash": hash, "data":block.get_data()})

@app.post('/search')
async def search_all_data(search:Search,api_key: APIKey = Depends(auth.get_api_key)):
    search_result = search_all_fields(search.query)
    return JSONResponse(content=search_result)

@app.post('/search/{field}')
async def search_field_data(search:Search, field: str,api_key: APIKey = Depends(auth.get_api_key)):
    if field not in utils.fields:
        return JSONResponse(content="Invalid Field")
    search_result = search_field(field,search.query)
    return JSONResponse(content=search_result)

