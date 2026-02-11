Trade Matrix Module : User Guide

*******

1. Overview
What is the Trade Matrix Module?
What You Can Do
Benefits
2. Getting Started
Prerequisites
Quick Start (5 Minutes)
3. Key Concepts
Mode (Export vs Import)
Reporter (Origin)
Partner (Destination)
Benchmark vs Reference
Forecast
Crop Year
Intraflows
Unreported
View Type
4. Understanding View Mode
4.1 Navigation & Settings Section
4.1.1 Trade Matrix Name & Tabs
4.1.2 Data Filters
4.1.3 Settings Buttons
4.2 Pivot Table
Key Components
4.3 Bottom Section
Priority Rules Button
5. Creating Your First Trade Matrix
Step 1: Initiate Trade Matrix Creation
Step 2: Configure General Settings
Step 3: Select Content & Sources
3.1 Content (Select Datasets)
3.2 Choose Reporters
3.3 Choose Partners (Destinations)
3.4 Select Products
Step 4: Configure Settings
4.1 Define Unreported Reporters
4.2 Define Intraflows
Step 5: Choose Default Forecasts
Step 6: Configure Priority Rules
Configure Period Settings
For Each Reporter (e.g., "United States"):
Example Configuration for USA:
Repeat for All Reporters
Step 7: Finalize and Save
What You Should See
Next Steps
6. Troubleshooting
Issue 1: No Data Appears in Pivot Table
Issue 2: Cannot Forecast Data
Issue 3: Reference Columns Showing Empty Cells
Issue 4: Intraflows Not Showing/Hiding Correctly
Issue 5: Unreported Data Affecting Totals
Issue 6: Summary Table Not Showing
*******

1. Overview
What is the Trade Matrix Module?
The Trade Matrix Module offers a detailed and dynamic overview of global trade flows for agricultural commodities. Track key trade data such as quantities of crops exported, imported, and transferred between countries, and monitor seasonal trends in crop shipments across different regions.

What You Can Do
Track Key Metrics - Monitor monthly trade volumes, exports, imports, and cross-border flows

Create Forecasts - Build and compare multiple trade forecast scenarios

Analyze Trends - Compare benchmark data with reference datasets and projections

Customize Views - Create personalized dashboards with pivot tables and charts

Monitor Seasonality - Examine monthly, quarterly, or yearly trade patterns

Benefits
Centralized monitoring of international agricultural trade flows

Support for strategic decision-making for importers and exporters

Identification of market opportunities and supply chain disruptions

Flexible data visualization and reporting across regions
*******

2. Getting Started
Prerequisites
Before you begin, ensure you have:

Active Dnext platform account

Appropriate module permissions

At least one production configured / or shared on your environment

Basic familiarity with pivot tables (helpful but not required)

Quick Start (5 Minutes)
View existing trade matrix data:

Navigate to Trade Matrix Module

Hover on Fundamentals in the left navigation menu

Click Trade Matrix in the main navigation menu

You'll see a list of available trade matrices

Open a Trade Matrix

Click on any trade matrix name

The View Mode dashboard opens

Explore Your Data

Use filters to select Origin, Destination, Product, Month, or Crop Year

Click expand arrows to view regional details

Switch between different view modes using tabs

✅ Success Check: You should now see a pivot table with trade data organized by crop year and region.

temp_images/tradematrix_user_guide/img1.png
 *******


3. Key Concepts
💡 Tip: Understanding these concepts will make the module much easier to use.

Mode (Export vs Import)
What it is: The perspective from which trade flows are viewed

Options:

Export Mode: Shows quantities shipped OUT from reporters to partners

Import Mode: Shows quantities received IN by reporters from partners

Why it matters: The same trade flow appears differently depending on the mode

Example: USA exports 1 Thousand Ton to China = China imports 1 Thousand Ton s from USA

Reporter (Origin)
What it is: The country or region reporting the trade data - the source of the trade statistics

Why it matters: Reporters are the countries whose trade statistics you're analyzing

Example: If "USA" is the reporter in Export mode, you'll see USA's exports to various destinations

Partner (Destination)
What it is: The country or region that the reporter is trading with

Why it matters: Partners appear as rows in your pivot table, showing bilateral trade relationships

Example: If USA is the reporter and "Brazil" is a partner, you'll see trade flows between USA and Brazil

