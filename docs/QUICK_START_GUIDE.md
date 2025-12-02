# Quick Start Guide - Transport Management System

## Welcome! 🚀

This guide will help you get started with the Transport Management System in just 10 minutes.

---

## Table of Contents

1. [Installation](#installation)
2. [First Launch](#first-launch)
3. [Basic Workflow](#basic-workflow)
4. [Sample Workflows](#sample-workflows)
5. [Next Steps](#next-steps)

---

## Installation

### Step 1: Install Python

Download and install Python 3.9+ from [python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
```

### Step 2: Download Application

```bash
# Clone or download the application
git clone <repository-url>
cd transport-management-system
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### Step 4: Initialize Database

```bash
# Set up the database with sample data
python test_database_setup.py
```

### Step 5: Launch Application

```bash
# Start the application
python main.py
```

✅ **You're ready to go!**

---

## First Launch

### What You'll See

When you first launch the application, you'll see:

```
┌────────────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Tools | Department | Help  │
├────────────────────────────────────────────────────────────┤
│  Toolbar: [New] [Save] [Import] [Export] [Filter] [...]   │
├────────────────────────────────────────────────────────────┤
│  Department Tabs: [Sales] [Processing] [Accounting]       │
├────────────────────────────────────────────────────────────┤
│  ┌──────────────┬──────────────────────────────────────┐  │
│  │ Input Form   │  Main Table                          │  │
│  │              │  (Shows existing trips)              │  │
│  └──────────────┴──────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Suggestion Tabs: [Filtered] [Company A] [B] [C]    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Sample Data

The database comes pre-loaded with:
- ✅ 50+ sample trips
- ✅ 3 departments (Sales, Processing, Accounting)
- ✅ Company price lists for 3 companies
- ✅ Sample employees and workspaces

---

## Basic Workflow

### Workflow 1: Add a New Trip (2 minutes)

**Step 1**: Fill in the form on the left side

```
┌─────────────────────────┐
│ Mã chuyến: [Auto]       │  ← Automatically generated
│ Khách hàng: [Viettel]   │  ← Start typing, select from dropdown
│ Điểm đi: [Hà Nội]       │  ← Autocomplete available
│ Điểm đến: [TP.HCM]      │  ← Autocomplete available
│ Giá cả: [5,000,000]     │  ← Required field
│ Khoán lương: [500,000]  │  ← Optional
│ Chi phí khác: [100,000] │  ← Optional
│ Ghi chú: [...]          │  ← Optional
│                         │
│      [Thêm]             │  ← Click to save
└─────────────────────────┘
```

**Step 2**: Click "Thêm" button (or press Ctrl+S)

**Step 3**: See your new trip appear in the table!

✅ **Done!** Your first trip is saved.

---

### Workflow 2: Search and Filter (1 minute)

**Quick Filter**:
1. Type in any field in the Input Form
2. Watch the "Filtered" tab update automatically
3. Results appear in real-time (300ms debounce)

**Advanced Filter**:
1. Click the filter icon (▼) in any column header
2. Check/uncheck values you want to see
3. Use the search box to find specific values
4. Click "Apply"

**Example**:
```
Filter by Customer:
☑ Viettel
☑ VNPT
☐ FPT
☐ Others

→ Shows only Viettel and VNPT trips
```

---

### Workflow 3: Use Price Lookup (1 minute)

**Step 1**: Switch to a Company tab (A, B, or C)

**Step 2**: Browse the price list

**Step 3**: Click on any row

**Step 4**: Form automatically fills with:
- Customer name
- Origin
- Destination
- Price
- Commission

**Step 5**: Adjust if needed and click "Thêm"

✅ **Super fast data entry!**

---

### Workflow 4: Edit Data (1 minute)

**Method 1: Direct Edit**
1. Double-click any cell in the table (or press F2)
2. Type new value
3. Press Enter
4. Changes save automatically

**Method 2: Context Menu**
1. Right-click on a row
2. Select "Edit Row"
3. Modify in the form
4. Click "Update"

---

### Workflow 5: Copy & Paste (30 seconds)

**From Excel to App**:
1. Copy cells in Excel (Ctrl+C)
2. Click in the table
3. Paste (Ctrl+V)
4. Data fills the cells

**Within App**:
1. Select cells (click and drag)
2. Copy (Ctrl+C)
3. Select destination
4. Paste (Ctrl+V)

**Duplicate Row**:
1. Right-click on row
2. Select "Duplicate Row" (or Ctrl+D)
3. New row created with auto-generated code

---

## Sample Workflows

### Scenario 1: Daily Data Entry

**Goal**: Enter 10 trips quickly

**Steps**:
1. Open the application
2. Use autocomplete for customer names
3. Use price lookup tabs for quick reference
4. Click on suggested prices to auto-fill
5. Adjust and save each trip
6. Use Ctrl+D to duplicate similar trips

**Time**: ~5 minutes for 10 trips

---

### Scenario 2: Monthly Report

**Goal**: Export filtered data to Excel

**Steps**:
1. Apply filters to show desired date range
2. Filter by department if needed
3. Menu → File → Export (Ctrl+E)
4. Select "Filtered Records"
5. Choose columns to export
6. Click "Export"
7. Open Excel file

**Time**: ~1 minute

---

### Scenario 3: Price Comparison

**Goal**: Compare prices across 3 companies

**Steps**:
1. Enter customer, origin, destination in form
2. Check "Filtered" tab for your data
3. Check "Company A" tab for their prices
4. Check "Company B" tab for their prices
5. Check "Company C" tab for their prices
6. Choose best price and click to fill form

**Time**: ~30 seconds

---

### Scenario 4: Bulk Import

**Goal**: Import 100 trips from Excel

**Steps**:
1. Prepare Excel file with columns:
   - ma_chuyen, khach_hang, diem_di, diem_den, gia_ca, etc.
2. Menu → File → Import (Ctrl+I)
3. Select your Excel file
4. Preview data and check for errors
5. Choose duplicate handling: Skip/Overwrite/Create New
6. Click "Import"
7. Wait for progress bar to complete

**Time**: ~2 minutes

---

### Scenario 5: Department Workflow

**Goal**: Push completed trips from Sales to Processing

**Steps**:
1. Switch to Sales department tab
2. Complete trip entries
3. Select trips to push
4. Right-click → "Push to Department"
5. Select "Processing"
6. Confirm push
7. Switch to Processing tab to verify

**Time**: ~1 minute

---

## Next Steps

### Learn More Features

Now that you know the basics, explore these advanced features:

1. **Dynamic Forms** (10 min)
   - Customize fields without coding
   - Menu → Tools → Field Manager
   - Add/remove/reorder fields

2. **Formulas** (10 min)
   - Auto-calculate fields
   - Menu → Tools → Formula Builder
   - Create expressions like `[Price] - [Cost]`

3. **Workflow Automation** (15 min)
   - Auto-push data between departments
   - Menu → Tools → Push Conditions
   - Set up rules and conditions

4. **Workspaces** (5 min)
   - Create multiple work environments
   - Menu → Department → Workspace Manager
   - Switch between projects easily

5. **Statistics** (5 min)
   - View system metrics
   - Menu → View → Statistics
   - Export reports

### Keyboard Shortcuts

Master these shortcuts to work faster:

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New record |
| Ctrl+S | Save record |
| Ctrl+C | Copy cells |
| Ctrl+V | Paste cells |
| Ctrl+D | Duplicate row |
| F2 | Edit cell |
| Delete | Delete rows |
| F5 | Refresh |

### Get Help

- **User Manual**: `docs/USER_MANUAL.md` - Complete guide
- **Technical Docs**: `docs/TECHNICAL_DOCUMENTATION.md` - For developers
- **Troubleshooting**: Check USER_MANUAL.md → "Xử Lý Sự Cố"
- **Logs**: Check `logs/transportapp.log` for errors

---

## Common Questions

### Q: How do I backup my data?

**A**: Database is stored in `data/transport.db`. Simply copy this file to backup.

```bash
# Manual backup
cp data/transport.db backups/transport_backup_$(date +%Y%m%d).db
```

### Q: Can I customize the fields?

**A**: Yes! Menu → Tools → Field Manager. Add/edit/remove fields without coding.

### Q: How do I import from my old Excel file?

**A**: Menu → File → Import. Make sure column names match (or map them in preview).

### Q: What if I make a mistake?

**A**: 
- For single record: Edit directly in table or use context menu
- For bulk changes: Export to Excel, fix, then re-import
- For deleted data: Restore from backup

### Q: How many records can it handle?

**A**: Tested with 10,000+ records. Performance remains good with pagination.

### Q: Can multiple users use it simultaneously?

**A**: Currently single-user. Multi-user support planned for future version.

### Q: Is my data secure?

**A**: Data stored locally in SQLite database. No cloud sync. You control your data.

---

## Video Tutorials (Optional)

### Tutorial 1: Getting Started (5 min)
- Installation
- First launch
- Adding your first trip

### Tutorial 2: Advanced Features (10 min)
- Filtering and search
- Price lookup
- Excel import/export

### Tutorial 3: Customization (10 min)
- Field management
- Formula builder
- Workflow automation

### Tutorial 4: Tips & Tricks (5 min)
- Keyboard shortcuts
- Copy/paste techniques
- Quick data entry methods

---

## Practice Exercises

### Exercise 1: Basic Entry
**Task**: Add 5 trips with different customers and routes

**Success Criteria**:
- All trips saved successfully
- Autocomplete used for at least 3 fields
- No validation errors

### Exercise 2: Filtering
**Task**: Find all trips for "Viettel" going to "TP.HCM"

**Success Criteria**:
- Correct filter applied
- Results displayed in table
- Count matches expectation

### Exercise 3: Price Lookup
**Task**: Use Company A price list to add 3 trips

**Success Criteria**:
- Clicked on price list rows
- Form auto-filled correctly
- Trips saved with correct prices

### Exercise 4: Excel Operations
**Task**: Export filtered data, modify in Excel, re-import

**Success Criteria**:
- Export successful
- Modifications made in Excel
- Import successful with no errors

### Exercise 5: Customization
**Task**: Add a new field "Driver Name" to the form

**Success Criteria**:
- Field added via Field Manager
- Field appears in form
- Data can be entered and saved

---

## Congratulations! 🎉

You've completed the Quick Start Guide!

You now know how to:
- ✅ Add and edit trips
- ✅ Search and filter data
- ✅ Use price lookup
- ✅ Import/Export Excel
- ✅ Navigate the interface

**Ready for more?** Check out the full User Manual for advanced features!

---

## Quick Reference Card

### Essential Actions

| Task | How To |
|------|--------|
| Add trip | Fill form → Click "Thêm" |
| Edit trip | Double-click cell → Edit → Enter |
| Delete trip | Select row → Delete key |
| Filter data | Type in form fields |
| Export | Ctrl+E → Choose options |
| Import | Ctrl+I → Select file |
| Copy cells | Ctrl+C |
| Paste cells | Ctrl+V |
| Duplicate row | Ctrl+D |
| Refresh | F5 |

### Need Help?

1. Press F1 for help
2. Check `docs/USER_MANUAL.md`
3. View logs in `logs/transportapp.log`
4. Contact support team

---

**Version**: 1.0  
**Last Updated**: 2024  
**Happy Managing! 🚚**
