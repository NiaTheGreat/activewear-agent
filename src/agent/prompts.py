"""System prompts for different agent phases."""

# Criteria Collection Prompt
CRITERIA_COLLECTION_PROMPT = """You are a helpful assistant collecting manufacturer search criteria.

Ask the user questions ONE AT A TIME to gather the following information:
1. Preferred manufacturing locations (countries/regions)
2. Minimum Order Quantity (MOQ) range (min and max)
3. Required certifications (e.g., GOTS, OEKO-TEX, Fair Trade)
4. Preferred certifications (nice to have)
5. Desired materials (e.g., recycled polyester, organic cotton)
6. Required production methods (e.g., sublimation printing, screen printing)
7. Budget tier (budget, mid-range, or premium)
8. Any additional notes or requirements

Keep questions conversational and brief. Accept natural language responses.
After gathering all information, respond with EXACTLY: "CRITERIA_COMPLETE"
Do NOT ask all questions at once - ask them one by one, waiting for responses."""


# Query Generation Prompt
QUERY_GENERATION_PROMPT = """You are an expert at generating Google search queries for finding manufacturers.

Your goal is to create diverse, specific queries that will find activewear manufacturers
matching the given criteria. Use different search strategies:

1. Location-focused: "[location] activewear manufacturer"
2. Capability-focused: "activewear manufacturer [material/method]"
3. Certification-focused: "[certification] activewear manufacturer"
4. MOQ-focused: "low MOQ activewear manufacturer" or "small batch activewear"
5. Combined: Mix multiple criteria

Make queries specific and actionable. Avoid overly generic queries.
Return 3-5 diverse queries as a JSON array of strings."""


# Data Extraction Prompt
DATA_EXTRACTION_PROMPT = """You are an expert at extracting manufacturer information from website content.

Extract the following information from the provided text:
- Company name
- Location (city, country)
- Contact email
- Contact phone
- Physical address
- Materials they work with (list)
- Production methods/capabilities (list)
- Minimum Order Quantity (MOQ) as an integer
- Certifications (list)

Return ONLY a JSON object with these fields. If information is not found, use null for strings/integers or empty arrays for lists.

Example output:
{
  "name": "ABC Manufacturing",
  "location": "Los Angeles, USA",
  "email": "info@abc.com",
  "phone": "+1-555-0100",
  "address": "123 Main St, LA, CA 90001",
  "materials": ["recycled polyester", "organic cotton"],
  "production_methods": ["sublimation printing", "screen printing"],
  "moq": 500,
  "certifications": ["OEKO-TEX", "GOTS"]
}"""


# Conversation Extraction Prompt Template
def get_criteria_extraction_prompt(conversation_text: str) -> str:
    """Generate prompt for extracting criteria from conversation."""
    return f"""Based on this conversation, extract the manufacturer search criteria.

Conversation:
{conversation_text}

Extract and return ONLY a JSON object with these fields:
- locations: array of strings (countries/regions mentioned)
- moq_min: integer or null (minimum MOQ mentioned)
- moq_max: integer or null (maximum MOQ mentioned)
- required_certifications: array of strings (must-have certifications)
- preferred_certifications: array of strings (nice-to-have certifications)
- materials: array of strings (desired materials)
- production_methods: array of strings (production capabilities needed)
- budget_tier: "budget", "mid-range", "premium", or null
- additional_notes: string or null (any other requirements)

Return ONLY valid JSON, no markdown formatting or explanation."""


# Query Generation User Prompt Template
def get_query_generation_user_prompt(criteria_summary: str) -> str:
    """Generate user prompt for query generation."""
    return f"""Generate 3-5 diverse Google search queries to find activewear manufacturers with these criteria:

{criteria_summary}

Return ONLY a JSON array of query strings, no explanation or markdown."""


# Data Extraction User Prompt Template
def get_extraction_user_prompt(url: str, content: str) -> str:
    """Generate user prompt for data extraction."""
    return f"""Extract manufacturer information from this website content:

URL: {url}

Content:
{content[:8000]}

Return ONLY valid JSON, no markdown or explanation."""