Benchmark vs Reference
What it is:

Benchmark (SND): The main dataset shown in your pivot table - the authoritative data source

Reference: A comparison dataset shown in yellow-highlighted columns

Why it matters: Allows you to compare different data sources 

Example: Use customs data as benchmark and lineup estimates as reference to spot discrepancies

Forecast
What it is: Projected values for future periods or incomplete current periods

Why it matters: Allows you to create multiple "what-if" scenarios and compare them side-by-side

Example: Create forecasts for next quarter's corn exports: "Conservative," "Expected," "Optimistic"

Crop Year
What it is: The market year for seasonal commodities

Why it matters: Tracks trade patterns across harvest cycles and marketing periods

Example: 2023/24, 2024/25 for crops following October-September marketing years

Intraflows
What it is: Trade flows between countries within the same region or group (e.g., within EU, within ASEAN)

Why it matters: Can be shown or hidden to focus on inter-regional vs intra-regional trade

Example: Trade between France and Germany can be classified as EU intraflow

⚠️ Note: Intraflows are defined based on the Trade Matrix configuration, allowing you to select which trade flows between countries within the same region or group  should be classified as intraflows. 

Unreported
What it is: Reporters whose data has been estimated or forecasted rather than coming from official sources

Why it matters: Helps distinguish between official trade statistics and estimates

Example: A country that doesn't publish monthly trade data may be set up as "unreported"

⚠️ Note: Unreported countries are defined through the Trade Matrix configuration, which allows you to select which countries' data should be classified as "Unreported" based on estimates or forecasts instead of official sources.

View Type
What it is: The time granularity at which data is displayed

Options:

Monthly: Shows data for each individual month

Quarterly: Aggregates data by quarter (Q1, Q2, Q3, Q4)

Yearly: Shows annual totals

Why it matters: Choose the view that matches your analysis needs - monthly for detailed patterns, yearly for trends
*******

4. Understanding View Mode
4.1 Navigation & Settings Section
Purpose: Control what data you see and how it's displayed

When to Use: Every time you open a trade matrix to filter, refresh, or customize your view

temp_images/tradematrix_user_guide/img2.png
4.1.1 Trade Matrix Name & Tabs
Location: Top-left corner of the screen

Function: Shows the current trade matrix name; tabs let you switch between different view modes

How to Use: Click any tab to view that perspective's data

Options: Click + button to create custom tabs (saved in your browser)

💡 Best Practice: Create custom tabs for frequently accessed combinations of filters and settings
********


4.1.2 Data Filters
Location: Center of the navigation bar

Function: Narrow down displayed data

How to Use:

Origin: Select reporting countries/regions

Origin Group: Filter by regional groupings of reporters

Destination: Choose destination countries/partners

Destination Group: Filter by regional groupings of partners

Product: Choose which commodity

Month: Select specific months

Crop Year: Pick one or multiple years

Options: Multi-select enabled (hold Ctrl/Cmd to select multiple)

Access: Click on the "Filters" icon to open the dropdown selection menu for each category. The filter options are presented as checkboxes, allowing users to select multiple values at once from a predefined list. This enables efficient filtering by combinations of origin, product, and crop year.

temp_images/tradematrix_user_guide/img3.png
********

4.1.3 Settings Buttons
SETTINGS BUTTONS (PARTIE 1)
Legends Button 🎨

temp_images/tradematrix_user_guide/img4.png
Function: Shows color coding for pivot table cells

How to Use: Hover over the button to see the legend popup

Color Meanings:

Yellow = Reference Data

White = Official Data

Honeydew= Cells available for forecast

Download Button 
temp_images/tradematrix_user_guide/img5.png
  

Function: Exports all aggregated trade matrix data

How to Use: Click to download as Excel/CSV

File Contents: Includes all visible data plus hidden rows if regions are collapsed

Refresh Data Button 
temp_images/tradematrix_user_guide/img6.png
  

Function: Updates trade matrix with latest data from source datasets

How to Use: Click to pull fresh data

When to Use:

After source datasets are updated

Before creating important forecasts

When data appears outdated

✅ Success Check: A success message appears on the top right of the screen

temp_images/tradematrix_user_guide/img7.png
********
SETTINGS BUTTONS (PARTIE 2)
View Settings Button ⚙️

Function: Opens configuration panel with three tabs

