# Brave Search API Setup Guide

This guide will walk you through setting up Brave Search API for the Activewear Manufacturer Research Agent.

## Why Brave Search API?

- **FREE**: 2,000 queries per month at no cost
- **No Credit Card**: Free tier doesn't require payment info
- **Independent**: Brave's own search index, not reselling Google/Bing
- **Privacy-Focused**: No tracking or data collection
- **Simple**: Easy 5-minute setup, clean JSON API
- **Reliable**: Professional API with good uptime

---

## Setup Steps (5 minutes)

### Step 1: Sign Up for Brave Search API

1. Go to [Brave Search API](https://brave.com/search/api/)
2. Click **"Get Started"** or **"Sign Up"**
3. Create an account:
   - Enter your email address
   - Create a password
   - Verify your email (check inbox for verification link)
   - Click the verification link

### Step 2: Choose Free Plan

1. After verifying email, log in to [API Dashboard](https://api.search.brave.com/app/dashboard)
2. You'll see pricing plans:
   - **Free Plan**: 2,000 queries/month - $0
   - **AI Plan**: 15,000 queries/month - $10/month
   - **Data for AI**: Custom pricing
3. **Select "Free Plan"** (no credit card required!)
4. Click **"Subscribe to Free Plan"** or **"Get Started"**

### Step 3: Get Your API Key

1. In the [Dashboard](https://api.search.brave.com/app/dashboard)
2. Look for **"API Keys"** section (usually on the main dashboard)
3. You should see your API key automatically generated
4. Click **"Copy"** or click the key to copy it
5. **Save this key** - you'll need it in the next step

**Your API key looks like:** `BSA1234567890abcdefghijklmnopqrstuvwxyz`

### Step 4: Add API Key to Your .env File

1. Open your `.env` file in the project root directory
2. Find the line: `BRAVE_API_KEY=`
3. Paste your API key:

```env
BRAVE_API_KEY=BSA1234567890abcdefghijklmnopqrstuvwxyz
```

4. Save the file

---

## Testing Your Setup

Run the agent to test:

```bash
python main.py
```

When you get to the search phase, the agent will use Brave Search API. You should see:
- ✅ Clean search results with manufacturer URLs
- ✅ No API configuration errors
- ✅ Fast, reliable performance

---

## Usage Quotas & Costs

### Free Plan
- **2,000 queries per month**: FREE forever
- **No credit card required**
- Perfect for this agent!

**With default settings (5 queries per run):**
- **400 agent runs per month = FREE**

### AI Plan (If You Need More)
- **First 2,000 queries**: Included
- **Additional 13,000 queries**: ~$10/month total
- **Total: 15,000 queries/month for $10**

**Cost example:**
- 3,000 agent runs/month = 15,000 queries = $10/month

### Data for AI Plan
- Custom pricing for high volume
- Contact Brave for enterprise needs

---

## Monitoring Your Usage

### Check Usage in Dashboard

1. Go to [Brave API Dashboard](https://api.search.brave.com/app/dashboard)
2. View **"Usage"** section
3. See your current month's query count
4. Monitor remaining quota

### Usage Alerts

- Brave will email you when you're close to quota limits
- You can upgrade to AI Plan if you exceed free tier
- API will return 429 error if quota exceeded

---

## Troubleshooting

### Error: "Invalid Brave API key"

**Solution**:
- Double-check your API key in `.env`
- Make sure there are no extra spaces or quotes
- Verify you copied the entire key (starts with `BSA`)
- Try regenerating a new key in the dashboard

### Error: "Brave API access forbidden"

**Cause**: Your API key may be disabled or account not verified

**Solution**:
- Verify your email address
- Check that your API key is active in the dashboard
- Try creating a new API key

### Error: "Brave API quota exceeded"

**Cause**: You've used all 2,000 free queries this month

**Solutions**:
1. **Wait** for monthly quota reset (1st of next month)
2. **Upgrade** to AI Plan ($10/month for 15,000 queries):
   - Go to Brave API Dashboard
   - Click "Upgrade Plan"
   - Select "AI Plan"
3. **Use manual URL input** by answering "y" when asked to skip search

### Error: "API key not found"

**Solution**:
- Make sure you created the `.env` file (not just `.env.example`)
- Verify `BRAVE_API_KEY` is spelled correctly
- Restart your terminal session after adding environment variables

### No Results Returned

**Solution**:
- Check your internet connection
- Verify the API key is correct and active
- Look for error messages in the console output
- Try a different search query
- Check Brave API status page

---

## API Key Security

### Best Practices

1. **Never commit `.env` to git**
   - It's already in `.gitignore`
   - Double-check before pushing code

2. **Rotate keys if exposed**
   - If you accidentally commit your key:
   - Dashboard → API Keys → Delete old key
   - Create new API key

3. **Monitor for unusual activity**
   - Check usage dashboard regularly
   - Set up email alerts (automatic with Brave)

4. **Use environment variables**
   - Never hardcode API keys in source code
   - Always use `.env` file

---

## Alternative: Manual URL Input

If you prefer not to set up the API or want to save quota, you can use manual URL input:

1. Run the agent: `python main.py`
2. After entering criteria, answer **"y"** to skip web search
3. Paste manufacturer URLs from `SAMPLE_URLS.md`
4. Type **"done"** when finished

---

## Comparing Search APIs

| Feature | Brave API | Google CSE | Bing API |
|---------|-----------|------------|----------|
| **Free queries** | 2,000/month | 100/day | RETIRED |
| **Setup time** | 3 minutes | 10 minutes | N/A |
| **Credit card** | Not required | Not required | N/A |
| **Restrictions** | None | "Entire web" deprecated | N/A |
| **Privacy** | Excellent | Poor | N/A |
| **Cost beyond free** | $10 for 15,000 | $5 per 1,000 | N/A |

**Winner**: Brave Search API - most free queries, easiest setup, no credit card! ✅

---

## Additional Resources

- [Brave Search API Documentation](https://api.search.brave.com/app/documentation/web-search/get-started)
- [Brave API Dashboard](https://api.search.brave.com/app/dashboard)
- [Brave Search API Pricing](https://brave.com/search/api/#pricing)
- [API Status Page](https://status.brave.com/)

---

## API Response Format

For reference, here's what Brave API returns:

```json
{
  "web": {
    "results": [
      {
        "title": "Manufacturer Name",
        "url": "https://example.com",
        "description": "Description of the manufacturer..."
      }
    ]
  }
}
```

Our agent extracts the `url` field from each result.

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the [Brave Search API documentation](https://api.search.brave.com/app/documentation)
3. Verify your `.env` file configuration
4. Check the Brave API Dashboard for usage and status

Happy researching! 🚀
