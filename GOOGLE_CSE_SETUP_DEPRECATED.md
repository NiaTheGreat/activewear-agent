# Google Custom Search API Setup Guide

> **⚠️ DEPRECATED - DO NOT USE**
>
> Google has deprecated the "Search the entire web" feature for Custom Search Engine, making this API unsuitable for our use case.
>
> **Please use Bing Search API instead:** See [BING_SEARCH_SETUP.md](BING_SEARCH_SETUP.md)
>
> This file is kept for reference only.

---

This guide will walk you through setting up Google Custom Search API for the Activewear Manufacturer Research Agent.

## Why Google Custom Search API?

- **FREE**: 100 queries per day at no cost
- **Reliable**: Official Google API, won't get blocked
- **Simple**: Clean JSON responses, no HTML parsing needed
- **Legal**: Complies with Google's Terms of Service

---

## Setup Steps

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** at the top
3. Click **"New Project"**
4. Enter project name: `activewear-agent` (or any name you prefer)
5. Click **"Create"**
6. Wait for the project to be created (~30 seconds)

### Step 2: Enable Custom Search API

1. In the Google Cloud Console, make sure your new project is selected
2. Go to **APIs & Services** → **Library** (or [click here](https://console.cloud.google.com/apis/library))
3. Search for **"Custom Search API"**
4. Click on **"Custom Search API"**
5. Click **"Enable"**
6. Wait for the API to be enabled

### Step 3: Create an API Key

1. Go to **APIs & Services** → **Credentials** (or [click here](https://console.cloud.google.com/apis/credentials))
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"API Key"**
4. A popup will show your new API key
5. **Copy the API key** and save it somewhere safe
6. Click **"RESTRICT KEY"** (recommended for security)

#### Optional: Restrict the API Key (Recommended)

1. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check **"Custom Search API"**
2. Under **"Application restrictions"** (optional):
   - Select **"IP addresses"** if you want to restrict to specific IPs
   - Or select **"None"** for flexibility
3. Click **"Save"**

### Step 4: Create a Custom Search Engine

1. Go to [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **"Get started"** or **"Add"**
3. Fill in the form:
   - **Search engine name**: `Manufacturer Search` (or any name)
   - **What to search**: Select **"Search the entire web"**
4. Click **"Create"**
5. You'll see a confirmation page

### Step 5: Get Your Search Engine ID

1. On the confirmation page, click **"Customize"**
2. In the left sidebar, click **"Setup"** or **"Basic"**
3. Look for **"Search engine ID"** (it's a string like `a1b2c3d4e5f6g7h8i`)
4. **Copy the Search Engine ID** and save it

### Step 6: Enable "Search the entire web"

1. Still in the Custom Search Engine control panel
2. Go to **"Setup"** → **"Basics"**
3. Under **"Search features"**, toggle **"Search the entire web"** to ON
4. Under **"Sites to search"**, you can:
   - Leave it empty to search everything
   - Or add specific domains if you want to limit results
5. Click **"Update"** to save changes

### Step 7: Add Credentials to Your .env File

1. Open your `.env` file in the project root directory
2. Add your credentials:

```env
# Google Custom Search API
GOOGLE_API_KEY=AIzaSyB1234567890abcdefghijklmnopqr
GOOGLE_CSE_ID=a1b2c3d4e5f6g7h8i
```

3. Save the file

---

## Testing Your Setup

Run a quick test to verify everything works:

```bash
python main.py
```

When you get to the search phase, the agent will use the Google Custom Search API. You should see:
- ✅ No "Google blocking" errors
- ✅ Clean search results with manufacturer URLs
- ✅ Consistent, reliable performance

---

## Troubleshooting

### Error: "Invalid API key or Search Engine ID"

**Solution**:
- Double-check your API key and CSE ID in `.env`
- Make sure there are no extra spaces or quotes
- Verify the API key is enabled for Custom Search API

### Error: "Google API quota exceeded"

**Cause**: You've exceeded the free tier limit (100 queries/day)

**Solutions**:
- Wait 24 hours for quota to reset
- Enable billing in Google Cloud to get 10,000 queries/day ($5 per 1,000 additional queries)
- Use manual URL input by answering "y" when asked to skip search

### Error: "API key not found"

**Solution**:
- Make sure you created the `.env` file (not just `.env.example`)
- Verify `GOOGLE_API_KEY` is spelled correctly
- Restart your terminal session after adding environment variables

### No Results Returned

**Solution**:
- Go back to your Custom Search Engine settings
- Make sure **"Search the entire web"** is enabled
- Check that there are no restrictive site filters

---

## Cost Information

### Free Tier
- **100 queries per day**: FREE forever
- Perfect for testing and moderate use

### Paid Tier (if you enable billing)
- **First 100 queries/day**: FREE
- **Next 10,000 queries/day**: $5 per 1,000 queries ($0.005 per query)
- **Beyond 10,000 queries/day**: Contact Google for pricing

### Cost Example for This Agent
With default settings (5 queries per run):
- **Free tier**: 20 agent runs per day = FREE
- **Paid tier**: 2,000 agent runs per day = $50

---

## Alternative: Manual URL Input

If you prefer not to set up the API, you can always use manual URL input:

1. Run the agent: `python main.py`
2. After entering criteria, answer **"y"** to skip web search
3. Paste manufacturer URLs from `SAMPLE_URLS.md`
4. Type **"done"** when finished

---

## Security Best Practices

1. **Never commit your `.env` file** to version control
2. **Use API key restrictions** in Google Cloud Console
3. **Rotate your API key** if it's accidentally exposed
4. **Monitor your usage** in Google Cloud Console to avoid unexpected charges

---

## Additional Resources

- [Google Custom Search API Documentation](https://developers.google.com/custom-search/v1/overview)
- [Programmable Search Engine Help](https://support.google.com/programmable-search/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Review the Google Custom Search API documentation
3. Verify your `.env` file configuration
4. Check the Google Cloud Console for error messages

Happy researching! 🚀
