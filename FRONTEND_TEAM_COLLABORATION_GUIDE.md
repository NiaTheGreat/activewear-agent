# Frontend Team Collaboration - Implementation Guide

## 🎉 What Was Built

I've successfully implemented the complete frontend UI for team collaboration with organizations and pipelines. Here's everything that was added:

---

## 📁 Files Created (14 new files)

### **TypeScript Types & API Client**
1. **Updated** `frontend/src/types/api.ts` - Added Organization, Pipeline, and related types
2. **Updated** `frontend/src/lib/api.ts` - Added API functions for organizations and pipelines

### **State Management & Hooks**
3. `frontend/src/store/organizationStore.ts` - Zustand store for organization context
4. `frontend/src/hooks/useOrganizations.ts` - React Query hooks for organizations
5. `frontend/src/hooks/usePipelines.ts` - React Query hooks for pipelines

### **Organization Components**
6. `frontend/src/components/organization/CreateOrganizationDialog.tsx` - Create organization modal
7. `frontend/src/components/organization/OrganizationMembersDialog.tsx` - Manage members & roles
8. `frontend/src/components/organization/OrganizationSwitcher.tsx` - Workspace switcher dropdown

### **Pipeline Components**
9. `frontend/src/components/pipeline/CreatePipelineDialog.tsx` - Create pipeline with colors & icons
10. `frontend/src/components/pipeline/PipelineCard.tsx` - Pipeline card component

### **Pages**
11. `frontend/src/app/(dashboard)/dashboard/org/pipelines/page.tsx` - Pipelines list page
12. `frontend/src/app/(dashboard)/dashboard/org/members/page.tsx` - Members management page

### **Updated Files**
13. **Updated** `frontend/src/components/layout/Sidebar.tsx` - Added organization switcher & dynamic navigation
14. **Updated** `frontend/src/app/(dashboard)/search/new/page.tsx` - Added organization context to searches

---

## 🚀 Features Implemented

### **1. Organization Management**
✅ Create organizations with name, slug, and description
✅ Organization switcher in sidebar (Personal Workspace ↔ Organizations)
✅ Auto-generated URL-friendly slugs
✅ Member count display

### **2. Member Management**
✅ Invite members by email
✅ Role-based permissions (Owner, Admin, Member, Viewer)
✅ Change member roles (owners only)
✅ Remove members
✅ Prevent removing the last owner

### **3. Pipeline Management**
✅ Create pipelines with custom names, colors, and icons
✅ Set default pipelines (auto-add new manufacturers)
✅ Pipeline cards with manufacturer counts
✅ Delete pipelines (manufacturers stay intact)
✅ Visual color coding and emoji icons

### **4. Context-Aware Navigation**
✅ Different navigation for Personal vs Organization workspace
✅ Dynamic sidebar based on selected workspace
✅ Organization name display in sidebar

### **5. Organization-Scoped Searches**
✅ Searches automatically use current organization context
✅ Personal searches when in Personal Workspace
✅ Team searches when in Organization workspace
✅ Search history filtered by workspace

---

## 🎨 UI Components Used

All components use **shadcn/ui** (Radix UI) for consistency:
- Dialog - Modals for create/edit forms
- Select - Dropdowns for roles and options
- Table - Member list display
- Badge - Role indicators
- Card - Pipeline cards
- Button, Input, Label, Textarea - Form elements
- DropdownMenu - Organization switcher and actions
- Checkbox - Default pipeline toggle

---

## 🧪 How to Test

### **1. Start the Frontend**
```bash
cd frontend
npm install  # If you haven't already
npm run dev
```

Visit http://localhost:3000

### **2. Test Organization Creation**

1. **Open Organization Switcher** (top of sidebar)
2. **Click "Create Organization"**
3. **Fill in the form:**
   - Name: "Test Company"
   - Slug: Auto-generates as "test-company" (or customize)
   - Description: Optional
4. **Click "Create Organization"**

### **3. Test Member Invitation**

1. **Navigate to:** `/dashboard/org/members` (or click "Members" in sidebar)
2. **Click "Invite Member"**
3. **Enter email and select role**
4. **Send invite**