How to Use: Click the gear icon

Tab 1: General Settings

Zoom: Adjust table text size 

View Type: Choose Monthly, Quarterly, or Yearly view

Crop Year Start: Define which month starts the crop year

View Start Date: Set beginning of visible date range

View End Date: Set end of visible date range

Summary: Show/hide Summary table

Regions: Show/hide regional groupings

Display Total Row: Show/hide total row

Sources: Show/hide data source information

Tab 2: Conversion Factor

Purpose: Apply multiplication factors to values

Example: Convert tons to kilograms (multiply by 1000)

Per Product: Each product can have its own conversion

Tab 3: Data Scope Settings

Intraflows: Toggle to include/exclude intra-continental trade flows

Unreported: Toggle to include/exclude reporters with estimated data

💡 Best Practice: Set view type and conversions once, then save as a custom tab
********
 SETTINGS BUTTONS (PARTIE 3)
Columns Button 
temp_images/tradematrix_user_guide/img8.png
  

Function: Customize pivot table structure

How to Use:

Click button to open field list

Drag fields between areas:

Column Labels: Data shown as columns (usually months/years)

Row Groups: Data shown as rows (usually destinations)

Values: Metrics to display

Changes apply immediately

temp_images/tradematrix_user_guide/img9.png
Analysis Button 
temp_images/tradematrix_user_guide/img10.png
 

Function: Opens comparison charts

How to Use: Click to view charts in popup window

Selection Tab:

Shows benchmark vs trend for ONE selected origin

Displays all available crop years

How to Use: Click a cell in pivot table, then open Analysis

Summary Tab:

Shows benchmark vs trend for ALL origins combined

Aggregates data across all crop years

Use Case: Get big-picture trade trend view

temp_images/tradematrix_user_guide/img11.png
******
SETTINGS BUTTONS (PARTIE 4)
Forecasts Button 
temp_images/tradematrix_user_guide/img12.png
 

Function: Manage forecast scenarios

How to Use:

Load: Check boxes to display existing forecasts

Create: Click + New Forecast

Enter Name (e.g., "Conservative Export Forecast")

Enter Code (e.g., "FC-EXP-001")

Choose Color for identification

Manage: Edit or delete forecasts through the platform

temp_images/tradematrix_user_guide/img13.png
Changes Button 
temp_images/tradematrix_user_guide/img14.png
 

Function: Shows audit log of modifications

How to Use: View all changes made to forecasted cells

Log Includes:

User who made the change

Date and time

Cell location (origin, destination, month, year)

Old value → New value

Options: Delete specific changes to revert them

temp_images/tradematrix_user_guide/img15.png
Fit To Window Button ⛶

Function: Auto-sizes the pivot table to fit your screen

How to Use: Click once to auto-fit

Result: Removes scrollbars and adjusts column widths

💡 Best Practice: Use after applying filters to optimize viewing space
*******

4.2 Pivot Table
Purpose: The main data display area showing your trade metrics in rows and columns

When to Use: This is your primary workspace for viewing and analyzing data

temp_images/tradematrix_user_guide/img16.png
Key Components
1.Expand Reference Button 👁️

Location: Top-left of pivot table

Function: Shows/hides reference columns (highlighted in yellow)

How to Use:

Click to reveal reference data

Click again to hide

Visual: Reference columns appear with yellow background

2.Summary Table

Location: Top row of data section

Function: Displays the Crop Year Total - a single aggregate value in the far-left cell for each crop year row, summarizing data across all 12 months

Calculation: Automatic sum for the crop year

Toggle: Can be hidden in General Settings (Summary option)

Example:



Crop Year  | Total   | Jan  | Feb  | Mar  | ...
2024/25    | 150,000 | 12k  | 13k  | 15k  | ...
******
PIVOT TABLE (SUITE)
3.Region Divider

Location: Throughout the row list

Function: Serves as a divider for destinations by region, providing organized data view

How to Use:

Click region name to expand/collapse

View regional totals (Display Total Row Option) 

Toggle: Can be hidden in General Settings (Regions option)

Example Structure:



▼ North America (8,500)
  ↳ USA: 7,000
  ↳ Canada: 1,500
▼ Europe (12,300)
  ↳ France: 4,200
  ↳ Germany: 8,100
4.Forecastable Cells

Visual: Color-coded based on status

