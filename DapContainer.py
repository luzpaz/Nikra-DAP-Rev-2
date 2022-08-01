# ************************************************************************************
# *                                                                                  *
# *   Copyright (c) 2022 Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>            *
# *   Copyright (c) 2022 Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>   *
# *   Copyright (c) 2022 Dewald Hattingh (UP) <u17082006@tuks.co.za>                 *
# *   Copyright (c) 2022 Varnu Govender (UP) <govender.v@tuks.co.za>                 *
# *   Copyright (c) 2022 Cecil Churms <churms@gmail.com>                             *
# *                                                                                  *
# *   This program is free software; you can redistribute it and/or modify           *
# *   it under the terms of the GNU Lesser General Public License (LGPL)             *
# *   as published by the Free Software Foundation; either version 2 of              *
# *   the License, or (at your option) any later version.                            *
# *   for detail see the LICENCE text file.                                          *
# *                                                                                  *
# *   This program is distributed in the hope that it will be useful,                *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of                 *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  *
# *   GNU Library General Public License for more details.                           *
# *                                                                                  *
# *   You should have received a copy of the GNU Library General Public              *
# *   License along with this program; if not, write to the Free Software            *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307           *
# *   USA                                                                            *
# *_________________________________________________________________________________ *
# *                                                                                  *
# *     Nikra-DAP FreeCAD WorkBench (c) 2022:                                        *
# *        - Please refer to the Documentation and README                            *
# *          for more information regarding this WorkBench and its usage.            *
# *                                                                                  *
# *     Author(s) of this file:                                                      *
# *          Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>               *
# *          Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                        *
# *          Cecil Churms <churms@gmail.com>                                         *
# *                                                                                  *
# ************************************************************************************

import FreeCAD
import DapTools
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True


#  -----------------------------------------------------------------------------
def makeDapContainer(name):
    """Create Dap Container group object"""
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    _DapContainer(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapContainer(obj.ViewObject)
    return obj


# =============================================================================
class _DapContainer:
    """The Dap analysis group"""

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        obj.Proxy = self
        self.Type = "DapContainer"
        self.initProperties(obj)

    #  -------------------------------------------------------------------------
    def initProperties(self, obj):
        """ """
        # obj.addProperty("App::PropertyPath", "OutputPath")
        DapTools.addObjectProperty(
            obj,
            "OutputPath",
            "",
            "App::PropertyPath",
            "",
            "Path to which cases are written (blank to use system default)",
        )
        DapTools.addObjectProperty(
            obj,
            "IsActiveContainer",
            False,
            "App::PropertyBool",
            "",
            "Active analysis object in document",
        )
        obj.setEditorMode("IsActiveContainer", 1)  # Make read-only (2 = hidden)

    #  -------------------------------------------------------------------------
    def onDocumenRestored(self, obj):
        """ """
        self.initProperties(obj)


# =============================================================================
class _CommandDapContainer:
    """The Dap Container command definition"""

    #  -------------------------------------------------------------------------
    def __init__(self):
        """ """
        pass

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon2.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Container_alias", "New Dap Container"
            ),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Container_alias", "Creates a Dap solver container"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return FreeCAD.ActiveDocument is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Container command is run"""
        if Debug:
            FreeCAD.Console.PrintMessage("Running: Container\n")

        FreeCAD.ActiveDocument.openTransaction("Create Dap Container")
        FreeCADGui.doCommand("")
        # import DapContainer
        # import DapTools
        # analysis = DapContainer.makeDapContainer("DapContainer")
        FreeCADGui.addModule("DapContainer")
        FreeCADGui.addModule("DapTools")
        FreeCADGui.doCommand("analysis = DapContainer.makeDapContainer('DapContainer')")
        FreeCADGui.doCommand("DapTools.setActiveContainer(analysis)")
        # TODO add any other object creations that should happen by default when
        #  the workbench is initialised here


# =============================================================================
class _ViewProviderDapContainer:
    """A view provider for the DapContainer container object"""

    #  -------------------------------------------------------------------------
    def __init__(self, vobj):
        """ """
        vobj.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):
        """ """
        icon_path = icon_path = os.path.join(
            DapTools.get_module_path(), "icons", "Icon2.png"
        )
        return icon_path

    #  -------------------------------------------------------------------------
    def attach(self, vobj):
        """ """
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.bubbles = None

    #  -------------------------------------------------------------------------
    def updateData(self, obj, prop):
        """ """
        return

    #  -------------------------------------------------------------------------
    def onChanged(self, vobj, prop):
        """ """
        return

    #  -------------------------------------------------------------------------
    def doubleClicked(self, vobj):
        """ """
        if not DapTools.getActiveContainer() == self.Object:
            if FreeCADGui.activeWorkbench().name() != "DapWorkbench":
                FreeCADGui.activateWorkbench("DapWorkbench")
            DapTools.setActiveContainer(self.Object)
            return True
        return True

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        """ """
        return None
