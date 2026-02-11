





Production Module: User Guide

*******


Table of content : 
1. Overview
What is the Production Module?
What You Can Do
Benefits
2. Getting Started
Prerequisites
Quick Start (5 Minutes)
3. Key Concepts
SND Items
Reporter
Benchmark vs Reference
Forecast
Crop Year
4. Understanding View Mode
4.1 Navigation & Settings Section
4.1.1 Production Name & Tabs
4.1.2 Data Filters
4.1.3 Settings Buttons
Download Button  
 Refresh Data Button   
4.2 Pivot Table
Key Components
4.3 Bottom Section
Configuration Button
Priority Rules Button
4.3 Bottom Section
Configuration Button
Priority Rules Button
5. Creating Your First Production
Goal: Create a production to track corn area and yield across multiple countries
Step 1: Initiate Production Creation
Step 2: Configure Base Settings
Step 3: Select SND Items
Step 4: Configure Each SND Item
Step 5: Select Content & Sources
5.1 Choose Reporters (Geographic Locations)
5.2 Select Products
Step 6: Choose Default Forecasts
Step 7: Configure Priority Rules
Configure Period Settings
For Each Reporter (e.g., "United States"):
Step 8: Finalize and Save
What You Should See
Next Steps
6. Troubleshooting
Issue 1: No Data Appears in Pivot Table
Issue 2: Cannot Forecast Data
Issue 3: Reference Columns Showing Empty Cells
Issue 4: Calculations Seem Wrong
*******

1. Overview
What is the Production Module?
The Production Module helps you track and analyze agricultural data across multiple regions and time periods. Monitor planting trends, crop yields, and production forecasts in one centralized dashboard.

What You Can Do
Track Key Metrics - Monitor area planted, harvested, abandoned, crop yield, and production

Create Forecasts - Build and compare multiple forecast scenarios

Analyze Trends - Compare historical data with benchmarks and projections

Customize Views - Create personalized dashboards with pivot tables and charts

Benefits
Centralized monitoring of agricultural production across regions and time periods

Streamlined forecast management and comparison

Flexible data visualization and reporting
*******

2. Getting Started
Prerequisites
Before you begin, ensure you have:

Active Dnext platform account

Appropriate module permissions

At least one dataset configured in your account

Basic familiarity with pivot tables (helpful but not required)

 

 

Quick Start (5 Minutes)
View existing production data:

Navigate to Production Module

Hover on the Fundamentals in the left navigation menu

Click Production in the main navigation menu

You'll see a list of available productions

Open a Production

Click on any production name

The View Mode dashboard opens

Explore Your Data

Use filters to select Origin, Product, or Crop Year

Click expand arrows to view regional details

✅ Success Check: You should now see a pivot table with agricultural data organized by crop year and region.

temp_images/production_module_user_guide/img1.png
*******

3. Key Concepts
💡 Tip: Understanding these concepts will make the module much easier to use.

SND Items
What it is: An SND item represents a specific agricultural metric you want to track — such as Area Planted, Crop Yield, or Area Harvested. Each item appears as a separate tab in the production view, letting you switch easily between different metrics.

Reporter
What it is: The geographical locations (countries, states, or regions) included in your production

Why it matters: Reporters appear as rows in your pivot table, showing data for each location

Example: For a global wheat production, your reporters might be USA, Canada, France, Australia, etc.

Benchmark vs Reference
What it is:

Benchmark: The main dataset shown in your pivot table. It represents the official, authoritative data, usually it is what we have over our SnD.

Reference: A comparison dataset shown in yellow-highlighted columns

Why it matters: This lets you compare current data against historical baselines or different data sources

Example: Use last year's official data as your benchmark and this year's preliminary estimates as your reference to spot differences

Forecast
What it is: Projected values for future periods or incomplete current periods

Why it matters: Allows you to create multiple "what-if" scenarios and compare them side-by-side

Example: Create three forecasts for next year's corn yield: "Conservative" (5 tons/ha), "Expected" (6 tons/ha), "Optimistic" (7 tons/ha)

