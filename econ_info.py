import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import urllib.request
import json
from fredapi import Fred

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

# Base set of known working countries
BASE_COUNTRIES = {
    '🇦🇷 Argentina': {
        'gdp': 'ARGRGDPEXP',
        'unemployment': 'LRHUTTTTARM156S',
        'inflation': 'FPCPITOTLZGAFA'
    },
    '🇦🇺 Australia': {
        'gdp': 'AUSGDPRQDSMEI',
        'unemployment': 'LRHUTTTTAUM156S',
        'inflation': 'CPALTT01AUM659N'
    },
    '🇦🇹 Austria': {
        'gdp': 'AUTRGDPEXP',
        'unemployment': 'LRHUTTTTAUM156S',
        'inflation': 'CPALTT01ATM659N'
    },
    '🇧🇪 Belgium': {
        'gdp': 'BENGDPRQDSMEI',
        'unemployment': 'LRHUTTTTBEM156S',
        'inflation': 'CPALTT01BEM659N'
    },
    '🇧🇷 Brazil': {
        'gdp': 'BRARGDPEXP',
        'unemployment': 'LRHUTTTTBRM156S',
        'inflation': 'FPCPITOTLZGBRA'
    },
    '🇨🇦 Canada': {
        'gdp': 'NGDPRSAXDCCAQ',
        'unemployment': 'LRHUTTTTCAM156S',
        'inflation': 'CPALTT01CAM659N'
    },
    '🇨🇱 Chile': {
        'gdp': 'CHLRGDPEXP',
        'unemployment': 'LRHUTTTTCLM156S',
        'inflation': 'FPCPITOTLZGCHL'
    },
    '🇨🇳 China': {
        'gdp': 'CHNRGDPEXP',
        'unemployment': 'LRHUTTTTCNM156S',
        'inflation': 'FPCPITOTLZGCHN'
    },
    '🇨🇴 Colombia': {
        'gdp': 'COLRGDPEXP',
        'unemployment': 'LRHUTTTTCLM156S',
        'inflation': 'FPCPITOTLZGCOL'
    },
    '🇨🇷 Costa Rica': {
        'gdp': 'CRIRGDPEXP',
        'unemployment': 'LRHUTTTTCRM156S',
        'inflation': 'FPCPITOTLZGCRI'
    },
    '🇨🇿 Czech Republic': {
        'gdp': 'CZEARGDPEXP',
        'unemployment': 'LRHUTTTTCZM156S',
        'inflation': 'CPALTT01CZM659N'
    },
    '🇩🇰 Denmark': {
        'gdp': 'DNKRGDPEXP',
        'unemployment': 'LRHUTTTTDEM156S',
        'inflation': 'CPALTT01DKM659N'
    },
    '🇪🇨 Ecuador': {
        'gdp': 'ECURGDPEXP',
        'unemployment': 'LRHUTTTTECM156S',
        'inflation': 'FPCPITOTLZGECU'
    },
    '🇪🇪 Estonia': {
        'gdp': 'ESTRGDPEXP',
        'unemployment': 'LRHUTTTTEST156S',
        'inflation': 'CPALTT01EEM659N'
    },
    '🇫🇮 Finland': {
        'gdp': 'FINRGDPEXP',
        'unemployment': 'LRHUTTTTFIM156S',
        'inflation': 'CPALTT01FIM659N'
    },
    '🇫🇷 France': {
        'gdp': 'CLVMNACSCAB1GQFR',
        'unemployment': 'LRHUTTTTFRM156S',
        'inflation': 'CPALTT01FRM659N'
    },
    '🇩🇪 Germany': {
        'gdp': 'CLVMNACSCAB1GQDE',
        'unemployment': 'LRHUTTTTDEM156S',
        'inflation': 'CPALTT01DEM659N'
    },
    '🇬🇷 Greece': {
        'gdp': 'GRCARGDPEXP',
        'unemployment': 'LRHUTTTTGRM156S',
        'inflation': 'CPALTT01GRM659N'
    },
    '🇭🇰 Hong Kong': {
        'gdp': 'HKGARGDPEXP',
        'unemployment': 'LRHUTTTTHKM156S',
        'inflation': 'FPCPITOTLZGHKG'
    },
    '🇭🇺 Hungary': {
        'gdp': 'HUNRGDPEXP',
        'unemployment': 'LRHUTTTTHUM156S',
        'inflation': 'CPALTT01HUM659N'
    },
    '🇮🇸 Iceland': {
        'gdp': 'ISLRGDPEXP',
        'unemployment': 'LRHUTTTTISM156S',
        'inflation': 'CPALTT01ISM659N'
    },
    '🇮🇳 India': {
        'gdp': 'INDRGDPEXP',
        'unemployment': 'LRHUTTTTINM156S',
        'inflation': 'FPCPITOTLZGIN'
    },
    '🇮🇩 Indonesia': {
        'gdp': 'IDNRGDPEXP',
        'unemployment': 'LRHUTTTTIDM156S',
        'inflation': 'FPCPITOTLZGIDN'
    },
    '🇮🇪 Ireland': {
        'gdp': 'IRLRGDPEXP',
        'unemployment': 'LRHUTTTTIRM156S',
        'inflation': 'CPALTT01IRM659N'
    },
    '🇮🇱 Israel': {
        'gdp': 'ISRRGDPEXP',
        'unemployment': 'LRHUTTTTILM156S',
        'inflation': 'FPCPITOTLZGISR'
    },
    '🇮🇹 Italy': {
        'gdp': 'ITARGDPEXP',
        'unemployment': 'LRHUTTTTITM156S',
        'inflation': 'CPALTT01ITM659N'
    },
     '🇯🇵 Japan': {
        'gdp': 'JPNRGDPEXP',
        'unemployment': 'LRHUTTTTJPM156S',
        'inflation': 'CPALTT01JPM659N'
    },
    '🇰🇪 Kenya': {
        'gdp': 'KENRGDPEXP',
        'unemployment': 'LRHUTTTTKEM156S',
        'inflation': 'FPCPITOTLZGKEN'
    },
    '🇰🇷 South Korea': {
        'gdp': 'KORRGDPEXP',
        'unemployment': 'LRHUTTTTKRM156S',
        'inflation': 'CPALTT01KRM659N'
    },
    '🇱🇻 Latvia': {
        'gdp': 'LVARGDPEXP',
        'unemployment': 'LRHUTTTTLVM156S',
        'inflation': 'CPALTT01LVM659N'
    },
    '🇱🇹 Lithuania': {
        'gdp': 'LTURGPDPEXP',
        'unemployment': 'LRHUTTTTLTM156S',
        'inflation': 'CPALTT01LTM659N'
    },
    '🇲🇾 Malaysia': {
        'gdp': 'MYSRGDPEXP',
        'unemployment': 'LRHUTTTTMYM156S',
        'inflation': 'FPCPITOTLZGMYS'
    },
    '🇲🇽 Mexico': {
        'gdp': 'MEXRGDPEXP',
        'unemployment': 'LRHUTTTTMXM156S',
        'inflation': 'FPCPITOTLZGMEX'
    },
    '🇳🇱 Netherlands': {
        'gdp': 'NLDRGDPEXP',
        'unemployment': 'LRHUTTTTNLM156S',
        'inflation': 'CPALTT01NLM659N'
    },
    '🇳🇿 New Zealand': {
        'gdp': 'NZLRGDPEXP',
        'unemployment': 'LRHUTTTTNZM156S',
        'inflation': 'CPALTT01NZM659N'
    },
    '🇳🇴 Norway': {
        'gdp': 'NORRGDPEXP',
        'unemployment': 'LRHUTTTTNOM156S',
        'inflation': 'CPALTT01NOM659N'
    },
    '🇵🇰 Pakistan': {
        'gdp': 'PAKRGDPEXP',
        'unemployment': 'LRHUTTTTPKM156S',
        'inflation': 'FPCPITOTLZGPak'
    },
    '🇵🇭 Philippines': {
        'gdp': 'PHLRGDPEXP',
        'unemployment': 'LRHUTTTTPHM156S',
        'inflation': 'FPCPITOTLZGPHL'
    },
    '🇵🇱 Poland': {
        'gdp': 'POLRGDPEXP',
        'unemployment': 'LRHUTTTTPLM156S',
        'inflation': 'CPALTT01PLM659N'
    },
    '🇵🇹 Portugal': {
        'gdp': 'PORRGDPEXP',
        'unemployment': 'LRHUTTTTPRM156S',
        'inflation': 'CPALTT01PRM659N'
    },
    '🇷🇴 Romania': {
        'gdp': 'ROMRGDPEXP',
        'unemployment': 'LRHUTTTTROM156S',
        'inflation': 'CPALTT01ROM659N'
    },
    '🇷🇺 Russia': {
        'gdp': 'RUSRRGDPEXP',
        'unemployment': 'LRHUTTTTRUM156S',
        'inflation': 'FPCPITOTLZGRUS'
    },
    '🇸🇦 Saudi Arabia': {
        'gdp': 'SAURGDPEXP',
        'unemployment': 'LRHUTTTTSAM156S',
        'inflation': 'FPCPITOTLZGSAU'
    },
    '🇿🇦 South Africa': {
        'gdp': 'ZAFRGDPEXP',
        'unemployment': 'LRHUTTTTZAM156S',
        'inflation': 'FPCPITOTLZGZAF'
    },
    '🇪🇸 Spain': {
        'gdp': 'ESPGDPRQDSMEI',
        'unemployment': 'LRHUTTTTESM156S',
        'inflation': 'CPALTT01ESM659N'
    },
    '🇸🇪 Sweden': {
        'gdp': 'SWENGDPRQDSMEI',
        'unemployment': 'LRHUTTTTSEM156S',
        'inflation': 'CPALTT01SEM659N'
    },
    '🇨🇭 Switzerland': {
        'gdp': 'CHEGDPRQDSMEI',
        'unemployment': 'LRHUTTTTCHM156S',
        'inflation': 'CPALTT01CHM659N'
    },
    '🇹🇷 Turkey': {
        'gdp': 'TURRGDPEXP',
        'unemployment': 'LRHUTTTTTRM156S',
        'inflation': 'FPCPITOTLZGTR'
    },
    '🇬🇧 United Kingdom': {
        'gdp': 'UKNGDP',
        'unemployment': 'LRHUTTTTGBM156S',
        'inflation': 'CPALTT01GBM659N'
    },
    '🇺🇸 United States': {
        'gdp': 'GDPC1',
        'unemployment': 'UNRATE',
        'inflation': 'CPALTT01USM657N'
    }
}

