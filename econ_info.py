import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.request
import json
from fredapi import Fred
import numpy as np

# Set page config and style
st.set_page_config(page_title="Economic Data Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    .stTabs [data-baseweb="tab-list"] {gap: 8px;}
    .stTabs [data-baseweb="tab"] {height: 50px; padding-left: 20px; padding-right: 20px;}
    .stDataFrame {font-size: 16px;}
    
    .data-status-good {
        background-color: rgba(144, 238, 144, 0.3) !important;
        border-radius: 4px !important;
    }
    
    .data-status-partial {
        background-color: rgba(255, 215, 0, 0.3) !important;
        border-radius: 4px !important;
    }
    
    .data-status-bad {
        background-color: rgba(255, 182, 193, 0.3) !important;
        border-radius: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hard-coded FRED API key
FRED_API_KEY = "292a22259a26aa4f7e00d9ba22db9c56"
fred = Fred(api_key=FRED_API_KEY)

# First, let's update the inflation series IDs to consistently use FPCPITOTLZG format
BASE_COUNTRIES = {
    '🇦🇷 Argentina': {
        'gdp': 'ARGRGDPEXP',
        'unemployment': 'LRHUTTTTARM156S',
        'inflation': 'FPCPITOTLZGAFA'  # Already correct
    },
    '🇦🇺 Australia': {
        'gdp': 'AUSGDPRQDSMEI',
        'unemployment': 'LRHUTTTTAUM156S',
        'inflation': 'FPCPITOTLZGAUS'  # Changed from CPALTT format
    },
    '🇦🇹 Austria': {
        'gdp': 'AUTRGDPEXP',
        'unemployment': 'LRHUTTTTAUM156S',
        'inflation': 'FPCPITOTLZGAUT'  # Changed from CPALTT format
    },
    '🇧🇪 Belgium': {
        'gdp': 'BENGDPRQDSMEI',
        'unemployment': 'LRHUTTTTBEM156S',
        'inflation': 'FPCPITOTLZGBEL'  # Changed from CPALTT format
    },
    '🇧🇷 Brazil': {
        'gdp': 'BRARGDPEXP',
        'unemployment': 'LRHUTTTTBRM156S',
        'inflation': 'FPCPITOTLZGBRA'  # Already correct
    },
    '🇨🇦 Canada': {
        'gdp': 'NGDPRSAXDCCAQ',
        'unemployment': 'LRHUTTTTCAM156S',
        'inflation': 'FPCPITOTLZGCAN'  # Changed from CPALTT format
    },
    '🇨🇱 Chile': {
        'gdp': 'CHLRGDPEXP',
        'unemployment': 'LRHUTTTTCLM156S',
        'inflation': 'FPCPITOTLZGCHL'  # Already correct
    },
    '🇨🇳 China': {
        'gdp': 'CHNRGDPEXP',
        'unemployment': 'LRHUTTTTCNM156S',
        'inflation': 'FPCPITOTLZGCHN'  # Already correct
    },
    '🇨🇴 Colombia': {
        'gdp': 'COLRGDPEXP',
        'unemployment': 'LRHUTTTTCLM156S',
        'inflation': 'FPCPITOTLZGCOL'  # Already correct
    },
    '🇨🇿 Czech Republic': {
        'gdp': 'CZEARGDPEXP',
        'unemployment': 'LRHUTTTTCZM156S',
        'inflation': 'FPCPITOTLZGCZE'  # Changed from CPALTT format
    },
    '🇩🇰 Denmark': {
        'gdp': 'DNKRGDPEXP',
        'unemployment': 'LRHUTTTTDEM156S',
        'inflation': 'FPCPITOTLZGDNK'  # Changed from CPALTT format
    },
    '🇫🇮 Finland': {
        'gdp': 'FINRGDPEXP',
        'unemployment': 'LRHUTTTTFIM156S',
        'inflation': 'FPCPITOTLZGFIN'  # Changed from CPALTT format
    },
    '🇫🇷 France': {
        'gdp': 'CLVMNACSCAB1GQFR',
        'unemployment': 'LRHUTTTTFRM156S',
        'inflation': 'FPCPITOTLZGFRA'  # Changed from CPALTT format
    },
    '🇩🇪 Germany': {
        'gdp': 'CLVMNACSCAB1GQDE',
        'unemployment': 'LRHUTTTTDEM156S',
        'inflation': 'FPCPITOTLZGDEU'  # Changed from CPALTT format
    },
    '🇬🇷 Greece': {
        'gdp': 'GRCARGDPEXP',
        'unemployment': 'LRHUTTTTGRM156S',
        'inflation': 'FPCPITOTLZGGRC'  # Changed from CPALTT format
    },
    '🇭🇰 Hong Kong': {
        'gdp': 'HKGRGDPEXP',
        'unemployment': 'LRHUTTTTHKM156S',
        'inflation': 'FPCPITOTLZGHKG'  # Already correct
    },
    '🇮🇳 India': {
        'gdp': 'INDRGDPEXP',
        'unemployment': 'LRHUTTTTINM156S',
        'inflation': 'FPCPITOTLZGIN'  # Already correct
    },
    '🇮🇩 Indonesia': {
        'gdp': 'IDNRGDPEXP',
        'unemployment': 'LRHUTTTTIDM156S',
        'inflation': 'FPCPITOTLZGIDN'  # Already correct
    },
    '🇮🇪 Ireland': {
        'gdp': 'IRLRGDPEXP',
        'unemployment': 'LRHUTTTTIRM156S',
        'inflation': 'FPCPITOTLZGIRL'  # Changed from CPALTT format
    },
    '🇮🇱 Israel': {
        'gdp': 'ISRRGDPEXP',
        'unemployment': 'LRHUTTTTILM156S',
        'inflation': 'FPCPITOTLZGISR'  # Already correct
    },
    '🇮🇹 Italy': {
        'gdp': 'ITARGDPEXP',
        'unemployment': 'LRHUTTTTITM156S',
        'inflation': 'FPCPITOTLZGITA'  # Changed from CPALTT format
    },
    '🇯🇵 Japan': {
        'gdp': 'JPNRGDPEXP',
        'unemployment': 'LRHUTTTTJPM156S',
        'inflation': 'FPCPITOTLZGJPN'  # Changed from CPALTT format
    },
    '🇰🇷 South Korea': {
        'gdp': 'KORRGDPEXP',
        'unemployment': 'LRHUTTTTKRM156S',
        'inflation': 'FPCPITOTLZGKOR'  # Changed from CPALTT format
    },
    '🇲🇽 Mexico': {
        'gdp': 'MEXRGDPEXP',
        'unemployment': 'LRHUTTTTMXM156S',
        'inflation': 'FPCPITOTLZGMEX'  # Already correct
    },
    '🇳🇱 Netherlands': {
        'gdp': 'NLDRGDPEXP',
        'unemployment': 'LRHUTTTTNLM156S',
        'inflation': 'FPCPITOTLZGNLD'  # Changed from CPALTT format
    },
    '🇳🇿 New Zealand': {
        'gdp': 'NZLRGDPEXP',
        'unemployment': 'LRHUTTTTNZM156S',
        'inflation': 'FPCPITOTLZGNZL'  # Changed from CPALTT format
    },
    '🇳🇴 Norway': {
        'gdp': 'NORRGDPEXP',
        'unemployment': 'LRHUTTTTNOM156S',
        'inflation': 'FPCPITOTLZGNOR'  # Changed from CPALTT format
    },
    '🇵🇱 Poland': {
        'gdp': 'POLRGDPEXP',
        'unemployment': 'LRHUTTTTPLM156S',
        'inflation': 'FPCPITOTLZGPOL'  # Changed from CPALTT format
    },
    '🇵🇹 Portugal': {
        'gdp': 'PORRGDPEXP',
        'unemployment': 'LRHUTTTTPRM156S',
        'inflation': 'FPCPITOTLZGPRT'  # Changed from CPALTT format
    },
    '🇷🇺 Russia': {
        'gdp': 'RUSRRGDPEXP',
        'unemployment': 'LRHUTTTTRUM156S',
        'inflation': 'FPCPITOTLZGRUS'  # Already correct
    },
    '🇿🇦 South Africa': {
        'gdp': 'ZAFRGDPEXP',
        'unemployment': 'LRHUTTTTZAM156S',
        'inflation': 'FPCPITOTLZGZAF'  # Already correct
    },
    '🇪🇸 Spain': {
        'gdp': 'ESPGDPRQDSMEI',
        'unemployment': 'LRHUTTTTESM156S',
        'inflation': 'FPCPITOTLZGESP'  # Changed from CPALTT format
    },
    '🇸🇪 Sweden': {
        'gdp': 'SWEGDPRQDSMEI',
        'unemployment': 'LRHUTTTTSEM156S',
        'inflation': 'FPCPITOTLZGSWE'  # Changed from CPALTT format
    },
    '🇨🇭 Switzerland': {
        'gdp': 'CHEGDPRQDSMEI',
        'unemployment': 'LRHUTTTTCHM156S',
        'inflation': 'FPCPITOTLZGCHE'  # Changed from CPALTT format
    },
    '🇹🇷 Turkey': {
        'gdp': 'TURRGDPEXP',
        'unemployment': 'LRHUTTTTTRM156S',
        'inflation': 'FPCPITOTLZGTUR'  # Already correct
    },
    '🇬🇧 United Kingdom': {
        'gdp': 'UKNGDP',
        'unemployment': 'LRHUTTTTGBM156S',
        'inflation': 'FPCPITOTLZGGBR'  # Changed from CPALTT format
    },
    '🇺🇸 United States': {
        'gdp': 'GDPC1',
        'unemployment': 'UNRATE',
        'inflation': 'FPCPITOTLZGUSA'  # Changed from CPIAUCSL
    }
}

def check_data_availability(data, frequency):
    """
    Check data availability and return status
    Returns: 'good' (>75% data), 'partial' (25-75% data), or 'bad' (<25% data)
    """
    if data is None or data.empty:
        return 'bad'
    
    # For DataFrame, calculate availability across all columns
    if isinstance(data, pd.DataFrame):
        # Count non-null values across all columns
        non_null_count = data.count().mean()  # Average of non-null counts across columns
        total_points = len(data)
    else:  # For Series
        non_null_count = data.count()
        total_points = len(data)
    
    if total_points > 0:
        availability_pct = float((non_null_count / total_points) * 100)
        if availability_pct >= 75:
            return 'good'
        elif availability_pct >= 25:
            return 'partial'
    
    return 'bad'

def fetch_fred_data(selected_countries, country_data, indicator_type='gdp', start_date=None, end_date=None):
    """Fetch data from FRED with proper transformations and error handling"""
    try:
        all_data = {}
        for country_name in selected_countries:
            if country_name in country_data:
                series_id = country_data[country_name][indicator_type]
                try:
                    # Fetch data with retry
                    attempts = 3
                    for attempt in range(attempts):
                        try:
                            data = fred.get_series(
                                series_id, 
                                observation_start=start_date,
                                observation_end=end_date
                            )
                            if not data.empty:
                                break
                        except Exception as e:
                            if attempt == attempts - 1:
                                raise e
                            continue
                    
                    if not data.empty:
                        # Handle different transformations based on indicator type
                        if indicator_type == 'gdp':
                            # GDP always needs quarter-over-quarter transformation
                            transformed_data = data.pct_change() * 100
                        
                        elif indicator_type == 'unemployment':
                            # Unemployment is already in percentage form
                            transformed_data = data
                        
                        elif indicator_type == 'inflation':
                            # FPCPITOTLZG series are already in correct percentage form
                            # No transformation needed, just use raw data
                            transformed_data = data.copy()
                        
                        # Handle resampling to quarterly if needed
                        if hasattr(transformed_data.index, 'freq') and transformed_data.index.freq != 'Q':
                            transformed_data = transformed_data.resample('Q').last()
                        
                        # Remove any infinite values
                        transformed_data = transformed_data.replace([np.inf, -np.inf], np.nan)
                        
                        all_data[country_name] = transformed_data
                    else:
                        all_data[country_name] = pd.Series(index=pd.date_range(start=start_date, 
                                                                             end=end_date, 
                                                                             freq='Q'))
                except Exception as e:
                    print(f"Error processing {country_name} {indicator_type}: {str(e)}")
                    print(f"Series ID: {series_id}")
                    all_data[country_name] = pd.Series(index=pd.date_range(start=start_date, 
                                                                         end=end_date, 
                                                                         freq='Q'))
        
        if all_data:
            # Create DataFrame with no additional calculations
            df = pd.DataFrame(all_data, copy=True)
            return df.sort_index(ascending=False)
        return None

    except Exception as e:
        print(f"Error in fetch_fred_data: {str(e)}")
        return None
    
def create_enhanced_plot(data, title, y_label):
    """Create an enhanced plot using plotly"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    for column in data.columns:
        # Only include non-null values in the plot
        valid_data = data[column].dropna()
        if not valid_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    name=column,
                    line=dict(width=3),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate="%{y:.2f}%<br>%{x}<extra></extra>"
                )
            )
    
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center', font=dict(size=24)),
        yaxis_title=dict(text=y_label, font=dict(size=14)),
        xaxis_title=dict(text="Quarter", font=dict(size=14)),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        template='plotly_white',
        margin=dict(t=100),
        showlegend=True
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def create_combined_metrics_plot(gdp_data, unemp_data, infl_data, country):
    """Create a plot showing all three metrics for a single country"""
    if all(data is None or data.empty for data in [gdp_data, unemp_data, infl_data]):
        return None
    
    fig = go.Figure()
    
    # Add GDP data
    if gdp_data is not None and not gdp_data.empty and country in gdp_data.columns:
        valid_data = gdp_data[country].dropna()
        if not valid_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    name="GDP Growth",
                    line=dict(width=3, color='rgb(99, 110, 250)'),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate="GDP: %{y:.2f}%<br>%{x}<extra></extra>"
                )
            )
def create_combined_metrics_plot(gdp_data, unemp_data, infl_data, country):
    """Create a plot showing all three metrics for a single country"""
    if all(data is None or data.empty for data in [gdp_data, unemp_data, infl_data]):
        return None
    
    fig = go.Figure()
    
    # Add GDP data
    if gdp_data is not None and not gdp_data.empty and country in gdp_data.columns:
        valid_data = gdp_data[country].dropna()
        if not valid_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    name="GDP Growth",
                    line=dict(width=3, color='rgb(99, 110, 250)'),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate="GDP: %{y:.2f}%<br>%{x}<extra></extra>"
                )
            )
    
    # Add Unemployment data
    if unemp_data is not None and not unemp_data.empty and country in unemp_data.columns:
        valid_data = unemp_data[country].dropna()
        if not valid_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    name="Unemployment",
                    line=dict(width=3, color='rgb(239, 85, 59)'),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate="Unemployment: %{y:.2f}%<br>%{x}<extra></extra>"
                )
            )
    
    # Add Inflation data
    if infl_data is not None and not infl_data.empty and country in infl_data.columns:
        valid_data = infl_data[country].dropna()
        if not valid_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    name="Inflation",
                    line=dict(width=3, color='rgb(0, 204, 150)'),
                    mode='lines+markers',
                    marker=dict(size=8),
                    hovertemplate="Inflation: %{y:.2f}%<br>%{x}<extra></extra>"
                )
            )
    
    fig.update_layout(
        title=dict(text=f"Combined Economic Metrics - {country}", x=0.5, xanchor='center', font=dict(size=24)),
        yaxis_title=dict(text="Rate (%)", font=dict(size=14)),
        xaxis_title=dict(text="Quarter", font=dict(size=14)),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        template='plotly_white',
        margin=dict(t=100),
        showlegend=True
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    
    return fig

def style_dataframe(df, frequency):
    """Style the dataframe with appropriate formatting"""
    if df is None or df.empty:
        return None
        
    # Create a copy to avoid modifying the original
    styled_df = df.copy()
    
    # Keep only last 12 quarters/months
    if frequency == 'quarterly':
        styled_df = styled_df.head(12)
    elif frequency == 'monthly':
        styled_df = styled_df.head(36)
    
    # Format the index to show only quarter end dates nicely
    styled_df.index = styled_df.index.strftime('%Y Q%q')
    
    # Format values with proper handling of missing data
    def format_value(x):
        if pd.isna(x):
            return "Not Available"
        if frequency == 'quarterly':
            return f"{x:.2f}%"
        elif frequency == 'monthly':
            return f"{x:.2f}%"
        else:
            return str(x)
    
    # Apply formatting to each column
    for col in styled_df.columns:
        styled_df[col] = styled_df[col].apply(format_value)
    
    return styled_df

# Initialize country data
st.session_state.all_countries = BASE_COUNTRIES

# Main app layout
st.title("🌍 Global Economic Data Dashboard")
st.markdown("---")

# Date range selection
col1, col2 = st.columns(2)
with col1:
    current_year = datetime.now().year
    years = list(range(2000, current_year + 1))
    start_year = st.selectbox(
        "Select Start Year:",
        options=years,
        index=years.index(2015)
    )
with col2:
    end_years = list(range(start_year, current_year + 1))
    end_year = st.selectbox(
        "Select End Year:",
        options=end_years,
        index=len(end_years)-1
    )

# Convert years to dates
start_date = f"{start_year}-01-01"
end_date = f"{end_year}-12-31"

# Country selection
selected_countries = st.multiselect(
    "Select countries to compare (max 5):",
    options=list(st.session_state.all_countries.keys()),
    default=["🇺🇸 United States"],
    max_selections=5
)

if selected_countries:
    # Pre-fetch data to determine status
    gdp_data = fetch_fred_data(selected_countries, st.session_state.all_countries, 
                              'gdp', start_date, end_date)
    unemp_data = fetch_fred_data(selected_countries, st.session_state.all_countries, 
                                'unemployment', start_date, end_date)
    infl_data = fetch_fred_data(selected_countries, st.session_state.all_countries, 
                               'inflation', start_date, end_date)
    
    def get_status_emoji(data, frequency):
        """Convert availability check to appropriate emoji"""
        if data is None or data.empty:
            return "🔴"  # red circle for bad
        
        status = check_data_availability(data, frequency)
        if status == 'good':
            return "🟢"  # green circle for good
        elif status == 'partial':
            return "🟡"  # yellow circle for partial
        else:
            return "🔴"  # red circle for bad
        
    def create_combined_metrics_plot_comparison(gdp_data, unemp_data, infl_data, country1, country2):
        """Create a plot showing all three metrics for two countries"""
        if all(data is None or data.empty for data in [gdp_data, unemp_data, infl_data]):
            return None
        
        fig = go.Figure()
        
        # Distinct colors for each metric and country
        colors = {
            'gdp': {'country1': 'rgb(99, 110, 250)', 'country2': 'rgb(132, 140, 255)'},
            'unemp': {'country1': 'rgb(239, 85, 59)', 'country2': 'rgb(255, 127, 102)'},
            'infl': {'country1': 'rgb(0, 204, 150)', 'country2': 'rgb(72, 240, 186)'}
        }
        
        # Helper function to add traces for a country
        def add_country_traces(country, country_type='country1'):
            # Add GDP data
            if gdp_data is not None and not gdp_data.empty and country in gdp_data.columns:
                valid_data = gdp_data[country].dropna()
                if not valid_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=valid_data.index,
                            y=valid_data,
                            name=f"GDP Growth ({country})",
                            line=dict(width=3, color=colors['gdp'][country_type]),
                            mode='lines+markers',
                            marker=dict(size=8),
                            hovertemplate=f"{country} GDP: %{{y:.2f}}%<br>%{{x}}<extra></extra>"
                        )
                    )
            
            # Add Unemployment data
            if unemp_data is not None and not unemp_data.empty and country in unemp_data.columns:
                valid_data = unemp_data[country].dropna()
                if not valid_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=valid_data.index,
                            y=valid_data,
                            name=f"Unemployment ({country})",
                            line=dict(width=3, color=colors['unemp'][country_type]),
                            mode='lines+markers',
                            marker=dict(size=8),
                            hovertemplate=f"{country} Unemployment: %{{y:.2f}}%<br>%{{x}}<extra></extra>"
                        )
                    )
            
            # Add Inflation data
            if infl_data is not None and not infl_data.empty and country in infl_data.columns:
                valid_data = infl_data[country].dropna()
                if not valid_data.empty:
                    fig.add_trace(
                        go.Scatter(
                            x=valid_data.index,
                            y=valid_data,
                            name=f"Inflation ({country})",
                            line=dict(width=3, color=colors['infl'][country_type]),
                            mode='lines+markers',
                            marker=dict(size=8),
                            hovertemplate=f"{country} Inflation: %{{y:.2f}}%<br>%{{x}}<extra></extra>"
                        )
                    )
        
        # Add traces for both countries
        add_country_traces(country1, 'country1')
        add_country_traces(country2, 'country2')
        
        fig.update_layout(
            title=dict(text=f"Combined Economic Metrics - {country1} vs {country2}", x=0.5, xanchor='center', font=dict(size=24)),
            yaxis_title=dict(text="Rate (%)", font=dict(size=14)),
            xaxis_title=dict(text="Quarter", font=dict(size=14)),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10)
            ),
            height=500,
            template='plotly_white',
            margin=dict(t=100),
            showlegend=True
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        
        return fig

    def style_comparison_dataframe(df1, df2, country1, country2, frequency='quarterly'):
        """Style the comparison dataframe with colors and formatting"""
        if df1 is None or df2 is None or df1.empty or df2.empty:
            return None
            
        # Create a copy and keep only last 12 quarters
        df1 = df1.head(12)
        df2 = df2.head(12)
        
        # Calculate differences and create combined DataFrame
        combined_df = pd.DataFrame(index=df1.index)
        
        # Helper function to calculate and format differences
        def calc_difference(val1, val2):
            if pd.isna(val1) or pd.isna(val2):
                return None
            return val2 - val1
        
        # Add columns for both countries and differences
        for col in df1.columns:
            if col in df2.columns:
                combined_df[f"{col} ({country1})"] = df1[col]
                combined_df[f"{col} ({country2})"] = df2[col]
                combined_df[f"{col} Diff"] = df1[col].combine(df2[col], calc_difference)
        
        # Format index to show quarters
        combined_df.index = combined_df.index.strftime('%Y Q%q')
        
        # Format values and add colors
        def style_value(val, is_diff=False):
            if pd.isna(val):
                return "Not Available"
            
            if is_diff:
                color = "red" if val < 0 else "green" if val > 0 else "black"
                return f'<span style="color: {color}">{val:+.2f}%</span>'
            return f"{val:.2f}%"
        
        # Apply formatting to each column
        styled_df = pd.DataFrame(index=combined_df.index)
        for col in combined_df.columns:
            is_diff = col.endswith('Diff')
            styled_df[col] = combined_df[col].apply(lambda x: style_value(x, is_diff))
        
        return styled_df

    # Create tabs with status emojis and data availability text
    tab1, tab2, tab3, tab4 = st.tabs([
        f"📈 GDP Growth (Data Availability: {get_status_emoji(gdp_data, 'quarterly')})",
        f"👥 Unemployment (Data Availability: {get_status_emoji(unemp_data, 'quarterly')})",
        f"💰 Inflation (Data Availability: {get_status_emoji(infl_data, 'quarterly')})",
        "📊 Combined View"
    ])

    with tab1:
        st.subheader("Quarterly GDP Growth Rate")
        if gdp_data is not None:
            fig = create_enhanced_plot(gdp_data, 
                                    "GDP Growth Rate (Quarter over Quarter)", 
                                    "Growth Rate (%)")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("GDP Growth - Last 12 Quarters")
                styled_gdp = style_dataframe(gdp_data, 'quarterly')
                if styled_gdp is not None:
                    st.dataframe(styled_gdp, use_container_width=True)
    
    with tab2:
        st.subheader("Unemployment Rate")
        if unemp_data is not None:
            fig = create_enhanced_plot(unemp_data,
                                    "Unemployment Rate Trends",
                                    "Unemployment Rate (%)")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Unemployment - Last 12 Quarters")
                styled_unemp = style_dataframe(unemp_data, 'quarterly')
                if styled_unemp is not None:
                    st.dataframe(styled_unemp, use_container_width=True)
    
    with tab3:
        st.subheader("Inflation Rate")
        if infl_data is not None:
            fig = create_enhanced_plot(infl_data,
                                    "Inflation Rate Trends",
                                    "Inflation Rate (%)")
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Inflation - Last 12 Quarters")
                styled_infl = style_dataframe(infl_data, 'quarterly')
                if styled_infl is not None:
                    st.dataframe(styled_infl, use_container_width=True)
    
    with tab4:
        st.subheader("Combined Economic Metrics - Country Comparison")
        if len(selected_countries) > 1:  # Check if we have at least 2 countries selected
            # Add country selectors for comparison
            col1, col2 = st.columns(2)
            with col1:
                country1 = st.selectbox(
                    "Select first country:",
                    options=selected_countries,
                    index=0,
                    key='country1'
                )
            with col2:
                remaining_countries = [c for c in selected_countries if c != country1]
                country2 = st.selectbox(
                    "Select second country:",
                    options=remaining_countries,
                    index=0,
                    key='country2'
                )
            
            if country1 and country2:  # Check if both countries are selected
                fig = create_combined_metrics_plot_comparison(gdp_data, unemp_data, infl_data, country1, country2)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Create comparison DataFrames
                    df1 = pd.DataFrame()
                    df2 = pd.DataFrame()
                    
                    # Add data for first country
                    if gdp_data is not None and country1 in gdp_data.columns:
                        df1['GDP Growth'] = gdp_data[country1]
                    if unemp_data is not None and country1 in unemp_data.columns:
                        df1['Unemployment'] = unemp_data[country1]
                    if infl_data is not None and country1 in infl_data.columns:
                        df1['Inflation'] = infl_data[country1]
                    
                    # Add data for second country
                    if gdp_data is not None and country2 in gdp_data.columns:
                        df2['GDP Growth'] = gdp_data[country2]
                    if unemp_data is not None and country2 in unemp_data.columns:
                        df2['Unemployment'] = unemp_data[country2]
                    if infl_data is not None and country2 in infl_data.columns:
                        df2['Inflation'] = infl_data[country2]
                    
                    # Style and display the comparison table
                    st.subheader(f"Metrics Comparison - Last 12 Quarters")
                    styled_comparison = style_comparison_dataframe(df1, df2, country1, country2, 'quarterly')
                    if styled_comparison is not None and not styled_comparison.empty:
                        st.write(styled_comparison.to_html(escape=False), unsafe_allow_html=True)
                    else:
                        st.warning("No comparison data available for the selected time period.")
                else:
                    st.warning("No data available for the selected countries and time period.")
        else:
            st.warning("Please select at least two countries from the main selection above to enable comparison.")
            
    # Download section
    if all(v is not None for v in [gdp_data, unemp_data, infl_data]):
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### Download Data")
            st.markdown("Get the complete dataset in CSV format for further analysis.")
        with col2:
            combined_data = pd.concat(
                [gdp_data.add_suffix('_GDP'), 
                 unemp_data.add_suffix('_Unemployment'), 
                 infl_data.add_suffix('_Inflation')], 
                axis=1
            )
            st.download_button(
                label="📥 Download All Data",
                data=combined_data.to_csv().encode('utf-8'),
                file_name='economic_data.csv',
                mime='text/csv',
            )

else:
    st.info("👆 Please select countries to compare from the dropdown above")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p style='color: #666; font-size: 14px;'>
            Data source: Federal Reserve Economic Data (FRED)<br>
            Last updated: {}
        </p>
    </div>
    """.format(datetime.now().strftime("%B %Y")), 
    unsafe_allow_html=True)
