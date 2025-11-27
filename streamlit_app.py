import streamlit as st
import math

# --- App Configuration ---
st.set_page_config(page_title="Civil Site Tools", page_icon="🏗️")

st.title("💧 Civil Engineer Tools")
st.caption("Storage Estimation & Pipe size quick check only.")
st.markdown("---")

# ==========================================
# TOOL 1: STORAGE ESTIMATOR
# ==========================================
st.header("1. Quick Storage Estimator")
st.info("Estimate attenuation volume based on Catchment Area & Rainfall.")

col1, col2 = st.columns(2)

with col1:
    # Input: Unit Selection
    area_unit = st.radio("Select Area Unit:", ["Square Meters (m²)", "Hectares (Ha)"])

    # Input: Area Value
    area_input = st.number_input("Catchment Area:", min_value=0.0, value=1000.0, step=10.0)

    # Input: Rainfall Intensity
    rainfall_intensity = st.number_input("Rainfall Intensity (mm/hr):", min_value=0.0, value=50.0)

with col2:
    # Input: Storm Duration
    duration_min = st.number_input("Storm Duration (mins):", min_value=1.0, value=60.0)

    # Input: Allowable Discharge
    allowable_discharge = st.number_input("Allowable Discharge Rate (l/s):", min_value=0.0, value=5.0)

# --- Logic: Storage Calculation ---
if area_unit == "Hectares (Ha)":
    area_m2 = area_input * 10000
else:
    area_m2 = area_input

# Calculate Inflow vs Outflow
rainfall_depth_m = (rainfall_intensity * (duration_min / 60)) / 1000
vol_in = area_m2 * rainfall_depth_m
vol_out = (allowable_discharge * (duration_min * 60)) / 1000

# Net Storage
storage_req = vol_in - vol_out
if storage_req < 0:
    storage_req = 0

st.subheader(f"📦 Storage Required: {storage_req:.2f} m³")
st.caption(f"For a 1.5m deep tank, plan area approx: **{(storage_req/1.5):.1f} m²**")


# ==========================================
# DIVIDER
# ==========================================
st.markdown("---")
st.markdown("##")


# ==========================================
# TOOL 2: PIPE VELOCITY CHECKER (Colebrook-White)
# ==========================================
st.header("2. Pipe Gradient Check")
st.info("Uses Roughness(Ks = 0.6mm). Checks for Min Velocity 1.0 m/s.")

p_col1, p_col2 = st.columns(2)

with p_col1:
    # Standard Pipe Sizes
    pipe_diameters = [150, 225, 300, 375, 450, 525, 600, 750, 900, 1050, 1200]
    diameter_mm = st.selectbox("Pipe Diameter (mm):", pipe_diameters)

with p_col2:
    # Gradient Input
    gradient_denominator = st.number_input("Gradient (1 in X):", min_value=10.0, value=150.0, step=10.0)

# --- Logic: Colebrook-White Equation ---
if gradient_denominator > 0:
    # Constants
    g = 9.81
    viscosity = 1.31e-6  # Kinematic viscosity of water at 10°C (m²/s)
    Ks_mm = 0.6          # Roughness height in mm
    Ks_m = Ks_mm / 1000.0 # Convert to meters

    # Pipe Geometry
    D_m = diameter_mm / 1000.0
    Area = (math.pi * D_m**2) / 4
    Hydraulic_Radius = D_m / 4
    Slope = 1 / gradient_denominator

    # Colebrook-White Calculation (Explicit form for Velocity)
    # V = -2 * sqrt(8gRS) * log10( (Ks / 14.8R) + (1.255v / R*sqrt(8gRS)) )

    shear_term = math.sqrt(8 * g * Hydraulic_Radius * Slope)

    term_a = Ks_m / (14.8 * Hydraulic_Radius)
    term_b = (1.255 * viscosity) / (Hydraulic_Radius * shear_term)

    velocity = -2 * shear_term * math.log10(term_a + term_b)

    # Calculate Capacity
    capacity_m3s = velocity * Area
    capacity_ls = capacity_m3s * 1000

    # Display Data
    st.write(f"**Full Bore Capacity:** {capacity_ls:.2f} l/s")
    st.write(f"**Velocity:** {velocity:.2f} m/s")

    # --- Check: 1.0 m/s Limit ---
    if velocity < 1.0:
        st.error(f"⛔ FAIL: Velocity is {velocity:.2f} m/s (Below 1.0 m/s). Risk of Silt.")
    elif velocity > 3.0:
        st.warning(f"⚠️ HIGH VELOCITY: {velocity:.2f} m/s. Scour risk.")
    else:
        st.success(f"✅ PASS: Velocity is {velocity:.2f} m/s (Self-Cleansing).")
