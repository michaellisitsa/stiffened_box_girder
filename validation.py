import streamlit as st
from streamlit_drawable_canvas import st_canvas

import pandas as pd
import forallpeople as u
u.environment('structural')
from PIL import Image

def input_description(label):
    """Create Menu for user input includes
    'Write' - Custom text message
    'Draw' - Sketch field by Streamlit Component
    'Upload Image' - Insert a png, jpg, or jpeg image that is displayed
    """
    input_methods = ["Write","Draw","Upload image"]
    input_options = []
    #Load Images for input_description function
    
    @st.cache
    def load_image(image_file):
        """Display images using Pillow that 
        have been added via the streamlit file_uploader
        using the input_description function"""
        img = Image.open(image_file)
        return img
        
    with st.beta_expander(label):
        input_methods_cols = st.beta_columns(3)
        for ind,inputs in enumerate(input_methods):
            input_options.append(input_methods_cols[ind].checkbox(inputs))
        if input_options[0]:
            st.text_area("Write a description:",key="write_area")
        if input_options[1]:
            #Provide drawing canvas
            draw_cols = st.beta_columns(2)
            stroke_width = draw_cols[0].number_input("Stroke width: ", 1, 6, 3)
            stroke_color = draw_cols[1].color_picker("Stroke color: ")
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                update_streamlit=False,
                height=300,
                drawing_mode="freedraw",
                key="canvas")
        if input_options[2]:
            st.subheader("Custom image:")
            image_file = st.file_uploader("Upload Images",
                type=["png","jpg","jpeg"])
            if image_file is not None:
                st.image(load_image(image_file),use_column_width=True)