Function: Indicates cells where you can enter forecast values

How to Use:

Hover over Legends button to view color coding

Click any color-coded cell to modify its value

Color Guide: Each forecast has its own color for easy identification

Example : 

Forecastable Cell : 

temp_images/tradematrix_user_guide/img17.png
⚠️ Note: Color of the cell may change depending on the color you chose for your forecast

Official data cell : 

temp_images/tradematrix_user_guide/img18.png
⚠️ Note: All cells can be forecasted in the absence of official data

5.Reference Column

Visual: Yellow-highlighted columns corresponding to each crop year

Function: Allows easy comparison between benchmarked data and reference data

Use Case: Compare customs data with lineup data to analyze variations and trends

Example: Official customs statistics (white) vs preliminary estimates (yellow)
*******

4.3 Bottom Section
Purpose: Access configuration and priority rules

Configuration Button

Function: Opens trade matrix setup page

How to Use: Click to modify trade matrix settings

Takes You To: Configuration page with 5 tabs:

General: Edit Trade Matrix Name, Label, Mode (Export/Import), Unit, Quantity Divisor, Period (maximum range for download), and View (range displayed in view mode)

Content: Adjust Reporters and Partners included in your trade matrix, and define the products to cover

Settings:

Define Reporter-Partner combinations considered as Intraflows

Define Reporters considered as "Unreported" (with estimated/non-official data)

Forecasts: Select forecasts to be loaded by default

Scheduling: Set up automated refresh schedule (e.g., first day of month at 10 AM)

💡 When to Use: After creating a trade matrix, come here to fine-tune settings

Priority Rules Button
Function: Opens dataset priority configuration

How to Use: Click to define which datasets are used as benchmark (SND) and reference

Takes You To: Priority Rules page for each Reporter

Features:

Select datasets and forecasts for each Reporter

Designate one dataset as Reference, another as SND

Assign multiple datasets to single Reporter for different time periods (non-overlapping)

⚠️ Important: You must configure priority rules before data appears in your trade matrix
*******

5. Creating Your First Trade Matrix
SECTION 5.1-CREATION ÉTAPES 1-2
Goal: Create a trade matrix to track wheat exports across multiple countries

Time: 15-20 minutes
Difficulty: ⭐⭐⭐☆☆

Step 1: Initiate Trade Matrix Creation
Navigate to Trade Matrix Module from main menu

Click Create a New Trade Matrix button (top-right corner)

The General Settings page opens

✅ Checkpoint: You should see a form with fields for Name, Code, Labels, etc.

Step 2: Configure General Settings
temp_images/tradematrix_user_guide/img19.png
Enter the following information:

Field

What To Enter

Example

Name

Descriptive name for this trade matrix

"Global Wheat Exports 2025"

Code

Unique identifier (no spaces)

"TM-WHEAT-EXP-2025"

Labels

Existing label (contact support to create new ones)

"Grains Trade"

Mode

Define trade perspective

"Export" or "Import"

Unit

Unit of measurement

"Metric Tons (MT)"

Quantity Divisor

Multiplier for values

1000 (to show thousands)

Period

Time range covered (max for download)

"2020-10-01=>2026-09-30"

View Date

Time range displayed in view mode

"2023-10-01=>2025-09-30"

Forecastable

✅ Check to enable forecasting

Checked

Display ROW

✅ Check to show "Rest of World"

Checked

💡 Best Practice: Use consistent naming conventions like "TM-[COMMODITY]-[MODE]-[YEAR]" for easier organization

Understanding Mode:

Export: Shows quantities shipped OUT from reporters to partners

Import: Shows quantities received IN by reporters from partners

Click Next to proceed to Content
*******
SECTION 5.2 - CONTENT & SOURCES
Step 3: Select Content & Sources
The Content step has four sections: Content (datasets), Reporters, Partners, and Products

3.1 Content (Select Datasets)
temp_images/tradematrix_user_guide/img20.png
In the Content section, you'll select datasets from which you want to see the statistics.

Select relevant trade datasets:

✅ Global Wheat Trade Statistics

✅ Customs Export Data

These datasets will feed data into your trade matrix.

3.2 Choose Reporters
temp_images/tradematrix_user_guide/img21.png
Left Panel: Available reporters
Right Panel: Selected reporters

