import streamlit as st
import math

# --- App Configuration ---
st.set_page_config(page_title="The Civil Engineer's Pocket Toolkit", page_icon="🇬🇧")

# --- CUSTOM CSS ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🇬🇧 The Civil Engineer's Pocket Toolkit")
st.caption("Site Estimator: Rainfall | Pipes | Ponds")
st.markdown("---")

# ==========================================
# TOOL 1: RAINFALL & STORAGE REQUIRED
# ==========================================
st.header("1. Rainfall & Storage Required")

col1, col2 = st.columns(2)

with col1:
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
    selected_city = st.selectbox("📍 Region:", list(city_m5_60.keys()))
    return_period = st.selectbox("Return Period:", ["1 in 30 Years", "1 in 100 Years"])
    add_cc = st.checkbox("Apply +40% CC?", value=True)

    m5_60_val = city_m5_60[selected_city]
    if return_period == "1 in 30 Years":
        z2_factor = 1.95 
    else:
        z2_factor = 2.45

    base_intensity = m5_60_val * z2_factor

    if add_cc:
        final_intensity = base_intensity * 1.40
        cc_text = "+40% CC"
    else:
        final_intensity = base_intensity
        cc_text = "No CC"

    area_unit = st.radio("Area Unit:", ["m²", "Ha"], horizontal=True)
    area_input = st.number_input("Catchment Area:", min_value=0.0, value=1000.0, step=10.0)

with col2:
    st.metric(label="Design Intensity", value=f"{final_intensity:.1f} mm/hr", delta=cc_text)
    duration_min = st.number_input("Duration (mins):", min_value=1.0, value=60.0)
    allowable_discharge = st.number_input("Discharge Limit (l/s):", min_value=0.0, value=5.0)

if area_unit == "Ha":
    area_m2 = area_input * 10000
else:
    area_m2 = area_input

rainfall_depth_m = (final_intensity * (duration_min / 60)) / 1000
vol_in = area_m2 * rainfall_depth_m
vol_out = (allowable_discharge * (duration_min * 60)) / 1000
storage_req = max(0, vol_in - vol_out)

st.success(f"📦 **Required Storage: {storage_req:.2f} m³**")

st.markdown("---")

# ==========================================
# TOOL 2: PIPE CHECK
# ==========================================
st.header("2. Pipe Capacity Check")

p_col1, p_col2 = st.columns(2)

with p_col1:
    pipe_diameters = [150, 225, 300, 375, 450, 525, 600, 750, 900, 1050, 1200]
    diameter_mm = st.selectbox("Diameter (mm):", pipe_diameters)

with p_col2:
    gradient_denominator = st.number_input("Gradient (1 in X):", min_value=10.0, value=150.0)

if gradient_denominator > 0:
    g = 9.81
    viscosity = 1.31e-6 
    Ks_m = 0.6 / 1000.0 
    D_m = diameter_mm / 1000.0
    Area = (math.pi * D_m**2) / 4
    Hydraulic_Radius = D_m / 4
    Slope = 1 / gradient_denominator
    shear_term = math.sqrt(8 * g * Hydraulic_Radius * Slope)
    term_a = Ks_m / (14.8 * Hydraulic_Radius)
    term_b = (1.255 * viscosity) / (Hydraulic_Radius * shear_term)
    velocity = -2 * shear_term * math.log10(term_a + term_b)
    capacity_ls = (velocity * Area) * 1000

    c1, c2 = st.columns(2)
    c1.write(f"**Cap:** {capacity_ls:.2f} l/s")
    c2.write(f"**Vel:** {velocity:.2f} m/s")

    if velocity < 1.0:
        st.error(f"⛔ Low Velocity")
    elif velocity > 3.0:
        st.warning(f"⚠️ High Velocity")
    else:
        st.success(f"✅ Self-Cleansing OK")

st.markdown("---")

# ==========================================
# TOOL 3: POND SIZING
# ==========================================
st.header("3. Pond Volume Calculator")
st.caption("Calculates available volume based on geometry and side slopes.")

pond_col1, pond_col2 = st.columns(2)

with pond_col1:
    # Geometry Inputs
    base_area = st.number_input("Base Area (m²):", min_value=1.0, value=50.0)
    base_perimeter = st.number_input("Base Perimeter (m):", min_value=1.0, value=30.0)
    side_slope = st.number_input("Side Slope (1 in X):", min_value=0.0, value=3.0, step=0.5)

with pond_col2:
    # Depth Inputs
    total_depth = st.number_input("Total Pond Depth (m):", min_value=0.1, value=1.5)
    freeboard = st.number_input("Freeboard (m):", min_value=0.0, value=0.3)

# --- POND MATH ---
water_depth = total_depth - freeboard

if water_depth <= 0:
    st.error("Error: Freeboard is deeper than the pond!")
else:
    # Calculation: Prismoidal Approximation

    # Horizontal offset distance
    offset = water_depth * side_slope

    # Area Top = Base Area + (Perimeter * Offset) + (4 * Corners * Offset^2)
    area_top = base_area + (base_perimeter * offset) + (4 * (offset**2))

    # Prismoidal Volume Formula
    pond_volume = (water_depth / 3) * (base_area + area_top + math.sqrt(base_area * area_top))

    # Display Results
    st.info(f"**Effective Water Depth:** {water_depth:.2f} m")
    st.success(f"💧 **Available Storage Volume:** {pond_volume:.2f} m³")
