

import matplotlib.pyplot as plt

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
    rhs_mesh=d/15
    stif_mesh=t_stif/2
    
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