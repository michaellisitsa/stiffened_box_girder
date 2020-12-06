

import matplotlib.pyplot as plt

import numpy as np

import streamlit as st


#Import unit aware modules
import forallpeople as u
u.environment('structural')

def boxgenerator(b,d,t_w,t_f,d_stif,t_stif,n_stif):
    """
    This function allows for generation of a stiffened box section
    This only works with Pint units aware data in SI format at the moment.
    """
    import copy
    import sectionproperties.pre.sections as sections
    from sectionproperties.analysis.cross_section import CrossSection

    # Create the main box sections
    top_flange = sections.RectangularSection(d=t_f, b=b, shift=[0,d-t_f])
    bot_flange = sections.RectangularSection(d=t_f, b=b, shift=[0,0])
    left_web = sections.RectangularSection(d=d-2*t_f, b=t_w, shift=[0,t_f])
    right_web = sections.RectangularSection(d=d-2*t_f, b=t_w, shift=[b-t_w,t_f])

    if n_stif == 3:
        #Create top stiffeners
        top_stif1 = sections.RectangularSection(d=d_stif, b=t_stif, shift=[(b-t_stif)/2,d-t_f-d_stif])

        top_stif2 = copy.deepcopy(top_stif1)
        top_stif3 = copy.deepcopy(top_stif1)
        top_stif2.shift = [-b/4,0]
        top_stif3.shift = [b/4,0]
        top_stif2.shift_section()
        top_stif3.shift_section()

        #Create left stiffeners
        left_stif1 = sections.RectangularSection(d=t_stif, b=d_stif, shift=[t_w,(d-t_stif)/2])

        left_stif2 = copy.deepcopy(left_stif1)
        left_stif3 = copy.deepcopy(left_stif1)
        left_stif2.shift = [0,-d/4]
        left_stif3.shift = [0,d/4]
        left_stif2.shift_section()
        left_stif3.shift_section()

        #Create right stiffeners
        right_stif1 = copy.deepcopy(left_stif1)
        right_stif2 = copy.deepcopy(left_stif2)
        right_stif3 = copy.deepcopy(left_stif3)
        right_stif1.shift = [b-2*t_w-d_stif,0]
        right_stif2.shift = [b-2*t_w-d_stif,0]
        right_stif3.shift = [b-2*t_w-d_stif,0]
        right_stif1.shift_section()
        right_stif2.shift_section()
        right_stif3.shift_section()

        # create a list of the sections to be merged
        section_list = [top_flange, bot_flange, left_web, right_web, 
                        top_stif1,top_stif2,top_stif3,
                        left_stif1,left_stif2,left_stif3,
                    right_stif1,right_stif2,right_stif3]

    elif n_stif == 2:
        #Create top stiffeners
        top_stif1 = sections.RectangularSection(d=d_stif, b=t_stif, shift=[(b-t_stif)/3.0,d-t_f-d_stif])

        top_stif2 = copy.deepcopy(top_stif1)
        top_stif2.shift = [b/3,0]
        top_stif2.shift_section()

        #Create left stiffeners
        left_stif1 = sections.RectangularSection(d=t_stif, b=d_stif, shift=[t_w,(d-t_stif)/3])

        left_stif2 = copy.deepcopy(left_stif1)
        left_stif2.shift = [0,d/3]
        left_stif2.shift_section()

        #Create right stiffeners
        right_stif1 = copy.deepcopy(left_stif1)
        right_stif2 = copy.deepcopy(left_stif2)
        right_stif1.shift = [b-2*t_w-d_stif,0]
        right_stif2.shift = [b-2*t_w-d_stif,0]
        right_stif1.shift_section()
        right_stif2.shift_section()

        # create a list of the sections to be merged
        section_list = [top_flange, bot_flange, left_web, right_web, 
                        top_stif1,top_stif2,
                        left_stif1,left_stif2,
                    right_stif1,right_stif2]
    else:
        print("Number of stiffeners not supported")

    # merge the three sections into one geometry object
    geometry = sections.MergedSection(section_list)

    geometry.clean_geometry(verbose=False) # clean the geometry
    geometry.add_hole([b/2, d/2])
    fig,ax = plt.subplots()
    ax.set_aspect('equal')
    geometry.plot_geometry(ax=ax)  # plot the geometry

    # create a mesh - use a mesh size of 12 for the RHS, 6 for stiffeners
    rhs_mesh=d/6
    stif_mesh=t_stif
    
    if n_stif == 3:
        mesh = geometry.create_mesh(mesh_sizes=[rhs_mesh,rhs_mesh,rhs_mesh,rhs_mesh,
                                                stif_mesh,stif_mesh,stif_mesh,stif_mesh,
                                                stif_mesh,stif_mesh,stif_mesh,stif_mesh,stif_mesh])
    elif n_stif == 2:
        mesh = geometry.create_mesh(mesh_sizes=[rhs_mesh,rhs_mesh,rhs_mesh,rhs_mesh,
                                                stif_mesh,stif_mesh,stif_mesh,
                                                stif_mesh,stif_mesh,stif_mesh])
    else:
        print("Number of stiffeners not supported")

    section = CrossSection(geometry, mesh) # create a CrossSection object
    
    return section, fig, ax


def in_plane_principle(section,Fy,Fz,Mx,My,Mz):
    """
    Determine in plane stresses and output peak stresses
    """
    stress_post = section.calculate_stress(Vy = Fy,
                                        Vx = Fz,
                                        Mxx = Mz,
                                        Myy = My,
                                        Mzz = Mx)
    col1, col2 = st.beta_columns(2)
    col1.markdown("**Principle Stresses due to BM only**")
    stress_post.plot_stress_m_zz()
    # https://sectionproperties.readthedocs.io/en/latest/rst/api.html?highlight=m_zz#sectionproperties.analysis.cross_section.StressPost.plot_stress_m_zz
    col1.pyplot()
    col2.markdown("**Shear Stresses due to $F_y$ and $F_z$**")
    stress_post.plot_stress_v_zxy()
    # https://sectionproperties.readthedocs.io/en/latest/rst/api.html?highlight=v_zxy#sectionproperties.analysis.cross_section.StressPost.plot_vector_v_zxy
    col2.pyplot()
    stresses = stress_post.get_stress()
    f_star_s_comp = stresses[0]['sig_zz_m'].max() * u.N/u.m**2
    f_star_s_tens = stresses[0]['sig_zz_m'].min() * u.N/u.m**2
    st.text(f'The maximum comp/tension stresses in the section are:\n'
        f'f_star_s_comp = {f_star_s_comp.to(u.MPa)}\n'
        f'f_star_s_tens = {f_star_s_tens.to(u.MPa)}')
    
    return f_star_s_comp, f_star_s_tens, stresses

# Extract stress from the critical locations at the longitudinal flange stiffener
# Result type can only be max, min or mean
def stress_location(x_stif,y_stif,tol_x,tol_y,nodes_xy,stresses,result_type):
    output = []
    x = nodes_xy[:,0]
    y = nodes_xy[:,1]
    for x,y,stress in zip(x,y,stresses):
        if (x_stif - tol_x) <= x <= (x_stif + tol_x)  and (y_stif - tol_y) <= y <= (y_stif + tol_y):
            output.append(stress)
        else:
            pass
    if result_type == "max":
        return abs(max(output))
    elif result_type == "min":
        return abs(min(output))
    elif result_type == "mean":
        return abs(np.mean(output))

