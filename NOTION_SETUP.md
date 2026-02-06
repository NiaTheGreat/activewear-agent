# Notion Integration Setup Guide

This guide will walk you through setting up Notion integration for the Activewear Manufacturer Research Agent.

## Why Notion?

- **✅ Free**: No cost for personal use
- **✅ Database-native**: Perfect for structured manufacturer data
- **✅ Easy setup**: Just 5 minutes, no OAuth required
- **✅ Beautiful UI**: Filter, sort, and organize manufacturers
- **✅ Mobile access**: Check manufacturers on the go
- **✅ Real-time collaboration**: Share with your team
- **✅ Multiple views**: Table, Board, Gallery, Calendar

---

## Setup Steps (5 minutes)

### Step 1: Create a Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"+ New integration"**
3. Fill in the details:
   - **Name**: "Activewear Agent" (or any name you prefer)
   - **Associated workspace**: Select your workspace
   - **Type**: Internal integration
4. Click **"Submit"**
5. **Copy the "Internal Integration Token"** (starts with `secret_`)
   - This is your `NOTION_API_TOKEN`
   - Keep it safe!

### Step 2: Create a Notion Database

1. Open Notion and create a new page
2. Type `/database` and select **"Table - Inline"**
3. Name it **"Manufacturers"** (or any name you prefer)
4. Delete the default columns (Name, Tags, Files)

### Step 3: Configure Database Properties

Add these columns (properties) to your database:

| Property Name | Type | Notes |
|--------------|------|-------|
| **Name** | Title | Primary field |
| **Match Score** | Number | Format: Number |
| **Location** | Text | - |
| **Website** | URL | - |
| **MOQ** | Text | - |
| **Confidence** | Text | - |
| **Materials** | Text | - |
| **Certifications** | Text | - |
| **Production Methods** | Text | - |
| **Email** | Email | - |
| **Phone** | Phone | - |
| **Address** | Text | - |
| **Notes** | Text | - |
| **Source URL** | URL | Used for deduplication |
| **Date Added** | Date | Auto-populated |

**How to add properties:**
1. Click the **"+"** button at the right of the header row
2. Enter the property name
3. Select the property type from the dropdown
4. Repeat for all properties above

### Step 4: Get Database ID

1. Open your Manufacturers database in Notion
2. Click **"Share"** button (top right)
3. Click **"Copy link"**
4. The link looks like: `https://www.notion.so/your-workspace/1234567890abcdef1234567890abcdef?v=...`
5. Your **Database ID** is the 32-character hex string: `1234567890abcdef1234567890abcdef`
   - It's between the workspace name and the `?v=`

### Step 5: Share Database with Integration

1. In your Manufacturers database, click **"Share"** (top right)
2. Click **"Invite"**
3. Search for your integration name ("Activewear Agent")
4. Select it and click **"Invite"**

### Step 6: Configure .env File

1. Open your `.env` file in the project root
2. Update these lines:

```env
# Notion Integration (Optional)
NOTION_ENABLED=true
NOTION_API_TOKEN=secret_your-actual-token-here
NOTION_DATABASE_ID=your-actual-database-id-here
```

3. Replace:
   - `secret_your-actual-token-here` with your integration token from Step 1
   - `your-actual-database-id-here` with your database ID from Step 4

4. Save the file

### Step 7: Install notion-client Package

```bash
pip install notion-client
```

---

## Testing Your Setup

Run the agent:

```bash
python main.py
```

After the agent completes, you should see:

```
✓ Excel report saved to: output/manufacturers_2026-02-05_14-30-45.xlsx

✓ Cumulative file updated: output/manufacturers_scores.xlsx (15 total manufacturers, 10 new)

Syncing to Notion...
Found 5 existing manufacturers in Notion
Adding 10 new manufacturers to Notion...
✓ Notion sync complete: 10 manufacturers added
```

Check your Notion database - you should see the new manufacturers!

---

## How It Works

### Automatic Deduplication

The agent automatically checks for duplicate URLs before adding to Notion:
- Queries Notion for all existing Source URLs
- Only adds manufacturers with **new/unique URLs**
- Prevents duplicates across multiple runs

### Data Flow

1. **Agent runs** → Finds manufacturers
2. **Excel files created** → Local backup (always happens)
3. **Notion sync** → If enabled, syncs to database (optional)

### Excel + Notion = Best of Both Worlds

- **Excel**: Offline backup, data analysis, pivot tables
- **Notion**: Beautiful UI, filtering, sorting, team collaboration

---

## Notion Database Views

Create custom views in your database:

### 1. All Manufacturers (Default Table View)
- Shows all manufacturers
- Sortable by any column