Crop Year
What it is: The market year, following the SnD calendar.

Why it matters: Allows you to track changes over time and identify trends

Example: 2023/24, 2024/25, 2025/26 for crops with multi-year growing seasons
*******

4. Understanding View Mode
4.1 Navigation & Settings Section
Purpose: Control what data you see and how it's displayed

When to Use: Every time you open a production to filter, refresh, or customize your view

temp_images/production_module_user_guide/img2.png
4.1.1 Production Name & Tabs
Location: Top-left corner of the screen

Function: Shows the current production name; tabs let you switch between SND items

How to Use: Click any tab to view that metric's data

Options: Click + button to create custom tabs (saved in your browser)

💡 Best Practice: Create custom tabs for frequently accessed combinations of filters and settings

4.1.2 Data Filters
Location: Center of the navigation bar

Function: Narrow down displayed data

How to Use:

Origin: Select specific countries/regions

Product: Choose which crop or commodity

Crop Year: Pick one or multiple years

Options: Multi-select enabled (hold Ctrl/Cmd to select multiple)

Access: Click on the "Filters" icon to open the dropdown selection menu for each category. The filter options are presented as checkboxes, allowing users to select multiple values at once from a predefined list. This enables efficient filtering by combinations of origin, product, and crop year.

temp_images/production_module_user_guide/img3.png
 ******
SETTINGS BUTTONS (PARTIE 1)
4.1.3 Settings Buttons
Legends Button 🎨

temp_images/production_module_user_guide/img4.png
Function: Shows color coding for forecast cells

How to Use: Hover over the button to see the legend popup

Color Meanings:

Yellow = Reference Data

White = Official Data

Honeydew= Cells available for forecast

Download Button 
temp_images/production_module_user_guide/img5.png
 
Function: Exports all aggregated production data

How to Use: Click to download as Excel/CSV

File Contents: Includes all visible data plus hidden rows if regions are collapsed

 Refresh Data Button  
temp_images/production_module_user_guide/img6.png
 
 ******
 SETTINGS BUTTONS (PARTIE 2)

Function: Updates production with latest data from source datasets

How to Use: Click to pull fresh data

When to Use:

After source datasets are updated

Before creating important forecasts

When data appears outdated

✅ Success Check: A Green Success Message Appear on the top right of the screen 

temp_images/production_module_user_guide/img7.png
 

View Settings Button ⚙️

Function: Opens configuration panel with three tabs

How to Use: Click the gear icon

Tab 1: General Settings

Zoom: Adjust table text size (80%-150%)

Summary: Show/hide total row at the top

Regions: Show/hide regional groupings

Sources: Show/hide data source information

Tab 2: Conversion Settings

Purpose: Apply multiplication factors to values

Example: Convert hectares to acres (multiply by 2.47)

Per Tab: Each SND item can have its own conversion

Tab 3: Decimal Settings

Purpose: Set decimal places displayed

Options: 0-4 decimal places

Default: 2 decimal places

temp_images/production_module_user_guide/img8.png
💡 Best Practice: Set conversions once, then save as a custom tab

Columns Button   
temp_images/production_module_user_guide/img9.png
 

Function: Customize pivot table structure

How to Use:

Click button to open field list

Drag fields between areas:

Column Labels: Data shown as columns (usually crop years)

Row Groups: Data shown as rows (usually origins/regions)

Values: Metrics to display (SND items)

Changes apply immediately

temp_images/production_module_user_guide/img10.png
********
SETTINGS BUTTONS (PARTIE 3)
Analysis Button 📈

Function: Opens comparison charts

How to Use: Click to view charts in popup window

Selection Tab:

Shows benchmark vs trend for ONE selected origin

Displays all available crop years

How to Use: Click a cell in pivot table, then open Analysis

Summary Tab:

Shows benchmark vs trend for ALL origins combined

Aggregates data across all crop years

Use Case: Get big-picture trend view

temp_images/production_module_user_guide/img11.png
Forecasts Button 🔮

Function: Manage forecast scenarios

How to Use:

Load: Check boxes to display existing forecasts

Create: Click + New Forecast

