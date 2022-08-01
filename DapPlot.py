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

PLOT_ITEMS = ["Position", "Velocity", "Path Trace", "Energy"]


# =============================================================================
class _CommandDapPlot:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon9.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Plot_alias", "Plot results"
            ),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Plot_alias", "Plot results"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return DapTools.getSolverObject().DapResults is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""

        if Debug:
            FreeCAD.Console.PrintMessage("Running Plot\n")

        import DapTools
        import DapPlot
        import _TaskPanelDapPlot

        taskd = _TaskPanelDapPlot.TaskPanelDapPlot()
        FreeCADGui.Control.showDialog(taskd)
