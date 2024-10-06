import maya.cmds as cmds

# To do:
# Put check that guides have unique names from anything in scene. if so dont build and spit out warning message

all_guides_grp = 'guides'
all_w_grp = 'all_w_group'
all_controls_grp = 'clothing_controls'


def exitEditMode():
    cmds.hide(all_guides_grp)
    cmds.showHidden(all_w_grp)
    cmds.showHidden(all_controls_grp)


def editMode():
    cmds.showHidden(all_guides_grp)
    cmds.hide(all_w_grp)
    cmds.hide(all_controls_grp)


def setup():
    '''
    Makes empty groups to hold guides, controls and wcontrols
    '''

    # Create a group to hold all guides
    if not cmds.objExists(all_guides_grp):
        cmds.group(em=True, n=all_guides_grp)

    # Create a group to hold all w_controls
    if cmds.objExists(all_w_grp):
        cmds.delete(all_w_grp)
    cmds.group(em=True, n=all_w_grp)

    # Create a group to hold all controls
    if cmds.objExists(all_controls_grp):
        cmds.delete(all_controls_grp)
    cmds.group(em=True, n=all_controls_grp)


def buildControls():
    '''
    Makes anim controls, offset groups, joints, and all needed connections based on guides
    '''

    # if any objects are selected, parent then under the guides group. Make sure selected objects are curves


    selection = get_selected_curves()
    setup()
    if selection:
        topSelected = getTopNodes(selection)
        for each in topSelected:
                parent = cmds.listRelatives(each, p=True)
                if parent == None:
                    cmds.parent(each, all_guides_grp)
                elif parent[0] != all_guides_grp:
                    cmds.parent(each, all_guides_grp)

    # Get all objects under guides grp
    guides = []
    guides = cmds.listRelatives(all_guides_grp, ad=1, typ='transform')
    if not guides:
        raise RuntimeError("Please select some curve objects to make into clothing controls!")


    # make controls
    controls = makeControls(guides)
    # make wControls
    wcontrols = make_wControls(guides)
    connectControlsTojointDrivers(controls, wcontrols)

    # parent controls and wcontrols to groups

    # find top guide nodes and use them to get top control and wcontrol nodes
    guide_topNodes = getTopNodes(guides)
    for each in guide_topNodes:
        wctr_offset = each + '_ctr_w_Offset'
        cmds.parent(wctr_offset, all_w_grp)
        ctr_offset = each + '_ctr_Offset'
        cmds.parent(ctr_offset, all_controls_grp)


    # set group visibilities
    exitEditMode()


def connectControlsTojointDrivers(controls, wcontrols):
    '''
    Creates direct connections on translate, rotate, and scale between controls and 'w_controls' AND their Extra offset group
    '''

    for i in range(len(controls)):
        ctr = controls[i]
        extra_grp = cmds.listRelatives(ctr, p=1)
        wctr = wcontrols[i]
        w_extra_grp = cmds.listRelatives(wctr, p=1)

        cmds.connectAttr(str(ctr) + '.t', wctr + '.t')
        cmds.connectAttr(str(ctr) + '.r', wctr + '.r')
        cmds.connectAttr(str(ctr) + '.s', wctr + '.s')

        cmds.connectAttr(str(extra_grp[0]) + '.t', w_extra_grp[0] + '.t')
        cmds.connectAttr(str(extra_grp[0]) + '.r', w_extra_grp[0] + '.r')
        cmds.connectAttr(str(extra_grp[0]) + '.s', w_extra_grp[0] + '.s')


def createJoints(objects):
    '''
    Creates a joint at each given object and parents it to that object
    '''

    for each in objects:
        joint = str(each).replace('ctr_w', 'jnt')
        cmds.joint(n=joint)
        cmds.matchTransform(joint, each)
        cmds.parent(joint, each)


