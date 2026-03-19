# NEXUS Search - Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- MetaMask or Web3 wallet

## Quick Start with Docker

1. **Clone and Setup**
```bash
cd NEXUS-SEARCH
cp .env.example .env
```

2. **Start All Services**
```bash
docker-compose up -d
```

This starts:
- Backend API (port 8000)
- Frontend (port 3000)
- Redis (port 6379)
- IPFS (port 5001)

3. **Access the Application**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- IPFS Gateway: http://localhost:8080

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat node  # Local blockchain
npx hardhat run scripts/deploy.js --network localhost
```

## Configuration

Edit `.env` files:
- `backend/.env` - Backend configuration
- `frontend/.env.local` - Frontend configuration
- `contracts/.env` - Contract deployment

## API Endpoints

- `GET /api/v1/search?q=query` - Search
- `GET /api/v1/auth/message?address=0x...` - Get auth message
- `POST /api/v1/auth/verify` - Verify signature
- `GET /api/v1/ipfs/{cid}` - Get from IPFS
- `GET /health` - Health check

## Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## Production Deployment

### Vercel (Frontend)

1. Connect GitHub repository
2. Set environment variables
3. Deploy

### Docker (Backend)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Support

- Docs: http://localhost:8000/docs
- GitHub: https://github.com/your-org/nexus-search
- Discord: https://discord.gg/nexus-search