def check_data_availability(data, frequency):
    """
    Check data availability and return status
    Returns: 'good' (>75% data), 'partial' (25-75% data), or 'bad' (<25% data)
    """
    if data is None or data.empty:
        return 'bad'
    
    # Determine the number of expected data points based on frequency
    if frequency == 'quarterly':
        total_points = len(pd.date_range(start=data.index[0], end=data.index[-1], freq='Q'))
    elif frequency == 'monthly':
        total_points = len(pd.date_range(start=data.index[0], end=data.index[-1], freq='M'))
    else:
        total_points = len(data)
    
    available_points = data.count()
    
    if total_points > 0:
        availability_pct = (available_points / total_points) * 100
        if availability_pct >= 75:
            return 'good'
        elif availability_pct >= 25:
            return 'partial'
        else:
            return 'bad'
    else:
        return 'bad'

def fetch_fred_data(selected_countries, country_data, indicator_type='gdp', start_date=None, end_date=None):
    """Fetch data from FRED with proper transformations"""
    try:
        all_data = {}
        for country_name in selected_countries:
            if country_name in country_data:
                series_id = country_data[country_name][indicator_type]
                try:
                    data = fred.get_series(series_id, 
                                         observation_start=start_date,
                                         observation_end=end_date)
                    
                    # Handle different frequencies and transformations
                    if indicator_type == 'gdp':
                        data = data.pct_change() * 100
                    elif indicator_type in ['unemployment', 'inflation']:
                        if len(data) > 0 and isinstance(data.index[0], pd.Timestamp):
                            # Resample to quarterly if the data is not already quarterly
                            if data.index.freq != 'Q':
                                data = data.resample('Q').last()
                    
                    all_data[country_name] = data
                except:
                    # Create a series of NaN values if data fetch fails
                    all_data[country_name] = pd.Series(index=pd.date_range(start=start_date, 
                                                                         end=end_date, 
                                                                         freq='Q'))
        
        if all_data:
            df = pd.DataFrame(all_data)
            return df.sort_index(ascending=False)
        return None

    except Exception as e:
        st.error(f"Error fetching {indicator_type} data: {str(e)}")
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

