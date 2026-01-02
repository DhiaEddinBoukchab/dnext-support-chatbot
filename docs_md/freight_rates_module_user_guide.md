Freight Rates Module User Guide
*******

Table of Content : 
 

Table of Content : 
1. Overview
What is the Net Freight Rates Module?
What You Can Do
Benefits
2. Getting Started
Prerequisites
Quick Start Guide (≈5 Minutes)
Step 1: Open the Module
Step 2: Select Your Data
Step 3: Explore the Table
3. Key Concepts
3.1 Dataset
3.2 Batches
3.3 Spot Date
3.4 Routing
3.5 Freight Terms
Common Freight Terms
3.6 Rate Columns
4. Understanding the Interface
4.1 Top Navigation Bar
4.1.1 Dataset Dropdown
4.1.2 Batch Selector
4.1.3 Spot Date Picker
4.1.4 Search Bar
4.1.5 Filter Panel
4.1.6 Freight Configuration Button ⚙️
Input Datasets
Output Datasets
Month Factor & Spot Day
4.1.7 Batches Button  
4.1.8 Estimates Button  
4.2 Main Table
Column Definitions
5. Batches & Estimates
5.1 What are Batches?
5.2 Managing Estimates (Edit or Create)
Estimate Overview (Top Section)
Basic Information
Financial Parameters
Vessel & Voyage Details
Trade & Timing
Vessel Details (Right Section)
Basic Vessel Information
Ballast Speed & Consumption
Loaded Speed & Consumption
Port Fuel Consumption
Additional Parameters
Total Times
Itinerary Section
Port Status Options
Itinerary Fields
Sea Passage
Draft Tab (Numeric Inputs)
Zone Tab (Categorical Selections)
Time Tab (Read-Only Outputs)
Bkr Cons Tab (Read-Only Outputs)
Practical Tips
Port Stay
Intake Tab
L. Intake Tab (Limit Intake)
Time Tab
Bkr Cons Tab
Tips
Bunkers
Columns
Notes
Misc Voyage Cost
Fields
Tips
Voyage Expenses & TC In Summary
Fields
Tips
Voyage Earnings Summary
Fields & Formulas
Tips
5.3 Forward Customization
View Options
Key Fields on Forward Customization Page
Direct Display
Forward Freight Market
Adjusted Forward Market
Baltic Route Raw
Premium vs Route
Additional Duration Parameters
Population of Spot & Forward Bunker Prices
Application of Relevant Bunker Prices
Variable Draft Port Intakes
Voyage Seasonal Adjustments
How Forward Customization Works
5.4 Managing Batches
Batches Page (List View)
Available Information
Available Actions
Create or Edit a Batch
Bulk Calculate
How It Works
Dialog Parameters
Notes
Operational Tips
6. Troubleshooting
6.1 Common Issues and Solutions
Issue: Module Not Visible in Dashboard
Issue: No Data Appearing in Table
Issue: Rate Values Showing as Empty or Zero
Issue: Estimates Not Calculating Correctly
Issue: Bulk Calculate Fails or Times Out
Issue: Filters Not Working as Expected
Issue: Forward Customization Not Displaying Data
Issue: Unable to Save Changes to Configuration
6.2 Data Quality Issues
Identifying Data Quality Problems
6.3 Getting Additional Help
Support Resources
Information to Include When Contacting Support
Appendix
Glossary of Terms
*******

1. Overview
What is the Net Freight Rates Module?
The Net Freight Rates module is your centralized platform for monitoring and analyzing shipping freight rates across different commodities, routes, and vessel types. It consolidates all your freight data,including spot rates, forward estimates, and configuration options—into one intuitive dashboard.

What You Can Do
Track Market Rates – Access current and historical freight rates for key commodities and trade routes

Compare Periods – Analyze rate fluctuations across current and future months (Spot, Nov, Dec, etc.)

Filter & Search – Instantly narrow results by commodity, vessel type, port, or routing

Manage Estimates – Generate freight estimates and simulate pricing scenarios

Batch Processing – Group freight lines into batches for streamlined review

Configure Freight Rules – Customize routing, terms, and default configurations

Benefits
Benefit

Description

Centralized View

Access all freight rate data in a single, unified workspace

Real-Time Market Insights

Always see the latest rates for each route and shipment type

Faster Decision-Making

Compare multiple months and routes side by side instantly

Customizable

Filter, configure, and visualize data in just a few clicks
*******

2. Getting Started
Prerequisites
Before you begin, ensure you have:

✅ An active DNEXT platform account

✅ Access rights to the Freight Rates module

✅ Access to at least one freight dataset (created in your environment or shared from another)

💡 Tip: If you don't see the module in your dashboard, contact support@dnext.io

Quick Start Guide (≈5 Minutes)
Step 1: Open the Module
From the DNEXT home page, navigate to Freight → Net Freight Rates

The default dataset (Daily Freight Rates (DNEXR)) loads automatically

temp_images/freight_rates_module_user_guide/img1.png
Step 2: Select Your Data
Use the Spot Date picker (top center) to choose the date for viewing rates

temp_images/freight_rates_module_user_guide/img2.png
 

Optionally select a Batch to filter by predefined groupings

temp_images/freight_rates_module_user_guide/img3.png
Step 3: Explore the Table
Each row represents a freight record (e.g., Barley from Constanta to Cai Mep)

