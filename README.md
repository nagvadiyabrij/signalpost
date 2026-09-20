# Signalpost - Norwegian Company Information Research Tool

A production-ready web application for researching Norwegian companies with verified, source-backed information. Every factual claim is linked to its source with evidence and timestamps.

## Project Overview

Signalpost is a full-stack application that:
- Accepts Norwegian organization numbers (9 digits)
- Researches companies from multiple permitted public sources
- Verifies company identity to prevent wrong-company matches
- Extracts and validates facts with evidence
- Displays comprehensive company profiles with source links
- Maintains strict anti-hallucination rules

## Features

- **Company Identity Verification**: Uses organization numbers as primary identifiers
- **Evidence-Backed Facts**: Every fact includes source URL, name, and retrieval date
- **Multi-Source Research**: Brønnøysundregistrene, company websites, annual reports
- **Financial Data Safety**: Currency, financial year, and source for every financial value
- **Freshness Tracking**: Retrieval dates and preference for newer sources
- **Conflict Resolution**: Priority-based source selection
- **No Fabrication**: Unknown facts shown as unavailable rather than guessed

## Technology Stack

### Frontend
- Next.js 15
- React
- TypeScript
- Tailwind CSS

### Backend
- FastAPI
- Python 3.11
- SQLAlchemy
- SQLite (development) / PostgreSQL (production)

## Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create environment file:
```bash
cp .env.example .env
```

6. Edit `.env` with your configuration (optional for basic usage):
```env
DATABASE_URL=sqlite:///./data/signalpost.db
OPENAI_API_KEY=your_key_here  # Optional
SEARCH_API_KEY=your_key_here  # Optional
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Option 1: Run Separately (Development)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Website Links

- Public demo: [https://long-sloths-cross.loca.lt](https://long-sloths-cross.loca.lt) *(temporary LocalTunnel URL)*
- Website: [http://127.0.0.1:3000](http://127.0.0.1:3000)
- Login: [http://127.0.0.1:3000/login](http://127.0.0.1:3000/login)
- Companies: [http://127.0.0.1:3000/companies](http://127.0.0.1:3000/companies)
- Admin: [http://127.0.0.1:3000/admin](http://127.0.0.1:3000/admin)

### Authentication

- Login: `/login`
- Register: `/register`
- Admin dashboard: `/admin`

Create or promote an administrator from the `backend` directory:
```bash
python -m app.create_admin --email admin@example.com --name Admin
```

### Option 2: Docker (Recommended)

```bash
docker-compose up --build
```

## Usage

### Web Interface

1. Open the frontend URL configured for your environment.
2. Enter a Norwegian organization number (9 digits)
3. Click "Find Company"
4. View the company profile with verified facts and sources

### API Endpoints

**Search for Company:**
```bash
POST `/api/company/search`
Content-Type: application/json

{
  "organization_number": "912345678"
}
```

**Get Company Profile:**
```bash
GET `/api/company/{organization_number}`
```

**Health Check:**
```bash
GET `/api/health`
```

**System Stats:**
```bash
GET `/api/stats`
```

### CLI (Generate Profiles)

Generate company profiles in bulk:
```bash
cd backend
python -m app.generate_profiles --count 1000
```

## Architecture

### Pipeline Stages

1. **Company Resolution**: Resolve canonical company identity from Brønnøysundregistrene
2. **Targeted Search**: Search additional sources using organization number and company name
3. **Source Extraction**: Fetch pages and extract candidate facts
4. **Identity Verification**: Verify information belongs to correct company
5. **Evidence Validation**: Validate every fact has source and evidence
6. **Fact Normalization**: Normalize dates, currency, numbers
7. **Conflict Resolution**: Resolve conflicting information using source priority
8. **Caching**: Cache results to minimize redundant requests

### Source Priority

1. Official government registry (Brønnøysundregistrene)
2. Official company source
3. Official annual report
4. Reliable public financial source
5. Other permitted public source

## Data Sources

### Primary Source
- **Brønnøysundregistrene**: Official Norwegian Register of Business Enterprises
  - Company identity and registration information
  - Address, industry, status, company type

### Secondary Sources
- **Company Websites**: Contact information, descriptions
- **Annual Reports**: Financial information
- **Public Financial Sources**: Where legally and technically accessible

## Evidence Strategy

Every fact includes:
- `source_url`: The actual URL where information was found
- `source_name`: Name of the source (e.g., "Brønnøysundregistrene")
- `retrieved_at`: When we fetched the information
- `source_published_date`: When the source was published (if available)
- `confidence`: Confidence score based on source authority

## Identity Verification

We verify company identity using:
1. **Organization Number**: Exact match (primary identifier)
2. **Company Name**: Secondary verification
3. **Address**: Tertiary verification
4. **Domain**: Additional confirmation

If organization number conflicts, information is rejected.

## Freshness

- Current facts (status, address, management): Refreshed on each research run
- Historical financial data: Preserved with financial year
- All facts include `retrieved_at` timestamp
- Newer sources preferred for current information

## Cost Estimation

### Per Company (Average)
- HTTP requests: 5-10
- LLM calls: 0-2 (optional)
- Estimated cost: $0.01 - $0.05

### For 100 Companies
- HTTP requests: 500-1000
- LLM calls: 0-200
- Estimated cost: $1 - $5

### For 1,000 Companies
- HTTP requests: 5,000-10,000 (with caching, actual ~2,000)
- LLM calls: 0-2,000
- Estimated cost: $5 - $10

*Note: Costs depend on which optional APIs are configured. Basic usage with Brønnøysund API is free.*

## Request Limits

The system is designed to stay within:
- **2,000 outbound requests** per session
- **45 minutes** execution time
- **$10** declared external API costs

Implemented controls:
- Request budget manager
- Caching and deduplication
- Connection pooling
- Configurable concurrency limits
- Retry with exponential backoff

## 1,000 Company Profiles

The profile generation pipeline:
```bash
cd backend
python -m app.generate_profiles --count 1000
```

This will:
1. Fetch real Norwegian organization numbers from permitted sources
2. Research each company
3. Verify company identity
4. Validate all facts with evidence
5. Store in database
6. Report success/failure statistics

**Note**: In a production environment, organization numbers would come from a permitted public source or API. The current implementation uses sample numbers for demonstration.

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Manual Testing
1. Start both frontend and backend
2. Navigate to the frontend URL configured for your environment.
3. Test with a real Norwegian organization number
4. Verify company identity, facts, and sources
5. Check source links open correctly
6. Test refresh functionality

## Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed
- Check virtual environment is activated
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend won't start
- Ensure Node.js 18+ is installed
- Check dependencies are installed: `npm install`
- Verify port 3000 is not in use

### Company not found
- Verify organization number is 9 digits
- Check Brønnøysund API is accessible
- Review backend logs for errors

### Source links broken
- Check backend logs for HTTP errors
- Verify source URLs are accessible
- Check network connectivity

## Security

- API keys stored in `.env` (never committed)
- Input validation on all endpoints
- SQL injection protection via SQLAlchemy
- XSS protection via React
- CORS configured for local development

## Submission Information

See `SUBMISSION.md` for challenge submission details.

## License

This project is built for the Signalpost challenge.

## Support

For issues or questions, please refer to the challenge documentation or create an issue in the repository.
