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

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class DapWorkbench(Workbench):
    """This class encompasses the whole DAP workbench"""

    #  -------------------------------------------------------------------------
    def __init__(self):
        """Called on startup of FreeCAD"""

        if Debug:
            FreeCAD.Console.PrintMessage("Running: DapWorkbench->__init__\n")

        import os
        import DapTools

        # Set up the text for the DAP workbench option, the Nikra-DAP icon, and the tooltip
        self.__class__.Icon = os.path.join(
            DapTools.get_module_path(), "icons", "Icon1.png"
        )
        self.__class__.MenuText = "Nikra-DAP"
        self.__class__.ToolTip = (
            "Planar multibody dynamics workbench based on Prof. Nikravesh's DAP solver"
        )

    #  -------------------------------------------------------------------------
    def Initialize(self):
        """Called on the first selection of the DapWorkbench"""

        if Debug:
            FreeCAD.Console.PrintMessage("Running: DapWorkbench->Initialize\n")

        # Import all the commands we might use from the respective files
        from DapContainer import _CommandDapContainer
        from DapBodySelection import _CommandDapBody
        from DapJointSelection import _CommandDapJoint
        from DapMaterialSelection import _CommandDapMaterial
        from DapForceSelection import _CommandDapForce
        from DapSolverRunner import _CommandDapSolver
        from DapAnimation import _CommandDapAnimation
        from DapPlot import _CommandDapPlot
        from DapPointSelection import _CommandDapPoint

        # Define which commands will be called with each command alias
        FreeCADGui.addCommand("Dap_Container_alias", _CommandDapContainer())
        FreeCADGui.addCommand("Dap_Body_alias", _CommandDapBody())
        FreeCADGui.addCommand("Dap_Joint_alias", _CommandDapJoint())
        FreeCADGui.addCommand("Dap_Force_alias", _CommandDapMaterial())
        FreeCADGui.addCommand("Dap_Material_alias", _CommandDapForce())
        FreeCADGui.addCommand("Dap_Solver_alias", _CommandDapSolver())
        FreeCADGui.addCommand("Dap_Animation_alias", _CommandDapAnimation())
        FreeCADGui.addCommand("Dap_Plot_alias", _CommandDapPlot())
        FreeCADGui.addCommand("Dap_Point_alias", _CommandDapPoint())

        # Create a toolbar with the DAP commands (icons)
        self.appendToolbar("Nikra-DAP Commands", self.MakeCommandList())

        # Create a drop-down menu item for the menu bar
        self.appendMenu("Nikra-Dap", self.MakeCommandList())

    #  -------------------------------------------------------------------------
    def MakeCommandList(self):
        """Define a list of our aliases for all the DAP functions
        TODO: Add "Dap_Point_alias" when it is implemented"""

        return [
            "Dap_Container_alias",
            "Separator",
            "Dap_Body_alias",
            "Dap_Joint_alias",
            "Dap_Material_alias",
            "Dap_Force_alias",
            "Separator",
            "Dap_Solver_alias",
            "Separator",
            "Dap_Animation_alias",
            "Dap_Plot_alias",
        ]

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""

        if Debug:
            FreeCAD.Console.PrintMessage("Running Animation\n")

        return

    #  -------------------------------------------------------------------------
    def Deactivated(self):
        """This function is executed each time the DAP workbench is deactivated"""

        return

    #  -------------------------------------------------------------------------
    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen
        'recipient' will be 'view' when mouse is in the VIEW window
        'recipient' will be 'tree' when mouse is in the TREE window"""

        # Append the DAP commands to the existing context menu
        self.appendContextMenu("Nikra-DAP Commands", self.MakeCommandList())

    #  -------------------------------------------------------------------------
    def GetClassName(self):
        """This function is mandatory if this is a full Python workbench
        The returned string should be exactly 'Gui::PythonWorkbench'"""

        return "Gui::PythonWorkbench"


# =============================================================================
# Add the workbench to the list of workbenches and initialize it
if Debug:
    FreeCAD.Console.PrintMessage("Adding DapWorkbench\n")

Gui.addWorkbench(DapWorkbench())
