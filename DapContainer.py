# *        -  Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>
import FreeCAD
import DapTools
from DapTools import addObjectProperty
import os
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


#  -----------------------------------------------------------------------------
def makeDapContainer(name):
    """ Create Dap Container group object """
    obj = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", name)
    _DapContainer(obj)
    if FreeCAD.GuiUp:
        _ViewProviderDapContainer(obj.ViewObject)
    return obj


# =============================================================================
class _DapContainer:
    """ The Dap analysis group """

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
        addObjectProperty(obj,
                          "OutputPath", "",
                          "App::PropertyPath", "",
                          "Path to which cases are written (blank to use system default)")
        addObjectProperty(obj, "IsActiveContainer", False, "App::PropertyBool", "", "Active analysis object in document")
        obj.setEditorMode("IsActiveContainer", 1)  # Make read-only (2 = hidden)

    #  -------------------------------------------------------------------------
    def onDocumenRestored(self, obj):
        """ """
        self.initProperties(obj)


# =============================================================================
class _CommandDapContainer:
    """ The Dap Container command definition """

    #  -------------------------------------------------------------------------
    def __init__(self):
        """ """
        pass

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """ Set up the menu text, the icon, and the tooltip """

        return {'Pixmap': os.path.join(DapTools.get_module_path(),
                                       "icons",
                                       "Icon2.png"),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Container",
                                                     "New Dap Container"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Container",
                                                    "Creates a Dap solver container")}

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """ Determine if the command/icon must be active or greyed out """

        return FreeCAD.ActiveDocument is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """ Called when the Container command is run """
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
    """ A view provider for the DapContainer container object """

    #  -------------------------------------------------------------------------
    def __init__(self, vobj):
        """ """
        vobj.Proxy = self

    #  -------------------------------------------------------------------------
    def getIcon(self):
        """ """
        icon_path = icon_path = os.path.join(DapTools.get_module_path(), "icons", "Icon2.png")
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
            if FreeCADGui.activeWorkbench().name() != 'DapWorkbench':
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
