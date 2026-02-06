# Activewear Manufacturer Research Agent

An AI-powered CLI agent that finds and evaluates activewear manufacturers based on custom search criteria. Built with Claude API and Python.

## Features

- **Interactive Criteria Collection**: Conversational Q&A to gather your requirements
- **Smart Search**: Generates optimized Google queries based on your criteria
- **Web Scraping**: Automatically scrapes manufacturer websites for key information
- **AI Evaluation**: Uses Claude to extract data and score manufacturers (0-100)
- **Excel Export**: Ranked results in a formatted Excel file
- **Preset Management**: Save and load criteria for repeated searches

## Installation

### Prerequisites

- Python 3.10 or higher
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

1. Clone or download this repository:
```bash
cd activewear-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your API key:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

### Basic Usage

Run the agent:
```bash
python main.py
```

The agent will:
1. Ask you questions to collect search criteria
2. Generate and execute search queries
3. Scrape manufacturer websites
4. Evaluate and score each manufacturer
5. Generate an Excel file with ranked results

### Criteria Presets

Save your criteria for future use:
```python
# The agent will ask if you want to save your criteria as a preset
# Presets are saved in config/presets/
```

Load a saved preset:
```python
# Select "Load preset" when the agent asks about criteria collection
```

## Search Criteria

The agent collects the following information:

- **Locations**: Countries/regions (USA, China, Vietnam, etc.)
- **MOQ Range**: Minimum and maximum order quantities
- **Required Certifications**: Must-have certifications (GOTS, OEKO-TEX, Fair Trade)
- **Preferred Certifications**: Nice-to-have certifications
- **Materials**: Desired materials (recycled polyester, organic cotton, etc.)
- **Production Methods**: Required capabilities (sublimation, screen printing, etc.)
- **Budget Tier**: budget, mid-range, or premium
- **Additional Notes**: Any other requirements

## Output Format

Results are exported to `output/manufacturers_YYYY-MM-DD_HH-MM-SS.xlsx` with:

| Column | Description |
|--------|-------------|
| Rank | Position based on match score |
| Name | Company name |
| Location | City, country |
| Website | Company website URL |
| MOQ | Minimum order quantity |
| Match Score | 0-100 score against your criteria |
| Confidence | Data quality: low, medium, high |
| Materials | Materials they work with |
| Certifications | Certifications held |
| Production Methods | Production capabilities |
| Email | Contact email |
| Phone | Contact phone |
| Address | Physical address |
| Notes | Strengths/weaknesses |
| Source URL | URL where data was scraped |

## Scoring System

Manufacturers are scored on a 0-100 scale:

- **Location Match** (20 points): Operates in desired regions
- **MOQ in Range** (20 points): MOQ fits your budget
- **Required Certifications** (20 points): Has all must-have certs
- **Materials Match** (20 points): Works with your desired materials
- **Production Methods** (20 points): Has required capabilities

## Configuration

Edit [config/settings.py](config/settings.py) to customize:

- `MAX_MANUFACTURERS`: Max results to return (default: 10)
- `REQUEST_DELAY_SECONDS`: Delay between scraping requests (default: 2)
- `SCRAPE_TIMEOUT_SECONDS`: Timeout per website (default: 30)
- `BUDGET_LIMIT_USD`: Maximum API spend (default: $50)

Or use environment variables in `.env`:
```bash
MAX_MANUFACTURERS=15
REQUEST_DELAY_SECONDS=3
SCRAPE_TIMEOUT_SECONDS=45
```

## Project Structure

```
activewear-agent/
├── src/
│   ├── agent/              # Agent orchestration
│   │   ├── core.py         # Main agent logic
│   │   ├── state.py        # State machine
│   │   └── prompts.py      # Claude prompts
│   ├── tools/              # Individual capabilities
│   │   ├── criteria_collector.py
│   │   ├── query_generator.py
│   │   ├── web_searcher.py
│   │   ├── web_scraper.py
│   │   ├── data_extractor.py
│   │   ├── evaluator.py
│   │   └── excel_generator.py
│   ├── models/             # Data models
│   │   ├── criteria.py     # SearchCriteria model
│   │   └── manufacturer.py # Manufacturer model
│   └── utils/              # Utilities
│       └── llm.py          # Claude API wrapper
├── config/                 # Configuration
│   ├── settings.py
│   └── presets/            # Saved criteria presets
├── output/                 # Generated Excel files
├── main.py                 # Entry point
└── README.md
```

## Architecture

The agent follows a state machine pattern:

```
INIT → COLLECTING_CRITERIA → GENERATING_QUERIES → SEARCHING
→ SCRAPING → EVALUATING → OUTPUTTING → COMPLETE
```

Each state is handled by specialized tools that use Claude's function calling capability.

## Budget & Rate Limiting

To stay within budget:
- Maximum 10-15 manufacturers scraped per run
- 2-second delay between web requests
- 30-second timeout per website
- Estimated cost: $1-5 per full search

## Future Enhancements

- [ ] Support for additional sources (Alibaba, Maker's Row, Reddit)
- [ ] Multi-page scraping (currently scrapes homepage + key pages)
- [ ] Historical tracking (compare searches over time)
- [ ] Email outreach templates
- [ ] CSV export option
- [ ] Web UI (Streamlit or Gradio)
- [ ] Async scraping for better performance
- [ ] Image extraction (factory photos, product samples)

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure you've created a `.env` file with your API key

**"No manufacturers found"**
- Try broader search criteria (fewer required certifications, more locations)
- Check your internet connection

**Scraping failures**
- Some websites block automated scraping
- The agent will continue with other URLs

**Low match scores**
- Adjust your criteria to be less restrictive
- Preferred certifications are weighted lower than required ones

## Examples

### Example 1: Sustainable Activewear
```
Locations: USA, Portugal
MOQ: 100-1000
Required Certifications: GOTS, Fair Trade
Materials: Organic cotton, Tencel
Production Methods: Cut-and-sew, Screen printing
Budget: Mid-range
```

### Example 2: Performance Wear
```
Locations: China, Vietnam, Taiwan
MOQ: 500-5000
Required Certifications: OEKO-TEX
Materials: Recycled polyester, Spandex
Production Methods: Sublimation, Seamless knitting
Budget: Budget
```

### Example 3: Luxury Yoga Wear
```
Locations: Italy, Portugal, USA
MOQ: 50-500
Required Certifications: GOTS, Bluesign
Preferred: B-Corp, Climate Neutral
Materials: Bamboo, Organic merino wool
Production Methods: Cut-and-sew, Embroidery
Budget: Premium
```

## Contributing

This is a learning project. Future improvements welcome:
- Better scraping logic
- More data sources
- UI improvements
- Export formats

## License

MIT License - feel free to use and modify

## Support

For issues or questions:
- Check the Troubleshooting section
- Review [config/settings.py](config/settings.py) for configuration options
- Ensure your API key is valid and has sufficient credits

---

**Built with**:
- [Anthropic Claude API](https://www.anthropic.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Rich](https://rich.readthedocs.io/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [openpyxl](https://openpyxl.readthedocs.io/)