**Note:** The invitee must already have an account. If not, they'll get a "User not found" error.

### **4. Test Pipeline Creation**

1. **Navigate to:** `/dashboard/org/pipelines` (or click "Pipelines" in sidebar)
2. **Click "Create Pipeline"**
3. **Fill in the form:**
   - Name: "Q1 2026 Production"
   - Description: Optional
   - Icon: Click an emoji (📌, 🎯, 🌱, etc.)
   - Color: Click a preset color or enter hex code
   - Default: Check if you want new manufacturers auto-added
4. **Click "Create Pipeline"**

### **5. Test Organization-Scoped Search**

1. **Ensure you're in an organization** (check sidebar shows org name)
2. **Click "New Search"** in sidebar
3. **Fill in search criteria**
4. **Submit** - This will create a team search visible to all org members
5. **Check "Search History"** - You'll see organization searches

### **6. Test Workspace Switching**

1. **Click Organization Switcher** (top of sidebar)
2. **Select "Personal Workspace"**
3. **Notice sidebar navigation changes** (back to personal items)
4. **Create a search** - Now it's a personal search
5. **Switch back to an organization** - Navigation updates again

---

## 🔑 Key Features to Demonstrate

### **Organization Switcher**
- Shows all organizations you're a member of
- Displays member count per organization
- Switches between Personal Workspace and Organizations
- Creates new organizations directly from dropdown

### **Dynamic Sidebar Navigation**

**Personal Workspace:**
- Dashboard
- New Search
- All Manufacturers
- Favorites
- Pipeline (old single pipeline)
- History
- Presets

**Organization Workspace:**
- Team Dashboard
- New Search
- **Pipelines** (new - multiple pipelines!)
- Manufacturers (team manufacturers)
- Search History (team searches)
- **Members** (team management)

### **Pipeline Cards**
- Colored left border
- Custom emoji icon
- Manufacturer count
- "Default" badge if applicable
- Click to view pipeline details
- Dropdown menu for Edit/Delete

### **Member Management**
- View all members with emails, names, roles
- Invite new members by email
- Change roles via dropdown (owners only)
- Remove members (with confirmation)
- Protection against removing last owner

---

## 🎯 User Flow Example

**Scenario: Setting up a team for manufacturer research**

1. **Alice creates "Acme Activewear Co." organization**
   - Uses organization switcher → "Create Organization"
   - Sets up company with description

2. **Alice invites team members**
   - Goes to Members page
   - Invites bob@acme.com as "Member"
   - Invites carol@acme.com as "Admin"

3. **Alice creates pipelines**
   - Creates "Q1 2026 Production" (📌, blue, default)
   - Creates "Sustainable Options" (🌱, green)
   - Creates "Backup Suppliers" (🔄, orange)

4. **Bob runs a team search**
   - Ensures he's in "Acme Activewear Co." workspace
   - Clicks "New Search"
   - Fills criteria: Vietnam manufacturers, polyester materials
   - Submits → Creates organization search
   - Manufacturers auto-added to "Q1 2026 Production" (default pipeline)

5. **Carol reviews and organizes**
   - Sees Bob's search in "Search History"
   - Views manufacturers in "Q1 Production" pipeline
   - Adds sustainable ones to "Sustainable Options" pipeline
   - All team members see the same data

---

## 🐛 Known Limitations & Future Enhancements

### **Current Limitations:**
1. **No email invitations** - Users must already have accounts
2. **No pipeline-manufacturer management** - Adding manufacturers to pipelines from UI not yet implemented
3. **No pipeline detail page** - Pipeline cards link to detail page that doesn't exist yet
4. **No organization settings page** - Can't edit org name/description after creation
5. **No organization dashboard** - `/dashboard/org` page not implemented

### **Recommended Next Steps:**
1. **Add Manufacturer → Pipeline UI**
   - "Add to Pipeline" button on manufacturer cards
   - Multi-select pipelines dialog
   - Pipeline-specific notes/status/priority fields