Columns include vessel type, route, terms, and rate values for multiple months 

Use the filter icon 
temp_images/freight_rates_module_user_guide/img4.png
  on any column to refine your view

temp_images/freight_rates_module_user_guide/img5.png
✅ Success Check: You should now see a list of freight records filtered by your selected date and dataset.
*******

3. Key Concepts
Understanding these fundamental elements will help you navigate the Freight Rates module efficiently.

3.1 Dataset
What it is:
A dataset represents the source of your freight data. Each dataset includes multiple routes, vessel types, and date-based rate records.

Example:
Daily Freight Rates (DNEXR) – The primary dataset for viewing live and historical freight rates

Why it matters:
Selecting the correct dataset ensures you're analyzing the right version of freight data (e.g., official vs. simulation)

temp_images/freight_rates_module_user_guide/img6.png
3.2 Batches
What it is:
A batch groups multiple freight estimates together for streamlined review and analysis.

When to use:

Analyze freight rates for a specific spot date, client, or shipment group

Compare multiple routes or vessel types within a defined scope

How to use:

Click Select Batch on the top bar

Choose the desired batch name from the dropdown

The table automatically updates to show only records from that batch

temp_images/freight_rates_module_user_guide/img7.png
3.3 Spot Date
What it is:
The Spot Date defines the market date for freight rate display.

Example:
Selecting 2025-11-03 displays rates valid on November 3, 2025

Why it matters:
Freight rates change frequently. The spot date aligns your analysis with a specific day's market value, ensuring accuracy and relevance.

temp_images/freight_rates_module_user_guide/img8.png
3.4 Routing
What it is:
Routing indicates the path the vessel takes between Load and Discharge ports (e.g., Suez, Good Hope).

Why it matters:
Different routes affect voyage duration, risk exposure, and overall cost. A route via Suez might differ from Good Hope by several dollars per ton.

Tip:
Use routing filters to focus on specific corridors (e.g., all routes via Suez)

temp_images/freight_rates_module_user_guide/img9.png
3.5 Freight Terms
What it is:
Freight terms define contract conditions such as SHEX, FHEX, SHINC, and specify operational details like loading and discharge rates.

Common Freight Terms
Term

Meaning

Example

SHEX

Sundays and Holidays Excluded

Loading/discharging time doesn't count on Sundays or holidays. If laytime is 5 days SHEX and Sunday falls during that period, Sunday is excluded.

FHEX

Fridays and Holidays Excluded

Common in Gulf regions where Friday is a rest day. If laytime is 4 days FHEX and Friday falls in the period, it's excluded.

SHINC

Sundays and Holidays Included

Sundays and public holidays count as working days. If laytime is 5 days SHINC and Sunday falls in the period, it's included.

Loading Rate

Agreed speed for loading cargo

Typically measured in metric tons per day. Example: 10,000 MT/day for 50,000 MT cargo = 5 days laytime

Discharge Rate

Agreed speed for unloading cargo

Determines laytime for discharge. Example: 8,000 MT/day for 40,000 MT cargo = 5 days laytime

Why it matters:
Understanding these terms ensures accurate voyage planning, fair cost comparison, and clear responsibility allocation between shipowner and charterer—especially when ports have different rest days or working schedules.

3.6 Rate Columns
What they are:
Rate columns display freight prices per metric ton for each available month.

Column

Meaning

Spot

Current freight rate

Nov (25)

Forward rate for November 2025

Dec (25)

Forward rate for December 2025

How to use:
Compare Spot vs. Forward months to assess market direction.

Example:
If Spot = $38.25 and Nov (25) = $40.25 → a decrease is expected in November
*******

temp_images/freight_rates_module_user_guide/img10.png
4. Understanding the Interface
The Net Freight Rates interface consists of three main areas:

Top Navigation Bar – Controls datasets, batches, dates, and global filters

Main Table – Displays all freight rate data

Action Buttons – Provides access to configuration, batches, and estimates

temp_images/freight_rates_module_user_guide/img11.png
4.1 Top Navigation Bar
4.1.1 Dataset Dropdown
Purpose: Choose which dataset to display

How to Use:

Click the Dataset dropdown at the top left

Select from available datasets (e.g., Daily Freight Rates)

The table refreshes automatically

💡 Tip: Different datasets may represent different calculation methodologies or data sources

temp_images/freight_rates_module_user_guide/img12.png
4.1.2 Batch Selector
Purpose: Filter freight records grouped under a specific batch

How to Use:

Click Select Batch

Choose the desired batch from the dropdown

Only rates from that batch appear in the table

4.1.3 Spot Date Picker
Purpose: Select the date for viewing freight rates

How to Use:

Click the Spot Date calendar icon

Choose a specific date (e.g., 2025-11-03)

Displayed rates update automatically

4.1.4 Search Bar
Purpose: Quickly locate specific records by keyword

How to Use:

Type part of a commodity, port, or vessel name (e.g., "Soybean")

The table filters results in real-time

temp_images/freight_rates_module_user_guide/img13.png
4.1.5 Filter Panel
Purpose: Save your filters for quick access

How to Use:

Apply you filters to the table columns

Click the Filters button (top right)

write the name of your filter in the input box 

click Save

temp_images/freight_rates_module_user_guide/img14.png
4.1.6 Freight Configuration Button ⚙️
Purpose:
Manage system settings that define how rates are calculated and displayed. Configure various datasets and adjust settings based on factors like fuel prices, port distances, and vessel types.

