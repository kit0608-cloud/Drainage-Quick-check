import streamlit as st
import math

# --- App Configuration ---
st.set_page_config(page_title="UK Drainage Check", page_icon="🇬🇧")

# --- CUSTOM CSS (Clean Look) ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🇬🇧 UK Drainage Quick-Check")
st.caption("For quick estimation only")
st.markdown("---")

# ==========================================
# TOOL 1: SMART RAINFALL & STORAGE
# ==========================================
st.header("1. Storage Estimator")

col1, col2 = st.columns(2)

with col1:
    # 1. City / Region (FSR M5-60 Data)
    city_m5_60 = {
        "Manual Input": 20.0,
        "London (South East)": 20.0,
        "Birmingham (Midlands)": 19.0,
        "Manchester (North West)": 19.0,
        "Leeds (Yorkshire)": 19.0,
        "Bristol (South West)": 20.5,
        "Cardiff (Wales)": 21.0,
        "Glasgow (Scotland)": 17.0,
        "Belfast (NI)": 16.0
    }
    selected_city = st.selectbox("📍 Select Region:", list(city_m5_60.keys()))
    
    # 2. Return Period (The question usually asked in meetings)
    return_period = st.selectbox("Return Period:", ["1 in 30 Years", "1 in 100 Years"])
    
    # 3. Climate Change (+40% is standard now)
    add_cc = st.checkbox("Apply +40% Climate Change?", value=True)

    # --- MATH ENGINE ---
    m5_60_val = city_m5_60[selected_city]
    
    # Z2 Growth Factors (FSR)
    if return_period == "1 in 30 Years":
        z2_factor = 1.95 
    else:
        z2_factor = 2.45

    # Base Intensity Calculation
    base_intensity = m5_60_val * z2_factor
    
    # Apply Climate Change
    if add_cc:
        final_intensity = base_intensity * 1.40
        cc_text = "+40% CC"
    else:
        final_intensity = base_intensity
        cc_text = "No CC"

    # 4. Area
    area_unit = st.radio("Select Area Unit:", ["Square Meters (m²)", "Hectares (Ha)"])
    area_input = st.number_input("Catchment Area:", min_value=0.0, value=1000.0, step=10.0)

with col2:
    # 5. Result Preview (Intensity)
    st.metric(
        label="Design Intensity", 
        value=f"{final_intensity:.1f} mm/hr",
        delta=cc_text
    )
    
    # 6. Parameters
    duration_min = st.number_input("Storm Duration (mins):", min_value=1.0, value=60.0)
    allowable_discharge = st.number_input("Allowable Discharge (l/s):", min_value=0.0, value=5.0)

# --- STORAGE CALCULATION ---
if area_unit == "Hectares (Ha)":
    area_m2 = area_input * 10000
else:
    area_m2 = area_input

rainfall_depth_m = (final_intensity * (duration_min / 60)) / 1000
vol_in = area_m2 * rainfall_depth_m
vol_out = (allowable_discharge * (duration_min * 60)) / 1000

storage_req = vol_in - vol_out
if storage_req < 0:
    storage_req = 0

# RESULT
st.success(f"📦 **Storage Required: {storage_req:.2f} m³**")
st.caption(f"Based on {selected_city} data ({return_period}).")

st.markdown("---")
st.markdown("##")

# ==========================================
# TOOL 2: PIPE HYDRAULICS
# ==========================================
st.header("2. Pipe Capacity Check")

p_col1, p_col2 = st.columns(2)

with p_col1:
    pipe_diameters = [150, 225, 300, 375, 450, 525, 600, 750, 900, 1050, 1200]
    diameter_mm = st.selectbox("Pipe Diameter (mm):", pipe_diameters)

with p_col2:
    gradient_denominator = st.number_input("Gradient (1 in X):", min_value=10.0, value=150.0, step=10.0)

# --- HYDRAULIC CALCULATION (Colebrook-White) ---
if gradient_denominator > 0:
    g = 9.81
    viscosity = 1.31e-6 
    Ks_m = 0.6 / 1000.0 # 0.6mm Roughness
    
    D_m = diameter_mm / 1000.0
    Area = (math.pi * D_m**2) / 4
    Hydraulic_Radius = D_m / 4
    Slope = 1 / gradient_denominator
    
    shear_term = math.sqrt(8 * g * Hydraulic_Radius * Slope)
    term_a = Ks_m / (14.8 * Hydraulic_Radius)
    term_b = (1.255 * viscosity) / (Hydraulic_Radius * shear_term)
    
    # Explicit Velocity Formula
    velocity = -2 * shear_term * math.log10(term_a + term_b)
    capacity_ls = (velocity * Area) * 1000

    # DISPLAY RESULTS
    st.write(f"**Capacity:** {capacity_ls:.2f} l/s")
    st.write(f"**Velocity:** {velocity:.2f} m/s")

    # VALIDATION
    if velocity < 1.0:
        st.error(f"⛔ FAIL: Velocity {velocity:.2f} m/s (Risk of Silt)")
    elif velocity > 3.0:
        st.warning(f"⚠️ WARNING: Velocity {velocity:.2f} m/s (Scour Risk)")
    else:
        st.success(f"✅ PASS: Self-Cleansing OK")
