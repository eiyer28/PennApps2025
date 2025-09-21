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


1. **Greenwashing & Lack of Trust**  
   - Many credits sold today are unverifiable or double-counted.  
   - Corporations often purchase credits without clear evidence of real impact.  
   - Many credits are sold on already existing platforms which means no additional emissions reductions are being created

2. **Fragmentation & Opaqueness**  
   - Multiple registries and standards create confusion.  
   - Lack of transparency makes it hard for investors to compare projects and justify their expenses.

3. **Limited Accessibility**  
   - Communities and engineers working on grassroots solutions face barriers to entry.  
   - Funding typically flows only to large, well-known organizations.  

4. **Slow & Manual Verification**  
   - Validation processes are lengthy, manual, and prone to error.  
   - Little use of real-time data (IoT, satellite, sensors) to confirm reductions.  

## Solution
We propose an **operating system for sustainable development**, powered by blockchain.  

- **Escrow Smart Contracts**: Investors fund projects directly. Funds are held in escrow until milestones are validated and are stored as cryptocurrency.
- **Proof-of-Impact NFTs**: Once a milestone is met, the system mints a certificate (project details, carbon reduced, date) that is **immutable and transparent**. Anyone in the world can view when a contract was created, its transaction history, and associated information. This improves transparency and traceability.

Existing blockchain carbon platforms (Toucan, KlimaDAO) tokenize *existing credits*, we move **upstream** to fund projects before they happen, creating **new carbon savings**.

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

What if the data is faked?  
- Short-term: rely on **trusted third-party verifiers**.  
- Long-term: integrate **sensor-driven proof** (satellite imagery for reforestation, smart meters for renewable energy).  
- Blockchain ensures that once submitted, **data cannot be altered or erased**.  

How do you make money?  
- **Transaction fees** (1–5% of funding flows).  
- **Premium dashboards** for corporates and investors.  
- **Verification fees** for projects seeking credibility.  
The fast-growing ESG and impact investing market provides a strong revenue base.  

What differentiates you from existing solutions?  
- They focus on **trading carbon credits**. We focus on **direct funding flows + milestone verification**.  
- Our platform is designed for **usability** by investors, NGOs, and cities—not just crypto traders.  
- Unique angle = **transparency + proactive accountability**, ensuring that money leads to measurable outcomes.  

## Hackathon Scope (MVP) 


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
### Frontend
- Next.js
- React
- Auth0
- Axios
- GSAP

### Backend
- FastAPI
- Web3.py
- PyMongo
- Motor
- Uvicorn
- Jinja2
- Pydantic
- python-jose
- python-multipart
- Authlib
- Requests

### Blockchain
- Sepolia Testnet

## Team
- **Samuel Lihn**
- **Eashan Iyer**
- **Jessi Shin**
- **Mateo Taylor**