How to Use:

Click the Freight Configuration button  in the Top Navigation Bar

temp_images/freight_rates_module_user_guide/img15.png
 

The Freight Configuration page opens with two main sections:

temp_images/freight_rates_module_user_guide/img16.png
Input Datasets
Control the underlying data used in freight rate calculations:

Parameter

Description

Bunkers Spot

Spot prices for marine fuel (essential for fuel cost calculations)

Port Distances

Distance data between ports (determines shipping costs by distance)

Bunkers

Fuel prices for total freight cost calculations

Forward Codes

Contractual terms for future freight shipments

Historical Spread

Historical freight rate spreads for comparison with current rates

Miscellaneous Costs

Insurance, handling charges, and other non-freight costs

Fuel EU Maritime

Maritime fuel pricing within the EU for European routes

Additional Values

Supplementary variables (regulations, route-specific factors)

CME Futures

Future marine fuel prices from commodities exchange

EU Ports

Port data within the EU influencing shipping costs

EWRI Dataset

Extra War Risk Insurance costs for conflict zones

Seasonal Margin

Seasonal adjustments for peak/off-peak periods

Port Terms

Port-specific terms and conditions affecting costs

Vessel Info

Vessel types, capacities, and operational details

Stowage Factors

Vessel stowage capacity for cargo volume/weight

Baltic Futures

Future prices for dry bulk commodities

Spot Routes

Shipping routes and associated spot rates

CO2 Applicability

Carbon emission regulation dates and impact

CO2 Type

CO2 emission types from vessels

Custom Misc. Costs

Customizable miscellaneous costs (special handling, storage)

TCE Factors

Time Charter Equivalent factors for vessel efficiency

Baltic Spot

Average spot rates for dry bulk commodities

TG Max Duration

Maximum duration for trade group contracts

ETS Price

EU ETS spot price for emissions (carbon compliance costs)

temp_images/freight_rates_module_user_guide/img17.png
Output Datasets
Define datasets used for output data (final freight rates, results, reports).

temp_images/freight_rates_module_user_guide/img18.png
Month Factor & Spot Day
Setting

Description

Current Month Factor

Adjusts freight calculations for the current month (e.g., 50% adjustment for market fluctuations)

Near Month Factor

Adjusts rates for the upcoming month (useful for predicting future pricing trends)

Current Spot Day

Defines which day of the month's rates to use (e.g., 15th for mid-month spot rates)

temp_images/freight_rates_module_user_guide/img19.png
 

Saving Changes:
Click the Save button at the bottom-right of the page to apply your configuration.

4.1.7 Batches Button 
temp_images/freight_rates_module_user_guide/img20.png
 
Purpose: Manage existing batches or create new ones

How to Use:

Click the Batches button to view all current batches

Available actions:

Create new batch

Edit existing batch

Delete batch

View batch details

Check batch statistics

Use Case:
Group batches by Name, Client, State, or Creation/Update Date for easy tracking and organization.

temp_images/freight_rates_module_user_guide/img21.png
4.1.8 Estimates Button 
temp_images/freight_rates_module_user_guide/img22.png
 
Purpose: Navigate to the Estimates Page for managing freight estimates

How to Use:

Click the Estimates button (top-right)

View available estimates with options to:

Create a New Estimate (button on top-right)

View Batches

Go to Freight Configuration page

Choose your desired action (edit, delete, or create an estimate)

temp_images/freight_rates_module_user_guide/img23.png
4.2 Main Table
The Main Table is the core of the module, displaying all your freight data in a structured, sortable format.

Each row represents a freight route with comprehensive details including commodity, vessel type, ports, routing, and rate values by month.

Preview unavailable
Column Definitions
Column

Description

Commodity 1 / 2

Primary and secondary commodities being shipped

Vessel

Vessel class (e.g., Handysize, Supramax, Kamsarmax)

Intake MT

Tonnage capacity in metric tons

Load / Discharge

Port of loading and discharge

Routing

Route path (Suez, Good Hope, etc.)

Origin

Geographical origin (e.g., Canakkale, Port Said)

L. Rate / D. Rate

Loading and discharging rates

L. Term / D. Term

Contractual terms (e.g., SHEX6, FHEX5)

Spot / Forward Columns

Current and forward freight values by month

Navigation Tips:

Click any column header to sort

Use column filter icons 
temp_images/freight_rates_module_user_guide/img24.png
  for quick filtering

Scroll horizontally to view all forward months

temp_images/freight_rates_module_user_guide/img25.png
Click any row to view detailed estimate information

temp_images/freight_rates_module_user_guide/img26.png
 
*******

5. Batches & Estimates

5.1 What are Batches?
Definition:
A batch groups multiple freight estimates together for streamlined review and recalculation.

When to use:

Analyze estimates for a specific spot date, client, or shipment group

Compare multiple routes or vessel types within a defined scope

Quick filter in Net Freight Rates:

Click Select Batch on the top bar

Choose a batch name

The table updates to show only records from that batch
*******

5.2 Managing Estimates (Edit or Create)
When you create or edit an estimate, you'll work with several interconnected sections that define the complete freight calculation.

temp_images/freight_rates_module_user_guide/img27.png
Estimate Overview (Top Section)
Basic Information
Field

Purpose

Estimate Name

Unique identifier for the freight transaction or shipment

