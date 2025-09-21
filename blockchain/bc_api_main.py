from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from carbon_escrow import CarbonEscrowContract
from pydantic import BaseModel
from typing import List
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
FACTORY_ADDRESS = "0x68B1D87F95878fE05B998F19b66F4baba5De1aed"

# Initialize factory contract handler
contract_handler = CarbonEscrowContract(
    factory_abi_path="forge/out/CarbonEscrow.sol/CarbonEscrow.json",
    contract_abi_path="forge/out/CarbonProject.sol/CarbonProject.json",
    web3_provider="http://localhost:8545",
    contract_address=FACTORY_ADDRESS
)

class FundProjectRequest(BaseModel):
    user_id: str
    project_address: str
    amount: str  # Amount in ETH (will be converted to wei)

class ProjectProposalRequest(BaseModel):
    proposer_id: str # Crypto ID of proposer
    beneficiary_id: str # Crypto ID of beneficiary
    initiative: str # Name of initiative
    verifier_id: str # Crypto ID of verifier
    metadata_uri: str # URI of project metadata
    goal: float  # Goal amount in ETH

class VerifyRequest(BaseModel):
    verifier_id: str
    project_address: str

class ProjectResponse(BaseModel):
    address: str
    proposer: str
    beneficiary: str
    initiative: str
    verifier: str
    metadata_uri: str
    state: int
    total_contributed: float  # in ETH
    goal: float  # Goal amount in ETH
    contributors: List[dict]

@app.post("/propose")
async def propose(request: ProjectProposalRequest):
    """Create a new project contract"""
    try:
        proposer_addr = get_addr(request.proposer_id)
        beneficiary_addr = get_addr(request.beneficiary_id)
        verifier_addr = get_addr(request.verifier_id)
        proposer_pk = get_pk(request.proposer_id)

        # Convert ETH goal to wei
        goal_wei = w3.to_wei(request.goal, 'ether')

        tx = contract_handler.propose_project(
            beneficiary=beneficiary_addr,
            verifier=verifier_addr,
            initiative=request.initiative,
            metadata_uri=request.metadata_uri,
            goal=goal_wei,
            from_address=proposer_addr,
        )


        signed_tx = w3.eth.account.sign_transaction(tx, private_key=proposer_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return JSONResponse(content={"status": "success", "receipt": Web3.to_json(receipt)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#
@app.post("/fund")
async def fund(request: FundProjectRequest):
    """Fund an existing project"""
    try:
        project = contract_handler.get_project(request.project_address)
        amount_wei = w3.to_wei(request.amount, 'ether')
        funder_addr = get_addr(request.user_id)

        tx = project.fund(
            from_address=funder_addr,
            amount=amount_wei
        )

        user_pk = get_pk(request.user_id)

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=user_pk)

        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return JSONResponse(content={"status": "success", "receipt": Web3.to_json(receipt)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/verify")
async def verify(request: VerifyRequest):
    """Verify a project and release funds"""
    try:
        project = contract_handler.get_project(request.project_address)

        verifier_addr = get_addr(request.verifier_id)
        print(verifier_addr)
        verifier_pk = get_pk(request.verifier_id)

        try:
            tx = project.verify(verifier_addr)
        except Exception as e:
            print(e)

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=verifier_pk)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return JSONResponse(content={"status": "success", "receipt": Web3.to_json(receipt)})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
#
@app.get("/project/{project_address}")
async def get_project(project_address: str):
    """Get project details and contributors"""
    try:
        project = contract_handler.get_project(project_address)
        details = project.get_details()

        contributors = project.get_contributors()

        # Add contribution amounts for each contributor
        contributor_details = []
        for addr in contributors:
            amount, refunded = project.get_contribution(addr)
            contributor_details.append({
                "address": addr,
                "amount": float(w3.from_wei(amount, 'ether')),
                "refunded": refunded
            })

        # Convert wei amounts to ETH for display
        response = ProjectResponse(
            address=project_address,
            proposer=details['proposer'],
            beneficiary=details['beneficiary'],
            verifier=details['verifier'],
            initiative=details['initiative'],
            metadata_uri=details['metadata_uri'],
            state=details['state'],
            total_contributed=float(w3.from_wei(details['total_contributed'], 'ether')),
            goal=float(w3.from_wei(details['goal'], 'ether')),
            contributors=contributor_details
        )

        return JSONResponse(content={"status": "success", "project": response.dict()})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/projects")
async def list_projects():
    """Get all deployed project addresses"""
    try:
        projects = contract_handler.get_all_projects()
        return JSONResponse(content={"status": "success", "projects": projects})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("bc_api_main:app", host="127.0.0.1", port=9000, reload=True)
