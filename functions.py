#Import streamlit
import streamlit as st

#Math and array modules
from math import sqrt, cos, sin, pi, atan
import numpy as np

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