Find reporters in the left panel and check boxes next to desired countries:

✅ United States

✅ European Union

✅ Canada

✅ Australia

✅ Argentina

Click the → arrow button to move them to the right panel

By default, selected reporters will be placed under the "Other" group

Organize into Regional Groups:

Click Add a New Folder

A new group named "New Folder" appears

Click the Edit icon (✏️) to rename it "Americas"

Drag USA, Canada, Argentina into the "Americas" folder

Create another folder "Oceania" and add Australia

Create "Europe" folder and add European Union

✅ Checkpoint: Your selected reporters should be organized in regional folders

💡 Best Practice: Create regional groups first, then select reporters to place them directly into the right folders
*******
SECTION 5.2 - SUITE (PARTNERS & PRODUCTS)
3.3 Choose Partners (Destinations)
temp_images/tradematrix_user_guide/img22.png
Left Panel: Available partners
Right Panel: Selected partners

Find partners in the left panel and check boxes next to desired countries:

✅ China

✅ Egypt

✅ Indonesia

✅ Japan

✅ Philippines

Click the → arrow button to move them to the right panel

By default, selected partners will be placed under the "Other" group

Organize into Regional Groups:

Click Add a New Folder

Rename it "Asia"

Drag China, Indonesia, Japan, Philippines into "Asia" folder

Create "Africa" folder and add Egypt

✅ Checkpoint: Your selected partners should be organized in regional folders

3.4 Select Products
temp_images/tradematrix_user_guide/img23.png
Left Panel: Available products
Right Panel: Selected products

In the Products section:

Check the box for: ✅ Wheat

Click the → arrow to move it to the right panel

If tracking multiple wheat varieties:

☐ Hard Red Winter Wheat

☐ Soft White Wheat

Click Next to proceed to Settings
*******
SECTION 5.3 - CONFIGURATION DES PARAMÈTRES
Step 4: Configure Settings
The Settings step has two sections: Unreported and Intraflows

temp_images/tradematrix_user_guide/img24.png
*******

4.1 Define Unreported Reporters
What it is: Reporters whose data has been estimated or forecasted rather than from official sources

How to Use:

Select from the dropdown menu one or more reporters

These will be marked as "Unreported"

You can toggle their visibility in View Mode using Data Scope Settings

Example:

Select "Argentina" if its data is estimated

This helps distinguish official statistics from estimates

Why it matters: Allows filtering between official and estimated data when analyzing trade flows

4.2 Define Intraflows
What it is: Trade flows between countries within the same region or group

How to Use:

Left input box: Choose the Reporter

Right input box: Choose the Partner

The flow between these two will be considered an intraflow

Example:

Reporter: "France" → Partner: "Germany" = EU Intraflow

Reporter: "USA" → Partner: "Canada" = North America Intraflow

Why it matters: You can later choose to show or hide intraflows in view mode or when downloading data

💡 Best Practice: Define all relevant intra-regional flows during setup to have flexibility in analysis later

Common Intraflow Groups:

EU countries trading with each other

Click Next to proceed to Forecasts
*******
SECTION 5.4 - FORECASTS ET RÈGLES DE PRIORITÉ
Step 5: Choose Default Forecasts
temp_images/tradematrix_user_guide/img25.png
Purpose: Determines which forecasts load automatically when you open this trade matrix

Check forecasts you want loaded by default:

✅ USDA Official Export Forecast

✅ Internal Trade Estimate Q1

☐ Other forecasts (load manually when needed)

💡 Tip: Only select frequently used forecasts. You can always load others manually from View Mode using the Forecasts button.

Click Next to proceed to Priority Rules

Step 6: Configure Priority Rules
This is the most critical step - it determines which datasets appear in your pivot table.

temp_images/tradematrix_user_guide/img26.png
Once you click "Next" from Forecasts, then click "Done," you'll be taken to the Priority Rules page.

What You'll See:

Configuration for each Reporter you selected

Each reporter can have its own data sources

Configure Period Settings
temp_images/tradematrix_user_guide/img27.png
Choose your approach:

Option A: Period with No Bounds

One configuration covers all time periods

Simpler but less flexible

Option B: Multiple Defined Periods

Different configurations for different time ranges

More flexible - useful when data sources change over time

