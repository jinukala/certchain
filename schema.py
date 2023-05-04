from pydantic import BaseModel
from typing import List, Dict

class Certificate(BaseModel):
    name: str
    parentName: str
    registeredNumber: str
    issuedDate: str
    stream: str
    degree: str
    institution: str

class Reference_Block_Data(Dict):
    action: str
    hash: str

class Block(BaseModel):
    index: int
    nonce: int
    hash: str
    previous_hash: str
    timestamp: str
    reference_blocks: List[Reference_Block_Data]
    data: Certificate

class Search(BaseModel):
    query: str

