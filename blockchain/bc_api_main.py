from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.carbon_escrow import CarbonEscrowContract
from pydantic import BaseModel
from typing import Optional, List
from web3 import Web3

app = FastAPI()

# Initialize Web3 and contracts
w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# Contract addresses - to be updated after deployment
FACTORY_ADDRESS = "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512"

# Initialize factory contract handler
contract_handler = CarbonEscrowContract(
    abi_path=".build/__local__.json",
    web3_provider="http://localhost:8545",
    contract_address=FACTORY_ADDRESS
)

class FundProjectRequest(BaseModel):
    user_address: str
    project_address: str
    amount: str  # Amount in ETH (will be converted to wei)

class ProjectProposalRequest(BaseModel):
    proposer_address: str
    beneficiary_address: str
    verifier_address: str
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
        tx = contract_handler.propose_project(
            beneficiary=request.beneficiary_address,
            verifier=request.verifier_address,
            metadata_uri=request.metadata_uri,
            deadline=request.deadline,
            from_address=request.proposer_address
        )
        return JSONResponse(content={"status": "success", "transaction": tx})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/fund")
async def fund(request: FundProjectRequest):
    """Fund an existing project"""
    try:
        project = contract_handler.get_project(request.project_address)
        amount_wei = w3.to_wei(request.amount, 'ether')
        tx = project.fund(
            from_address=request.user_address,
            amount=amount_wei
        )
        return JSONResponse(content={"status": "success", "transaction": tx})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify")
async def verify(request: VerifyRequest):
    """Verify a project and release funds"""
    try:
        project = contract_handler.get_project(request.project_address)
        tx = project.verify(request.verifier_address)
        return JSONResponse(content={"status": "success", "transaction": tx})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
            amount = project.get_contribution(addr)
            contributor_details.append({
                "address": addr,
                "amount": w3.from_wei(amount, 'ether')
            })

        # Convert wei amounts to ETH for display
        response = ProjectResponse(
            address=project_address,
            proposer=details['proposer'],
            beneficiary=details['beneficiary'],
            verifier=details['verifier'],
            metadata_uri=details['metadata_uri'],
            state=details['state'],
            total_contributed=w3.from_wei(details['total_contributed'], 'ether'),
            deadline=details['deadline'],
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
    uvicorn.run("bc_api_main:app", host="127.0.0.1", port=8000, reload=True)
