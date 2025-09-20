# CarbonChain: Transparent Funding for Sustainable Projects
Project by Samuel Lihn, Eashan Iyer, Jessi Shin, Mateo Taylor

## Problem
Those with the capital to fund sustainable development are not being connected with the people and places engineering the solutions that can meaningfully reduce our carbon output and improve the resilience of our cities. 

- Companies are willing to pay for sustainability, but face the risk of **double crediting and greenwashing.** 
- Cities want sustainable projects but face **bureaucratic delays** and lack of funding alternatives. 
- Money is hard to trace, making it hard for clients to know if their money is being well spent.
- It can be difficult for individuals to buy reliable, small amounts of carbon offsets. 
- Projects are stalled by **complicated federal funding cycles** with no transparent workaround.  

**Result:** billions of dollars of potential climate impact never materializes.

## Solution
We propose an **operating system for sustainable development**, powered by blockchain.  

- **Escrow Smart Contracts**: Investors fund projects directly. Funds are held in escrow until milestones are validated and are stored as cryptocurrency.
- **Proof-of-Impact NFTs**: Once a milestone is met, the system mints a certificate (project details, carbon reduced, date) that is **immutable and transparent**. Anyone in the world can view when a contract was created, its transaction history, and associated information. This improves transparency and traceability.

Existing blockchain carbon platforms (Toucan, KlimaDAO) tokenize *existing credits*, we move **upstream** to fund projects before they happen, creating **new carbon savings**.

We also want to make a simpler system that makes it easy for individuals unfamiliar with crypto to take advantage of blockchain.

## Value Proposition
- **For Investors**: Trustworthy and verifiable climate impact. No double counting. Infra can work across countries provided blockchain regulation does not provide a major issue. 
- **For Projects**: Faster, direct access to capital without bureaucratic drag. 
- **For Corporates/NGOs**: ESG-ready impact reports backed by immutable data. 

## Addressing Challenges
**Why blockchain? Why not a database?**  
- Traditional databases = centralized, prone to tampering and greenwashing.  
- Blockchain = immutable, transparent, globally verifiable by everyone. 

## Hackathon Scope (MVP) 


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
Frontend(specific tech not important for this) needs to do the following things:
Be well designed, modern looking, and pretty so that the demo looks good. 
Have a dashboard for transactions, a place where anyone can read the blockchain ledger, stripe button for people to but the credits, as well as a good looking landing page that explains the valueprop of our specific project. 

Backend 
We will use fastAPI for the backend API that will interface with the frontend. The backend should also have stripe webhooks to handle payment infrastructure, though this will all be testing for the case of our project. We need a cryptowallet connected to each user account, which will programatically be created for each user account. We will use auto0 for user authentication. Additionally the accounts and the transactions will be stored in a database which we will be using mongoDB for. There is also a web3.py api that will probably be useful here and the backend will primarily be in python. We will be using the CETH ethereum teching clockchain and probably the celera python ai as well here.

## Team
- **Samuel Lihn**
- **Eashan Iyer**
- **Jessi Shin**
- **Mateo Taylor**