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

import os
import FreeCAD
import DapTools

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class _CommandDapAnimation:
    """Command to Perform an Animation of the solved system"""

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when 'FreeCADGui.addCommand' is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon8.png"),
            "MenuText": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Animation_alias", "Animate solution"
            ),
            "ToolTip": PySide.QtCore.QT_TRANSLATE_NOOP(
                "Dap_Animation_alias", "Animates the motion of the moving bodies"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if there are already some results stored in the solver object
        i.e. Determine if the animate command/icon must be active or greyed out"""

        return DapTools.getSolverObject().DapResults is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""

        import DapAnimation
        import _TaskPanelDapAnimate

        # Get the identity of the solver object
        solver_object = DapTools.getSolverObject()

        # Get the identity of the solver document
        # (which is the active document on entry)
        solver_document = FreeCAD.ActiveDocument

        # Get the list of body objects from the
        # solver document while it is still the active document
        body_objects = DapTools.getListOfBodyObjects()

        # Set an existing "Animation" document active
        # or create it if it does not exist yet
        if "Animation" in FreeCAD.listDocuments():
            FreeCAD.setActiveDocument("Animation")
        else:
            FreeCAD.newDocument("Animation")
        animation_document = FreeCAD.ActiveDocument

        # Generate the list of bodies and
        # add their shapes to the animation_document
        # and append their body labels to the list_of_bodies
        list_of_bodies = []
        for body in body_objects:
            animation_object = animation_document.addObject("Part::Feature", body.Label)
            animation_document.getObject(
                animation_object.Name
            ).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)

        # Request the animation window zoom to be set to fit the entire system
        FreeCADGui.SendMsgToActiveView("ViewFit")

        # Display (and run) the Animation dialog
        FreeCADGui.Control.showDialog(
            _TaskPanelDapAnimate.TaskPanelDapAnimate(
                solver_object,
                solver_document,
                animation_document,
                list_of_bodies,
            )
        )
