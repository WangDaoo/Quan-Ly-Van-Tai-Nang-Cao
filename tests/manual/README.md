# Manual Testing Tools

This directory contains tools and utilities for manual testing of the Hệ Thống Quản Lý Vận Tải application.

## Files

### 1. Manual Testing Guide (`../../docs/MANUAL_TESTING_GUIDE.md`)
Comprehensive manual testing guide with detailed test cases covering:
- GUI Interactions
- Keyboard Shortcuts
- Responsive Design
- Error Scenarios

### 2. Manual Test Helper (`manual_test_helper.py`)
Automated verification script that checks:
- Database structure and sample data
- GUI components presence
- Keyboard shortcuts registration
- Responsive design capabilities

**Usage:**
```bash
python tests/manual/manual_test_helper.py
```

The script will:
1. Run database verification checks
2. Ask if you want to launch the GUI for testing
3. If yes, launch the application and run GUI verification
4. Display results in console and message box

### 3. Interactive Test Checklist (`interactive_test_checklist.py`)
GUI application for guided manual testing with interactive checklist.

**Features:**
- Organized test cases in tree structure
- Test descriptions and instructions
- Status tracking (Pass/Fail/Blocked/Not Tested)
- Notes for each test case
- Progress tracking
- Export results to file
- Summary statistics

**Usage:**
```bash
python tests/manual/interactive_test_checklist.py
```

**Workflow:**
1. Launch the interactive checklist application
2. Expand test categories to see individual test cases
3. Click on a test case to see its description
4. Perform the test manually
5. Add notes about observations or issues
6. Mark the test as Pass, Fail, or Blocked
7. The application auto-advances to the next test
8. View summary statistics at any time
9. Export results when complete

## Test Categories

### 1. GUI Interactions
- Main Window components
- Input Form Widget
- Autocomplete functionality
- Main Table Widget
- Excel-Like Features
- Advanced Filtering
- Suggestion Tabs
- Employee Tab Widget
- Pagination Widget
- Dialogs (Field Manager, Formula Builder, etc.)
- Import/Export functionality

### 2. Keyboard Shortcuts
- F2 (Edit cell)
- Enter (Move down)
- Tab (Move right)
- Shift+Tab (Move left)
- Ctrl+C (Copy)
- Ctrl+V (Paste)
- Ctrl+D (Duplicate row)
- Delete (Delete rows)
- Ctrl+Plus (Insert row below)
- F5 (Refresh)

### 3. Responsive Design
- Window resizing (minimum, maximum, various resolutions)
- Splitter behavior
- Component scaling
- Font scaling

### 4. Error Scenarios
- Validation errors
- Database errors
- Import/Export errors
- Formula errors
- Workflow errors
- Recovery testing

## Requirements

All manual testing tools require:
- Python 3.8+
- PyQt6
- Access to the application database
- All application dependencies installed

## Tips for Manual Testing

1. **Be Systematic**: Follow the checklist in order to ensure complete coverage
2. **Document Everything**: Add detailed notes for any issues found
3. **Test Edge Cases**: Don't just test the happy path
4. **Test Different Scenarios**: Try different data, different screen sizes, etc.
5. **Verify Error Messages**: Ensure error messages are user-friendly and helpful
6. **Check Performance**: Note any slow operations or UI lag
7. **Test Keyboard Navigation**: Verify all features work with keyboard only
8. **Test Accessibility**: Check contrast, font sizes, etc.

## Reporting Issues

When you find an issue during manual testing:

1. **Document in Notes**: Add detailed notes in the interactive checklist
2. **Mark as Failed**: Set the test status to "Fail"
3. **Include Steps to Reproduce**: Write clear steps in the notes
4. **Add Screenshots**: If possible, take screenshots (save separately)
5. **Export Results**: Export the test results when complete
6. **Create Issue**: Create a GitHub issue or bug report with details

## Example Test Session

```bash
# 1. Run automated verification first
python tests/manual/manual_test_helper.py
# Answer 'y' to launch GUI and run automated checks

# 2. Launch interactive checklist
python tests/manual/interactive_test_checklist.py

# 3. Work through test cases systematically
# - Click on each test case
# - Read the description
# - Perform the test
# - Add notes
# - Mark Pass/Fail/Blocked

# 4. Export results when complete
# Click "Export Results" button

# 5. Review summary
# Click "Show Summary" to see statistics
```

## Continuous Improvement

This manual testing suite should be updated when:
- New features are added
- Bugs are fixed
- User feedback suggests new test cases
- Edge cases are discovered

Keep the test cases relevant and comprehensive!