Client Name

Customer associated with the estimate

Product 1

Primary commodity being shipped (e.g., Grains, Wheat, Barley)

Stowage Factor 1

Volume/space occupied by primary cargo per unit weight

Product 2

Optional secondary product for multi-commodity shipments

Stowage Factor 2

Stowage factor for secondary product (if applicable)

Cargo Size

Total quantity of cargo (measured in metric tons)

Financial Parameters
Field

Purpose

Moloo (%)

Percentage allocated for moisture loss (common for grains)

Brokerage (%)

Brokerage fee as percentage of total shipment cost

Add Com (%)

Additional commission paid to brokers/agents

temp_images/freight_rates_module_user_guide/img28.png
Vessel & Voyage Details
Trade & Timing
Field

Purpose

Trade Group

Classification for internal tracking by region/trade category

Max Duration

Maximum allowed shipment duration (for time-sensitive contracts)

Spot Date

Date for spot rate calculation (current or shipment start date)

Hedge Price

Locked-in price from hedge contracts (protection against market fluctuations)

Benchmark Price

Reference baseline price for calculating freight rates

Premium

Calculated as: Hedge Price - Benchmark Price

Ratio (%)

Calculated as: Benchmark Price / Hedge Price

temp_images/freight_rates_module_user_guide/img29.png
Vessel Details (Right Section)
Basic Vessel Information
Field

Purpose

Vessel Name

Name of vessel carrying the cargo

Calc Speed

Operating speed selection (Full Speed or Eco-Friendly Speed)

Dwt (Metric Ton)

Maximum weight capacity (cargo, fuel, crew, provisions) excluding ship's weight

Draft

Depth below waterline (affects fuel consumption and port accessibility)

TPC

Tonnage Per Centimeter - weight needed to change draft by 1 cm

Cubic

Total cubic volume for cargo capacity determination

Ballast Speed & Consumption
Field

Purpose

Bal Speed

Vessel speed while unladen (in ballast)

Bal VLSFO

Very Low Sulfur Fuel Oil cost during ballast

Bal LSMGO

Low Sulfur Marine Gas Oil cost during ballast

Loaded Speed & Consumption
Field

Purpose

Lad Speed

Vessel speed when fully loaded

Lad VLSFO

Very Low Sulfur Fuel Oil cost when loaded

Lad LSMGO

Low Sulfur Marine Gas Oil cost when loaded

Port Fuel Consumption
Field

Purpose

Port Idle VLSFO

VLSFO used while vessel is idle at port

Port Idle LSMGO

LSMGO used while vessel is idle at port

Port Working VLSFO

VLSFO used while vessel is actively working

Port Working LSMGO

LSMGO used while vessel is actively working

Additional Parameters
Field

Purpose

CST-FW-ROB

Conditions for fuel viscosity (CST), fresh water (FW), and remaining fuel/cargo (ROB)

temp_images/freight_rates_module_user_guide/img30.png
Total Times
This section calculates and displays the complete voyage timeline.

Field

Purpose

Bal Days

Total days vessel spends in ballast (affects fuel consumption)

Lad Days

Total days vessel is loaded with cargo

Rep Days

Days allowed before demurrage/detention charges apply

Total Sea Days

Total days spent traveling at sea

Load Days

Days spent loading cargo at ports

Discharge Days

Days spent unloading cargo at ports

Other Days

Days not accounted for in other categories

Total Port Days

Total port turnaround/dwell time

Total Duration

Complete voyage time from loading start to final unloading

temp_images/freight_rates_module_user_guide/img31.png
Itinerary Section
The Itinerary defines each stop along the voyage route.

Port Status Options
Status

Description

Origin

Port where cargo is loaded onto vessel

Load

Port where cargo is loaded into vessel

Discharge

Port where cargo will be unloaded

Top Off

Additional cargo loaded during transit

Waypoint

Temporary stopping point (not a destination)

Repositioning

Ports used for vessel repositioning

Discharge 2

Secondary unloading port

Itinerary Fields
Field

Purpose

Port Status

Defines the type of port activity (select from dropdown)

Port Name

Specific port name associated with the status

Berth

Specific berth for vessel docking

Geared

Whether port has equipment for cargo handling

Warzone

Whether port is in a high-risk/conflict zone

temp_images/freight_rates_module_user_guide/img32.png
How to Use:

Add rows for each port stop

Select appropriate Port Status for each row

Specify Port Name and additional parameters

Mark special conditions (Geared, Warzone) as needed

Sea Passage
The Sea Passage panel models sailing leg-by-leg with two main sections, each containing multiple tabs.

ℹ️ Note: A row is auto-created for every entry in the Itinerary (Origin, Load, Discharge, Top Off, Waypoint, Repositioning, Discharge 2)

Draft Tab (Numeric Inputs)
Field

Purpose

Draft

Sailing draft used for the leg

Density

Water density factor for the leg

VLSFO Dist

Sailing distance on VLSFO (auto-fills; editable)

LSMGO Dist

Sailing distance on LSMGO (auto-fills; editable)

Sea Margin (%)

Sea margin applied to leg (auto-fills; editable)

Behavior: These distances and margins auto-populate when you select Port Status and Port Name in Itinerary. Fine-tune them here if needed.

temp_images/freight_rates_module_user_guide/img33.png
Zone Tab (Categorical Selections)
Field

Purpose

LL Zone

