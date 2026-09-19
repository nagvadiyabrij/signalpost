import asyncio
import sys
from app.agents.company_agent import CompanyAgent
from app.database import SessionLocal, init_db
from app.models.company import Company
from app.validators.identity import IdentityVerifier
import random


# Sample Norwegian organization numbers for testing
# In production, these would come from a permitted source or API
SAMPLE_ORG_NUMBERS = [
    "912345678",  # Example - replace with real numbers
    "987654321",
    "991234567",
]


async def generate_profiles(count: int = 1000):
    """Generate company profiles for Norwegian companies"""
    print(f"Starting profile generation for {count} companies...")
    
    # Initialize database
    init_db()
    
    agent = CompanyAgent()
    verifier = IdentityVerifier()
    
    success_count = 0
    failure_count = 0
    
    try:
        # In a real implementation, you would fetch a list of organization numbers
        # from a permitted public source or API
        org_numbers = SAMPLE_ORG_NUMBERS * (count // len(SAMPLE_ORG_NUMBERS) + 1)
        org_numbers = org_numbers[:count]
        
        for i, org_number in enumerate(org_numbers):
            print(f"Processing {i+1}/{count}: {org_number}")
            
            try:
                # Validate organization number
                if not verifier.is_valid_norwegian_org_number(org_number):
                    print(f"  Invalid organization number: {org_number}")
                    failure_count += 1
                    continue
                
                # Research company
                result = await agent.research_company(org_number)
                
                if result["status"] == "success":
                    success_count += 1
                    print(f"  ✓ Success: {result['company'].get('company_name', 'Unknown')}")
                else:
                    failure_count += 1
                    print(f"  ✗ Failed: {result.get('message', 'Unknown error')}")
                
                # Small delay to be respectful to APIs
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failure_count += 1
                print(f"  ✗ Error: {str(e)}")
    
    finally:
        await agent.close()
    
    # Print summary
    print("\n" + "="*50)
    print("Profile Generation Summary")
    print("="*50)
    print(f"Total attempted: {count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Success rate: {(success_count/count)*100:.1f}%")
    
    # Check database
    db = SessionLocal()
    try:
        total_companies = db.query(Company).count()
        print(f"\nTotal companies in database: {total_companies}")
    finally:
        db.close()


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    asyncio.run(generate_profiles(count))
