'''
Clothing Offset AutoRigger

This tool facilitates the process of creating Offset controls for our clothing rigs.
It uses guides to generate:
    - animation control curves
    - a duplicated structure that holds the bind joints and is driven by the control curves
The purpose of the duplicated structure is because we want the control curves to follow the character rig,
but we don't want to actually activate deformations since we layer the clothing deformations through blendshapes.

The tool uses the guides to create the controls structure.
This tool can import pre-made guides or the user can make new ones.
The user must manually parent the generated controls to follow the rig

Author: Karla Chang

How to run:
# run this part just once when you first open maya.
import sys
sys.path.append('C:\\your\\path\\to\\scripts')

## UI
import importlib
import ghostControlRigger.ghostControlRiggerUI as cRig
importlib.reload(cRig)
cRig.showUI()


'''

import sys
import importlib
import maya.cmds as cmds
import pymel.core as pm


from . import ghostControlRigger as r
importlib.reload(r)
from . import templates as t
importlib.reload(t)

import sys
import os

from vendor.Qt import QtWidgets, QtCore, QtGui
PLATFORM = sys.platform
if 'darwin' in PLATFORM:
    WINTYPE = QtCore.Qt.Tool
else:
    WINTYPE = QtCore.Qt.Window



def showUI():
    '''
    Main function you call to show the UI
    Args:
    Returns:
    '''

    if pm.cmds.window('ClothingRiggerUI', q=True, ex=True):
        pm.cmds.deleteUI('ClothingRiggerUI')

    win = ClothingRiggerUI()
    win.resize(400, 400)
    win = createMayaWindow(win)
    win.show()

