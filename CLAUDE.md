# CarbonChain: Transparent Funding for Sustainable Projects
Project by Samuel Lihn, Eashan Iyer, Jessi Shin, Mateo Taylor

## Problem
Those with the capital to fund sustainable development are not being connected with the people and places engineering the solutions that can meaningfully reduce our carbon output and improve the resilience of our cities. 

- Companies are willing to pay for sustainability, but often face **greenwashing risks**.  
- Cities want sustainable projects but face **bureaucratic delays** and lack of funding alternatives.  
- Projects are stalled by **complicated federal funding cycles** with no transparent workaround.  

**Result:** billions of dollars of potential climate impact never materializes.

## Solution
We propose an **operating system for sustainable development**, powered by blockchain.  

- **Escrow Smart Contracts**: Investors fund projects directly. Funds are held in escrow until milestones are validated and are stored as cryptocurrency.
- **Proof-of-Impact NFTs**: Once a milestone is met, the system mints a certificate (project details, carbon reduced, date) that is **immutable and transparent**. Anyone in the world can view when a contract was created, its transaction history, and associated information
- **Simple Dashboard**: Investors see their portfolio of funded projects and verified impact, so they can track their impact.

Existing blockchain carbon platforms (Toucan, KlimaDAO) tokenize *existing credits*, we move **upstream** to fund projects **before they happen**, creating **new carbon savings**.

## Value Proposition
- **For Investors**: Trustworthy and verifiable climate impact. No double counting. Infra can work across countries provided blockchain regulation does not provide a major issue. 
- **For Projects**: Faster, direct access to capital without bureaucratic drag. 
- **For Corporates/NGOs**: ESG-ready impact reports backed by immutable data. 

## Addressing Challenges
**Why blockchain? Why not a database?**  
- Traditional databases = centralized, prone to tampering and greenwashing.  
- Blockchain = immutable, transparent, globally verifiable.  

**What makes us unique?**  
- Current players act as **middlemen** trading after-the-fact credits instead of actually creating new environmental value. 
- We use blockchain as a **decentralized regulatory body** as opposed to an exchange service. 
  - Investors delegate funds to projects.  
  - Smart contracts hold money in escrow.  
  - Funds release only when impact is validated.  

## Hackathon Scope (MVP)
For PennApps, we will deliver a **minimal but powerful demo**:  

- **Investor → Project → Impact Flow**: Select a demo project, invest, and see funds locked.  
- **Milestone Simulation**: Trigger milestone completion (button) to release funds.  
- **Proof-of-Impact NFT**: Minted certificate showing project, carbon saved, date.  
- **Minimal UI**: Project list, funding tracker, investor’s NFT gallery.  

## Business Model
- **Transaction Fees**: % of funds flowing through contracts.  
- **Verification Services**: Paid milestone validation.  
- **Premium Dashboards**: ESG analytics for corporates and investors.  
- **Partnerships & Grants**: Early support from NGOs and foundations.  

---

## Go-To-Market
1. **Pilot** with university & NGO projects (solar rooftops, reforestation).  
2. **Case Studies** proving transparent milestone-based funding.  
3. **Corporate Partnerships** with ESG teams needing traceable impact.  
4. **Integration** into carbon marketplaces & reporting platforms.  


## Differentiation vs Existing Solutions
| Feature                        | Toucan / KlimaDAO | **CarbonChain** |
|--------------------------------|-------------------|-----------------|
| Tokenizes existing credits      | ✅                | ❌ |
| Creates *new* carbon savings    | ❌                | ✅ |
| Milestone-based funding escrow  | ❌                | ✅ |
| Proof-of-Impact certificates    | Limited           | ✅ |
| Accessible UI for non-crypto    | ❌ (DeFi heavy)   | ✅ |

## Tech Stack
- **Smart Contracts**: Solidity (Ethereum Sepolia / Polygon Mumbai testnet).  
- **NFTs**: ERC721 via OpenZeppelin.  
- **Frontend**: React/Next.js + ethers.js.  
- **Wallets**: MetaMask + blockchain explorer for verification.  
- **Demo Data**: 3 mock projects (solar, reforestation, bike lanes).  