### 2. Top Matches
- **Filter**: Match Score ≥ 70
- **Sort**: Match Score (descending)
- See only the best matches!

### 3. Recently Added
- **Sort**: Date Added (descending)
- See what you found in your last run

### 4. By Location
- **Group by**: Location
- Organize manufacturers by country/region

**How to create views:**
1. Click the view dropdown (top left, next to "Table")
2. Click "+ New view"
3. Choose view type (Table, Board, Gallery, etc.)
4. Add filters and sorting

---

## Advanced Notion Features

### Add Custom Properties

You can add more columns to track additional info:

- **Status** (Select): New, Contacted, Qualified, Rejected
- **Priority** (Select): High, Medium, Low
- **Last Contact** (Date): When you last reached out
- **Tags** (Multi-select): Custom tags
- **Assigned To** (Person): Team member responsible

The agent won't populate these, but you can fill them in manually!

### Relations

Link to other Notion databases:
- **Orders** database → Track orders from manufacturers
- **Samples** database → Track sample requests
- **Contacts** database → Link to contact persons

### Formulas

Add calculated fields:
- **Days Since Added**: `dateBetween(now(), prop("Date Added"), "days")`
- **Score Grade**: `if(prop("Match Score") >= 70, "A", if(prop("Match Score") >= 50, "B", "C"))`

---

## Troubleshooting

### Error: "notion-client not installed"

**Solution:**
```bash
pip install notion-client
```

### Error: "Could not fetch existing URLs from Notion"

**Cause**: Integration doesn't have access to database

**Solution:**
1. Open database in Notion
2. Click "Share" → "Invite"
3. Add your integration
4. Verify integration name matches

### Error: "Unauthorized" or "Invalid token"

**Solution:**
- Double-check `NOTION_API_TOKEN` in `.env`
- Make sure token starts with `secret_`
- Verify no extra spaces or quotes
- Try regenerating token in Notion integration settings

### Database ID Not Working

**Solution:**
- Database ID should be 32 hex characters (no dashes)
- Extract from URL: `https://notion.so/workspace/DATABASE_ID?v=...`
- Should look like: `1234567890abcdef1234567890abcdef`

### No Manufacturers Added

**Cause**: All URLs already exist in Notion (deduplication working!)

**Solution:**
- This is normal if you've already synced these manufacturers
- Try running agent with different search criteria
- Check Notion database to verify existing data

### Property Type Mismatch

**Cause**: Database property types don't match expected types

**Solution:**
- Verify property types match the table in Step 3
- Email property must be type "Email" (not Text)
- URL properties must be type "URL" (not Text)
- Date Added must be type "Date" (not Text)

---

## Disabling Notion Integration

To turn off Notion sync (but keep Excel files):

1. Open `.env` file
2. Change: `NOTION_ENABLED=false`
3. Save file

Excel files will still be generated!

---

## Security Best Practices

1. **Never commit `.env` to git**
   - Already in `.gitignore`
   - Double-check before pushing code

2. **Rotate tokens if exposed**
   - If you accidentally commit your token:
   - Go to Notion integrations → Delete old token
   - Create new integration token
   - Update `.env` with new token

3. **Limit integration permissions**
   - Only share specific databases with integration
   - Don't give access to entire workspace

---

## Cost

**Notion is FREE for:**
- Personal use
- Unlimited pages and databases
- Basic integrations

**Paid plans (optional):**
- Notion Plus ($10/month): Version history, unlimited uploads
- Notion Business ($18/user/month): SAML SSO, advanced permissions
- Notion Enterprise: Custom pricing

For this agent, **free tier is perfect!** ✅

---

## Comparison: Notion vs Excel

| Feature | Notion | Excel File |
|---------|--------|-----------|
| **Offline Access** | ❌ | ✅ |
| **Data Analysis** | Basic | Advanced (pivot tables, formulas) |
| **Filtering/Sorting** | ✅ Excellent | ⚠️ Manual |
| **Visual Appeal** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Team Collaboration** | ✅ Real-time | ⚠️ File sharing |
| **Mobile Access** | ✅ Great app | ⚠️ Limited |
| **Custom Views** | ✅ Multiple views | ❌ |
| **Relations** | ✅ Link databases | ❌ |
| **API Access** | ✅ | Limited |

**Best approach**: Use **both**!
- Excel for backup and analysis
- Notion for daily management and collaboration

---

## Additional Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Notion Integration Guide](https://www.notion.so/help/add-and-manage-integrations)
- [notion-client Python Package](https://github.com/ramnes/notion-sdk-py)

---

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all setup steps were completed
3. Check Notion API status page
4. Review database property types

Happy organizing! 🚀