Enter Name (e.g., "Conservative Estimate")

Enter Code (e.g., "FC-001")

Choose Color for identification

Manage: Edit or delete forecasts

temp_images/production_module_user_guide/img12.png
********
 SETTINGS BUTTONS (PARTIE 4)
Changes Button 📝

Function: Shows audit log of modifications

How to Use: View all changes made to forecasted cells

Log Includes:

User who made the change

Date and time

Cell location (origin, year, item)

Old value → New value

Options: Delete specific changes to revert them

temp_images/production_module_user_guide/img13.png
Fit To Window Button ⛶

Function: Auto-sizes the pivot table to fit your screen

How to Use: Click once to auto-fit

Result: Removes scrollbars and adjusts column widths

💡 Best Practice: Use after applying filters to optimize viewing space
*******

4.2 Pivot Table
Purpose: The main data display area showing your production metrics in rows and columns

When to Use: This is your primary workspace for viewing and analyzing data

temp_images/production_module_user_guide/img14.png
Key Components
Expand Reference Button 👁️

Location: Top-left of pivot table

Function: Shows/hides reference columns (highlighted in yellow)

How to Use:

Click to reveal reference data

Click again to hide

Visual: Reference columns appear with yellow background

Summary Row

Location: Top row of data section

Function: Displays totals for each crop year across all origins

Calculation: Automatic sum for current SND item

Toggle: Can be hidden in General Settings

Example:



Summary    | 2023    | 2024    | 2025
Area       | 15,000  | 16,200  | 17,500
Region Divider

Location: Throughout the row list

Function: Groups origins by geographical region

How to Use:

Click region name to expand/collapse

View regional totals

Toggle: Can be hidden in General Settings

Example Structure:



▼ North America (Total: 8,500)
  ↳ USA: 7,000
  ↳ Canada: 1,500
▼ Europe (Total: 12,300)
  ↳ France: 4,200
  ↳ Germany: 3,100
Forecastable Cells

Visual: Color-coded based on status

Function: Indicates cells where you can enter forecast values

How to Use: Click any colored cell to modify its value

Color Guide: Hover over Legends button for current color scheme

Example : 

Forecastable Cell : 

temp_images/production_module_user_guide/img15.png
⚠️ Note: Color of the Cell may change depending on the color you chose for your forecast: 

Official data cell : 

temp_images/production_module_user_guide/img16.png
⚠️ Note: All cells can be forecasted in the absence of official data

Reference Column

Visual: Yellow-highlighted columns next to each crop year

Function: Shows comparison data from your reference dataset

Use Case: Quickly spot differences between benchmark and reference

Example: Compare preliminary estimates (benchmark) against last year's final data (reference)
*******

4.3 Bottom Section
Purpose: Access configuration and priority rules

Configuration Button
Function: Opens production setup page

How to Use: Click to modify production settings

Takes You To: Configuration page with 5 tabs:

Base Settings

Configuration

Content & Sources

Forecasts

Scheduling

💡 When to Use: After creating a production, come here to fine-tune settings

Priority Rules Button
Function: Opens dataset priority configuration

How to Use: Click to define which datasets are used as benchmark/reference

Takes You To: Priority Rules page organized by reporter

⚠️ Important: You must configure priority rules before data appears in your production

*******


5. Creating Your First Production
CRÉATION ÉTAPES 1-2
Goal: Create a production to track corn area and yield across multiple countries
Time: 15-20 minutes Difficulty: ⭐⭐⭐☆☆

Step 1: Initiate Production Creation
Navigate to Production Module from main menu

Click Create a New Production button (top-right corner)

The Base Settings page opens

✅ Checkpoint: You should see a form with fields for Name, Code, Labels, etc.

Step 2: Configure Base Settings
temp_images/production_module_user_guide/img17.png
Enter the following information:

Field

What To Enter

Example

Name

Descriptive name for this production

"Global Corn Production 2025"

Code

Unique identifier (no spaces)

"PRD-CORN-2025"

Labels

Existing label (contact support to create new ones)

"Grains"

Origin

Geographic scope