Loadline/geographic zone classification for consumption/route rules

ECA/NECA

Emission Control Area flag (affects fuel mix/consumption logic)

temp_images/freight_rates_module_user_guide/img34.png
Time Tab (Read-Only Outputs)
Field

Purpose

VLSFO Time

Sailing time attributed to VLSFO on this leg

LSMGO Time

Sailing time attributed to LSMGO on this leg

Total Time

Total sailing time for the leg

Sources: Computed from distances, speed profile (Full/Eco), sea margin, and configuration.

temp_images/freight_rates_module_user_guide/img35.png
Bkr Cons Tab (Read-Only Outputs)
Field

Purpose

VLSFO Cons

Fuel consumption on VLSFO for the leg

LSMGO Cons

Fuel consumption on LSMGO for the leg

Total Mass

Total bunker mass consumed for the leg

Sources: Computed from distances, speeds, zone flags (ECA/NECA), vessel/fuel parameters.

temp_images/freight_rates_module_user_guide/img36.png
Practical Tips
Keep in sync: Changing ports/statuses in Itinerary refreshes calculated distances and margins

Override sparingly: If you edit calculated fields (e.g., VLSFO Dist), downstream outputs update accordingly

View mode matters: When viewing via Forward Customization, the Full/Eco filter impacts speed assumptions and Time/Consumption results

Port Stay
The Port Stay panel models loading/discharging operations at each port, containing four tabs.

ℹ️ Legend:
Output = read-only result cells
Derived = auto-computed from other inputs/config; usually editable only by changing upstream fields

Intake Tab
Field

Type

Purpose

MT

Output

Calculated intake tonnage for this port stop (reflects draft/zone constraints, vessel, and configuration)

temp_images/freight_rates_module_user_guide/img37.png
 

L. Intake Tab (Limit Intake)
Field

Type

Purpose

MT

Output

Maximum allowable intake at port (factors local restrictions like draft/berth limits and vessel characteristics)

temp_images/freight_rates_module_user_guide/img38.png
Time Tab
Field

Type

Purpose

Rate (MT/Day)

Derived

Effective loading/discharging rate based on vessel/port terms and configuration

Terms

Dropdown

Contract terms at port (e.g., SHEX, SHEX5)

Factor

Derived

Adjustment factor applied to base rate per selected Terms and port rules

Turn Time (Hours)

Derived

Port turnaround time (paperwork, shifting, mooring)

Idle Time (Hours)

Derived

Planned idle time at port (non-working hours, holidays, windows)

Total Time (Days)

Output

Computed total port time combining rate-based time and time components

Expense (USD)

Derived

Port call cost for this stop (port charges & misc) from configuration and terms

temp_images/freight_rates_module_user_guide/img39.png
Bkr Cons Tab
Field

Type

Purpose

VLSFO Cons

Output

Fuel consumed on VLSFO while at port (working/idle)

LSMGO Cons

Output

Fuel consumed on LSMGO while at port (ECA/NECA requirements)

Total Mass

Output

Total bunker mass consumed during port stay

temp_images/freight_rates_module_user_guide/img40.png
Tips
Itinerary drives rows: Add/remove/rename stops in Itinerary; Port Stay mirrors them

Upstream changes: Modify Itinerary, Terms, or Sea Passage to influence Derived values; Output cells refresh automatically

Terms and zones matter: Port Terms and ECA/NECA selections can materially change Rate, Factor, Time, and Bunker Cons results

Bunkers
The Bunkers panel sets fuel quotation points and displays per-leg bunker pricing and totals across three rows:

Bal – ballast leg (unladen)

Lad – laden leg (with cargo)

Total Mass – aggregated totals

ℹ️ Legend:
Input = user-editable field
Derived = auto-computed from configuration/market and selections
Output = read-only totals

Columns
Column

Type

Description

Bunkers

Input (Bal, Lad)

Select quotation location/market for pricing bunkers (dropdown). Changes update derived price fields

VLSFO

Derived (Bal, Lad) / Output (Total Mass)

Bal/Lad: Unit price for VLSFO at selected location<br>Total Mass: Total VLSFO consumed across voyage (tons)

LSMGO

Derived (Bal, Lad) / Output (Total Mass)

Bal/Lad: Unit price for Low Sulfur MGO at selected location<br>Total Mass: Total LSMGO consumed across voyage (tons)

Carbon

Derived (Bal, Lad) / Output (Total Mass)

Bal/Lad: Per-leg carbon cost/price from sum of fuel components<br>Total Mass: Total carbon tonnage for voyage (tons)

temp_images/freight_rates_module_user_guide/img41.png
Notes
Fuel/Carbon relationships: Carbon values for Bal and Lad derive from fuel components (VLSFO, USFO/ULSFO, LSMGO) priced at chosen bunker location

Downstream impact: These prices and totals feed Voyage Expenses & TC In Summary, driving Bunkers Total Cost and related EU ETS/FuelEU calculations

Misc Voyage Cost
This panel captures voyage-level extras outside of bunkers or port charges. Values flow into Voyage Expenses & TC In Summary.

ℹ️ Legend:
Input = user-entered
Derived = auto-computed from inputs/config
Output = read-only result

Fields
Field

Type

Purpose

Hold Cleaning

Derived

Cost to clean holds before loading (from product/port rules and configuration)

Dispatch

Input

Operational dispatch/agency charge per voyage or call