class ClothingRiggerUI(QtWidgets.QWidget):

    def __init__(self):
        super(ClothingRiggerUI, self).__init__()

        self.buildUI()

        # setup main window
        self.setWindowTitle("Build Clothing Controls")
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.Window |
                            QtCore.Qt.WindowStaysOnTopHint |
                            WINTYPE)

    def buildUI(self):

        # layouts
        mainlayout = QtWidgets.QVBoxLayout()

        # guide creation layout
        createGuides_v_layout = QtWidgets.QVBoxLayout()
        setguidepath_h_layout = QtWidgets.QHBoxLayout()
        importexport_h_layout = QtWidgets.QHBoxLayout()

        # build controls Layout
        build_v_layout = QtWidgets.QVBoxLayout()
        buildbuttons_h_layout = QtWidgets.QHBoxLayout()

        # elements
        # guide creation elements
        createguidesLabel = QtWidgets.QLabel()
        createguidesLabel.setText('1. CREATE GUIDES')

        instructionsLabel = QtWidgets.QLabel()
        instructionsLabel.setText('Place your own curves to use as guides')
        orLabel = QtWidgets.QLabel()
        orLabel.setText('-OR-')
        importtemplateLabel = QtWidgets.QLabel()
        importtemplateLabel.setText('Import pre-made guides:')
        guide_path_field = QtWidgets.QLineEdit()
        set_guidepathBtn = QtWidgets.QPushButton('Set')

        guidestemplatesList = QtWidgets.QListWidget()
        importBtn = QtWidgets.QPushButton('Import Selected')
        exportBtn = QtWidgets.QPushButton('Export Selected as Template')
        guidecreationLine = QtWidgets.QFrame()
        guidecreationLine.setFrameShape(QtWidgets.QFrame.HLine)

        # build elements
        buildLabel = QtWidgets.QLabel()
        buildLabel.setText('2. BUILD CONTROLS')
        buildinstructionsLabel = QtWidgets.QLabel()
        buildinstructionsLabel.setText('Karla: select guides or build everything under guide group?')
        buildBtn = QtWidgets.QPushButton('Build')
        editBtn = QtWidgets.QPushButton('Edit Mode')
        exitEditBtn = QtWidgets.QPushButton('Exit Edit Mode')




        # add elements and layouts

        # guide section
        self.setLayout(mainlayout)

        mainlayout.addLayout(createGuides_v_layout)
        createGuides_v_layout.addWidget(createguidesLabel)
        createGuides_v_layout.addWidget(instructionsLabel)
        createGuides_v_layout.addWidget(orLabel)
        createGuides_v_layout.addLayout(setguidepath_h_layout)
        setguidepath_h_layout.addWidget(importtemplateLabel)
        setguidepath_h_layout.addWidget(guide_path_field)
        setguidepath_h_layout.addWidget(set_guidepathBtn)

        createGuides_v_layout.addWidget(guidestemplatesList)
        createGuides_v_layout.addLayout(importexport_h_layout)
        importexport_h_layout.addWidget(importBtn)
        importexport_h_layout.addWidget(exportBtn)
        createGuides_v_layout.addWidget(guidecreationLine)


        # build section
        mainlayout.addLayout(build_v_layout)
        build_v_layout.addWidget(buildLabel)
        build_v_layout.addWidget(buildinstructionsLabel)
        build_v_layout.addLayout(buildbuttons_h_layout)
        buildbuttons_h_layout.addWidget(buildBtn)
        buildbuttons_h_layout.addWidget(editBtn)
        buildbuttons_h_layout.addWidget(exitEditBtn)


        self.data = {
            'buttons': {
                'setGuidePath' : set_guidepathBtn,
                'importguides' : importBtn,
                'exportguides' : exportBtn,
                'build' : buildBtn,
                'editmode' : editBtn,
                'exiteditmode' : exitEditBtn
            },
            'lists':{
                'guidetemplates': guidestemplatesList
            },
            'layouts':{
                'guidesection': createGuides_v_layout,
                'importexport': importexport_h_layout,
                'buildsection': build_v_layout,
                'buildbuttons': buildbuttons_h_layout
            },
            'textfields':{
                'guidepath': guide_path_field
            }


        }

        # setup clicks
        self.initialState()
        self.setupSlots()

    def setButtonState_1(self):
        '''
        State of build & edit buttons when not in edit mode
        '''
        #self.data['buttons']['build'].setEnabled(False)
        self.data['buttons']['editmode'].setEnabled(True)
        self.data['buttons']['exiteditmode'].setEnabled(False)

    def setButtonState_2(self):
        '''
        State of build & edit buttons when in edit mode
        '''
        #self.data['buttons']['build'].setEnabled(True)
        self.data['buttons']['editmode'].setEnabled(False)
        self.data['buttons']['exiteditmode'].setEnabled(True)

    def build(self):
        '''
        Called when Build button is pressed
        '''

        # enable edit buttons and disable build

        self.setButtonState_1()
        self.data['buttons']['build'].setText('Rebuild')

        r.buildControls()


    def enterEditMode(self):
        '''
        Called when Edit Mode button is pressed
        '''
        self.setButtonState_2()
        r.editMode()

    def exitEditMode(self):
        '''
        Called when Edit Mode button is pressed
        '''
        self.setButtonState_1()
        r.exitEditMode()

    def setTemplatesDir(self):
        '''
        Called when set button is clicked
        Opens file dialog and sets returned path to guide template path
        '''


        # get default directory from guides.py
        defaultDir = t.get_templates_Dir()
        # use QFileDialog to open window to select a directory
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory", defaultDir)
        # set guide directory in guides.py
        t.set_templates_Dir(dir)

        # set the text box and templates list to match selected folder
        self.data['textfields']['guidepath'].setText(t.get_templates_Dir())
        self.data['textfields']['guidepath'].deselect()
        self.refreshInSceneList()

    def importGuides(self):
        '''
        Called when import button is clicked
        '''
        # Get selected item from list
        getSelectedItem = self.data['lists']['guidetemplates'].currentItem()
        if getSelectedItem is not None:
            template = getSelectedItem.text()
            t.template_import(template)

    def exportGuides(self):
        '''
        Called when export button is clicked
        '''

        # Get user input to name template
        input, ok = QtWidgets.QInputDialog.getText(self, "Set Template Name", "What is the name of this guide template?")
        if ok:
            filename = str(input)

        t.template_export(filename)
        self.refreshInSceneList()

    def getExistingTemplates(self):
        '''
        Looks in guide directory and returns a list of all items found in directory
        Returns:
            templates: (list) of all fbx items found in guides Dir
        '''
        templates = []
        path = t.get_templates_Dir()
        for file in os.listdir(path):
            #if file.endswith(".ma"):
            templates.append(file)


        return templates

    def refreshInSceneList(self):
        '''
        Refreshes the list existing guide templates
        '''

        # clear list
        self.data['lists']['guidetemplates'].clear()

        # get a list guide templates in above path
        templates = self.getExistingTemplates()

        if templates is not None and len(templates) > 0:
            for each in templates:
                self.data['lists']['guidetemplates'].addItem(each)


    def initialState(self):
        '''
        Sets initial states of UI buttons and populates Guide Template list
        '''
        self.refreshInSceneList()
        self.data['textfields']['guidepath'].setText(t.get_templates_Dir())
        self.data['textfields']['guidepath'].setReadOnly(True)

        # disable edit buttons
        self.data['buttons']['exiteditmode'].setEnabled(False)
        self.data['buttons']['editmode'].setEnabled(False)

        # if guide group isnt empty, enable edit button and disable Build button
        if cmds.objExists('guides'):
            if cmds.listRelatives('guides', c=1):
                self.data['buttons']['build'].setText('Rebuild')
                self.data['buttons']['editmode'].setEnabled(True)




    def setupSlots(self):
        '''
        Associates all of the UI clicks with their functions
        '''
        self.data['buttons']['setGuidePath'].clicked.connect(self.setTemplatesDir)

        self.data['buttons']['importguides'].clicked.connect(self.importGuides)
        self.data['buttons']['exportguides'].clicked.connect(self.exportGuides)
        self.data['buttons']['build'].clicked.connect(self.build)
        self.data['buttons']['editmode'].clicked.connect(self.enterEditMode)
        self.data['buttons']['exiteditmode'].clicked.connect(self.exitEditMode)


def createMayaWindow(widget, *args, **kwargs):
    """A safe way to parent a widget to a Maya window.

    Args:
        widget(QtWidgets.QWidget): A Qt widget to parent to a Maya window
    Returns:
        The new Maya window Qt object.
    """
    pmWin = pm.window(*args, **kwargs)
    win = pmWin.asQtObject()
    win.setObjectName('{0}Safe'.format(widget.objectName()))
    lay = win.layout()
    if not lay:
        lay = QtWidgets.QVBoxLayout(win)
    lay.addWidget(widget)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    title = widget.windowTitle()
    if title:
        win.setWindowTitle(title)
    icon = widget.windowIcon()
    if icon:
        win.setWindowIcon(icon)
    win.resize(widget.size())
    return win