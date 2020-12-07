#Import streamlit
import streamlit as st

#Math and array modules
from math import sqrt, cos, sin, pi, atan
import numpy as np
from bisect import bisect_right

#Section properties module
import sectionproperties.pre.sections as sections
from sectionproperties.analysis.cross_section import CrossSection

#Import other py files
import section_funcs

#Import handcalcs
from handcalcs import handcalc

#Import unit aware modules
import forallpeople as u
u.environment('structural')

import matplotlib.pyplot as plt

@handcalc(override="long")
def longit_stif_spacing(b, d, n_stif):
    b_flange = b / (n_stif + 1)
    b_web = d / (n_stif + 1)
    return b_flange, b_web

def stress_locations(b,d,t_f,t_w,n_stif: int):
    """
    Calculate the critical locations to be used for determining stresses
    within the sectionproperties module
    """
    x_f_stif = b/(n_stif+1) #x-coord of the critical flange stiffener next to the highly stressed top left corner.
    y_f_stif = d - t_f #y-coord of above

    x_w_stif = t_w #x-coord of the critical web stiffener closest to the highly stressed top left corner.
    y_w_stif = d - d/(n_stif+1) #y-coord of above

    x_f_mid = b/(n_stif+1)/2 #x-coord of the mid-plane of the critical flange-plate for yield checks only (Cl.7.3.2)
    y_f_mid = d - t_f/2 #y-coord of the mid-plane of the critical flange plate

    x_w_mid = t_w/2
    y_w_mid = d - d/(n_stif+1)/2 #location of the mid-plane of the critical web-plate for yield checks only (Cl.7.3.2)
    
    return x_f_stif,y_f_stif,x_w_stif,y_w_stif,x_f_mid,y_f_mid,x_w_mid,y_w_mid

@handcalc(override="long")
def flange_yield(f_star_vt,f_star_v,f_star_s_fl_mid):
    f_star_vf = f_star_vt + 0.5 * f_star_v
    f_star_comb = (f_star_s_fl_mid**2 + 3 * f_star_vf**2)**0.5
    return f_star_comb

def K_buckling(n_stif,a_panel,b_panel,t,f_y):
    '''Function defines a method for calculating the K-value from the curve Fig 7.3.3.2 or Fig 7.4.3.3(A):
    Input params:
    n_stif: number of longitudinal stiffeners 2 and 3 accepted
    a_panel: length along beam between transverse stiffeners
    b_panel: width perpendicular to beam between longitudinal stiffeners
    t: thickness of main plate
    f_y: yield strength of plates
    
    Output:
    K: Buckling coefficient
    lamda_k_a: Slenderness in 'a' direction
    lamda_k_b: Slenderness in 'b' direction
    '''
    #All inputs in SI units
    #Outputs include 
    lamda_k_a = a_panel/t * sqrt(f_y/(355 * 10**6)) #Slenderness in between transverse stiffeners
    lamda_k_b = b_panel/t * sqrt(f_y/(355 * 10**6)) #Slenderness in between longitudinal stiffeners
    #Set out the points for each curve.
    x_k = np.array([0,10,25,30, 50, 100, 130,150, 250]) # get several x data points
    y_k_cv1 = np.array([1,1,1,0.89, 0.68, 0.4, 0.317,0.31, 0.27]) #get several y data points
    y_k_cv2 = np.array([1,1,1,0.86, 0.58, 0.32, 0.257,0.255, 0.242]) #get several y data points
    y_k_cv3 = np.array([1,1,0.54,0.46, 0.17, 0.045, 0.025,0.02, 0.01]) #get several y data points
    K_cv1 = min(1.0,np.interp(lamda_k_b,x_k,y_k_cv1))
    K_cv2 = min(1.0,np.interp(lamda_k_b,x_k,y_k_cv2))
    K_cv3 = min(1.0,np.interp(lamda_k_a,x_k,y_k_cv3))
    
    fig, ax = plt.subplots()
    ax.plot(x_k,y_k_cv1,label="Curve 1")
    ax.plot(x_k,y_k_cv2,label="Curve 2")
    ax.plot(x_k,y_k_cv3,label="Curve 3")
    ax.legend()
    st.text(f'Lamda_k_b (Crv 1/2) = {lamda_k_b:0.2f}\n'
          f'Lamda_k_a (Crv 3) {lamda_k_a:0.2f}\n')

    st.text(f'The coefficient K for plate panels is:\n'
          f'K_cv1 = {K_cv1:0.3f}\n'
          f'K_cv2 = {K_cv2:0.3f}\n'
          f'K_cv3 = {K_cv3:0.3f}\n')
    
    if n_stif == 3:
        if K_cv1 > K_cv3:
            K = K_cv1
            ax.plot(lamda_k_b,K,'ro')
            ax.plot(lamda_k_a,K_cv3,'bx')
            st.text(f'The highest value to be used is K_cv1 = {K:0.3f}\n')
            return K, lamda_k_a, lamda_k_b, fig, ax
        else:
            K = K_cv3
            ax.plot(lamda_k_a,K,'ro')
            ax.plot(lamda_k_b,K_cv1,'bx')
            st.text(f'The highest value to be used is K_cv3 = {K:0.3f}\n')
            return K, lamda_k_a, lamda_k_b, fig, ax
    elif n_stif == 2:
        if (K_cv1+K_cv2)/2 > K_cv3:
            K = (K_cv1+K_cv2)/2
            ax.plot(lamda_k_b,K,'ro')
            ax.plot(lamda_k_a,K_cv3,'bx')
            st.text(f'The highest value to be used is:\nave(K_cv1 & K_cv2): {K:0.3f}\n')
            return K, lamda_k_a, lamda_k_b, fig, ax
        else:
            K = K_cv3
            ax.plot(lamda_k_a,K,'ro')
            ax.plot(lamda_k_b,K_cv1,'bx')
            st.text(f'The highest value to be used is K_cv3 = {K:0.3f}\n')
            return K, lamda_k_a, lamda_k_b, fig, ax
    else:
        st.text("Number of stiffeners not programmed into calculation")
        return None, lamda_k_a, lamda_k_b, None,None