Misc 1 (Per Day)

Derived

Per-day miscellaneous allowance from configuration (applied over voyage/port days)

Misc 2 (Per Day)

Input

Per-day user-defined miscellaneous amount added to derived allowances

W. Routing

Derived

Weather/routing allowance from route class, season, or configuration factors

CVE (30 Days)

Derived

Continuous voyage expense for 30-day basis (comms, victualing) from configuration

EU ETS ($)

Output

Cost for EU Emissions Trading Scheme based on consumption/route exposure

FuelEU ($)

Output

Cost for FuelEU Maritime compliance based on fuel mix and voyage parameters

Freight Tax (%)

Input

Percentage tax on freight revenue per jurisdictional rules

Basic Insur.

Input

Fixed/basic insurance premium or deductible for voyage

EWRI ($)

Output

Extra War Risk Insurance cost from EWRI dataset and Itinerary risk flags (Warzone)

Surveys ($)

Input

Surveyor/inspection fees (pre-loading, draft survey, etc.) as lump sum

temp_images/freight_rates_module_user_guide/img42.png
Tips
Upstream drivers: Change Itinerary risk flags, product, or season to affect Derived costs

Auto-recalculation: Outputs (EU ETS, FuelEU, EWRI) recalculate automatically from fuel consumption, zones (ECA/NECA), and configuration

User discretion: Input fields allow manual adjustments for specific voyage requirements

Voyage Expenses & TC In Summary
This panel aggregates voyage costs and time-charter (TC) elements into a comprehensive summary.

ℹ️ Legend:
Input = user-entered
Derived = auto-computed from upstream data/config
Output = read-only result

Fields
Field

Type

Formula/Description

Bunkers

Output

Total bunker cost from Bunkers panel (Bal + Lad + port consumption)

Ports & Misc

Output

Sum of port charges and miscellaneous voyage costs (Port Stay + Misc Voyage Cost)

Total Voyage Cost

Output

Aggregate operating cost excluding hire<br>Formula: Bunkers + Ports & Misc

TC In Add Com (%)

Input

Additional commission percentage applied to TC-in (hire) calculations

Net Hire Cost

Output

Cost of vessel hire over voyage, after commissions/adjustments<br>Formula: Daily Hire × Total Days (adjusted per commission/terms)

Total Cost Inc. Hire

Output

Grand total cost including hire<br>Formula: Total Voyage Cost + Net Hire Cost

Delivery

Derived

Delivery port/basis for hire calculations (from itinerary/route logic)

Gross TC Hire ($/d)

Derived

Daily gross time-charter rate for hire computations (from vessel/market inputs)

Gross BB

Input

Gross ballast bonus (gross adjustment for delivery/redelivery economics)

FIO Result (Pmt)

Output

Free In/Out result in payment terms—freight outcome after costs and TC economics

temp_images/freight_rates_module_user_guide/img43.png
Tips
Automatic updates: Adjusting Bunkers, Port Stay, or Misc Voyage Cost updates Ports & Misc, Total Voyage Cost, and downstream totals

Commission impact: TC In Add Com (%) directly affects Net Hire Cost—use carefully to reflect contractual terms

Comprehensive view: This summary provides complete cost visibility for informed decision-making

Voyage Earnings Summary
This panel summarizes revenue-side outcomes and converts them into time-normalized earning metrics.

ℹ️ Legend:
Input = user-entered
Output = read-only result (computed)
Com Amount = commission percentage from Add Com (%) / freight commission settings

Fields & Formulas
Field

Type

Formula/Description

Final Intake

Output

Final shipped tonnage after intake limits/adjustments (from Port Stay/Sea Passage)

Gross Freight

Output

Freight before commission<br>Formula: FIO Rate × Final Intake

Net Freight

Output

Freight after commission<br>Formula: FIO Rate × (1 − Com Amount) × Final Intake

Net Result

Output

Voyage P&L before hire normalization<br>Formula: Net Freight − Total Voyage Cost<br>Note: Total Voyage Cost includes bunkers, ports & misc, and hire if using "Total Cost Inc. Hire" basis

FIO Rate (Pmt)

Input

Contracted Free-In/Out freight rate per metric ton

Net TCE ($/D)

Output

Net Time-Charter Equivalent per day (normalized earnings)<br>Formula: ((Final Intake × (FIO Rate × (1 − Com Amount))) − Total Voyage) / Total Duration

temp_images/freight_rates_module_user_guide/img44.png
Tips
Real-time updates: Changing FIO Rate (Pmt) or Add Com (%) immediately updates Gross Freight, Net Freight, Net Result, and Net TCE

Prerequisite accuracy: Ensure Total Duration and Total Voyage Cost are finalized (Sea Passage, Port Stay, Bunkers, Misc, Hire) for meaningful Net TCE

Performance metric: Net TCE provides a standardized daily earnings metric for comparing different voyage scenarios
*******

5.3 Forward Customization
The Forward Customization page is designed exclusively for visualizing future freight pricing scenarios. It provides insights into how various factors—such as market conditions, bunker prices, and vessel speeds—could impact freight rates for future periods.

Preview unavailable
View Options
Users can toggle between two operational views to see how vessel speeds affect projected prices:

Full (Full Speed): Displays forward pricing based on full operational speed

Eco (Eco-friendly speed): Displays forward pricing based on more fuel-efficient, eco-friendly speed

