from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.carbon_escrow import CarbonEscrowContract
from pydantic import BaseModel
from typing import Optional, List
from web3 import Web3


from dotenv import load_dotenv
import os

load_dotenv("test_accounts.env")

# placeholder function for unencrypting and getting private key from keystore
def get_pk(account_id: str):
    return os.getenv(f"{account_id}_PK")

def get_addr(account_id: str):
    return os.getenv(f"{account_id}")
app = FastAPI()

# Initialize Web3 and contracts
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Contract addresses - to be updated after deployment
FACTORY_ADDRESS = "0xc6e7DF5E7b4f2A278906862b61205850344D4e7d"

# Initialize factory contract handler
contract_handler = CarbonEscrowContract(
    factory_abi_path="forge/out/CarbonEscrow.sol/CarbonEscrow.json",
    contract_abi_path="forge/out/CarbonProject.sol/CarbonProject.json",
    web3_provider="http://localhost:8545",
    contract_address=FACTORY_ADDRESS
)

class FundProjectRequest(BaseModel):
    user_address: str
    project_address: str
    amount: str  # Amount in ETH (will be converted to wei)

class ProjectProposalRequest(BaseModel):
    proposer_id: str
    beneficiary_id: str
    verifier_id: str
    metadata_uri: str
    deadline: int  # Unix timestamp

class VerifyRequest(BaseModel):
    verifier_address: str
    project_address: str

class ProjectResponse(BaseModel):
    address: str
    proposer: str
    beneficiary: str
    verifier: str
    metadata_uri: str
    state: int
    total_contributed: str  # in ETH
    deadline: int
    contributors: List[dict]

@app.post("/propose")
async def propose(request: ProjectProposalRequest):
    """Create a new project contract"""
    try:

        proposer_addr = get_addr(request.proposer_id)
        beneficiary_addr = get_addr(request.beneficiary_id)
        verifier_addr = get_addr(request.verifier_id)

        proposer_pk = get_pk(request.proposer_id)

        tx = contract_handler.propose_project(
            beneficiary=beneficiary_addr,
            verifier=verifier_addr,
            metadata_uri=request.metadata_uri,
            deadline=request.deadline,
            from_address=proposer_addr,
        )
        print(tx)

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=proposer_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return JSONResponse(content={"status": "success", "receipt": Web3.to_json(receipt)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#
# @app.post("/fund")
# async def fund(request: FundProjectRequest):
#     """Fund an existing project"""
#     try:
#         project = contract_handler.get_project(request.project_address)
#         amount_wei = w3.to_wei(request.amount, 'ether')
#         tx = project.fund(
#             from_address=request.user_address,
#             amount=amount_wei
#         )
#         return JSONResponse(content={"status": "success", "transaction": tx})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @app.post("/verify")
# async def verify(request: VerifyRequest):
#     """Verify a project and release funds"""
#     try:
#         project = contract_handler.get_project(request.project_address)
#         tx = project.verify(request.verifier_address)
#         return JSONResponse(content={"status": "success", "transaction": tx})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
# @app.get("/project/{project_address}")
# async def get_project(project_address: str):
#     """Get project details and contributors"""
#     try:
#         project = contract_handler.get_project(project_address)
#         details = project.get_details()
#         contributors = project.get_contributors()
#
#         # Add contribution amounts for each contributor
#         contributor_details = []
#         for addr in contributors:
#             amount = project.get_contribution(addr)
#             contributor_details.append({
#                 "address": addr,
#                 "amount": w3.from_wei(amount, 'ether')
#             })
#
#         # Convert wei amounts to ETH for display
#         response = ProjectResponse(
#             address=project_address,
#             proposer=details['proposer'],
#             beneficiary=details['beneficiary'],
#             verifier=details['verifier'],
#             metadata_uri=details['metadata_uri'],
#             state=details['state'],
#             total_contributed=w3.from_wei(details['total_contributed'], 'ether'),
#             deadline=details['deadline'],
#             contributors=contributor_details
#         )
#
#         return JSONResponse(content={"status": "success", "project": response.dict()})
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#
@app.get("/projects")
async def list_projects():
    """Get all deployed project addresses"""
    try:
        projects = contract_handler.get_all_projects()
        return JSONResponse(content={"status": "success", "projects": projects})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("bc_api_main:app", host="127.0.0.1", port=8000, reload=True)
