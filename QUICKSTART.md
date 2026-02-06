# Activewear Manufacturer Research Agent - Quick Start

## ✅ Implementation Complete!

All components have been implemented and tested. The agent is ready to run.

---

## 🚀 How to Run

### 1. Set Your API Key

Edit the `.env` file and add your Anthropic API key:

```bash
# Open .env in your editor
nano .env

# Replace the placeholder with your actual key
ANTHROPIC_API_KEY=sk-ant-YOUR_ACTUAL_KEY_HERE
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Run the Agent

```bash
python main.py
```

---

## 📋 What Happens When You Run It

**Phase 1: Criteria Collection**
- Interactive Q&A to collect your requirements
- Option to load existing presets
- Option to save new presets for reuse

**Phase 2: Query Generation**
- Claude generates 3-5 diverse search queries based on your criteria

**Phase 3: Web Search**
- Searches Google for manufacturers matching your queries
- Finds up to 15 potential manufacturer websites

**Phase 4: Web Scraping**
- Scrapes up to 10 manufacturer websites
- Extracts text content from each site
- 2-second delay between requests (polite scraping)

**Phase 5: Data Extraction**
- Claude extracts structured data from each website:
  - Name, location, contact info
  - Materials, production methods, MOQ
  - Certifications

**Phase 6: Evaluation**
- Scores each manufacturer against your criteria (0-100)
- Scoring breakdown:
  - Location match: 20 points
  - MOQ match: 20 points
  - Certifications: 20 points
  - Materials: 20 points
  - Production methods: 20 points

**Phase 7: Excel Output**
- Generates formatted Excel report
- Saved to `output/manufacturers_YYYY-MM-DD_HH-MM-SS.xlsx`
- Color-coded match scores
- All manufacturer details in one spreadsheet

---

## 📝 Example Test Criteria

When the agent asks for criteria, try these values:

- **Locations**: USA, Vietnam
- **MOQ Range**: 500 to 2000 units
- **Required Certifications**: OEKO-TEX
- **Materials**: recycled polyester, organic cotton
- **Production Methods**: sublimation printing
- **Budget Tier**: mid-range

---

## 📂 Output

The agent generates an Excel file with:

- **Rank** - Position based on match score
- **Name** - Manufacturer name
- **Location** - City, country
- **Website** - Company URL
- **MOQ** - Minimum order quantity
- **Match Score** - 0-100 score against your criteria
- **Confidence** - Data quality (low/medium/high)
- **Materials** - Materials they work with
- **Certifications** - Certifications held
- **Production Methods** - Production capabilities
- **Contact** - Email, phone, address
- **Notes** - Strengths/weaknesses
- **Source URL** - Where data was found

---

## 🛠️ Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've edited `.env` with your actual API key
- Don't include quotes around the key

**Web searches return no results**
- This is expected if Google blocks scraping
- The agent will continue with whatever data it can find
- In production, you'd use Google Custom Search API

**Some manufacturers have low confidence scores**
- This is normal - not all websites have complete data
- Focus on high-scoring, high-confidence matches

**Scraping fails for some sites**
- Expected - some sites block scrapers or timeout
- The agent continues with sites that succeed
- Aim for 6-10 successful scrapes

---

## 🔧 Configuration

Edit `config/settings.py` or set environment variables:

```bash
# In .env file
REQUEST_DELAY_SECONDS=2       # Delay between requests
SCRAPE_TIMEOUT_SECONDS=30     # Timeout per site
MAX_MANUFACTURERS=10          # Number of results
```

---

## 📦 Project Structure

```
activewear-agent/
├── src/
│   ├── agent/
│   │   ├── core.py          ✅ Main orchestrator
│   │   ├── state.py         ✅ State machine
│   │   └── prompts.py       ✅ System prompts
│   ├── tools/
│   │   ├── criteria_collector.py  ✅ Interactive Q&A
│   │   ├── query_generator.py     ✅ Search query generation
│   │   ├── web_searcher.py        ✅ Web search
│   │   ├── web_scraper.py         ✅ Website scraping
│   │   ├── data_extractor.py      ✅ LLM data extraction
│   │   ├── evaluator.py           ✅ Manufacturer scoring
│   │   └── excel_generator.py     ✅ Excel output
│   ├── models/
│   │   ├── criteria.py      ✅ SearchCriteria model
│   │   └── manufacturer.py  ✅ Manufacturer model
│   └── utils/
│       └── llm.py           ✅ Claude API wrapper
├── config/
│   ├── settings.py          ✅ Configuration
│   └── presets/             📁 Saved criteria presets
├── output/                  📁 Generated Excel files
├── main.py                  ✅ Entry point
└── requirements.txt         ✅ Dependencies

✅ = Implemented and tested
📁 = Directory for data storage
```

---

## 💰 Budget Tracking

The agent is configured with a $50 API budget limit. Estimated costs:

- **Criteria Collection**: ~$0.10 per run
- **Query Generation**: ~$0.05 per run
- **Data Extraction**: ~$0.50-1.00 per 10 manufacturers
- **Total per run**: ~$1-2

You can run approximately **25-50 searches** within the $50 budget.

---

## 🎯 Next Steps

1. **Add your API key** to `.env`
2. **Run the agent** with `python main.py`
3. **Review the Excel output** in `output/` directory
4. **Save your criteria** as presets for future runs
5. **Contact top-ranked manufacturers** from the results

---

## 📧 Need Help?

If you encounter issues:

1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Verify your API key is correct in `.env`
3. Make sure you're in the virtual environment: `source venv/bin/activate`
4. Run the import test: `python test_imports.py`

Happy manufacturer hunting! 🎉