2. **Pipeline Detail Page**
   - View all manufacturers in pipeline
   - Drag-and-drop to reorder by priority
   - Inline editing of pipeline-specific context

3. **Organization Dashboard**
   - Team activity feed
   - Recent searches by team members
   - Pipeline stats (which has most manufacturers)

4. **Email Invitations System**
   - Send email when inviting non-existent users
   - Invitation tokens
   - Accept/decline flow

5. **Organization Settings**
   - Edit org name, description
   - Delete organization
   - Transfer ownership

---

## 🎨 Color Palette Used

**Preset Colors for Pipelines:**
- Blue: `#3B82F6`
- Green: `#10B981`
- Orange: `#F59E0B`
- Purple: `#8B5CF6`
- Red: `#EF4444`
- Pink: `#EC4899`

**Preset Icons:**
📌 🎯 🌱 🔄 ⭐ 🚀 💎 🏆

---

## 📊 State Management

### **Zustand Store (`organizationStore.ts`)**
```typescript
{
  currentOrganization: Organization | null,  // Selected workspace
  organizations: Organization[],             // All user's orgs
  setCurrentOrganization: (org) => void,
  setOrganizations: (orgs) => void,
  isPersonalWorkspace: () => boolean,
  getCurrentOrgId: () => string | undefined,
}
```

**Persistence:** Uses `zustand/persist` to save selected org to localStorage

### **React Query Cache Keys**
- `["organizations"]` - All organizations
- `["organizations", orgId]` - Single organization
- `["organizations", orgId, "members"]` - Organization members
- `["organizations", orgId, "pipelines"]` - Organization pipelines
- `["pipelines", pipelineId]` - Single pipeline
- `["pipelines", pipelineId, "manufacturers"]` - Pipeline manufacturers

---

## 🔐 Permissions Overview

### **Organization Roles:**

**Owner:**
- ✅ Everything Admins can do
- ✅ Delete organization
- ✅ Change member roles
- ✅ Remove members (including admins)
- ⚠️ Can't remove themselves if they're the only owner

**Admin:**
- ✅ Invite members
- ✅ Remove members (except owners)
- ✅ Create/edit/delete pipelines
- ✅ Create searches
- ❌ Can't change roles
- ❌ Can't delete organization

**Member:**
- ✅ Create searches
- ✅ Create/edit pipelines
- ✅ Add manufacturers to pipelines
- ✅ View all team data
- ❌ Can't invite members
- ❌ Can't change roles

**Viewer:**
- ✅ View all team data
- ❌ Can't create searches
- ❌ Can't modify anything

---

## ✅ Testing Checklist

### **Organization Management**
- [ ] Create organization with custom slug
- [ ] Create organization with auto-generated slug
- [ ] Switch between Personal and Organization workspaces
- [ ] Organization switcher shows member counts
- [ ] Organization persists after page refresh (localStorage)

### **Member Management**
- [ ] Invite member with "Member" role
- [ ] Invite member with "Admin" role
- [ ] Change member role (as owner)
- [ ] Remove member (with confirmation)
- [ ] Try to remove last owner (should be blocked)
- [ ] Member list shows email, name, role, join date

### **Pipeline Management**
- [ ] Create pipeline with custom color and icon
- [ ] Create default pipeline
- [ ] Only one pipeline can be default at a time
- [ ] Pipeline cards show manufacturer count
- [ ] Delete pipeline (manufacturers stay in other pipelines)

### **Organization-Scoped Searches**
- [ ] Create search in Personal Workspace → Personal search
- [ ] Create search in Organization → Team search
- [ ] Team members see the same search history
- [ ] Search history filters by workspace

### **Navigation**
- [ ] Sidebar navigation changes based on workspace
- [ ] Links work correctly for both workspace types
- [ ] Active states highlight correctly

---

## 🎊 You're All Set!

The frontend is now fully integrated with the backend team collaboration features. Users can:
- Create and manage organizations
- Invite team members with role-based permissions
- Create multiple pipelines to organize manufacturers
- Run team searches visible to all members
- Switch seamlessly between personal and team workspaces

**Next:** Build the manufacturer → pipeline UI to complete the collaboration workflow!
