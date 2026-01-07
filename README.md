# Borehole Analyzer MVP

Simple Streamlit application for visualizing borehole geology data from CSV files.

## Overview

This tool generates ground subsurface profiles from borehole geology data exported from tablogs. It creates side-by-side visualizations of multiple boreholes with color-coded soil classifications and interactive features.

## Features

- 📊 Side-by-side borehole log visualization
- 🎨 Color-coded soil classifications (CH, CI, CL, GW, etc.)
- 🖱️ Interactive hover tooltips with detailed layer information
- 🔍 Filter and select specific boreholes to display
- 📄 **Subsurface Conditions Summary Table** - Professional geological unit grouping
- 🏗️ Automatic unit classification (Fill F1, F2; Residual R1, R2, etc.)
- 📝 Standards-compliant descriptions following BS 5930 format
- 📥 Download filtered data and summary table as CSV
- 📋 View raw data in table format

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Navigate to the project directory:
```bash
cd geo-borehole-analyzer
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the App

Start the Streamlit app:
```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

### Using the App

1. **Upload CSV File**: Click "Browse files" in the sidebar and select your GEOLOGY.csv file
2. **View Statistics**: See project summary (number of boreholes, layers, max depth)
3. **Select Boreholes**: Choose which boreholes to display using the multiselect dropdown
4. **Explore**: Hover over soil layers to see detailed information
5. **View Legend**: Expand the "Soil Classification Legend" to see color meanings
6. **📄 Subsurface Summary Table**: Expand this section to see professional geological unit grouping
   - Automatically groups soil layers into geological units (F1, F2, R1, R2, etc.)
   - Provides professional descriptions following geotechnical standards
   - Shows extent of occurrence (which boreholes, depths)
   - Download as CSV for inclusion in reports
7. **Download Data**: Expand "View Raw Data" to see and download filtered data

## CSV Format

The application expects a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `PROJ_ID` | Project identifier | S#239126 |
| `POINT_ID` | Borehole ID | BH01, BH02 |
| `TOP` | Top depth of layer (m) | 0.0 |
| `BASE` | Bottom depth of layer (m) | 0.3 |
| `Legend` | Soil classification | CH, CI, CL, GW |
| `Description` | Full soil description | "CLAY CH: high plasticity..." |
| `Classification` | Soil classification code | CH |
| `Origin1` | Soil origin | Fill, Residual |
| `Color` | Soil color | brown, grey, red brown |

## Soil Classifications

The app recognizes standard USCS soil classifications:

### Clays
- **CH**: High plasticity clay
- **CI**: Intermediate plasticity clay
- **CL**: Low plasticity clay
- **CI-CH**: CI-CH transition

### Gravels
- **GW**: Well-graded gravel
- **GP**: Poorly graded gravel
- **GM**: Silty gravel
- **GC**: Clayey gravel

### Sands
- **SW**: Well-graded sand
- **SP**: Poorly graded sand
- **SM**: Silty sand
- **SC**: Clayey sand

### Silts & Organics
- **ML**: Silt
- **MH**: Elastic silt
- **OL**: Organic silt
- **OH**: Organic clay
- **Pt**: Peat

## Subsurface Conditions Summary Table

The app automatically generates a professional geotechnical summary table that groups individual soil layers into geological units. This feature follows industry standards (BS 5930, AGS) for geotechnical reporting.

### How It Works

1. **Automatic Grouping**: Soil layers are grouped based on:
   - Geological origin (Fill, Residual, Alluvium)
   - Soil classification (CH, CI, CL, GW, etc.)
   - Stratigraphic position (depth)

2. **Unit Naming**: Units are assigned standard codes:
   - Fill: F1, F2, F3...
   - Residual: R1, R2, R3...
   - Alluvium: AL1, AL2...

3. **Professional Descriptions**: Each unit gets a description including:
   - Origin and material type
   - Soil classification (USCS)
   - Plasticity or density
   - Color range
   - Special features

4. **Extent of Occurrence**: Shows which boreholes and depth ranges

### Example Output

```
Unit: F1
Description: FILL – CLAY (CI to CL): medium to low plasticity, grey brown to brown, gravelly
Extent: Encountered from surface to approximately 0.3 mbgl in BH01, BH02, BH03.

Unit: R1
Description: RESIDUAL SOIL – CLAY (CI-CH): medium to high plasticity, light brown to red brown
Extent: Encountered from approximately 0.3 to 1.7 mbgl in all boreholes.
```

## Example

Using the provided sample file in `../geo_team/Reference/GEOLOGY.csv`:

```bash
streamlit run app.py
```

Then upload the sample CSV to see:
- 6 boreholes (BH01-BH06)
- Ground profile from 0-5m depth
- Fill and residual soil layers
- Predominantly clay soils (CH, CI, CL, CI-CH)
- **Subsurface summary table** with automatically grouped geological units

## Troubleshooting

### Missing columns error
Ensure your CSV has all required columns listed above. The app will show which columns are missing.

### No visualization shown
Make sure you've selected at least one borehole from the multiselect dropdown.

### App won't start
- Check Python version: `python --version` (needs 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

## Future Enhancements

Potential improvements for future versions:
- Cross-section correlation between boreholes
- 3D visualization of borehole array
- Export to PDF/image formats
- Statistical analysis of soil layers
- AGS format support
- SPT/CPT data integration
- ML-based soil classification

## Built With

- **Streamlit** - Web app framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations

## Project Structure

```
geo-borehole-analyzer/
├── app.py              # Main Streamlit application (single file)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Contributing

This is a MVP (Minimum Viable Product). Suggestions and improvements are welcome!

## License

Open source - use freely for geotechnical engineering projects.

---

**Built with guidance from GEO_TEAM multi-agent consultancy**
