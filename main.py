#Import streamlit modules
import streamlit as st

#Import associated py files with functions
import functions as fnc
import validation as vld
import section_funcs
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
    
    with st.beta_expander("Table of contents:"):
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
    longit_stif_spacing_latex, longit_stif_spacing_vals = fnc.longit_stif_spacing(b * u.m, d * u.m, n_stif)
    st.sidebar.latex(longit_stif_spacing_latex)
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
    Mx = st.sidebar.number_input("Mx Torsion Force (kNm)",0,5000,100,10,"%i") * 1000
    My = st.sidebar.number_input("My Transverse BM (kNm)",0,20000,1000,10,"%i") * 1000
    Mz = st.sidebar.number_input("Mz Vertical BM (kNm)",0,20000,1000,10,"%i") * 1000
    rho = st.sidebar.slider("Proportion of longitudinal stress assumed to be redistributed from web to flange (%)",0,100,0,5,"%i") / 100

    #Precamber
    camb1 = st.sidebar.slider("Assumed pre-camber for imperfection calculations:",0,1000,100,10,"%i") / 1000
    x1 = L/2

    with st.beta_expander("Box Girder Section Properties Check"):
        st.markdown("""
        Below section calculates the following box girder properties:

        - Section Properties
            - *area* Area
            - *cx, cy* Centroids
            - *ixx_c, iyy_c* Second Mom Area
            - *J* Torsion Constant
        - Stress Outputs - Max
            - *f_star_s_comp* Max Compression due to Biaxial BM
            - *f_star_s_tens* Max Tension ...
        - The maximum stress in the for the critical stiffeners is:
            - *f_star_s_fl* Max compression at Effective flange stiffener section due to Biaxial BM
            - *f_star_s_web* Max compression at Effective web stiffener ...
            - *f_star_s_fl_mid* Max compression at mid-panel of flange due to Triaxial BM
            - *f_star_s_web_mid* Max compression at mid-panel of web ...

        The below calculations are using the ***SectionProperties*** library in Python to calculate the stiffener critical stresses to be used.

        A separate Python file is used for the box girder geometry generator.
        """)

    st.set_option('deprecation.showPyplotGlobalUse', False)
    section, fig1, ax1 = section_funcs.boxgenerator(b,
                                     d,
                                     t_w,
                                     t_f,
                                     d_stif,
                                     t_stif,
                                     n_stif)
    @st.cache
    def calculate_section(section):
        section.calculate_geometric_properties(time_info=False)
        section.calculate_warping_properties(time_info=False)
        return section
    
    section = calculate_section(section)

    area = section.get_area()
    (cx, cy) = section.get_c()
    (ixx_c, iyy_c, ixy_c) = section.get_ic()

    x_f_stif,y_f_stif,x_w_stif,y_w_stif,x_f_mid,y_f_mid,x_w_mid,y_w_mid = fnc.stress_locations(b * u.m,d * u.m,t_f * u.m,t_w * u.m,n_stif)

    #Plot stress points to consider
    ax1.plot(x_f_stif.value,y_f_stif.value,'ro')
    ax1.annotate(f"Crit Flange Stiffener",(x_f_stif.value,y_f_stif.value),(x_f_stif.value+0.3,y_f_stif.value+0.3),arrowprops={'arrowstyle':'->'})
    ax1.plot(x_w_stif.value,y_w_stif.value,'ro')
    ax1.annotate(f"Crit Web Stiffener",(x_w_stif.value,y_w_stif.value),(x_w_stif.value-1.0,y_w_stif.value+0.3),arrowprops={'arrowstyle':'->'})
    ax1.plot(x_f_mid.value,y_f_mid.value,'ro')
    ax1.annotate(f"Crit flange panel",(x_f_mid.value,y_f_mid.value),(x_f_mid.value-0.4,y_f_mid.value+0.3),arrowprops={'arrowstyle':'->'})
    ax1.plot(x_w_mid.value,y_w_mid.value,'ro')
    ax1.annotate(f"Crit web panel",(x_w_mid.value,y_w_mid.value),(x_w_mid.value-0.4,y_w_mid.value+0.3),arrowprops={'arrowstyle':'->'})
 
    st.pyplot(fig1) #Plot the cross section shape of the box girder

    #Output section properties for box girder
    st.text(f'A: {area:.4f} m^2 \n\n'
    f'Section centroids are:\ncx = {cx:.3f} m\n'
    f'cy = {cy:.3f} m \n\n'
    f'Second Moments of area are:\n'
    f'ixx_c = {ixx_c:.4f} m^4 \niyy_c = {iyy_c:.4f} m^4')

    # Get stresses on beam
    f_star_s_comp, f_star_s_tens, stresses = section_funcs.in_plane_principle(section,Fy,Fz,Mx,My,Mz)


    f_star_s_fl = section_funcs.stress_location(x_f_stif.value,
                              y_f_stif.value,
                              0.05,
                              0.05, 
                              section.mesh_nodes, 
                              stresses[0]['sig_zz_m'],
                              'max')
    f_star_s_web = section_funcs.stress_location(x_w_stif.value,
                                y_w_stif.value,
                                0.05,
                                0.05,
                                section.mesh_nodes,
                                stresses[0]['sig_zz_m'],
                                'max')
    f_star_s_fl_mid = section_funcs.stress_location(x_f_mid.value,
                                    y_f_mid.value,
                                    0.05,
                                    0.05, 
                                    section.mesh_nodes, 
                                    stresses[0]['sig_zz_m'],
                                    'max')
    f_star_s_web_mid = section_funcs.stress_location(x_w_mid.value,
                                    y_w_mid.value,
                                    0.05,
                                    0.05,
                                    section.mesh_nodes, 
                                    stresses[0]['sig_zz_m'],
                                    'max')
    f_star_s_fl_mean = section_funcs.stress_location(b/2,d,b/2,t_f, section.mesh_nodes, stresses[0]['sig_zz_m'],"mean")
    f_star_v = stresses[0]['sig_zy_vy'].max()
    f_star_vt = stresses[0]['sig_zxy_mzz'].max()

    st.text(f'The maximum stress in for the critical stiffeners is:\n'
      f'f_star_s_fl = {f_star_s_fl/1e6:.0f} MPa\n'
      f'f_star_s_web = {f_star_s_web/1e6:.0f} MPa\n\n'
      f'The maximum stress in the mid-panel sections is:\n'
      f'f_star_s_fl_mid = {f_star_s_fl_mid/1e6:.0f} MPa\n'
      f'f_star_s_web_mid = {f_star_s_web_mid/1e6:.0f} MPa\n\n'
      f'The average stress across the top flange is:\n'
      f'f_star_s_fl_mean = {f_star_s_fl_mean/1e6:.0f} MPa\n\n'
      f'The max torsion shear stress is:\n'
      f'f_star_vt = {f_star_vt/1e6:.0f} MPa')

    flange_yield_latex, f_star_comb = fnc.flange_yield(f_star_vt * u.Pa,f_star_v * u.Pa,f_star_s_fl_mid * u.Pa)
    st.latex(flange_yield_latex)

    if f_star_comb > phi*f_y * u.Pa:
        st.error("FAIL {0} > {1} Util = {2:.2f}".format(f_star_comb,phi*f_y * u.Pa,f_star_comb/(phi*f_y * u.Pa)))
    else:
        st.success("PASS {0} < {1} Util = {2:.2f}".format(f_star_comb,phi*f_y * u.Pa,f_star_comb/(phi*f_y * u.Pa)))

    with st.beta_expander("Effective section of flange stiffener"):
        st.markdown("""
        The slenderness of K_c value of the flange stiffeners are calculated in this section

        - Stiffened flanges Section 7- Section 9.10.2 - BS5400.3-2000
        - $K_c$ as per Fig 7.3.3.2 AS5100.6-2017 (Also BS5400 Fig 5)

        Number of stiffeners:
        - For **Stiffeners** >= 3, use greater of: 
            - Curve 1
            - Curve 3
        - For **Stiffeners** =2, use greater of:
            - Ave (Curve 1 + Curve 2)
            - Curve 3

        Slenderness:
        - Curve 1 or 2:""")
        st.latex(r"\lambda_{kb} = \frac{b}{t}\sqrt{\frac{f_y}{355}}")
        st.markdown("- Curve 3:")
        st.latex(r"\lambda_{ka} = \frac{a}{t}\sqrt{\frac{f_y}{355}}")

    K_c, lamda_kc_a, lamda_kc_b, fig2, ax2 = fnc.K_buckling(n_stif,a_panel,b_flange.value,t_f,f_y)
    st.pyplot(fig2)
if __name__ == '__main__':
    main()