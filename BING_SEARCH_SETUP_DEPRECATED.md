# Bing Search API Setup Guide

> **⚠️ DEPRECATED - DO NOT USE**
>
> Microsoft has retired the traditional Bing Search API (v7). The only option now is "Grounding with Bing" which is designed for Azure AI Foundry Agents and is overly complex for this use case.
>
> **Please use Brave Search API instead:** See [BRAVE_SEARCH_SETUP.md](BRAVE_SEARCH_SETUP.md)
>
> This file is kept for reference only.

---

This guide will walk you through setting up Bing Search API for the Activewear Manufacturer Research Agent.

## Why Bing Search API?

- **FREE**: 1,000 queries per month at no cost
- **Generous**: 10x more than Google's free tier
- **Reliable**: Official Microsoft API
- **Simple**: Clean JSON responses, easy integration
- **No Restrictions**: Searches the entire web by default

---

## Setup Steps (5 minutes)

### Step 1: Create a Microsoft Azure Account

1. Go to [Azure Portal](https://portal.azure.com/)
2. Click **"Start free"** or **"Sign in"** if you have an account
3. Sign in with your Microsoft account (or create one)
4. Complete the free account setup:
   - Enter your information
   - Verify phone number
   - **Note**: Credit card required for verification, but **you won't be charged** for free tier
5. Click **"Sign up"**

### Step 2: Create a Bing Search Resource

1. Once logged into Azure Portal, click **"Create a resource"** (top left)
2. In the search box, type **"Bing Search v7"**
3. Select **"Bing Search v7"** from the results
4. Click **"Create"**

### Step 3: Configure Your Resource

Fill in the resource details:

1. **Subscription**: Select your Azure subscription (usually "Free Trial" or "Pay-As-You-Go")
2. **Resource Group**:
   - Click **"Create new"**
   - Name it: `activewear-agent-rg` (or any name)
3. **Region**: Select a region close to you (e.g., "East US", "West Europe")
4. **Name**: Enter a unique name (e.g., `activewear-bing-search`)
5. **Pricing tier**: Select **"F1 (Free)"**
   - **1,000 queries/month FREE**
   - If F1 is not available, select **"S1"** (paid tier: $7 per 1,000 queries)

6. Click **"Review + create"**
7. Review the details
8. Click **"Create"**
9. Wait ~30 seconds for deployment to complete

### Step 4: Get Your API Key

1. After deployment, click **"Go to resource"**
2. In the left sidebar, click **"Keys and Endpoint"** (under Resource Management)
3. You'll see two keys: **KEY 1** and **KEY 2**
4. Click the **copy icon** next to **KEY 1** to copy it
5. **Save this key** - you'll need it in the next step

**Your key looks like:** `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Step 5: Add API Key to Your .env File

1. Open your `.env` file in the project root directory
2. Find the line: `BING_API_KEY=`
3. Paste your API key:

```env
BING_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

4. Save the file

---

## Testing Your Setup

Run the agent to test:

```bash
python main.py
```

When you get to the search phase, the agent will use Bing Search API. You should see:
- ✅ Clean search results with manufacturer URLs
- ✅ No API configuration errors
- ✅ Fast, reliable performance

---

## Usage Quotas & Costs

### Free Tier (F1)
- **1,000 queries per month**: FREE
- **Transactions per second**: 1
- Perfect for this agent!

**With default settings (5 queries per run):**
- **200 agent runs per month = FREE**

### Paid Tier (S1) - If You Need More
- **First 1,000 queries**: ~$7
- **Beyond that**: $7 per 1,000 queries
- **Transactions per second**: 10 (faster)

**Cost example:**
- 2,000 agent runs/month = 10,000 queries = ~$70/month

---

## Monitoring Your Usage

### Check Usage in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to your Bing Search resource
3. Click **"Metrics"** in the left sidebar
4. Select metric: **"Total Calls"**
5. View your API usage over time

### Set Up Spending Alerts (Optional)

1. In Azure Portal, click **"Cost Management + Billing"**
2. Click **"Cost alerts"**
3. Click **"Add"** → **"Budget"**
4. Set a budget limit (e.g., $10/month)
5. Configure email alerts when you reach 80% of budget

---

## Troubleshooting

### Error: "Invalid Bing API key"

**Solution**:
- Double-check your API key in `.env`
- Make sure there are no extra spaces or quotes
- Try copying **KEY 2** instead of KEY 1
- Verify the resource is deployed and active in Azure Portal

### Error: "Bing API access forbidden"

**Cause**: Your subscription may not be active or verified

**Solution**:
- Go to Azure Portal → Your Bing Search resource
- Check the status is **"Succeeded"** (not "Failed")
- Verify your Azure account is active
- Try creating a new resource

### Error: "Bing API quota exceeded"

**Cause**: You've used all 1,000 free queries this month

**Solutions**:
1. **Wait** for the monthly quota to reset (1st of next month)
2. **Upgrade** to S1 tier for more queries:
   - Go to your resource in Azure Portal
   - Click **"Pricing tier"** (left sidebar)
   - Select **"S1"**
   - Click **"Apply"**
3. **Use manual URL input** by answering "y" when asked to skip search

### Error: "API key not found"

**Solution**:
- Make sure you created the `.env` file (not just `.env.example`)
- Verify `BING_API_KEY` is spelled correctly
- Restart your terminal session after adding environment variables

### No Results Returned

**Solution**:
- Check your internet connection
- Verify the API key is correct
- Look for error messages in the console output
- Try a different search query

---

## API Key Security

### Best Practices

1. **Never commit `.env` to git**
   - It's already in `.gitignore`
   - Double-check before pushing code

2. **Rotate keys if exposed**
   - If you accidentally commit your key, regenerate it:
   - Azure Portal → Your resource → Keys and Endpoint
   - Click **"Regenerate Key 1"**

3. **Use KEY 2 as backup**
   - If KEY 1 is compromised, switch to KEY 2 immediately
   - Regenerate KEY 1 while using KEY 2

4. **Monitor for unusual activity**
   - Check metrics in Azure Portal regularly
   - Set up budget alerts

---

## Alternative: Manual URL Input

If you prefer not to set up the API or want to save quota, you can use manual URL input:

1. Run the agent: `python main.py`
2. After entering criteria, answer **"y"** to skip web search
3. Paste manufacturer URLs from `SAMPLE_URLS.md`
4. Type **"done"** when finished

---

## Comparing to Google Custom Search

| Feature | Bing Search API (F1) | Google CSE |
|---------|---------------------|------------|
| **Free queries** | 1,000/month | 100/day (~3,000/month) |
| **Setup time** | ~5 minutes | ~10 minutes |
| **Restrictions** | None - full web search | "Search entire web" deprecated |
| **Reliability** | Excellent | Blocked deprecated feature |
| **Cost beyond free** | $7 per 1,000 | $5 per 1,000 |

**Winner**: Bing Search API - more free queries, simpler setup, no restrictions! ✅

---

## Additional Resources

- [Bing Web Search API Documentation](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/)
- [Azure Portal](https://portal.azure.com/)
- [Bing Search API Pricing](https://www.microsoft.com/en-us/bing/apis/pricing)
- [Azure Free Account FAQ](https://azure.microsoft.com/en-us/free/free-account-faq/)

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the Bing Search API documentation
3. Verify your `.env` file configuration
4. Check the Azure Portal for resource status and error messages

Happy researching! 🚀