"Global" or specific country

Period

Time range covered

"2020-10-01=>2026-10-01"

View Date

Time range displayed in the view mode

"2023-10-01=>2025-10-01"

Forecastable

✅ Check to enable forecasting

Checked

Display ROW

✅ Check to show "Rest of World"

Checked

💡 Best Practice: Use consistent naming conventions like "PRD-[CROP]-[YEAR]" for easier organization

Click Next to proceed to Configuration

Step 3: Select SND Items
temp_images/production_module_user_guide/img18.png
SND Items are the metrics you want to track.

In the SND Item section, you'll see a list of available items

Check the boxes for items you want to include:

✅ Area Planted

✅ Area Harvested

✅ Crop Yield

✅ Crop Production

✅ Area Abandoned

Click on the “>” Button to bring them to the right panel

✅ Checkpoint: Selected items appear on the right panel

Click Next to configure each item

Step 4: Configure Each SND Item
You'll configure each selected item individually.

temp_images/production_module_user_guide/img19.png
Example For "Area Abandoned":

Enable Forecast: ✅ Check (allows forecasting future values)

Is National Undefined the Sum of Each Region:

✅ Check if national = sum of all regions

☐ Uncheck if using a formula or separate dataset

Formula: Leave blank (unless calculating from other items)

Example for Area Abandoned : (Area harvested - Area planted) / Area harvested

Quantity Divisor: Enter the divisor 

Example : use 1000 to convert to thousands

Unit: Enter the unit 

Example : use Precent for Area Abandoned

Repeat for other items

Click Next when all items are configured
Step 5: Select Content & Sources
*******

5.1 Choose Reporters (Geographic Locations)
temp_images/production_module_user_guide/img20.png
Left Panel: Available reporters Right Panel: Selected reporters

Find reporters in the left panel

Check the boxes next to desired countries:

✅ United States

✅ Brazil

✅ Argentina

✅ China

✅ Ukraine

Click the →arrow button to move them to the right panel

Organize into Regional Groups:

Click Add a New Folder

A folder named "New Folder" appears

Click the edit icon (✏️) and rename it "Americas"

Drag USA, Brazil, Argentina into the "Americas" folder

Create another folder "Asia" and add China

Create "Europe" folder and add Ukraine

✅ Checkpoint: Your selected reporters should be organized in regional folders

💡 Best Practice: the most efficient way here is to create the desired regional groups , then select the reporters. And Even if you have made mistakes you can just drag the reporter to the correct regional group


5.2 Select Products
temp_images/production_module_user_guide/img21.png
In the Products section, check the box for:

✅ Corn 

If tracking multiple varieties, you can select:

☐ Yellow Corn 

☐ Corn - White

Click Next to proceed to Forecasts

Step 6: Choose Default Forecasts

temp_images/production_module_user_guide/img22.png
This determines which forecasts load automatically when you open this production.

Check forecasts you want loaded by default:

✅ USDA Official Forecast

✅ Internal Estimate Q1

☐ Other forecasts (load manually when needed)

💡 Tip: Only select frequently used forecasts. You can always load others manually from View Mode.

Click Next to proceed to Priority Rules

Step 7: Configure Priority Rules
This is the most critical step - it determines which datasets appear in your pivot table.

temp_images/production_module_user_guide/img23.png
You'll see:

Tabs for each SND Item (Area Planted, Crop Yield, etc.)

Each reporter (USA, Brazil, etc.) has its own configuration

Configure Period Settings
temp_images/production_module_user_guide/img24.png
Choose your approach:

Option A: Single Period (No Bounds)

One configuration covers all time periods

Simpler but less flexible

Option B: Multiple Defined Periods

Different configurations for different time ranges

More flexible but requires more setup

For Each Reporter (e.g., "United States"):
temp_images/production_module_user_guide/img25.png
Add Datasets Or Forecasts

Click + Add Dataset or Add Forecast (top-right)

Select your data source from the dropdown

Example: "USDA NASS Corn Data"

The dataset appears in the Available section

Assign to SND (Benchmark)