⚠️ Important: No actual customizations or edits can be made on this page. It serves as a visualization tool only.

temp_images/freight_rates_module_user_guide/img45.png
Key Fields on Forward Customization Page
Direct Display
Purpose: Displays initial values used for forward freight calculation, such as Baltic pricing. This read-only field shows the market data used to calculate freight prices for different routes.

Forward Freight Market
Purpose: Displays forecasted freight values for future months. This data represents projected pricing trends, providing insights into how rates may evolve.

Adjusted Forward Market
Purpose: Shows adjusted forward market values reflecting anticipated changes in market conditions or external factors. This field displays the impact of anticipated adjustments but is not editable.

Baltic Route Raw
Purpose: Displays the raw (unmodified) Baltic route price. This base value is used to calculate freight prices and is shown for informational purposes only.

Premium vs Route
Purpose: Shows the premium or discount applied to specific routes, indicating how route-specific factors (demand, conditions) influence final pricing.

Additional Duration Parameters
Purpose: Displays voyage duration, reflecting how time factors into pricing for specific routes. Helps visualize duration's effect on cost but cannot be adjusted directly.

Population of Spot & Forward Bunker Prices
Purpose: Displays bunker fuel prices broken down by spot and forward prices. These prices reflect fuel costs affecting freight pricing in future periods.

Application of Relevant Bunker Prices
Purpose: Shows how bunker prices are applied across different route segments (load port, discharge port). This read-only display reflects fuel pricing for various voyage legs.

Variable Draft Port Intakes
Purpose: Displays intake rates for ports based on draft characteristics. Helps visualize how draft-related factors affect cargo intake but is not editable.

Voyage Seasonal Adjustments
Purpose: Displays seasonal factors that may influence freight costs, such as idle time or port congestion. This data provides insight into how seasonal variations may affect costs.

How Forward Customization Works
Visualization Options: At the page top, select between Full (Full Speed) and Eco (Eco-friendly speed) views to see how vessel speed impacts freight pricing across different time periods

Display Only: The Forward Customization page is read-only and does not allow data changes. It's used solely for visualizing how various factors influence future freight rates

Quick Comparison: Users can quickly compare different operational scenarios by toggling the speed filter, enabling informed decision-making
*******

5.4 Managing Batches
Batches Page (List View)
The Batches page lists all existing batches with their key attributes, providing a centralized management hub.

temp_images/freight_rates_module_user_guide/img46.png
Available Information
Batch name

Client

Creator

Status

Created/Updated dates

Available Actions
From the Batches page, you can:

Open a batch to review its estimates

Create a new batch

Edit batch details

Delete a batch

Bulk Calculate selected batches

View basic statistics (count of estimates, last run, status)

Create or Edit a Batch
From the Batches page:

Click Create Batch (or select a batch and click Edit)

Fill in or update the core fields:

Batch Name – Human-readable identifier

Client – Customer this batch belongs to

Comment – Optional context for collaborators

temp_images/freight_rates_module_user_guide/img47.png
Add/Remove estimates the batch should contain

temp_images/freight_rates_module_user_guide/img48.png
 

Click Save

💡 Tip: Keep batch naming consistent for easy searching and organization

Bulk Calculate
Use Bulk Calculate to run or re-run estimate computations for multiple batches simultaneously.

temp_images/freight_rates_module_user_guide/img49.png
How It Works
On the Batches page, select one or more batches

Click Bulk Calculate

If no batch is selected, the action applies to batches not currently running

A dialog opens requesting run parameters

temp_images/freight_rates_module_user_guide/img50.png
 

After submission, recalculations are queued

Batch statuses update as runs progress

Dialog Parameters
All parameters are visible in the pop-up:

Parameter

Description

VC Dataset

Dataset for virtual/visible calculations during the run

TC Dataset

Dataset for test/time-charter output (or configured TC target)

Spot Dates

One or more dates to use as pricing position for all estimates in scope

Current Month Factor (%)

Factor applied to current month pricing logic for forward curves

Near Month Factor (%)

Factor applied to next month in forward logic

Execution Type

Scheduling behavior for the run:
• Daily – Run using each selected spot date's daily settings
• Friday – Run using end-of-week pricing cadence (Friday logic)

Notes
Month Factors: Mirror controls in Freight Configuration and weight how near-dated forward months populate during calculation

Input respect: The run respects each estimate's inputs (vessel profile, itinerary, port terms) and chosen datasets

Dataset selection: Choose datasets carefully to ensure calculations use appropriate market data

Operational Tips
Pre-flight checks:
Confirm Freight Configuration datasets and priority rules are up to date before bulk runs

Scope carefully:
Use batch filters (client, creator, date) to target only the sets you intend to recalculate

Monitor status:
After submitting Bulk Calculate, watch batch status and last run timestamps. Investigate any failures via the estimate's Changes/Logs

Reproducibility:
Record the VC/TC datasets and Month Factors used when you need a repeatable analysis trail
*******

6. Troubleshooting
This section helps you resolve common issues and optimize your use of the Net Freight Rates module.

6.1 Common Issues and Solutions
Issue: Module Not Visible in Dashboard
Problem: Cannot find the Net Freight Rates module in your DNEXT dashboard

Solutions:

Verify you have the correct access permissions

Check if you're logged into the correct DNEXT environment

Contact support@dnext.io to request module access

Clear browser cache and cookies, then log in again

