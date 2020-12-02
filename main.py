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
        - **5.10** - Stiffened Web $\alpha_v$ calculation
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

    # Input results
    #TODO
    
if __name__ == '__main__':
    main()