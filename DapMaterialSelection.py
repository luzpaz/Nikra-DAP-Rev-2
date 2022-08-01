# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
import FreeCAD
import os
import DapTools
from DapTools import addObjectProperty
from pivy import coin
import Part
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


# -------------------------------------------------------------------------
def makeDapMaterial(name="DapMaterial"):
    obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    _DapMaterial(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapJoint(obj.ViewObject)
    return obj


# =============================================================================
class _CommandDapMaterial:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """ Set up the menu text, the icon, and the tooltip """

        return {'Pixmap': os.path.join(DapTools.get_module_path(),
                                       "icons",
                                       "Icon5.png"),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Material_alias",
                                                     "Define material properties"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Material_alias",
                                                    "Define the material properties associated with each body.")}

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """ Determine if the command/icon must be active or greyed out """

        return DapTools.getActiveContainer() is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """ Called when the Material Selection command is run """

        if Debug:
            FreeCAD.Console.PrintMessage("Running: Material Selection\n")

        import DapTools
        import DapMaterialSelection
        matObject = DapTools.getMaterialObject()
        if matObject == None:
            DapTools.getActiveContainer().addObject(DapMaterialSelection.makeDapMaterial())
            FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)
        else:
            FreeCADGui.ActiveDocument.setEdit(matObject.Name)


# =============================================================================
class _DapMaterial:

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        obj.Proxy = self
        self.Type = "DapMaterial"
        self.initProperties(obj)

    #  -------------------------------------------------------------------------
    def initProperties(self, obj):
        """ """
        # PythonObject
        addObjectProperty(obj, 'MaterialDictionary', {}, "App::PropertyPythonObject", "", "Dictionary of parts and linked material properties")
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
        icon_path = os.path.join(DapTools.get_module_path(), "icons", "Icon5.png")
        return icon_path

    #  -------------------------------------------------------------------------
    def attach(self, vobj):
        """ """
        self.ViewObject = vobj
        self.Object = vobj.Object
        self.standard = coin.SoGroup()
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
            FreeCAD.Console.PrintError('Task dialog already active\n')
        return True

    #  -------------------------------------------------------------------------
    def setEdit(self, vobj, mode):
        """ """
        import _TaskPanelDapMaterial
        taskd = _TaskPanelDapMaterial.TaskPanelDapMaterial(self.Object)
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
