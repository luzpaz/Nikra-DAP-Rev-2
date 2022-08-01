# Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>
# Cecil Churms <churms@gmail.com>

import FreeCAD
import DapTools
import os

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True

PLOT_ITEMS = ["Position",
              "Velocity",
              "Path Trace",
              "Energy"]


# =============================================================================
class _CommandDapPlot:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """ Set up the menu text, the icon, and the tooltip """

        return {'Pixmap': os.path.join(DapTools.get_module_path(),
                                       "icons",
                                       "Icon9.png"),
            'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Plot_alias",
                                                 "Plot results"),
            'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Plot_alias",
                                                "Plot results")}

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """ Determine if the command/icon must be active or greyed out """

        return DapTools.getSolverObject().DapResults is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """ Called when the Animation command is run """
        
        if Debug:
            FreeCAD.Console.PrintMessage("Running Plot\n")

        import DapTools
        import DapPlot
        import _TaskPanelDapPlot

        taskd = _TaskPanelDapPlot.TaskPanelDapPlot()
        FreeCADGui.Control.showDialog(taskd)