def style_dataframe(df, frequency):
    """Style the dataframe with appropriate formatting"""
    if df is None or df.empty:
        return None
        
    # Keep only last 12 quarters/months
    if frequency == 'quarterly':
        df = df.head(12)
    elif frequency == 'monthly':
        df = df.head(36)
    
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
    
    styled_df = df.applymap(format_value)
    
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
    default=list(st.session_state.all_countries.keys())[:2],
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

    # Create tabs with status emojis and data availability text
    tab1, tab2, tab3 = st.tabs([
        f"📈 GDP Growth (Data Availability: {get_status_emoji(gdp_data, 'quarterly')})",
        f"👥 Unemployment (Data Availability: {get_status_emoji(unemp_data, 'quarterly')})",
        f"💰 Inflation (Data Availability: {get_status_emoji(infl_data, 'quarterly')})"
    ])
    # Add JavaScript to handle tab coloring
    st.markdown("""
        <script>
            function updateTabStyles() {
                const tabs = document.querySelectorAll('[role="tab"]');
                tabs.forEach(tab => {
                    const text = tab.textContent;
                    if (text.includes('##good')) {
                        tab.classList.add('data-status-good');
                        tab.textContent = text.replace('##good', '');
                    } else if (text.includes('##partial')) {
                        tab.classList.add('data-status-partial');
                        tab.textContent = text.replace('##partial', '');
                    } else if (text.includes('##bad')) {
                        tab.classList.add('data-status-bad');
                        tab.textContent = text.replace('##bad', '');
                    }
                });
            }
            updateTabStyles();
            const observer = new MutationObserver(updateTabStyles);
            observer.observe(document.body, { childList: true, subtree: true });
        </script>
    """, unsafe_allow_html=True)
    
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
    unsafe_allow_html=True
)