Periods must not overlap
********
SECTION 5.4 - RÈGLES DE PRIORITÉ (SUITE)
For Each Reporter (e.g., "United States"):
temp_images/tradematrix_user_guide/img28.png
Each period configuration has four sections:

1. Datasets & Forecasts

Function: Add available data sources

How to Use:

Click action buttons in the top-right corner

Click + Add Dataset or Add Forecast

Select your data source from dropdown

Example: "USA Census Bureau Export Data"

The dataset appears in the Available section

Repeat to add multiple datasets or forecasts as needed.

2. SND Section (Benchmark)

Function: Select which inputs act as benchmarks - the main data displayed

How to Use:

Drag and drop datasets from Available section into SND section

This becomes your primary data shown in the pivot table

Example:



📊 USA Census Bureau Export Data
3. As Reference Section

Function: Define reference inputs to compare against the benchmark

How to Use:

Drag and drop datasets from Available section into Reference section

This creates yellow-highlighted reference columns in your pivot table

Example:



📊 Previous Year USA Export Data
💡 Best Practice: Use reference data to compare:

Current year vs previous year

Preliminary data vs revised data

Official customs vs Lineups estimates
*******
SECTION 5.4 - RÈGLES DE PRIORITÉ (FIN)
4. Finalization Settings

Purpose: Define when values are finalized (cannot be forecasted or changed)

For each dataset in SND and Reference sections, choose:

Option

Meaning

Example Usage

Never Finalized

Values remain editable and forecastable

Internal estimates, future projections

Always Finalized

Values cannot be changed or forecasted

Historical official data, audited statistics

Conditional Finalization

Finalized based on criteria such as   

Publication Date

Shipment date

User validation within the Trade Matrix view mode

For preliminary data that becomes final

Conditional Finalization Options:

Publication Date: Data finalizes automatically for rows that have a publication date that match the condition

Shipment date: Data finalizes automaticly for rows that have a shipment date that match the condition

User Validation: You manually mark as final within the production view mode

💡 Best Practice:

Historical data (past years): Always Finalized

Current year: Conditional - Publication Date

Future years: Never Finalized (allows forecasting)

Example Configuration for USA:
Period: No Bounds

Available:



📊 USA Census Bureau Export Data
📊 USA Export Estimates 2024
📊 Previous Year Official Data
SND Section (Benchmark):



📊 USA Census Bureau Export Data
   Finalization: Conditional - Publication Date
As Reference Section:



📊 Previous Year Official Data
   Finalization: Always Finalized
Repeat for All Reporters
You must configure priority rules for each reporter:

United States

European Union

Canada

Australia

Argentina

⚠️ Important: If you don't configure a reporter, it won't show data in the trade matrix

********
SECTION 5.5 - FINALISATION ET DÉPANNAGE
Step 7: Finalize and Save
Review all configurations in the Priority Rules page

Ensure each reporter has at least one dataset in the SND section

Click Save Trade Matrix (top-right corner)

✅ Success: Your trade matrix is now created! You'll be taken to View Mode.

What You Should See
After creation, your trade matrix opens in View Mode displaying:

Trade matrix name at the top

Filters for Origin, Destination, Product, Month, Crop Year

Pivot table with:

Regional groups for destinations (Asia, Africa, etc.)

Countries under each region

Months or crop years as columns

Trade volume values in cells

Settings buttons across the top

Summary row showing crop year totals

🎉 Congratulations! You've created your first trade matrix.

Next Steps
Now that your trade matrix is created:

Explore the data:

Switch between different reporters using Origin filter

Click through regional groupings

Change view type (By Destination→  By Origin→ Monthly → Quarterly → Yearly)

Toggle data scope:

Open View Settings → Data Scope Settings

Toggle Intraflows on/off to see impact

Toggle Unreported on/off to filter estimated data

Create a forecast:

Click Forecasts button

Add projections for future months

Compare multiple forecast scenarios

Analyze trends:

Click Analysis button

View benchmark vs trend charts

Identify seasonal patterns

Compare with reference:

Click Expand Reference button

Spot differences between benchmark and reference data

Investigate discrepancies

Schedule refreshes:

Go to Configuration → Scheduling

Set up automated updates (e.g., monthly on the 1st at 10 AM)
*******

6. Troubleshooting
Issue 1: No Data Appears in Pivot Table
Symptoms: Empty cells or "No data" error message

Causes:

Priority rules not configured