Prevention: Ensure your account has been provisioned with appropriate module permissions during onboarding

Issue: No Data Appearing in Table
Problem: The main table shows no freight records despite selecting a dataset and date

Solutions:

Check Dataset: Ensure you've selected an active dataset with data for the chosen date

Verify Spot Date: Confirm the spot date has available data (try selecting a different date)

Clear Filters: Remove all active filters by clicking the filter reset button

Check Batch Selection: If a batch is selected, try removing the selection to get the default view

Reload Page: Refresh your browser (Ctrl+F5 or Cmd+Shift+R)

Prevention: Always start with a known valid dataset and recent spot date when opening the module

Issue: Rate Values Showing as Empty or Zero
Problem: Some or all rate columns display empty cells or zero values

Solutions:

Market Data Availability: Verify that market data exists for the selected spot date and forward months

Configuration Check: Review Freight Configuration to ensure all required input datasets are properly selected

Route Coverage: Confirm the route is covered in your dataset's scope

Calculation Status: Check if estimates need recalculation (status indicator)

Forward Month Availability: Some forward months may not yet have published rates

Prevention: Regularly update input datasets in Freight Configuration and run batch calculations on schedule

Issue: Estimates Not Calculating Correctly
Problem: Estimate calculations produce unexpected results or fail to complete

Solutions:

Check Itinerary: Ensure all itinerary rows have valid Port Names and Port Status selections

Verify Vessel Details: Confirm all required vessel parameters are filled in (Dwt, speeds, consumption rates)

Review Configuration: Check that all input datasets in Freight Configuration are current and valid

Port Compatibility: Ensure selected ports are compatible with vessel draft and size

Bunker Prices: Verify bunker location selections have valid price data for the spot date

View Logs: Check the estimate's Changes/Logs for specific error messages

Prevention: Validate all inputs before saving estimates; 

Issue: Bulk Calculate Fails or Times Out
Problem: Bulk Calculate operation fails to complete or shows timeout errors

Solutions:

Reduce Batch Size: Select fewer batches per bulk calculate operation

Verify Datasets: Ensure VC and TC datasets specified in parameters exist and are accessible

Sequential Processing: Try calculating batches one at a time to identify problematic estimates

Review Spot Dates: Ensure selected spot dates have available market data

Check Network: Verify stable internet connection during calculation

Prevention: limit to small number of  batches per operation

Issue: Filters Not Working as Expected
Problem: Applied filters don't narrow results correctly or seem to be ignored

Solutions:

Clear All Filters: Reset filters and apply them one at a time

Check Filter Syntax: Ensure filter text matches exact values (case-sensitive in some fields)

Multiple Filters: When using multiple filters, they work as AND conditions (all must match)

Refresh Data: Click the refresh button after applying filters

Browser Cache: Clear browser cache if filters persistently malfunction

Prevention: Apply filters methodically, testing each one individually before combining

Issue: Forward Customization Not Displaying Data
Problem: Forward Customization page shows no visualization or incomplete data

Solutions:

Speed Selection: Ensure Full or Eco speed is selected at the top of the page

Estimate Calculation: Verify the underlying estimate has been calculated successfully

Forward Data Availability: Check if forward month data exists in configuration datasets

Configuration Complete: Ensure all required configuration parameters are set (Month Factors, datasets)

Prevention: Calculate estimates fully before viewing Forward Customization; keep configuration current

Issue: Unable to Save Changes to Configuration
Problem: Changes made in Freight Configuration don't save or revert after saving

Solutions:

Permission Check: Verify you have configuration edit permissions

Required Fields: Ensure all mandatory fields are populated before saving

Dataset Validity: Confirm selected datasets exist and are accessible

Browser Session: Log out and log back in, then try again

Network Interruption: Ensure stable connection during save operation

Prevention: Only authorized users should modify configuration; coordinate with team before making changes

6.2 Data Quality Issues
Identifying Data Quality Problems
Common indicators:

Unexpected zero values in rate columns

Missing port or vessel information

Inconsistent routing data

Extreme outliers in freight rates

Calculation errors or warnings

Solutions:

Source Data Review: Check original data sources for completeness and accuracy

Configuration Audit: Review all input dataset selections in Freight Configuration

Historical Comparison: Compare current rates with historical data for anomalies

Dataset Updates: Ensure all datasets are updated to latest versions

Contact Support: Report persistent data quality issues to support@dnext.io
*******

6.3 Getting Additional Help
Support Resources
Email Support:
support@dnext.io
Response time: 24-48 hours

 

Information to Include When Contacting Support
When reporting an issue, please provide:

New User Training:
Contact  support@dnext.io for:

onboarding sessions

Team training workshops

Custom configuration assistance

Appendix
Glossary of Terms
Term

Definition

Term

Definition

Ballast

Vessel traveling empty without cargo

Dwt

Deadweight Tonnage - maximum weight capacity

ECA/NECA

Emission Control Area / North American ECA

FIO

Free In/Out - freight terms excluding loading/discharging costs

Laytime

Time allowed for loading/discharging cargo

TCE

Time Charter Equivalent - normalized daily earnings

VLSFO

Very Low Sulfur Fuel Oil

LSMGO

Low Sulfur Marine Gas Oil

SHEX

Sundays and Holidays Excluded

SHINC

Sundays and Holidays Included

For additional assistance, please don't hesitate to contact our support team at support@dnext.io.*******
