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

@handcalc(override="long")
def longit_stif_spacing(b, d, n_stif):
    b_flange = b / (n_stif + 1) #spacing of longitudinal stiffeners in flange
    b_web = d / (n_stif + 1) #spacing of longitudinal stiffeners in web
    return b_flange, b_web