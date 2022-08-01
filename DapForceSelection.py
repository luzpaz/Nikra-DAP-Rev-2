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
# *          Varnu Govender (UP) <govender.v@tuks.co.za>                             *
# *          Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                        *
# *          Cecil Churms <churms@gmail.com>                                         *
# *                                                                                  *
# ************************************************************************************

# from unicodedata import name
import FreeCAD
import math
import os
import DapTools
import _DapBodySelector
import pivy
import Part

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True

FORCE_TYPES = [
    "Gravity",
    "Spring",
    "Linear Spring Damper",
    "Rotational Spring",
    "Rotational Spring Damper",
]
FORCE_TYPE_HELPER_TEXT = [
    "Universal force of attraction between all matter",
    "Linear Spring connecting two points with stiffness and undeformed length",
    "A device used to limit or retard vibration ",
    "Device that stores energy when twisted and exerts a toraue in the opposite direction",
    "Device used to limit movement and vibration through continuous rotation",
]
# container


#  -------------------------------------------------------------------------
def makeDapForce(name="DapForce"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapForce(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapForce(obj.ViewObject)
    return obj


# =============================================================================
class _CommandDapForce:
    """Basic building block of the FreeCAD interface. They appear as a button on the FreeCAD interface, and as a menu entry in menus"""

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon6.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP("Dap_Force_alias", "Add Force"),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Force_alias", "Creates and defines a force for the DAP analysis"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return DapTools.getActiveContainer() is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Force Selection command is run"""
        if Debug:
            FreeCAD.Console.PrintMessage("Running: Force Selection\n")

        # FreeCAD.ActiveDocument.openTransaction("Create CfdFluidBoundary")
        # FreeCADGui.doCommand("")
        # FreeCADGui.addModule("CfdFluidBoundary")
        # FreeCADGui.addModule("DapTools")
        # FreeCADGui.doCommand("DapTools.getActiveContainer().addObject(CfdFluidBoundary.makeCfdFluidBoundary())")
        # FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        import DapTools
        import DapForceSelection

        DapTools.getActiveContainer().addObject(DapForceSelection.makeDapForce())
        FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)


# =============================================================================
class _DapForce:

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        self.initProperties(obj)
        obj.Proxy = self
        self.Type = "DapForce"

    #  -------------------------------------------------------------------------
    def initProperties(self, obj):
        """ """
        DapTools.addObjectProperty(
            obj,
            "ForceTypes",
            FORCE_TYPES,
            "App::PropertyEnumeration",
            "",
            "Types of Forces",
        )
        DapTools.addObjectProperty(
            obj, "gx", "", "App::PropertyAcceleration", "", "X Component"
        )
        DapTools.addObjectProperty(
            obj, "gy", "-9.81 m/s^2", "App::PropertyAcceleration", "", "Y Component"
        )
        DapTools.addObjectProperty(
            obj, "gz", "", "App::PropertyAcceleration", "", "Z Component"
        )
        DapTools.addObjectProperty(
            obj, "Stiffness", "", "App::PropertyQuantity", "", "Linear Spring Stiffness"
        )
        DapTools.addObjectProperty(
            obj,
            "RotStiffness",
            "",
            "App::PropertyQuantity",
            "",
            "Rotational Spring Stiffness",
        )
        DapTools.addObjectProperty(
            obj,
            "LinDampCoeff",
            "",
            "App::PropertyQuantity",
            "",
            "Linear damping coefficient",
        )
        DapTools.addObjectProperty(
            obj,
            "RotDampCoeff",
            "",
            "App::PropertyQuantity",
            "",
            "Rotational damping coefficient",
        )
        DapTools.addObjectProperty(
            obj,
            "UndeformedLength",
            "",
            "App::PropertyLength",
            "",
            "Linear undeformed Length",
        )
        DapTools.addObjectProperty(
            obj, "UndeformedAngle", "", "App::PropertyAngle", "", "Undeformed angle"
        )
        DapTools.addObjectProperty(
            obj, "Body1", "Ground", "App::PropertyString", "", "Body 1 label"
        )
        DapTools.addObjectProperty(
            obj, "Body2", "Ground", "App::PropertyString", "", "Body 2 label"
        )
        DapTools.addObjectProperty(
            obj, "Joint1", "", "App::PropertyString", "", "Joint 1 label"
        )
        DapTools.addObjectProperty(
            obj, "Joint2", "", "App::PropertyString", "", "Joint 2 label"
        )
        DapTools.addObjectProperty(
            obj,
            "DampCondition",
            "",
            "App::PropertyString",
            "",
            "Displays the damping condition",
        )
        DapTools.addObjectProperty(
            obj,
            "JointCoord1",
            FreeCAD.Vector(0, 0, 0),
            "App::PropertyVector",
            "",
            "Vector to display joint visualisation",
        )
        DapTools.addObjectProperty(
            obj,
            "JointCoord2",
            FreeCAD.Vector(0, 0, 0),
            "App::PropertyVector",
            "",
            "Vector to display joint visualisation",
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
        DapTools.addObjectProperty(obj, "Checker", False, "App::PropertyBool", "", "")
        DapTools.addObjectProperty(obj, "a_Checker", False, "App::PropertyBool", "", "")
        DapTools.addObjectProperty(obj, "b_Checker", False, "App::PropertyBool", "", "")
        DapTools.addObjectProperty(obj, "c_Checker", False, "App::PropertyBool", "", "")
        obj.setEditorMode("Checker", 2)
        obj.setEditorMode("a_Checker", 2)
        obj.setEditorMode("b_Checker", 2)
        obj.setEditorMode("c_Checker", 2)
        obj.Stiffness = FreeCAD.Units.Unit("kg/s^2")
        obj.RotStiffness = FreeCAD.Units.Unit("N*m/rad")
        obj.LinDampCoeff = FreeCAD.Units.Unit("kg/s")
        obj.RotDampCoeff = FreeCAD.Units.Unit("(J*s)/rad")
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
        """ Create compound part at recompute. """
        #  if LCS positions were changed then the new coordinates should be calculated.
        #  this is a wasteful way of achieving this, since the objects coordinates are changed
        #  within the ui
        doc_name = str(obj.Document.Name)
        doc = FreeCAD.getDocument(doc_name)
        if obj.Joint1 != "":
            lcs_obj = doc.getObjectsByLabel(obj.Joint1)[0]
            obj.JointCoord1 = lcs_obj.Placement.Base
        if obj.Joint2 != "":
            lcs_obj = doc.getObjectsByLabel(obj.Joint2)[0]
            obj.JointCoord2 = lcs_obj.Placement.Base
        if obj.ForceTypes == "Spring" or obj.ForceTypes == "Linear Spring Damper":
            h = (obj.JointCoord1 - obj.JointCoord2).Length
            p = h / 10
            r = h / 10
            #  r_1 = r/(h+0.0001)
            r_1 = h / 150  # Assigned but never used
            creation_axis = FreeCAD.Vector(0, 0, 1)
            desired_direction = obj.JointCoord2 - obj.JointCoord1
            if h > 0:
                desired_direction = desired_direction.normalize()
                angle = degrees(math.acos(desired_direction * creation_axis))
                axis = creation_axis.cross(desired_direction)
                helix = Part.makeHelix(p, h, r)
                #  circle = Part.makeCircle(r_1, FreeCAD.Base.Vector(r, 0, 0), FreeCAD.Base.Vector(0,1, 0))
                #  circle = Part.Wire([circle])
                #  pipe = Part.Wire(helix).makePipe(circle)
                #  obj.Shape = pipe
                obj.Shape = helix
                if obj.ForceTypes == "Spring":
                    obj.ViewObject.LineColor = 0.0, 0.0, 0.0, 0.0
                elif obj.ForceTypes == "Linear Spring Damper":
                    obj.ViewObject.LineColor = 0.0, 250.0, 20.0, 0.0
                # First reset the placement in case multiple recomputes are performed
                obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
                obj.Placement.Rotation = FreeCAD.Rotation(0, 0, 0, 1)
                obj.Placement.rotate(FreeCAD.Vector(0, 0, 0), axis, angle)
                obj.Placement.translate(obj.JointCoord1)
            else:
                obj.Shape = Part.Shape()
        elif (
            obj.ForceTypes == "Rotational Spring"
            or obj.ForceTypes == "Rotational Spring Damper"
        ):
            doc_name = str(obj.Document.Name)
            doc = FreeCAD.getDocument(doc_name)
            vol1 = 0
            vol2 = 0
            if obj.Body1 != "Ground":
                vol1 = doc.getObjectsByLabel(obj.Body1)[0].Shape.Volume
            if obj.Body2 != "Ground":
                vol2 = doc.getObjectsByLabel(obj.Body2)[0].Shape.Volume
            if vol1 + vol2 == 0:
                vol1 = 100000
            scale = (vol1 + vol2) / 30000
            r = 2 * scale
            g = r / 2
            r_ = 4
            t = r / 10  # Assigned but never used
            doc_name = str(obj.Document.Name)
            document = FreeCAD.getDocument(doc_name)
            spiral = document.addObject("Part::Spiral", "Spiral")
            spiral.Growth = g
            spiral.Radius = r
            spiral.Rotations = r_
            spiral.Placement.Base = FreeCAD.Vector(0, 0, 0)
            spiral = document.getObject("Spiral").Shape
            #  circle = Part.makeCircle(t, FreeCAD.Base.Vector(r, 0, 0), FreeCAD.Base.Vector(0,1, 0))
            #  circle = Part.Wire([circle])
            #  pipe = Part.Wire(spiral)
            #  pipe = pipe.makePipe(circle)
            obj.Shape = spiral
            if obj.ForceTypes == "Rotational Spring":
                obj.ViewObject.LineColor = 0.0, 0.0, 0.0, 0.0
            elif obj.ForceTypes == "Rotational Spring Damper":
                obj.ViewObject.LineColor = 0.0, 250.0, 20.0, 0.0
            obj.Placement.Base = obj.JointCoord1
            document.removeObject("Spiral")
        else:
            obj.Shape = Part.Shape()
        return None

    #  -------------------------------------------------------------------------
    def __getstate__(self):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def __setstate__(self, state):
        """ """
        return None

    #  -------------------------------------------------------------------------
    def onChanged(self, obj, prop):
        """ """
        #  The property editor for all Type Cases has been added in _DapForceDriver.py.
        #  Only if form.driveCheck is checked will all Driver properties be hidden here
        if prop == "ForceTypes":
            #  FreeCAD.Console.PrintError('This is working')
            self.lstMultiGrav = []
            if obj.ForceTypes == "Gravity":
                obj.setEditorMode("gx", 0)
                obj.setEditorMode("gy", 0)
                obj.setEditorMode("gz", 0)
                obj.setEditorMode("Stiffness", 2)
                obj.setEditorMode("UndeformedLength", 2)
                obj.setEditorMode("Body1", 2)
                obj.setEditorMode("Body2", 2)
                obj.setEditorMode("Joint1", 2)
                obj.setEditorMode("Joint2", 2)
                obj.setEditorMode("RotStiffness", 2)
                obj.setEditorMode("LinDampCoeff", 2)
                obj.setEditorMode("UndeformedAngle", 2)
                obj.setEditorMode("RotDampCoeff", 2)
                obj.setEditorMode("Joint2", 2)
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
            elif obj.ForceTypes == "Spring":
                obj.setEditorMode("gx", 2)
                obj.setEditorMode("gy", 2)
                obj.setEditorMode("gz", 2)
                obj.setEditorMode("Stiffness", 0)
                obj.setEditorMode("UndeformedLength", 0)
                obj.setEditorMode("RotStiffness", 2)
                obj.setEditorMode("LinDampCoeff", 2)
                obj.setEditorMode("UndeformedAngle", 2)
                obj.setEditorMode("RotDampCoeff", 2)
                obj.setEditorMode("Body1", 0)
                obj.setEditorMode("Body2", 0)
                obj.setEditorMode("Joint1", 0)
                obj.setEditorMode("Joint2", 0)
                if obj.Checker == False:
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
            elif obj.ForceTypes == "Linear Spring Damper":
                obj.setEditorMode("gx", 2)
                obj.setEditorMode("gy", 2)
                obj.setEditorMode("gz", 2)
                obj.setEditorMode("Stiffness", 0)
                obj.setEditorMode("UndeformedLength", 2)
                obj.setEditorMode("RotStiffness", 2)
                obj.setEditorMode("LinDampCoeff", 0)
                obj.setEditorMode("UndeformedAngle", 2)
                obj.setEditorMode("RotDampCoeff", 2)
                obj.setEditorMode("Body1", 0)
                obj.setEditorMode("Body2", 0)
                obj.setEditorMode("Joint1", 0)
                obj.setEditorMode("Joint2", 0)
                if obj.Checker == False:
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
            elif obj.ForceTypes == "Rotational Spring":
                obj.setEditorMode("gx", 2)
                obj.setEditorMode("gy", 2)
                obj.setEditorMode("gz", 2)
                obj.setEditorMode("Stiffness", 2)
                obj.setEditorMode("UndeformedLength", 2)
                obj.setEditorMode("RotStiffness", 0)
                obj.setEditorMode("LinDampCoeff", 2)
                obj.setEditorMode("UndeformedAngle", 0)
                obj.setEditorMode("RotDampCoeff", 2)
                obj.setEditorMode("Body1", 0)
                obj.setEditorMode("Body2", 0)
                obj.setEditorMode("Joint1", 0)
                obj.setEditorMode("Joint2", 2)
                if obj.Checker == False:
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
            elif obj.ForceTypes == "Rotational Spring Damper":
                obj.setEditorMode("gx", 2)
                obj.setEditorMode("gy", 2)
                obj.setEditorMode("gz", 2)
                obj.setEditorMode("Stiffness", 2)
                obj.setEditorMode("UndeformedLength", 2)
                obj.setEditorMode("RotStiffness", 0)
                obj.setEditorMode("LinDampCoeff", 2)
                obj.setEditorMode("UndeformedAngle", 2)
                obj.setEditorMode("RotDampCoeff", 0)
                obj.setEditorMode("Body1", 0)
                obj.setEditorMode("Body2", 0)
                obj.setEditorMode("Joint1", 0)
                obj.setEditorMode("Joint2", 2)
                if obj.Checker == False:
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


# =============================================================================
class _ViewProviderDapForce:

    #  -------------------------------------------------------------------------
    def __init__(self, vobj):
        """ """
        vobj.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):
        """ """
        icon_path = os.path.join(DapTools.get_module_path(), "icons", "Icon6.png")
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
        #  TODO choose default display style
        # return "Flat Lines"
        return "Flat Lines"

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
        import _TaskPanelDapForce

        taskd = _TaskPanelDapForce.TaskPanelDapForce(self.Object)
        # for obj in FreeCAD.ActiveDocument.Objects:
        #    # if obj.isDerivedFrom("Fem::FemMeshObject"):
        #        # obj.ViewObject.hide()
        # self.Object.ViewObject.show()
        # taskd.obj = vobj.Object
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