Drag the dataset from Available to SND Section

This becomes your main data displayed in the pivot table

Assign to Reference 

If you have a comparison dataset, drag it to As Reference Section

This creates the yellow-highlighted reference columns

Example: Use previous year's final data as reference

Set Finalization Rules

For each dataset, choose when values cannot be changed:

Option

Meaning

Example Usage

Never Finalized

Always editable

For internal estimates

Always Finalized

Cannot change or forecast

For official published data

Conditional

Finalized based on criteria such as   

Publication Date

Cut-off Date

User validation within the production view mode

For preliminary data that becomes final

Conditional Options:

Publication Date: Finalizes after dataset publishes

Cut-off Date: Finalizes after specific date

User Validation: You manually mark as final in View Mode

💡 Best Practice:

Historical data → Always Finalized

Current year → Conditional (Publication Date)

Future years → Never Finalized (for forecasting)

Example Configuration for USA - Area Planted:

SND (Benchmark):

As Reference:

  📊 USDA NASS Corn Area
     Finalization: Conditional - Publication Date

📊 USDA Previous Season Final
     Finalization: Always Finalized

✅ Checkpoint: Each reporter should have at least one dataset in the SND section

Repeat for all reporters:

Brazil

Argentina

China

Ukraine

⚠️ Important: If you don't configure a reporter, it won't show data in the production

Configure Other SND Items

Switch to the next tab (e.g., "Crop Yield") and repeat the priority rules setup.

Time-Saving Tip: If using the same datasets across items, the configuration will be similar.

Step 8: Finalize and Save
Review all configurations

Click Done at the bottom of the page

You'll be redirected to the Priority Rules summary page

Click Save Production (top-right corner)

✅ Success: Your production is now created! You'll be taken to View Mode.

What You Should See
After creation, your production opens in View Mode displaying:

Tabs for each SND item (Area Planted, Crop Yield, etc.)

Pivot table with:

Regional groups (Americas, Asia, Europe)

Countries under each region

Crop years as columns

Data values in cells

Filters at the top

Settings buttons

🎉 Congratulations! You've created your first production.

Next Steps
Now that your production is created:

Explore the data: Click through tabs and expand regions

Create a forecast: Use the Forecasts button to add projections

Analyze trends: Click Analysis to view charts

Schedule refreshes: Go to Configuration > Scheduling to automate updates
*******

6. Troubleshooting
Issue 1: No Data Appears in Pivot Table
Symptoms: Empty cells or "No data" Error message

Causes:

Priority rules not configured

Loaded datasets in the priority rules do not have data 

Date range doesn't match data availability

Solutions:

Check Priority Rules:

Click Configuration button

Navigate to Priority Rules

Ensure each reporter has datasets in SND section

ensure the dataset has data that matches with the reporter , product & time range

Verify Filters:

Clear all filters temporarily

Check if data appears

Refresh Data:

Click Refresh Data button

Wait for completion message

Check Date Range:

Ensure View Date in Base Settings covers available data periods

Issue 2: Cannot Forecast Data
Symptoms: cells not clickable

Causes:

Forecastable option disabled in Base Settings

Solutions:

Check Base Settings:

Click Configuration button

Go to Base Settings tab

Ensure Forecastable is checked

Save changes

Check Finalization Rules:

Go to Priority Rules

Review Finalization Settings for that reporter

If "Always Finalized", change to "Never Finalized" for future periods

Issue 3: Reference Columns Showing Empty Cells
Symptoms: Empty cells in the Reference Column

Causes:

No reference dataset assigned

Reference dataset has no data for visible period

Solutions:

Click Expand Reference Button (top-left of pivot table)

Check Priority Rules:

Go to Priority Rules page

Verify datasets are in "As Reference" section

If empty, add a dataset then drag & drop it there

Verify Data Availability:

Ensure reference dataset covers the crop years in view

Issue 4: Calculations Seem Wrong
Symptoms: Totals don't match, formulas giving unexpected results

Causes:

Incorrect formula in Configuration

Still Encountering issues or want more assistance? Please  Contact support@dnext.io *******
********