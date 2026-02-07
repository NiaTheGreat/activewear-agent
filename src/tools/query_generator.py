"""Generate diverse search queries from criteria using Claude."""

import json
import logging
from typing import List

from config import settings
from models.criteria import SearchCriteria
from utils.llm import get_client

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates optimized search queries for finding manufacturers using strategic diversity."""

    def __init__(self):
        """Initialize the query generator."""
        self.client = get_client()

    def generate(self, criteria: SearchCriteria) -> List[str]:
        """
        Generate 7-10 diverse, strategic search queries from criteria.

        Uses multiple search strategies:
        - Direct manufacturer searches (with specific criteria)
        - B2B platform searches (Alibaba, Maker's Row, IndiaMART)
        - Certification/association directory searches
        - Material-specific searches
        - Production method searches
        - MOQ-focused searches
        - Sustainability-angle searches

        Args:
            criteria: SearchCriteria object with user requirements

        Returns:
            List of 7-10 strategic search query strings
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(criteria)

        logger.info("Generating search queries with enhanced strategy...")

        response = self.client.create_message(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=2000,  # Increased for more detailed responses
            temperature=0.5,  # Lower for more consistent quality
        )

        response_text = self.client.extract_text_response(response)

        # Clean up markdown if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            result = json.loads(response_text)

            # Handle both formats: simple list or structured dict
            if isinstance(result, dict) and "queries" in result:
                queries = [item["query"] for item in result["queries"]]
                # Log the strategies used
                logger.info("Generated %d queries using these strategies:", len(queries))
                for item in result["queries"]:
                    logger.info("  - [%s] %s", item.get("strategy", "unknown"), item["query"])
            elif isinstance(result, list):
                queries = result
                logger.info("Generated %d queries", len(queries))
                for q in queries:
                    logger.info("  - %s", q)
            else:
                raise ValueError("Unexpected response format")

            # Ensure we have valid strings
            if not all(isinstance(q, str) and len(q.strip()) > 0 for q in queries):
                raise ValueError("Invalid query format")

            # Limit to MAX_SEARCH_QUERIES
            final_queries = queries[: settings.MAX_SEARCH_QUERIES]
            logger.info("Using %d queries for search", len(final_queries))

            return final_queries

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("Failed to parse LLM response: %s. Using fallback queries.", e)
            # Fallback to basic queries if parsing fails
            fallback_queries = self._generate_fallback_queries(criteria)
            return fallback_queries[: settings.MAX_SEARCH_QUERIES]

    def _build_system_prompt(self) -> str:
        """Build the comprehensive system prompt with all strategies and examples."""
        return """You are an expert at generating strategic Google search queries for finding activewear manufacturers.

# YOUR MISSION
Generate 7-10 diverse, high-quality search queries that will find manufacturers matching specific criteria.
Each query should use a DIFFERENT search strategy to maximize coverage.

# SEARCH STRATEGIES (Use a variety of these)

1. **Direct Manufacturer Searches** - Specific criteria combinations
   - Use industry terms: "OEM", "ODM", "contract manufacturer", "private label"
   - Combine 2-3 criteria: location + material, certification + production method, etc.

2. **B2B Platform Searches** - Target major platforms
   - Use site: operators: site:alibaba.com, site:makersrow.com, site:indiamart.com
   - Combine with location/capability filters

3. **Certification/Association Directories** - Find certified manufacturers
   - Search for: "[certification] directory manufacturers", "GOTS member directory activewear"
   - Target trade associations: "textile manufacturers association [location]"

4. **Material-Specific Searches** - Focus on specific materials
   - "recycled polyester activewear suppliers", "organic cotton sportswear OEM"
   - Combine material + location or material + production method

5. **Production Method Searches** - Target specific capabilities
   - "sublimation printing activewear manufacturer", "cut-and-sew fitness apparel"
   - Use terms: "CMT" (cut-make-trim), "full package manufacturing"

6. **MOQ-Focused Searches** - Emphasize order quantities
   - For low MOQ (<1000): "low MOQ activewear", "small batch sportswear manufacturer"
   - For specific ranges: "activewear manufacturer 500 minimum order"

7. **Sustainability-Angle Searches** - Eco-friendly focus
   - "sustainable activewear manufacturer", "eco-friendly sportswear OEM"
   - "GOTS certified yoga pants manufacturer"

# INDUSTRY TERMINOLOGY TO USE

- **Manufacturing types**: OEM, ODM, contract manufacturer, private label, cut-and-sew, CMT
- **Product terms**: activewear, athletic apparel, sportswear, fitness clothing, performance wear, yoga pants, leggings
- **Location terms**:
  * USA: "domestic", "American-made", "California", "New York", "Los Angeles"
  * China: "Guangdong", "Zhejiang", "Shenzhen", "OEM China"
  * Vietnam/Bangladesh: "CMT Vietnam", "garment manufacturer Bangladesh"
- **Certification terms**: Use quotes for exact match: "OEKO-TEX certified", "GOTS certified"

# QUERY QUALITY EXAMPLES

❌ BAD (too generic):
- "activewear manufacturers"
- "clothing manufacturers USA"
- "sportswear factory"

✅ GOOD (strategic & specific):
- "OEKO-TEX certified sublimation activewear manufacturer California"
- "sustainable yoga pants contract manufacturer Vietnam low MOQ"
- "recycled polyester sportswear OEM manufacturers directory"
- "organic cotton athletic apparel cut-and-sew USA 500 minimum"
- "activewear manufacturer site:alibaba.com Vietnam sustainable"
- "GOTS certified manufacturers member directory activewear"
- "sublimation printing fitness apparel OEM Guangdong China"

# QUERY CONSTRUCTION RULES

1. **Combine 2-3 criteria per query** (not all at once - too narrow)
2. **Use exact phrases with quotes** when needed: "OEKO-TEX certified", "low MOQ"
3. **Vary emphasis** - don't make all queries similar
4. **Balance location coverage** - if multiple locations, spread across queries
5. **Include site: operators** for at least 1-2 queries targeting B2B platforms
6. **Avoid near-duplicates** - each query should have a distinct angle
7. **Prioritize actionable queries** that find manufacturers (not just articles)

# CRITERIA-AWARE LOGIC

- **Low MOQ (<1000)**: Emphasize "low MOQ", "small batch", "startups" in 2+ queries
- **Certifications required**: Make prominent in 2-3 queries + search certification directories
- **Specific materials**: Create material + location/method combinations
- **Sustainability (organic/recycled materials)**: Create sustainability-focused queries
- **Multiple locations**: Balance coverage, don't put all queries on one location

# RESPONSE FORMAT

Return a JSON object with this structure:
{
  "queries": [
    {
      "query": "the actual search query string",
      "strategy": "brief strategy name (e.g., 'B2B Platform', 'Material-Specific')"
    },
    ...
  ]
}

Generate 7-10 queries with DIVERSE strategies. Avoid duplicates."""

    def _build_user_prompt(self, criteria: SearchCriteria) -> str:
        """Build the user prompt with formatted criteria."""
        criteria_parts = []

        if criteria.locations:
            criteria_parts.append(f"📍 Locations: {', '.join(criteria.locations)}")

        if criteria.moq_min is not None or criteria.moq_max is not None:
            moq_str = []
            if criteria.moq_min is not None:
                moq_str.append(f"min: {criteria.moq_min}")
            if criteria.moq_max is not None:
                moq_str.append(f"max: {criteria.moq_max}")
            criteria_parts.append(f"📦 MOQ: {', '.join(moq_str)}")

        if criteria.certifications_of_interest:
            criteria_parts.append(f"✅ Certifications of Interest: {', '.join(criteria.certifications_of_interest)}")

        if criteria.materials:
            criteria_parts.append(f"🧵 Materials: {', '.join(criteria.materials)}")

        if criteria.production_methods:
            criteria_parts.append(f"⚙️ Production Methods: {', '.join(criteria.production_methods)}")

        if criteria.budget_tier:
            criteria_parts.append(f"💰 Budget Tier: {', '.join(criteria.budget_tier)}")

        if criteria.additional_notes:
            criteria_parts.append(f"📝 Notes: {criteria.additional_notes}")

        criteria_summary = "\n".join(criteria_parts) if criteria_parts else "No specific criteria (general search)"

        return f"""Generate 7-10 diverse, strategic search queries for finding activewear manufacturers with these criteria:

{criteria_summary}

Analyze the criteria and select appropriate strategies. Ensure query diversity.
Return the JSON object with queries and their strategies."""

    def _generate_fallback_queries(self, criteria: SearchCriteria) -> List[str]:
        """
        Generate strategic fallback queries if LLM parsing fails.

        Uses a rule-based approach to create diverse queries based on criteria.

        Args:
            criteria: SearchCriteria object

        Returns:
            List of strategic query strings
        """
        queries = []

        # Strategy 1: Direct location-based query
        if criteria.locations:
            for location in criteria.locations[:2]:  # Use up to 2 locations
                queries.append(f"{location} activewear manufacturer OEM")

        # Strategy 2: Material + location combination
        if criteria.materials and criteria.locations:
            queries.append(
                f"{criteria.materials[0]} {criteria.locations[0]} sportswear manufacturer"
            )

        # Strategy 3: Certification-focused
        if criteria.certifications_of_interest:
            cert = criteria.certifications_of_interest[0]
            queries.append(f'"{cert} certified" activewear manufacturers directory')

        # Strategy 4: Production method specific
        if criteria.production_methods:
            method = criteria.production_methods[0]
            queries.append(f"{method} athletic apparel contract manufacturer")

        # Strategy 5: MOQ-focused
        if criteria.moq_min and criteria.moq_min < 1000:
            queries.append("low MOQ activewear manufacturer small batch")
        elif criteria.moq_min:
            queries.append(f"activewear manufacturer {criteria.moq_min} minimum order")

        # Strategy 6: B2B platform search
        if criteria.locations:
            queries.append(
                f"activewear manufacturer site:alibaba.com {criteria.locations[0]}"
            )

        # Strategy 7: Sustainability angle (if relevant materials)
        sustainable_keywords = ["organic", "recycled", "sustainable", "eco"]
        if criteria.materials and any(
            kw in " ".join(criteria.materials).lower() for kw in sustainable_keywords
        ):
            queries.append("sustainable activewear manufacturer eco-friendly")

        # Fallback: If no queries generated, add generic but strategic ones
        if not queries:
            queries = [
                "activewear manufacturer private label",
                "athletic apparel contract manufacturer",
                "sportswear OEM manufacturers directory",
            ]

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)

        logger.info("Generated %d fallback queries", len(unique_queries))
        return unique_queries
