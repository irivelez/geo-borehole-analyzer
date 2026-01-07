"""
Borehole Analyzer MVP
Simple Streamlit app for visualizing borehole geology data from CSV files
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================================
# CONFIGURATION
# ============================================================================

# Soil classification color mapping (based on common geotechnical colors)
SOIL_COLORS = {
    'CH': '#8B4513',      # High plasticity clay - dark brown
    'CI': '#A0522D',      # Intermediate plasticity clay - sienna
    'CL': '#D2691E',      # Low plasticity clay - chocolate
    'CI-CH': '#8B6914',   # CI-CH transition - dark goldenrod
    'GW': '#808080',      # Well-graded gravel - grey
    'GP': '#A9A9A9',      # Poorly graded gravel - dark grey
    'GM': '#888888',      # Silty gravel - grey
    'GC': '#777777',      # Clayey gravel - dim grey
    'SW': '#F4A460',      # Well-graded sand - sandy brown
    'SP': '#DEB887',      # Poorly graded sand - burlywood
    'SM': '#D2B48C',      # Silty sand - tan
    'SC': '#BC8F8F',      # Clayey sand - rosy brown
    'ML': '#DAA520',      # Silt - goldenrod
    'MH': '#B8860B',      # Elastic silt - dark goldenrod
    'OL': '#556B2F',      # Organic silt - dark olive green
    'OH': '#6B8E23',      # Organic clay - olive drab
    'Pt': '#2F4F4F',      # Peat - dark slate grey
}

# Default color for unknown classifications
DEFAULT_COLOR = '#CCCCCC'

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

@st.cache_data
def load_borehole_data(uploaded_file):
    """
    Load and parse borehole geology CSV file

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        pandas.DataFrame: Cleaned borehole data
    """
    df = pd.read_csv(uploaded_file)

    # Select only the columns we need
    required_cols = ['PROJ_ID', 'POINT_ID', 'TOP', 'BASE', 'Legend',
                     'Description', 'Classification', 'Origin1', 'Color']

    # Check if all required columns exist
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        return None

    df = df[required_cols].copy()

    # Ensure numeric depth columns
    df['TOP'] = pd.to_numeric(df['TOP'], errors='coerce')
    df['BASE'] = pd.to_numeric(df['BASE'], errors='coerce')

    # Calculate layer thickness
    df['THICKNESS'] = df['BASE'] - df['TOP']

    # Sort by borehole ID and depth
    df = df.sort_values(['POINT_ID', 'TOP'])

    return df

def get_soil_color(classification):
    """
    Get color for soil classification

    Args:
        classification: Soil classification code (e.g., 'CH', 'CI', 'GW')

    Returns:
        str: Hex color code
    """
    if pd.isna(classification):
        return DEFAULT_COLOR
    return SOIL_COLORS.get(str(classification).strip(), DEFAULT_COLOR)

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_borehole_logs(df, selected_boreholes, show_descriptions=True):
    """
    Create side-by-side borehole log visualization

    Args:
        df: DataFrame with borehole data
        selected_boreholes: List of borehole IDs to display
        show_descriptions: Whether to show full descriptions in hover

    Returns:
        plotly.graph_objects.Figure
    """
    if not selected_boreholes:
        st.warning("Please select at least one borehole")
        return None

    # Create subplots - one column per borehole
    fig = make_subplots(
        rows=1,
        cols=len(selected_boreholes),
        subplot_titles=selected_boreholes,
        shared_yaxes=True,
        horizontal_spacing=0.02
    )

    # Find max depth for consistent y-axis
    max_depth = df[df['POINT_ID'].isin(selected_boreholes)]['BASE'].max()

    for col_idx, bh_id in enumerate(selected_boreholes, start=1):
        # Filter data for this borehole
        bh_data = df[df['POINT_ID'] == bh_id].copy()

        if bh_data.empty:
            continue

        # Create bars for each soil layer
        for idx, row in bh_data.iterrows():
            # Prepare hover text
            hover_text = f"<b>{row['Legend']}</b><br>"
            hover_text += f"Depth: {row['TOP']:.2f} - {row['BASE']:.2f} m<br>"
            hover_text += f"Thickness: {row['THICKNESS']:.2f} m<br>"
            hover_text += f"Origin: {row['Origin1']}<br>"
            if show_descriptions and not pd.isna(row['Description']):
                # Truncate long descriptions
                desc = str(row['Description'])[:150]
                if len(str(row['Description'])) > 150:
                    desc += "..."
                hover_text += f"<br>{desc}"

            # Add bar for this layer
            fig.add_trace(
                go.Bar(
                    x=[1],
                    y=[row['THICKNESS']],
                    base=row['TOP'],
                    marker=dict(
                        color=get_soil_color(row['Legend']),
                        line=dict(color='black', width=0.5)
                    ),
                    hovertext=hover_text,
                    hoverinfo='text',
                    showlegend=False,
                    name=row['Legend']
                ),
                row=1,
                col=col_idx
            )

    # Update layout
    fig.update_layout(
        title="Borehole Logs - Ground Subsurface Profile",
        height=800,
        barmode='stack',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=10),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Update y-axis (depth axis) - inverted so depth increases downward
    fig.update_yaxes(
        title_text="Depth (m)",
        autorange="reversed",
        range=[0, max_depth * 1.05],  # Add 5% padding
        tickformat=".1f",
        gridcolor='lightgrey',
        showgrid=True,
        row=1,
        col=1
    )

    # Update x-axes - hide them as they're not meaningful
    for col_idx in range(1, len(selected_boreholes) + 1):
        fig.update_xaxes(
            showticklabels=False,
            showgrid=False,
            row=1,
            col=col_idx
        )

    return fig

def create_soil_legend():
    """Create a legend showing soil classifications and colors"""
    st.markdown("### Soil Classification Legend")

    # Group by soil type
    clay_soils = {'CH': 'High plasticity clay', 'CI': 'Intermediate plasticity clay',
                  'CL': 'Low plasticity clay', 'CI-CH': 'CI-CH transition'}
    gravel_soils = {'GW': 'Well-graded gravel', 'GP': 'Poorly graded gravel',
                    'GM': 'Silty gravel', 'GC': 'Clayey gravel'}
    sand_soils = {'SW': 'Well-graded sand', 'SP': 'Poorly graded sand',
                  'SM': 'Silty sand', 'SC': 'Clayey sand'}

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Clays:**")
        for code, name in clay_soils.items():
            color = SOIL_COLORS.get(code, DEFAULT_COLOR)
            st.markdown(
                f'<div style="background-color:{color}; padding:5px; margin:2px; border-radius:3px;">'
                f'<span style="color:white; font-weight:bold;">{code}</span> - {name}</div>',
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("**Gravels:**")
        for code, name in gravel_soils.items():
            color = SOIL_COLORS.get(code, DEFAULT_COLOR)
            st.markdown(
                f'<div style="background-color:{color}; padding:5px; margin:2px; border-radius:3px;">'
                f'<span style="color:white; font-weight:bold;">{code}</span> - {name}</div>',
                unsafe_allow_html=True
            )

    with col3:
        st.markdown("**Sands:**")
        for code, name in sand_soils.items():
            color = SOIL_COLORS.get(code, DEFAULT_COLOR)
            st.markdown(
                f'<div style="background-color:{color}; padding:5px; margin:2px; border-radius:3px;">'
                f'<span style="color:white; font-weight:bold;">{code}</span> - {name}</div>',
                unsafe_allow_html=True
            )

# ============================================================================
# SUBSURFACE CONDITIONS SUMMARY TABLE
# ============================================================================

def classify_soil_group(legend):
    """
    Group similar soil classifications for unit formation

    Args:
        legend: Soil classification code (e.g., 'CH', 'CI-CH')

    Returns:
        str: Group identifier
    """
    if pd.isna(legend):
        return 'Unknown'

    legend = str(legend).strip()

    # Clay groupings
    if legend in ['CL', 'CL-CI']:
        return 'CL_Group'
    elif legend in ['CI', 'CI-CH']:
        return 'CI_Group'
    elif legend == 'CH':
        return 'CH_Group'
    # Gravel groupings
    elif legend in ['GW', 'GP', 'GM', 'GC']:
        return 'Gravel_Group'
    # Sand groupings
    elif legend in ['SW', 'SP', 'SM', 'SC']:
        return 'Sand_Group'
    # Silt groupings
    elif legend in ['ML', 'MH']:
        return 'Silt_Group'
    else:
        return legend

def assign_geological_units(df):
    """
    Assign geological unit codes to soil layers based on hierarchical criteria

    Args:
        df: DataFrame with geology data

    Returns:
        DataFrame with added 'Unit' column
    """
    df = df.copy()

    # Calculate average depth for sorting
    df['AvgDepth'] = (df['TOP'] + df['BASE']) / 2

    # Create classification group
    df['ClassGroup'] = df['Legend'].apply(classify_soil_group)

    # Group by Origin and Classification
    df['GroupKey'] = df['Origin1'].fillna('Unknown') + '_' + df['ClassGroup']

    # Assign unit codes
    origin_counters = {}
    unit_assignments = {}

    # Sort groups by average depth
    group_depths = df.groupby('GroupKey')['AvgDepth'].mean().sort_values()

    for group_key in group_depths.index:
        origin = group_key.split('_')[0]

        # Get prefix based on origin
        if origin == 'Fill':
            prefix = 'F'
        elif origin == 'Residual':
            prefix = 'R'
        elif origin == 'Alluvium':
            prefix = 'AL'
        elif origin == 'Colluvium':
            prefix = 'CO'
        else:
            prefix = 'U'

        # Increment counter for this origin
        if origin not in origin_counters:
            origin_counters[origin] = 0
        origin_counters[origin] += 1

        # Assign unit code
        unit_code = f"{prefix}{origin_counters[origin]}"
        unit_assignments[group_key] = unit_code

    # Map back to dataframe
    df['Unit'] = df['GroupKey'].map(unit_assignments)

    return df

def generate_unit_description(unit_df):
    """
    Generate professional unit description from grouped layers

    Args:
        unit_df: DataFrame containing all layers for one unit

    Returns:
        str: Formatted unit description
    """
    if unit_df.empty:
        return ""

    # Extract common characteristics
    origin = unit_df['Origin1'].mode()[0] if not unit_df['Origin1'].mode().empty else 'Unknown'

    # Get primary material name
    if 'PrimaryName' in unit_df.columns:
        primary_material = unit_df['PrimaryName'].mode()[0] if not unit_df['PrimaryName'].mode().empty else 'SOIL'
        primary_material = str(primary_material).upper()
    else:
        primary_material = 'SOIL'

    # Get classification range
    classifications = sorted(unit_df['Legend'].dropna().unique())
    if len(classifications) == 1:
        class_str = f"({classifications[0]})"
    elif len(classifications) > 1:
        class_str = f"({' to '.join(classifications)})"
    else:
        class_str = ""

    # Get plasticity descriptor
    plasticity_parts = []
    if 'PlasticityMin' in unit_df.columns:
        plas_vals = unit_df['PlasticityMin'].dropna().unique()
        if len(plas_vals) > 0:
            plasticity_parts.append(str(plas_vals[0]))

    if 'PlasticityJoiner' in unit_df.columns:
        joiners = unit_df['PlasticityJoiner'].dropna().unique()
        if len(joiners) > 0 and str(joiners[0]) == 'to':
            plasticity_parts.append('to')

    if 'PlasticityMax' in unit_df.columns:
        plas_max = unit_df['PlasticityMax'].dropna().unique()
        if len(plas_max) > 0 and 'to' in plasticity_parts:
            plasticity_parts.append(str(plas_max[0]))

    plasticity_str = ' '.join(plasticity_parts) + ' plasticity' if plasticity_parts else ''

    # Get color range
    colors = unit_df['Color'].dropna().unique()
    if len(colors) == 1:
        color_str = str(colors[0])
    elif len(colors) > 1:
        color_str = f"{colors[0]} to {colors[-1]}"
    else:
        color_str = ""

    # Build description
    parts = [f"{origin.upper()} –", primary_material]

    if class_str:
        parts.append(class_str + ":")

    desc_parts = []
    if plasticity_str:
        desc_parts.append(plasticity_str)
    if color_str:
        desc_parts.append(color_str)

    # Add secondary components
    if 'PrimaryNameQualifier' in unit_df.columns:
        qualifiers = unit_df['PrimaryNameQualifier'].dropna().unique()
        if len(qualifiers) > 0:
            desc_parts.append(str(qualifiers[0]).lower())

    if desc_parts:
        parts.append(', '.join(desc_parts))

    # Add special remarks if present
    if 'Remarks' in unit_df.columns:
        remarks = unit_df['Remarks'].dropna().unique()
        if len(remarks) > 0:
            parts.append(str(remarks[0]))

    description = ' '.join(parts).strip()

    # Clean up extra spaces
    description = ' '.join(description.split())

    return description

def generate_extent_statement(unit_df):
    """
    Generate extent of occurrence statement for a geological unit

    Args:
        unit_df: DataFrame with POINT_ID, TOP, BASE for the unit

    Returns:
        str: Extent description
    """
    if unit_df.empty:
        return ""

    # Group by borehole
    bh_summary = []
    for bh in sorted(unit_df['POINT_ID'].unique()):
        bh_data = unit_df[unit_df['POINT_ID'] == bh]
        top = bh_data['TOP'].min()
        base = bh_data['BASE'].max()
        bh_summary.append({'BH': bh, 'TOP': top, 'BASE': base})

    summary_df = pd.DataFrame(bh_summary)

    # Check if occurrence is uniform
    top_var = summary_df['TOP'].max() - summary_df['TOP'].min()
    base_var = summary_df['BASE'].max() - summary_df['BASE'].min()

    bh_list = ', '.join(summary_df['BH'])

    if top_var < 0.2 and base_var < 0.3:
        # Uniform occurrence
        avg_top = summary_df['TOP'].mean()
        avg_base = summary_df['BASE'].mean()

        if avg_top < 0.1:
            extent = f"Encountered from surface to approximately {avg_base:.1f} mbgl in {bh_list}."
        else:
            extent = f"Encountered from approximately {avg_top:.1f} to {avg_base:.1f} mbgl in {bh_list}."
    else:
        # Variable occurrence
        if summary_df['TOP'].min() < 0.1:
            depth_desc = f"from surface to {summary_df['BASE'].min():.1f}-{summary_df['BASE'].max():.1f} mbgl"
        else:
            depth_desc = f"from {summary_df['TOP'].min():.1f} to {summary_df['BASE'].max():.1f} mbgl"

        extent = f"Encountered {depth_desc} in {bh_list}. Depth varies across boreholes."

    return extent

def create_subsurface_summary_table(df):
    """
    Create subsurface conditions summary table

    Args:
        df: DataFrame with geology data

    Returns:
        DataFrame with columns: Unit, Description, Extent of Occurrence
    """
    # Assign units
    df_with_units = assign_geological_units(df)

    # Generate summary for each unit
    summary_rows = []

    for unit_code in sorted(df_with_units['Unit'].unique(),
                           key=lambda x: df_with_units[df_with_units['Unit']==x]['AvgDepth'].min()):
        unit_data = df_with_units[df_with_units['Unit'] == unit_code]

        description = generate_unit_description(unit_data)
        extent = generate_extent_statement(unit_data)

        summary_rows.append({
            'Unit': unit_code,
            'Description, material, relative consistency, Extent of occurrence': f"{description}\n\n{extent}"
        })

    summary_table = pd.DataFrame(summary_rows)

    return summary_table

# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    st.set_page_config(
        page_title="Borehole Analyzer",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 Borehole Analyzer MVP")
    st.markdown("Upload your geology CSV file to visualize borehole subsurface profiles")

    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("Upload Data")
        uploaded_file = st.file_uploader(
            "Choose GEOLOGY.csv file",
            type=['csv'],
            help="Upload a CSV file containing borehole geology data"
        )

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This tool visualizes borehole geology data from CSV files.

        **Features:**
        - Side-by-side borehole logs
        - Color-coded soil classifications
        - Interactive hover information
        - Borehole selection filters
        - **NEW:** Subsurface conditions summary table
        - Professional geological unit grouping
        - Export capabilities
        """)

    # Main content
    if uploaded_file is not None:
        # Load data
        with st.spinner("Loading data..."):
            df = load_borehole_data(uploaded_file)

        if df is not None and not df.empty:
            st.success(f"✅ Loaded {len(df)} soil layers from {df['POINT_ID'].nunique()} boreholes")

            # Show basic statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Project ID", df['PROJ_ID'].iloc[0])
            with col2:
                st.metric("Boreholes", df['POINT_ID'].nunique())
            with col3:
                st.metric("Soil Layers", len(df))
            with col4:
                max_depth = df['BASE'].max()
                st.metric("Max Depth", f"{max_depth:.1f} m")

            st.markdown("---")

            # Borehole selection
            st.subheader("Select Boreholes to Display")
            all_boreholes = sorted(df['POINT_ID'].unique())

            col1, col2 = st.columns([3, 1])
            with col1:
                selected_boreholes = st.multiselect(
                    "Choose boreholes:",
                    options=all_boreholes,
                    default=all_boreholes[:5] if len(all_boreholes) > 5 else all_boreholes,
                    help="Select up to 10 boreholes for best visualization"
                )
            with col2:
                show_descriptions = st.checkbox("Show descriptions", value=True)

            if selected_boreholes:
                # Create and display plot
                with st.spinner("Generating visualization..."):
                    fig = create_borehole_logs(df, selected_boreholes, show_descriptions)

                if fig:
                    st.plotly_chart(fig, use_container_width=True)

                    # Show legend
                    with st.expander("📊 Soil Classification Legend", expanded=False):
                        create_soil_legend()

                    # Show subsurface conditions summary table
                    with st.expander("📄 Subsurface Conditions Summary Table", expanded=True):
                        st.markdown("### Table 3-1: Geological Units")
                        st.markdown("*Professional summary of geotechnical units encountered*")

                        with st.spinner("Generating subsurface summary..."):
                            summary_table = create_subsurface_summary_table(df)

                        if not summary_table.empty:
                            # Display table with custom styling
                            st.dataframe(
                                summary_table,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Unit": st.column_config.TextColumn(
                                        "Unit",
                                        width="small",
                                        help="Geological unit code (F=Fill, R=Residual, AL=Alluvium)"
                                    ),
                                    "Description, material, relative consistency, Extent of occurrence": st.column_config.TextColumn(
                                        "Description, material, relative consistency, Extent of occurrence",
                                        width="large",
                                        help="Professional geological description and spatial extent"
                                    )
                                }
                            )

                            # Download button for summary table
                            csv_summary = summary_table.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Summary Table (CSV)",
                                data=csv_summary,
                                file_name="subsurface_conditions_summary.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("Unable to generate summary table. Please check data format.")

                    # Show raw data table
                    with st.expander("📋 View Raw Data", expanded=False):
                        filtered_df = df[df['POINT_ID'].isin(selected_boreholes)]
                        st.dataframe(
                            filtered_df,
                            use_container_width=True,
                            height=400
                        )

                        # Download button
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Filtered Data (CSV)",
                            data=csv,
                            file_name="filtered_borehole_data.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("⚠️ Please select at least one borehole to display")

        else:
            st.error("❌ Failed to load data. Please check your CSV file format.")

    else:
        # Show instructions when no file is uploaded
        st.info("👆 Upload a GEOLOGY.csv file using the sidebar to get started")

        st.markdown("### Expected CSV Format")
        st.markdown("""
        The CSV file should contain the following columns:
        - `PROJ_ID`: Project identifier
        - `POINT_ID`: Borehole ID (e.g., BH01, BH02)
        - `TOP`: Top depth of soil layer (m)
        - `BASE`: Bottom depth of soil layer (m)
        - `Legend`: Soil classification code (e.g., CH, CI, GW)
        - `Description`: Full description of soil layer
        - `Classification`: Soil classification
        - `Origin1`: Soil origin (e.g., Fill, Residual)
        - `Color`: Soil color description
        """)

if __name__ == "__main__":
    main()