Selected datasets don't have data for the chosen reporters

Date range doesn't match data availability

Filters excluding all data

Solutions:

Check Priority Rules:

Click Configuration button

Navigate to Priority Rules

Ensure each reporter has datasets in SND section

Verify datasets cover the products and time periods you selected

Verify Filters:

Clear all filters temporarily

Check if data appears

Add filters back one by one to identify the issue

Refresh Data:

Click Refresh Data button (🔄)

Wait for success message

Check if data now appears

Check Date Range:

Click Configuration button

Verify View Date range aligns with available data

Expand View Date range if needed

Remember: Trade data often has reporting delays

Verify Mode Setting:

Check if Mode is set to "Export" or "Import"

Ensure your datasets match the selected mode

If viewing exports, datasets must contain export data

Issue 2: Cannot Forecast Data
Symptoms: Cells not clickable, no color-coded forecastable cells appear

Causes:

Forecastable option disabled in General Settings

Cell data is finalized (Always Finalized rule)

Solutions:

Check General Settings:

Click Configuration button

Go to General tab

Ensure Forecastable is checked

Save changes

Check Finalization Rules:

Click Priority Rules button

Review Finalization Settings for that reporter

If "Always Finalized," change to:

"Never Finalized" for future periods

"Conditional" for current periods

Verify Cell Eligibility:

Hover over Legends button to see color guide

Only color-coded cells can be forecasted

White cells with official data cannot be forecasted unless finalization rules allow it
*******
SECTION 6 - DÉPANNAGE (SUITE)
Issue 3: Reference Columns Showing Empty Cells
Symptoms: Yellow-highlighted reference columns exist but contain no data

Causes:

No reference dataset assigned in Priority Rules

Reference dataset doesn't cover the visible time period

Reference dataset doesn't have data for the selected reporter

Solutions:

Expand Reference View:

Click Expand Reference button (👁️) at top-left of pivot table

Verify reference columns are visible

Check Priority Rules:

Click Priority Rules button

Navigate to the reporter configuration

Verify datasets are in "As Reference" section

If empty, drag a dataset from Available to As Reference

Verify Data Coverage:

Ensure reference dataset covers the crop years displayed

Check if reference dataset includes the selected product

Verify reporter exists in the reference dataset

Add Reference Data:

If no suitable reference exists, go to Priority Rules

Add a dataset to As Reference section

Save and refresh the trade matrix

Issue 4: Intraflows Not Showing/Hiding Correctly
Symptoms: Intraflows appear when they should be hidden, or vice versa

Causes:

Intraflows not properly configured in Settings

Data Scope Settings not toggled correctly

Reporter-Partner combinations don't match configuration

Solutions:

Check Intraflows Configuration:

Click Configuration button

Go to Settings tab

Review Intraflows section

Verify Reporter-Partner combinations are listed

Example: USA → Canada, France → Germany

Toggle Data Scope:

In View Mode, click View Settings button (⚙️)

Go to Data Scope Settings tab

Toggle Intraflows Button

Close settings and observe changes

Verify Flow Direction:

Ensure Reporter → Partner combination matches your Mode

If Mode is "Export," USA → Canada means USA exports to Canada

If Mode is "Import," USA → Canada means USA imports from Canada
*********
SECTION 6 - DÉPANNAGE (FIN)
Issue 5: Unreported Data Affecting Totals
Symptoms: Summary totals seem inflated or include estimated data

Causes:

Unreported reporters included in view

Data Scope Settings showing all reporters regardless of source quality

Solutions:

Check Unreported Configuration:

Click Configuration button

Go to Settings tab

Review Unreported section

Verify which reporters are marked as unreported

Toggle Unreported Visibility:

Click View Settings button (⚙️)

Go to Data Scope Settings tab

Toggle Unreported Button:

Watch summary totals adjust

Filter by Origin:

Use Origin filter to exclude unreported reporters manually

Compare totals with and without unreported data

Document which reporters use estimated vs official data

Issue 6: Summary Table Not Showing
Symptoms: Crop Years Total rows is missing from pivot table

Causes:

Summary option disabled in General Settings

Solutions:

Enable Summary:

Click View Settings button (⚙️)

Go to General Settings tab

Check that the Summary Button is toggled

Still Encountering issues or want more assistance? Please  Contact support@dnext.io 
*********