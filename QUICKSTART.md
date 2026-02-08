# Activewear Agent - Quick Start Guide

Get up and running with the **CLI agent** in 5 minutes.

For the **web application** setup, see the main [README.md](README.md).

---

## Prerequisites

- **Python 3.12+**
- **Anthropic API key** - [Get one here](https://console.anthropic.com/)
- **Brave Search API key** (optional) - [Free tier: 2,000 queries/month](https://brave.com/search/api/)

---

## Installation

### 1. Install Dependencies

```bash
cd activewear-agent
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# Recommended (for web search)
BRAVE_API_KEY=BSA-your-actual-key-here

# Optional settings
REQUEST_DELAY_SECONDS=2
SCRAPE_TIMEOUT_SECONDS=30
MAX_MANUFACTURERS=10
```

**Need a Brave API key?** See [BRAVE_SEARCH_SETUP.md](BRAVE_SEARCH_SETUP.md) for detailed setup instructions.

---

## Running the Agent

### Basic Usage

```bash
# Activate virtual environment (if using venv)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the agent with proper Python path
PYTHONPATH="$PWD/src:$PWD" python main.py
```

**Note**: The `PYTHONPATH` setting is required because the agent imports from both `src/` and `config/` directories.

### Alternative: Simplified Command

If you don't want to set `PYTHONPATH` each time, activate the virtual environment:

```bash
source venv/bin/activate
python main.py
```

---

## What Happens When You Run It

### Phase 1: Criteria Collection
Interactive Q&A to gather your manufacturer requirements:
- Locations (USA, Vietnam, China, etc.)
- MOQ range (Minimum Order Quantities)
- Certifications (GOTS, OEKO-TEX, Fair Trade, etc.)
- Materials (recycled polyester, organic cotton, etc.)
- Production methods (sublimation, screen printing, etc.)
- Budget tier (budget, mid-range, premium)

You can:
- Load existing presets
- Enter new criteria
- Save new presets for future use

### Phase 2: Query Generation
Claude generates 7-10 strategically diverse search queries:
- Location-focused queries
- Material-specific queries
- Certification directory searches
- B2B platform searches (Alibaba, Maker's Row)
- Industry terminology (OEM, CMT, cut-and-sew)

### Phase 3: Web Search
Uses Brave Search API to find manufacturer websites:
- Executes up to 5 search queries (configurable)
- Finds 15-30 potential manufacturer URLs
- Deduplicates and ranks results

**No Brave API key?** The agent will prompt you to enter URLs manually. See [SAMPLE_URLS.md](SAMPLE_URLS.md) for test URLs.

### Phase 4: Web Scraping
Scrapes up to 10 manufacturer websites:
- Extracts text content from key pages
- 2-second delay between requests (polite scraping)
- 30-second timeout per site
- Continues if some sites fail

### Phase 5: Data Extraction
Claude extracts structured data from each website:
- Company name and location
- Contact information (email, phone, address)
- MOQ (Minimum Order Quantity)
- Materials they work with
- Production methods/capabilities
- Certifications held

### Phase 6: Evaluation
Scores each manufacturer against your criteria (0-100):
- **Location match**: 25 pts max
- **MOQ match**: 20 pts max
- **Certifications**: 25 pts max
- **Materials**: 15 pts max
- **Production methods**: 15 pts max
- **Bonuses**: Contact info, website quality, etc.

### Phase 7: Excel Output
Generates a formatted Excel file:
- Saved to: `output/manufacturers_YYYY-MM-DD_HH-MM-SS.xlsx`
- Color-coded match scores
- Sortable columns
- All manufacturer details in one spreadsheet

---

## Example Test Criteria

Try these values when prompted:

```
Locations: USA, Vietnam
MOQ Range: 500 to 2000 units
Required Certifications: OEKO-TEX
Preferred Certifications: (leave blank or press Enter)
Materials: recycled polyester, organic cotton
Production Methods: sublimation printing
Budget Tier: mid-range
Additional Notes: Looking for sustainable options
```

---

## Output Format

The Excel file includes these columns:

| Column | Description |
|--------|-------------|
| **Rank** | Position based on match score |
| **Name** | Manufacturer name |
| **Location** | City, country |
| **Website** | Company URL |
| **MOQ** | Minimum order quantity |
| **Match Score** | 0-100 score against criteria |
| **Confidence** | Data quality: low, medium, high |
| **Materials** | Materials they work with |
| **Certifications** | Certifications held |
| **Production Methods** | Production capabilities |
| **Email** | Contact email |
| **Phone** | Contact phone |
| **Address** | Physical address |
| **Notes** | Strengths/weaknesses analysis |
| **Source URL** | URL where data was found |

---

## Using Presets

### Saving a Preset

After entering criteria, the agent will ask:
```
Would you like to save these criteria as a preset? (y/n)
```

Type `y` and provide a name:
```
Enter preset name: Sustainable Yoga Wear
```

Presets are saved in: `config/presets/`

### Loading a Preset

When starting the agent, select option:
```
How would you like to provide search criteria?
1. Answer questions interactively
2. Load existing preset
> 2
```

Then choose from your saved presets.

---

## Configuration

### Via Environment Variables (`.env`)

```bash
# Web scraping
REQUEST_DELAY_SECONDS=2        # Delay between requests
SCRAPE_TIMEOUT_SECONDS=30      # Timeout per site
MAX_MANUFACTURERS=10           # Number of results

# Budget control
BUDGET_LIMIT_USD=50.0          # API spend limit
```

### Via Settings File

Edit [config/settings.py](config/settings.py):

```python
MAX_MANUFACTURERS: int = 10           # Results to return
MAX_SEARCH_QUERIES: int = 5           # Search queries to execute
REQUEST_DELAY_SECONDS: float = 2.0    # Scraping delay
SCRAPE_TIMEOUT_SECONDS: int = 30      # Scraping timeout
BUDGET_LIMIT_USD: float = 50.0        # API budget
```

**Tip**: To get more results, increase `MAX_SEARCH_QUERIES` to 8-10. The query generator creates 10 queries, but by default only the first 5 are used.

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"
**Solution**:
- Ensure you created `.env` file (not just `.env.example`)
- Verify the key is correct and has no quotes
- Check the key at [Anthropic Console](https://console.anthropic.com/)

### "Brave API key invalid"
**Solution**:
- Get a free key: [Brave Search API](https://brave.com/search/api/)
- Follow setup guide: [BRAVE_SEARCH_SETUP.md](BRAVE_SEARCH_SETUP.md)
- Or skip web search and enter URLs manually

### Import Errors
**Solution**:
- Always run with PYTHONPATH: `PYTHONPATH="$PWD/src:$PWD" python main.py`
- Or activate virtual environment first: `source venv/bin/activate`
- Test imports: `python test_imports.py`

### "No module named 'config'"
**Solution**:
- Your PYTHONPATH doesn't include the project root
- Use the full command: `PYTHONPATH="$PWD/src:$PWD" python main.py`

### Web Search Returns No Results
**Solutions**:
1. Use manual URL input (choose 'y' when prompted)
2. Use sample URLs from [SAMPLE_URLS.md](SAMPLE_URLS.md)
3. Check Brave API quota hasn't been exceeded
4. Verify your internet connection

### Scraping Fails for Some Sites
**Expected behavior**:
- Some sites block scrapers or timeout
- The agent continues with sites that succeed
- Aim for 6-10 successful scrapes out of 10 attempts
- Check the console output for specific errors

### Low Match Scores
**Solutions**:
- Broaden your criteria (fewer required certifications)
- Add more locations
- Accept wider MOQ range
- Use "certifications of interest" instead of strict requirements

### Excel File Not Generated
**Causes**:
- No manufacturers successfully scraped
- Output directory permissions
- Disk space

**Solutions**:
- Check console output for errors
- Verify `output/` directory exists and is writable
- Try broader search criteria to find more results

---

## Cost Estimates

### API Usage Per Search

- **Criteria collection**: ~$0.10
- **Query generation**: ~$0.05
- **Data extraction** (10 manufacturers): ~$0.50-1.00
- **Evaluation** (10 manufacturers): ~$0.30-0.50

**Total per search**: ~$1-2

With a $50 budget, you can run approximately **25-50 searches**.

### Brave Search Quotas

- **Free tier**: 2,000 queries/month
- **Per search**: ~5 queries used
- **Total searches**: ~400 per month (free)

---

## Advanced Usage

### Skip Web Search (Manual URLs)

If you want to test specific manufacturers:

1. Run the agent normally
2. When web search completes (or fails), answer `y` to "Enter URLs manually?"
3. Paste manufacturer URLs one at a time
4. Type `done` when finished

Use [SAMPLE_URLS.md](SAMPLE_URLS.md) for test URLs.

### Testing Without Web Search

To quickly test data extraction and evaluation:

```bash
PYTHONPATH="$PWD/src:$PWD" python main.py
# Enter criteria
# Skip search or let it fail
# Enter sample URLs manually
# Type 'done'
```

This saves Brave API quota while testing.

### Adjusting Number of Results

Edit [config/settings.py](config/settings.py):

```python
MAX_MANUFACTURERS = 15        # Get more results
MAX_SEARCH_QUERIES = 8        # Use more search queries
```

**Note**: More results = higher API costs but better coverage.

---

## Next Steps

### After Your First Successful Run

1. **Review the Excel output** in `output/` directory
2. **Check match scores** - Focus on scores above 70
3. **Read the Notes column** - See strengths/weaknesses
4. **Visit high-scoring websites** for more details
5. **Save your criteria** as presets for future searches

### For More Details

- **Full documentation**: [README.md](README.md)
- **Web application setup**: [README.md#running-the-web-app-locally](README.md#running-the-web-app-locally)
- **Brave Search setup**: [BRAVE_SEARCH_SETUP.md](BRAVE_SEARCH_SETUP.md)
- **Query generation deep dive**: [QUERY_GENERATION_ANALYSIS.md](QUERY_GENERATION_ANALYSIS.md)
- **Sample test URLs**: [SAMPLE_URLS.md](SAMPLE_URLS.md)

---

## Getting Help

If you encounter issues:

1. **Check this guide** - Most common issues are covered
2. **Review error messages** - Console output shows specific errors
3. **Test imports**: `python test_imports.py`
4. **Verify API keys** - Check `.env` file
5. **Try sample URLs** - Test without web search
6. **Check main README**: [README.md](README.md)

---

## Example Session

Here's what a typical session looks like:

```bash
$ PYTHONPATH="$PWD/src:$PWD" python main.py

=== Activewear Manufacturer Research Agent ===

How would you like to provide search criteria?
1. Answer questions interactively
2. Load existing preset
> 1

[Agent asks questions about your requirements...]

Locations (comma-separated): USA, Vietnam
MOQ minimum: 500
MOQ maximum: 2000
Certifications of interest: OEKO-TEX
Materials: recycled polyester, organic cotton
Production methods: sublimation printing
Budget tier: mid-range

[Agent generates 10 strategic search queries...]
[Agent searches web and finds 20 manufacturer URLs...]
[Agent scrapes 10 websites...]
[Agent extracts and evaluates data...]
[Agent generates Excel file...]

✓ Search complete!
Results saved to: output/manufacturers_2025-02-08_14-30-22.xlsx

Top 3 manufacturers:
1. EcoWear Manufacturing (Score: 87) - Vietnam, OEKO-TEX certified
2. Sustainable Apparel Co. (Score: 82) - California, USA
3. Green Textiles Ltd. (Score: 78) - Vietnam

Would you like to save these criteria as a preset? (y/n): y
Preset name: Sustainable Activewear
✓ Preset saved!
```

---

Happy manufacturer hunting! 🎉
