# This contains functions needed for exporting and importing guide templates

import maya.mel as mel
import maya.cmds as cmds
import sys


# Guide Template' Directory
templates_Dir = '/Users/karlachang/Documents/Projects/karla_tools/clothingRigger/guide_templates'



def template_import(filename):
    '''
    Imports guide templates
    Args:
        filename (str): filename of the guide template
    '''

    # Get separator based on os
    platform = sys.platform
    sep = r'\\'
    if 'win32' not in platform:
        print ('Not windows OS')
        sep = '/'
    filepath = '{}{}{}'.format(templates_Dir, sep, filename)
    cmds.file(filepath, i=True)


def template_export(filename):
    '''
    Exports selected guides
    Args:
        filename: (string) name of file to be exported
    '''

    # get selected objects, make sure they are curves
    selection = get_selected_curves()
    cmds.select(selection)

    # Get separator based on os
    platform = sys.platform
    sep = r'\\'
    if 'win32' not in platform:
        print ('Not windows OS')
        sep = '/'

    filepath = '{}{}{}'.format(templates_Dir, sep, filename)
    cmds.file(filepath, force=True, exportSelected=True, type='mayaAscii' )

def get_selected_curves():
    '''
    Gets selected objects that are curves
    Returns:
        selected: (list) selected objects after checking they are curves
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
    if not selected:
        raise RuntimeError(
            "No valid objects selected. Please select guides to export.")
    return selected


def set_templates_Dir(path):
    '''
    Sets global variable 'templates_Dir' to given path
    Args:
        path(string): Directory where we want to export and import guide templates from
    '''
    global templates_Dir
    templates_Dir = path

def get_templates_Dir():
    '''
    Returns:
        templates_Dir(string): Directory where we want to export and import guide templates from
    '''
    return templates_Dir