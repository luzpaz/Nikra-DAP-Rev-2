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
# *          Dewald Hattingh (UP) <u17082006@tuks.co.za>                             *
# *          Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                        *
# *          Cecil Churms <churms@gmail.com>                                         *
# *                                                                                  *
# ************************************************************************************

import FreeCAD
import os
import DapTools
import pivy
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True

MOTION_PLANES = ["X-Y Plane", "Y-Z Plane", "X-Z Plane", "Custom Plane..."]
MOTION_PLANES_HELPER_TEXT = [
    "Planar Motion is in XY Plane",
    "Planar Motion is in YZ Plane",
    "Planar Motion is in XZ Plane",
    "User-defined Plane",
]
SELECTION_TYPE = [
    "Normal Vector Definition",
    "Object Selection",
]
SELECTION_TYPE_HELPER_TEXT = [
    "Define the normal vector of the plane of motion",
    "Experimental: select object entities to define plane of motion. \
                              Valid selections include a plane, a face or a sketch.",
]


#  -------------------------------------------------------------------------
def makeDapSolver(name="DapSolver"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapSolver(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapSolver(obj.ViewObject)
    return obj


# =============================================================================
class _CommandDapSolver:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon7.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Solver_alias", "Run the analysis"
            ),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Solver_alias", "Run the analysis."
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return DapTools.getActiveContainer() is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Solver command is run"""

        if Debug:
            FreeCAD.Console.PrintMessage("Running: Solver\n")

        import DapTools
        import DapSolverRunner

        solverObject = DapTools.getSolverObject()
        if solverObject == None:
            DapTools.getActiveContainer().addObject(DapSolverRunner.makeDapSolver())
            FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        else:
            FreeCADGui.ActiveDocument.setEdit(solverObject.Name)


# =============================================================================
class _DapSolver:

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapSolver"

    #  -------------------------------------------------------------------------
    def initProperties(self, obj):
        """ """
        DapTools.addObjectProperty(
            obj, "XVector", 0.0, "App::PropertyFloat", "", "Vector in X-Direction"
        )
        DapTools.addObjectProperty(
            obj, "YVector", 0.0, "App::PropertyFloat", "", "Vector in Y-Direction"
        )
        DapTools.addObjectProperty(
            obj, "ZVector", 0.0, "App::PropertyFloat", "", "Vector in Z-Direction"
        )
        DapTools.addObjectProperty(
            obj,
            "FileDirectory",
            "",
            "App::PropertyString",
            "",
            "Location where Solver Results will be Stored",
        )
        DapTools.addObjectProperty(
            obj,
            "MotionPlane",
            MOTION_PLANES,
            "App::PropertyEnumeration",
            "",
            "Plane of Motion",
        )
        DapTools.addObjectProperty(
            obj,
            "SelectionType",
            SELECTION_TYPE,
            "App::PropertyEnumeration",
            "",
            "Type of Custom Plane Selection",
        )
        # DapTools.addObjectProperty(obj, 'ObjectEntities', [], "App::PropertyStringList", "", "Objects used for Plane Definition")
        DapTools.addObjectProperty(
            obj,
            "PlaneObjectName",
            "",
            "App::PropertyString",
            "",
            "Name of object to create custom plane of motion",
        )
        DapTools.addObjectProperty(
            obj, "StartTime", 0.0, "App::PropertyFloat", "", "Start Time"
        )
        DapTools.addObjectProperty(
            obj, "EndTime", 0.5, "App::PropertyFloat", "", "Start Time"
        )
        DapTools.addObjectProperty(
            obj,
            "ReportingTimeStep",
            0.01,
            "App::PropertyFloat",
            "",
            "Time intervals for the solution",
        )
        DapTools.addObjectProperty(
            obj,
            "UnitVector",
            FreeCAD.Vector(0, 0, 0),
            "App::PropertyVector",
            "",
            "Vector Normal to Planar Motion",
        )
        DapTools.addObjectProperty(
            obj, "DapResults", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "ReportedTimes", None, "App::PropertyPythonObject", "", ""
        )
        # DapTools.addObjectProperty(obj, 'BodiesCoG', None, "App::PropertyPythonObject", "", "")
        DapTools.addObjectProperty(
            obj, "Bodies_r", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Bodies_p", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Points_r", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Points_r_d", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Bodies_p_d", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Bodies_r_d", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Bodies_p_d_d", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "Bodies_r_d_d", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "kinetic_energy", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "potential_energy", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj, "total_energy", None, "App::PropertyPythonObject", "", ""
        )
        DapTools.addObjectProperty(
            obj,
            "object_to_point",
            {},
            "App::PropertyPythonObject",
            "",
            "Dictionary linking FC object (eg joint) to DAP point, required for postProcessing",
        )
        DapTools.addObjectProperty(
            obj,
            "object_to_moving_body",
            {},
            "App::PropertyPythonObject",
            "",
            "Dictionary linking FC object to DAP body, required for postProcessing (only moving bodies used)",
        )
        DapTools.addObjectProperty(
            obj,
            "global_rotation_matrix",
            FreeCAD.Matrix(),
            "App::PropertyMatrix",
            "",
            "Global orthonormal rotation matrix",
        )
        return

    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, obj):
        """ """
        self.initProperties(obj)

    #  -------------------------------------------------------------------------
    def execute(self, obj):
        """ """
        """ Create joint representation part at recompute. """

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def onChanged(self, obj, prop):
        """ """
        standard_planes = ["X-Y Plane", "Y-Z Plane", "X-Z Plane"]
        if prop == "FileDirectory":
            if obj.FileDirectory == "":
                obj.FileDirectory = os.getcwd()
        if prop == "MotionPlane":
            if obj.MotionPlane in standard_planes:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("SelectionType", 2)
                    obj.setEditorMode("UnitVector", 1)
                if obj.MotionPlane == "X-Y Plane":
                    obj.XVector = 0.0
                    obj.YVector = 0.0
                    obj.ZVector = 1.0
                elif obj.MotionPlane == "Y-Z Plane":
                    obj.XVector = 1.0
                    obj.YVector = 0.0
                    obj.ZVector = 0.0
                else:
                    obj.XVector = 0.0
                    obj.YVector = 1.0
                    obj.ZVector = 0.0
            else:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("SelectionType", 0)
                    obj.setEditorMode("UnitVector", 1)
            if (obj.XVector != 0) or (obj.YVector != 0) or (obj.ZVector != 0):
                mag = (obj.XVector ** 2 + obj.YVector ** 2 + obj.ZVector ** 2) ** 0.5
                rounder = 3
                obj.UnitVector = FreeCAD.Vector(
                    round(obj.XVector / mag, rounder),
                    round(obj.YVector / mag, rounder),
                    round(obj.ZVector / mag, rounder),
                )
        if prop == "SelectionType":
            if obj.SelectionType == "Object Selection":
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 2)
                    obj.setEditorMode("YVector", 2)
                    obj.setEditorMode("ZVector", 2)
                    obj.setEditorMode("UnitVector", 1)
                # insert code here to determine the positioning of the vector normal to the selection
            else:
                if hasattr(obj, "XVector"):
                    obj.setEditorMode("XVector", 0)
                    obj.setEditorMode("YVector", 0)
                    obj.setEditorMode("ZVector", 0)
                    obj.setEditorMode("UnitVector", 1)
        if (
            hasattr(obj, "XVector")
            and hasattr(obj, "YVector")
            and hasattr(obj, "ZVector")
        ):
            if prop == "XVector" or prop == "YVector" or prop == "ZVector":
                if (obj.XVector != 0) or (obj.YVector != 0) or (obj.ZVector != 0):
                    mag = (
                        obj.XVector ** 2 + obj.YVector ** 2 + obj.ZVector ** 2
                    ) ** 0.5
                    rounder = 3
                    obj.UnitVector = FreeCAD.Vector(
                        round(obj.XVector / mag, rounder),
                        round(obj.YVector / mag, rounder),
                        round(obj.ZVector / mag, rounder),
                    )

    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        """ """
        return None


# =============================================================================
class _ViewProviderDapSolver:

    #  -------------------------------------------------------------------------
    def __init__(self, vobj):
        """ """
        vobj.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):
        """ """
        icon_path = os.path.join(DapTools.get_module_path(), "icons", "Icon7.png")
        return icon_path

    #  -------------------------------------------------------------------------
    def attach(self, vobj):
        """ """
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = pivy.coin.SoGroup()
        vobj.addDisplayMode(self.standard, "Standard")
        # self.ViewObject.Transparency = 95
        return

    #  -------------------------------------------------------------------------
    def getDisplayModes(self, obj):
        """ """
        modes = []
        return modes

    #  -------------------------------------------------------------------------
    def getDefaultDisplayMode(self):
        """ """
        return "Shaded"

    #  -------------------------------------------------------------------------
    def setDisplayMode(self, mode):
        """ """
        return mode

    #  -------------------------------------------------------------------------
    def updateData(self, obj, prop):
        """ """
        return

    #  -------------------------------------------------------------------------
    def doubleClicked(self, vobj):
        """ """
        doc = FreeCADGui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            FreeCAD.Console.PrintError("Task dialog already active\n")
        return True

    #  -------------------------------------------------------------------------
    def setEdit(self, vobj, mode):
        """ """
        import _TaskPanelDapSolver

        taskd = _TaskPanelDapSolver.TaskPanelDapSolver(self.Object)
        FreeCADGui.Control.showDialog(taskd)
        return True

    #  -------------------------------------------------------------------------
    def unsetEdit(self, vobj, mode):
        """ """
        FreeCADGui.Control.closeDialog()
        return

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        """ """
        return None