def makeControls(guides):
    '''
    Creates the anim controls and their offset groups
    Args:
        guides: (list) guides determine location and hierarchy of controls
    Returns:
        controls: (list) list of control names
    '''

    controls = []
    extra_grps = []
    offset_grps = []

    for guide in guides:
        name = str(guide)
        control = str(name) + '_ctr'

        # Create control
        cmds.circle(n=control)
        # Create offset groups
        extra_grp = control + '_Extra'
        top_grp = control + '_Offset'

        cmds.group(em=True, n=extra_grp)
        cmds.group(em=True, n=top_grp)
        # Move offset grps to match control location
        cmds.parent(control, extra_grp)
        cmds.parent(extra_grp, top_grp)
        cmds.matchTransform(top_grp, guide)
        controls.append(control)
        extra_grps.append(extra_grp)
        offset_grps.append(top_grp)


    # Copy over shape nodes
    for i in range(len(guides)):
        # Duplicate guide
        guide = guides[i]
        shapeTransform = cmds.duplicate(guide, renameChildren=1)[0]
        # Get shape nodes
        shape_node = cmds.listRelatives(shapeTransform, c=True, s=True, pa=True)[0]
        # Get circle shape node
        old_shape_node = cmds.listRelatives(controls[i], c=True, s=True, pa=True)
        cmds.delete(old_shape_node)
        # Parent duplicate guide shape to control transform
        cmds.parent(shape_node, controls[i], s=True, r=True)
        print(shape_node)
        print(old_shape_node[0])
        #cmds.rename(shape_node, str(old_shape_node[0]))
        cmds.delete(shapeTransform)

    # Match parenting structure
    for i in range(len(guides)):
        # Find corresponding control offset group
        offset_grp = str(controls[i]) + '_Offset'
        # Find guide parent
        guide_parent = cmds.listRelatives(guides[i], p=True)
        if guide_parent:
            if guide_parent == all_guides_grp:
                continue
            control_parent = str(guide_parent[0]) + '_ctr'
            if cmds.objExists(control_parent):
                cmds.parent(offset_grp, control_parent)



    return controls


def make_wControls(guides):
    '''
    Creates "w_Controls" which are just the same as the controls
    but they have joints parented under them, no shape node and are directly connected to anim controls.
    Args:
        guides: (list) guides determine location and hierarchy of controls
    Returns:
        wcontrols: (list) list of wcontrol names
    '''

    wcontrols = []
    extra_grps = []
    offset_grps = []
    suffix = '_w'

    for guide in guides:
        name = str(guide)
        control = str(name) + '_ctr' + suffix

        # Create control
        cmds.circle(n=control)
        # Create offset groups
        extra_grp = control + '_Extra'
        top_grp = control + '_Offset'

        cmds.group(em=True, n=extra_grp)
        cmds.group(em=True, n=top_grp)
        # Move offset grps to match control location
        cmds.parent(control, extra_grp)
        cmds.parent(extra_grp, top_grp)
        cmds.matchTransform(top_grp, guide)
        wcontrols.append(control)
        extra_grps.append(extra_grp)
        offset_grps.append(top_grp)

    # Match parenting structure
    for i in range(len(guides)):
        # Find corresponding control offset group
        offset_grp = str(wcontrols[i]) + '_Offset'
        # Find guide parent
        guide_parent = cmds.listRelatives(guides[i], p=True)
        if guide_parent:
            if guide_parent == all_guides_grp:
                continue
            control_parent = str(guide_parent[0]) + '_ctr' + suffix
            if cmds.objExists(control_parent):
                cmds.parent(offset_grp, control_parent)

    for i in range(len(wcontrols)):
        # Delete circle shape node
        shape_node = cmds.listRelatives(wcontrols[i], c=True, s=True, pa=True)
        cmds.delete(shape_node)

    # Create joints
    createJoints(wcontrols)
    return wcontrols

def getTopNodes(objects):
    '''
    Gets the top nodes from given objects. Each selection is a top node unless it's parent is also selected, then just the parent is the top node
    Args:
        objects: (list) given maya objects
    Returns:
        topNodes: (list) list of all the top nodes selected of their own hierarchies
    '''

    topNodes = []
    for each in objects:
        parents = cmds.listRelatives(each, allParents=1, pa=1, type='transform')

        # does it have a parent that isn't world?
        if parents:
            # is its parent also in selection?
            if (common_data(parents, objects)):
                print('parent in selection. Skipping :' + str(each))
                continue

            else:
                print('Parent not in selection. Adding: ' + str(each))
                topNodes.append(each)
        # no parent
        else:
            # skip if its already in topNodes
            if (each in topNodes):
                continue
            else:
                topNodes.append(each)
    return topNodes


def common_data(list1, list2):
    '''
    Function to check if two lists have at least one common element
    '''

    result = False

    # traverse in the 1st list
    for x in list1:

        # traverse in the 2nd list
        for y in list2:

            # if one common
            if x == y:
                result = True
                return result

    return result

def get_selected_curves():
    '''
    Gets selected objects that are NurbsCurves transform nodes
    Returns:
        selected: selected objects after checking they are curves
    '''

    selected = []
    sel = cmds.ls(sl=1)
    if sel:
        for each in sel:

            children = cmds.listRelatives(each, children=True, s=1, fullPath=1) or []
            if children:
                # take the first child
                child = children[0]
                objType = cmds.objectType(child)

                if objType == 'nurbsCurve':
                    selected.append(each)
                else:
                    print('Selected object not curve. Skipping: ' + str(each))
    return selected
