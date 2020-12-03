#Import streamlit modules
import streamlit as st

#Import associated py files with functions
import functions as fnc
import validation as vld
import plots

#Import data and plotting
import pandas as pd
import matplotlib.pyplot as plt

#Import unit aware modules
import forallpeople as u
u.environment('structural')

from handcalcs import handcalc

#Main function calls made at each run of Streamlit
def main():
    """This function is run at the beginning of each script"""
    st.title("Box Girder Design - Stiffener calculations")
    st.markdown("""
    The below worksheet shows the calculations that are required for the longitudinal and transverse stiffeners as per 

    Sec 7.3 - AS5100.6-2017
    or
    Sec 7.3 - AS5100.6-2004

    # TABLE OF CONTENTS:

    **Section 7.3** - *Longitudinal Flange Stiffeners*
    - **7.3.3.1** - Yielding of flange plate
    - **7.3.3.2** - Effective Section of Flange Plate Stiffener
    - **7.3.3.3** - Strength of Longitudinal Flange Stiffeners


    **Section 7.4** - *Web in Beams with Longitudinal Stiffeners*
    - **7.4.2** - Yielding of Web Panels
    - **7.4.3** - Buckling of Web Panels
    - **7.4.4** - Longitudinal Web Stiffeners
    - **7.4.6** - Transverse Stiffeners of Longitudinally Stiffened Webs
        - **5.10** - Stiffened Web alpha_v calculation
        - **5.14** - Design of Intermediate Transverse Web Stiffeners
        
        
    **Section 7.5** - *Transverse Members in Stiffened Flanges*
    - **7.5.2** - Effective Section and Stiffness for Transverse Members
    - **7.5.3** - Stiffness of Transverse Members

    **BS5400 - Sec 9 used for supplementary information**
    """)

    #Create Menu for various options
    vld.input_description("Click here to add custom description, sketch or image")
    
    # Out of order Results Summary
    st.header("Results Summary")
    results_container = st.beta_container()

    # Choice of standards
    st.sidebar.markdown("## Input Design Requirements")
    version = st.sidebar.radio("Edition of AS5100.6",("2004","2017"))
    panel_pos = st.sidebar.radio("Panel being analysed",("outer","inner"))

    #Geometry of box girder
    st.sidebar.markdown("## Input Structure Geometry")
    L = st.sidebar.number_input('Length of Box Girder (m)',5.0,100.0,50.0,step=1.0,format='%f')

    #Box dimension inputs
    st.sidebar.markdown("## Input box dimensions")
    b = st.sidebar.slider('Width of Box Girder (mm)',500,3000,1000,step=50,format='%i') / 1000
    d = st.sidebar.slider('Height of Box Girder (mm)',500,3000,1000,step=50,format='%i') / 1000
    t_w = st.sidebar.slider('Thickness of Webs (mm)',5,30,12,step=1,format='%i') / 1000
    t_f = st.sidebar.slider('Thickness of Flanges (mm)',5,30,12,step=1,format='%i') / 1000

    #Stiffener dimensions
    st.sidebar.markdown("## Input Stiffener dimensions")
    n_stif = st.sidebar.radio("Number of stiffeners",(2,3))
    d_stif = st.sidebar.slider('Depth/Height longit. stiffeners(mm)',50,300,100,step=5,format='%i') / 1000
    t_stif = st.sidebar.slider('Thickness longit. stiffeners (mm)',5,30,12,step=1,format='%i') / 1000
    d_stif_trans = st.sidebar.slider('Depth/Height tranv. stiffeners / diaphragm (mm)',50,300,100,step=5,format='%i') / 1000
    t_stif_trans = st.sidebar.slider('Thickness of transv. stiffeners / diaphragm(mm)',5,30,12,step=1,format='%i') / 1000
    a_panel = st.sidebar.slider('Spacing of transverse stiffeners (mm)',300,3000,1000,step=50,format='%i') / 1000

    #Calculate stiffener dimensions
    longit_stif_spacing_latex, longit_stif_spacing_vals = fnc.longit_stif_spacing(b, d, n_stif)
    st.latex(longit_stif_spacing_latex)
    b_flange,b_web = longit_stif_spacing_vals

    #Input Materials
    st.sidebar.markdown("## Input Material Properties")
    f_y = st.sidebar.number_input("Yield Strength (MPa)",150,500,350,10,"%i") * 10**6
    E_s = st.sidebar.number_input("Young's Modulus (GPa)",40,300,200,5,"%i") * 10**9

    phi = 0.9 #T3.2 (b) (i) - Members subject to bending Cl7.3
    rho_steel = 7850 #Density of steel
    g = 9.81 #Gravity

    st.sidebar.latex(r"\phi={0.9}")
    st.sidebar.latex(r"\rho_{steel}=7850 \frac{kg}{m^3}")
    st.sidebar.latex(r"g=9.81 \frac{N}{kg}")

    #Force values
    st.sidebar.markdown("## Input Forces")
    Fx = st.sidebar.number_input("F_x Axial Force typically due to thermal or restraint effects (kN)",0,1000,100,10,"%i") * 1000
    Fy = st.sidebar.number_input("F_y Vertical Shear Force (kN)",0,5000,100,10,"%i") * 1000
    Fz = st.sidebar.number_input("F_z Horizontal Shear Force (kN)",0,5000,100,10,"%i") * 1000
    Mx = st.sidebar.number_input("Mx Torsion Force (kNm)",0,5000,100,10,"%i")
    My = st.sidebar.number_input("My Transverse BM (kNm)",0,20000,1000,10,"%i")
    Mz = st.sidebar.number_input("Mz Vertical BM (kNm)",0,20000,1000,10,"%i") * 1000
    rho = st.sidebar.slider("Proportion of longitudinal stress assumed to be redistributed from web to flange (%)",0,100,0,5,"%i") / 100

if __name__ == '__main__':
    main()