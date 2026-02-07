"""Test the improved query generator with example criteria."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.criteria import SearchCriteria
from tools.query_generator import QueryGenerator

# Configure logging to see the strategy details
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

def main():
    """Test query generation with the example criteria."""

    print("=" * 80)
    print("TESTING IMPROVED QUERY GENERATOR")
    print("=" * 80)
    print()

    # Create the test criteria from the user's example
    criteria = SearchCriteria(
        locations=["USA", "Vietnam"],
        moq_min=500,
        moq_max=2000,
        certifications_of_interest=["OEKO-TEX"],
        materials=["recycled polyester", "organic cotton"],
        production_methods=["sublimation printing"],
        budget_tier="mid-range"
    )

    print("TEST CRITERIA:")
    print(criteria.to_summary())
    print()
    print("=" * 80)
    print()

    # Generate queries
    generator = QueryGenerator()

    print("GENERATING QUERIES...")
    print()

    queries = generator.generate(criteria)

    print()
    print("=" * 80)
    print(f"GENERATED {len(queries)} QUERIES:")
    print("=" * 80)
    print()

    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")

    print()
    print("=" * 80)
    print("ANALYSIS:")
    print("=" * 80)
    print()
    print("✅ Query count:", len(queries))
    print("✅ Average query length:", sum(len(q) for q in queries) // len(queries), "chars")
    print("✅ Unique queries:", len(set(queries)) == len(queries))

    # Check for strategic diversity
    print()
    print("Strategic Elements Found:")

    checks = {
        "Industry terms (OEM/ODM/CMT)": any("OEM" in q or "ODM" in q or "CMT" in q.upper() for q in queries),
        "Site operators (site:)": any("site:" in q for q in queries),
        "Quoted phrases": any('"' in q for q in queries),
        "Location diversity": sum(1 for q in queries if "USA" in q or "America" in q) > 0 and sum(1 for q in queries if "Vietnam" in q) > 0,
        "Material mentions": any("recycled polyester" in q.lower() or "organic cotton" in q.lower() for q in queries),
        "Certification focus": any("OEKO-TEX" in q or "certified" in q for q in queries),
        "MOQ emphasis": any("MOQ" in q or "minimum" in q or "small batch" in q for q in queries),
        "Production method": any("sublimation" in q.lower() for q in queries),
    }

    for check, passed in checks.items():
        symbol = "✅" if passed else "❌"
        print(f"  {symbol} {check}")

    print()
    print("=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
