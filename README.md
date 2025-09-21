# CarbonChain: Transparent Funding for Sustainable Projects
Project by Samuel Lihn, Eashan Iyer, Jessi Shin, Mateo Taylor

## Problem
Consumer marketed 'carbon offset' programs obscure the carbon credit purchasing process, often funnelling money into low-quality credits and inefficient carbon solutions. 

- Companies are willing to pay for sustainability, but face the risk of **double crediting and greenwashing.** 
- Cities want sustainable projects but face **bureaucratic delays** and lack of funding alternatives. 
- Money is hard to trace, making it hard for clients to know if their money is being well spent.
- It can be difficult for individuals to buy reliable, small amounts of carbon offsets. 

**Result:** billions of dollars of potential climate impact never materializes.

1. **Greenwashing & Lack of Trust**  
   - Many credits sold today are unverifiable or double-counted.  
   - Corporations often purchase credits without clear evidence of real impact.  
   - Many credits are sold on already existing platforms which means no additional emissions reductions are being created

2. **Fragmentation & Opaqueness**  
   - Multiple registries and standards create confusion.  
   - Lack of transparency makes it hard for investors to compare projects and justify their expenses.

## SETUP:
  Our blockchain setup requires a linux distribution and Foundry testnet. You can speak to Sam for specific setups because it's a bit complex.
  The rest of our project should set up easily, install the package, and run the backend via /fastapi_webapp, then run the frontend in /client. Note you'll need an env        linking to a MongoDB atlas cluster and a carbonmark sandbox api-key to simulate purchases.

## Solution
We propose an **operating system for sustainable development**, powered by blockchain.  

- **Pick your carbon project**: Credit buyers can access high-quality registry data and fund projects directly, eliminating obscurity.

- **Proof-of-Impact NFTs**: Once a credit is bought, the system mints a certificate (project details, carbon reduced, date) that is **immutable and transparent**. Anyone in the world can view when a contract was created, its transaction history, and associated information. This improves transparency and traceability.

We also want to make a simple system so that individuals that do not use cryptocurrency are still able to take advantage of the blockchain-based solution. 

## Value Proposition
- **For Investors**: Trustworthy and verifiable climate impact. No double counting.
- **For Projects**: Faster, direct access to capital without bureaucratic drag. 
- **For Corporates/NGOs**: ESG-ready impact reports backed by immutable data. 

## Addressing Challenges
**Why blockchain? Why not a database?**  
- Traditional databases = centralized, prone to tampering and greenwashing.  
- Blockchain = immutable, transparent, globally verifiable by everyone. 

Greenwashing & Lack of Trust → Verifiable Impact**  
 - Smart contracts ensure funds are only released when pre-defined milestones are met.  
 - Every credit is tracked on-chain, with a transparent history of issuance, transfer, and retirement.  
 - Future roadmap includes integrations with IoT devices, satellite imagery, and independent verifiers to provide **real-world proof** of carbon reduction.  

Isn’t this just another carbon credit scheme?  
Most existing platforms focus on **secondary trading of offsets**. Our focus is on **primary funding for real projects**.  
- Milestone-based smart contracts release funds only after verified progress.  
- This closes the loop between **investor → project → verified outcome**, something current credit markets don’t achieve.  

What about regulatory or legal issues?  
Our MVP runs on a **testnet demo**, meaning no real money and no regulatory exposure.  
- Future versions can align with existing frameworks (green bonds, Verified Carbon Standard).  

How will you get adoption?  
We see adoption happening in three stages:  

1. **Early Adopters (Low-barrier pilots)**  
   - Universities, NGOs, and community projects are the ideal first users.  
   - They face fewer regulatory hurdles and are motivated to showcase transparency in sustainability initiatives.  

2. **Scaling Partners (Municipalities, mid-size organizations)**  
   - Cities and regional governments increasingly need to report climate progress.  
   - Our platform provides a cost-effective and auditable way to fund local green projects and share outcomes publicly.  

3. **Corporates & Institutional Investors (High-volume adoption)**  
- According to PwC, ESG-focused institutional investment is projected to grow to **US$33.9 trillion by 2026**, making up **21.5% of total assets under management** ([PwC Report](https://www.pwc.com/id/en/media-centre/press-release/2022/english/esg-focused-institutional-investment-seen-soaring-84-to-usd-33-9-trillion-in-2026-making-up-21-5-percent-of-assets-under-management-pwc-report.html)).  
- Our platform lowers transaction friction and ensures **verifiable outcomes**, directly addressing investor and compliance needs.  
- We lower transaction friction and provide proof of impact, which directly helps them meet compliance and investor demands.  

What if the project data is faked?  
- Short-term: rely on **trusted third-party verifiers**.  
- Long-term: integrate **sensor-driven proof** (satellite imagery for reforestation, smart meters for renewable energy).  
- Blockchain ensures that once submitted, **data cannot be altered or erased**.  

## Tech Stack
### Frontend
- Next.js
- React
- Auth0
- Axios
- GSAP

### Backend
- FastAPI
- Web3.py
- MongoDB Atlas

### Blockchain
- Forge Testnet

## Team
- **Samuel Lihn**
- **Eashan Iyer**
- **Jessi Shin**
- **Mateo Taylor**
