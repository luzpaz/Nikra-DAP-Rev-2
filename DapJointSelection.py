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
import os
import DapTools
import pivy

import Part
import math

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True

JOINT_TYPES = ["Rotation", "Linear Movement"]
DEFINITION_MODES = [["1 Point + 2 Bodies", "alt def mode"], ["2 Points + 2 Bodies"]]
HELPER_TEXT = [
    [
        "Choose a point (by picking an LCS) and the two bodies attached to the point.",
        "Alternative Deifinition Mode Description",
    ],
    [
        "Choose two points (by picking two LCS's) and two bodies, (each point must be attached to its own body)"
    ],
]
YES_NO = ["No", "Yes"]
FUNCTION_TYPES = [
    "Not Applicable",
    "Function type 'a'",
    "Function type 'b'",
    "Function type 'c'",
]


#  -------------------------------------------------------------------------
def makeDapJoints(name="DapRelativeMovement"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapJoint(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapJoint(obj.ViewObject)
    return obj


# =============================================================================
class _CommandDapJoint:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon4.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Joint_alias", "Add New Relative Movement Between 2 Bodies"
            ),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Joint_alias", "Add a new relative movement between two bodies"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return DapTools.getActiveContainer() is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""
        if Debug:
            FreeCAD.Console.PrintMessage("Running Animation\n")

        """ """
        # FreeCAD.ActiveDocument.openTransaction("Create CfdFluidBoundary")
        # FreeCADGui.doCommand("")
        # FreeCADGui.addModule("CfdFluidBoundary")
        # FreeCADGui.addModule("DapTools")
        # FreeCADGui.doCommand("DapTools.getActiveContainer().addObject(CfdFluidBoundary.makeCfdFluidBoundary())")
        # FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        import DapTools
        import DapJointSelection

        DapTools.getActiveContainer().addObject(DapJointSelection.makeDapJoints())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


# =============================================================================
class _DapJoint:

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        obj.Proxy = self
        self.Type = "DapJoint"
        self.initProperties(obj)

    #  -------------------------------------------------------------------------
    def initProperties(self, obj):
        """ """
        # addObjectProperty(obj, 'References', [], "App::PropertyStringList", "", "List of Parts")
        all_subtypes = []
        for s in DEFINITION_MODES:
            all_subtypes += s
        DapTools.addObjectProperty(
            obj,
            "RelMovDefinitionMode",
            all_subtypes,
            "App::PropertyEnumeration",
            "",
            "Define the relative movement between 2 bodies",
        )
        DapTools.addObjectProperty(
            obj,
            "TypeOfRelMov",
            JOINT_TYPES,
            "App::PropertyEnumeration",
            "",
            "Type of Relative Movement",
        )
        DapTools.addObjectProperty(
            obj,
            "CoordPoint1RelMov",
            FreeCAD.Vector(0, 0, 0),
            "App::PropertyVector",
            "",
            "Point 1 used to define relative movement between 2 bodies",
        )
        DapTools.addObjectProperty(
            obj,
            "CoordPoint2RelMov",
            FreeCAD.Vector(0, 0, 0),
            "App::PropertyVector",
            "",
            "Point 2 used to define relative movement between 2 bodies",
        )
        DapTools.addObjectProperty(
            obj, "Body1", "Ground", "App::PropertyString", "", "Label: Body 1"
        )
        DapTools.addObjectProperty(
            obj, "Body2", "Ground", "App::PropertyString", "", "Label: Body 2"
        )
        DapTools.addObjectProperty(
            obj,
            "Point1RelMov",
            "",
            "App::PropertyString",
            "",
            "Label: Point 1 of Relative Movement",
        )
        DapTools.addObjectProperty(
            obj,
            "Point2RelMov",
            "",
            "App::PropertyString",
            "",
            "Label: Point 2 of Relative Movement",
        )
        DapTools.addObjectProperty(
            obj,
            "DriverOn",
            YES_NO,
            "App::PropertyEnumeration",
            "",
            "Is a 'driver' switched on to control the defined relative movement?",
        )
        DapTools.addObjectProperty(
            obj,
            "DriverFunctionType",
            FUNCTION_TYPES,
            "App::PropertyEnumeration",
            "",
            "Function type that the (switched on) 'driver' will use to control the defined relative movement.",
        )
        DapTools.addObjectProperty(
            obj,
            "tEndDriverFuncTypeA",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type A: End time (t_end)",
        )
        DapTools.addObjectProperty(
            obj,
            "coefC1DriverFuncTypeA",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type A: coefficient 'c_1'",
        )
        DapTools.addObjectProperty(
            obj,
            "coefC2DriverFuncTypeA",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type A: coefficient 'c_2'",
        )
        DapTools.addObjectProperty(
            obj,
            "coefC3DriverFuncTypeA",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type A: coefficient 'c_3'",
        )
        DapTools.addObjectProperty(
            obj,
            "tStartDriverFuncTypeB",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type B: Start time (t_start)",
        )
        DapTools.addObjectProperty(
            obj,
            "tEndDriverFuncTypeB",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type B: End time (t_end)",
        )
        DapTools.addObjectProperty(
            obj,
            "initialValueDriverFuncTypeB",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type B: initial function value",
        )
        DapTools.addObjectProperty(
            obj,
            "endValueDriverFuncTypeB",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type B: function value at t_end",
        )
        DapTools.addObjectProperty(
            obj,
            "tStartDriverFuncTypeC",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type C: Start time (t_start)",
        )
        DapTools.addObjectProperty(
            obj,
            "tEndDriverFuncTypeC",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type C: End time (t_end)",
        )
        DapTools.addObjectProperty(
            obj,
            "initialValueDriverFuncTypeC",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type C: initial function value",
        )
        DapTools.addObjectProperty(
            obj,
            "endDerivativeDriverFuncTypeC",
            "",
            "App::PropertyQuantity",
            "",
            "Driver Function Type C: function derivative at t_end",
        )
        # NOTE: hiding all properties that have anything to do with functions until the python code works
        obj.setEditorMode("DriverOn", 2)
        obj.setEditorMode("DriverFunctionType", 2)
        obj.setEditorMode("tEndDriverFuncTypeA", 2)
        obj.setEditorMode("coefC1DriverFuncTypeA", 2)
        obj.setEditorMode("coefC2DriverFuncTypeA", 2)
        obj.setEditorMode("coefC3DriverFuncTypeA", 2)
        obj.setEditorMode("tStartDriverFuncTypeB", 2)
        obj.setEditorMode("tEndDriverFuncTypeB", 2)
        obj.setEditorMode("initialValueDriverFuncTypeB", 2)
        obj.setEditorMode("endValueDriverFuncTypeB", 2)
        obj.setEditorMode("tStartDriverFuncTypeC", 2)
        obj.setEditorMode("tEndDriverFuncTypeC", 2)
        obj.setEditorMode("initialValueDriverFuncTypeC", 2)
        obj.setEditorMode("endDerivativeDriverFuncTypeC", 2)
        # obj.setEditorMode("DriverOn", 2)
        obj.tEndDriverFuncTypeA = FreeCAD.Units.Unit("")
        obj.coefC1DriverFuncTypeA = FreeCAD.Units.Unit("")
        obj.coefC2DriverFuncTypeA = FreeCAD.Units.Unit("")
        obj.coefC3DriverFuncTypeA = FreeCAD.Units.Unit("")
        obj.tStartDriverFuncTypeB = FreeCAD.Units.Unit("")
        obj.tEndDriverFuncTypeB = FreeCAD.Units.Unit("")
        obj.initialValueDriverFuncTypeB = FreeCAD.Units.Unit("")
        obj.endValueDriverFuncTypeB = FreeCAD.Units.Unit("")
        obj.tStartDriverFuncTypeC = FreeCAD.Units.Unit("")
        obj.tEndDriverFuncTypeC = FreeCAD.Units.Unit("")
        obj.initialValueDriverFuncTypeC = FreeCAD.Units.Unit("")
        obj.endDerivativeDriverFuncTypeC = FreeCAD.Units.Unit("")

    #  -------------------------------------------------------------------------
    def onDocumentRestored(self, obj):
        """ """
        self.initProperties(obj)

    #  -------------------------------------------------------------------------
    def execute(self, obj):
        """ """
        """ Create joint representation part at recompute. """
        # TODO visual representation of the joint should only be visible if the joint definition mode was correctly specified, e.g. rotation joint needs 1 point AND 2 separate bodies, translation joint needs 2 points AND 2 bodies
        doc_name = str(obj.Document.Name)
        doc = FreeCAD.getDocument(doc_name)
        #  if LCS positions were changed then the new coordinates should be calculated.
        #  this is a wasteful way of achieving this, since the objects coordinates are changed
        #  within the ui
        if obj.Point1RelMov != "":
            lcs_obj = doc.getObjectsByLabel(obj.Point1RelMov)[0]
            obj.CoordPoint1RelMov = lcs_obj.Placement.Base
        if obj.Point2RelMov != "":
            lcs_obj = doc.getObjectsByLabel(obj.Point2RelMov)[0]
            obj.CoordPoint2RelMov = lcs_obj.Placement.Base
        scale_param = 50000
        joint_index = DapTools.indexOrDefault(JOINT_TYPES, obj.TypeOfRelMov, 0)
        if joint_index == 0 and obj.Point1RelMov != "":
            vol_counter = 0
            vol = 0
            if obj.Body1 != "Ground":
                body1 = doc.getObjectsByLabel(obj.Body1)
                vol += body1[0].Shape.Volume
                vol_counter += 1
            if obj.Body2 != "Ground":
                body2 = doc.getObjectsByLabel(obj.Body2)
                vol += body2[0].Shape.Volume
                vol_counter += 1
            if vol_counter > 0:
                vol = vol / vol_counter
            else:
                vol = 100000
            scale_factor = vol / scale_param
            r1 = 7 * scale_factor
            r2 = scale_factor
            torus_dir = FreeCAD.Vector(0, 0, 1)
            torus = Part.makeTorus(
                r1, r2, obj.CoordPoint1RelMov, torus_dir, -180, 180, 240
            )
            cone1_pos = obj.CoordPoint1RelMov + FreeCAD.Vector(r1, -5 * r2, 0)
            cone1_dir = FreeCAD.Vector(0, 1, 0)
            cone1 = Part.makeCone(0, 2 * r2, 5 * r2, cone1_pos, cone1_dir)
            cone2_pos_x = (
                obj.CoordPoint1RelMov.x
                - r1 * math.cos(math.pi / 3)
                + 5 * r2 * math.cos(math.pi / 6)
            )
            cone2_pos_y = (
                obj.CoordPoint1RelMov.y
                - r1 * math.sin(math.pi / 3)
                - 5 * r2 * math.sin(math.pi / 6)
            )
            cone2_pos = FreeCAD.Vector(cone2_pos_x, cone2_pos_y, 0)
            cone2_dir = FreeCAD.Vector(-math.cos(math.pi / 6), math.sin(math.pi / 6), 0)
            cone2 = Part.makeCone(0, 2 * r2, 5 * r2, cone2_pos, cone2_dir)
            torus_w_arrows = Part.makeCompound([torus, cone1, cone2])
            obj.Shape = torus_w_arrows
            obj.ViewObject.ShapeColor = (
                1.0,
                0.843137264251709,
                0.0,
                0.6000000238418579,
            )
        elif joint_index == 1 and obj.Point1RelMov != "" and obj.Point2RelMov != "":
            llen = (obj.CoordPoint2RelMov - obj.CoordPoint1RelMov).Length
            if llen > 1e-6 and obj.Point1RelMov != "":
                lin_move_dir = (
                    obj.CoordPoint2RelMov - obj.CoordPoint1RelMov
                ).normalize()
                cylinder = Part.makeCylinder(
                    0.05 * llen,
                    0.5 * llen,
                    obj.CoordPoint1RelMov + 0.25 * llen * lin_move_dir,
                    lin_move_dir,
                )
                cone1 = Part.makeCone(
                    0, 0.1 * llen, 0.25 * llen, obj.CoordPoint1RelMov, lin_move_dir
                )
                cone2 = Part.makeCone(
                    0, 0.1 * llen, 0.25 * llen, obj.CoordPoint2RelMov, -lin_move_dir
                )
                double_arrow = Part.makeCompound([cylinder, cone1, cone2])
                obj.Shape = double_arrow
                obj.ViewObject.ShapeColor = (1.0, 0.0, 0.0, 0.0)
            else:
                # adding a checker to make sure the error does not come up when first instantiating a new undefined joint
                obj.Shape = Part.Shape()
                if obj.Point1RelMov != "" and obj.Point2RelMov != "":
                    FreeCAD.Console.PrintError(
                        "The selected 2 points either coincide, or are too close together!!!"
                    )
        else:
            obj.Shape = Part.Shape()

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        """ """
        return None


# =============================================================================
class _ViewProviderDapJoint:

    #  -------------------------------------------------------------------------
    def __init__(self, vobj):
        """ """
        vobj.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):
        """ """
        icon_path = os.path.join(DapTools.get_module_path(), "icons", "Icon4.png")
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
    def onChanged(self, vobj, prop):
        """ """
        # DapTools.setCompSolid(vobj)
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
        import _TaskPanelDapJoint

        taskd = _TaskPanelDapJoint.TaskPanelDapJoint(self.Object)
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
