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
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class _CommandDapAnimation:

    #  -------------------------------------------------------------------------
    def GetResources(self):
        """Called by FreeCAD when addCommand is run in InitGui.py
        Returns a dictionary defining the icon, the menu text and the tooltip"""

        return {
            "Pixmap": os.path.join(DapTools.get_module_path(), "icons", "Icon8.png"),
            "MenuText": QtCore.QT_TRANSLATE_NOOP(
                "Dap_Animation_alias", "Animate solution"
            ),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP(
                "Dap_Animation_alias", "Animates the motion of the moving bodies"
            ),
        }

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """Determine if the command/icon must be active or greyed out"""

        return DapTools.getSolverObject().DapResults is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """Called when the Animation command is run"""

        import DapTools
        import DapAnimation
        import _TaskPanelDapAnimate

        # Get the identity of the objects and the solver document (which is the current active document)
        solver_object = DapTools.getSolverObject()
        solver_document = FreeCAD.ActiveDocument
        body_objects = DapTools.getListOfBodyObjects()

        # Make "Animation" document active (or create it)
        if "Animation" in FreeCAD.listDocuments():
            FreeCAD.setActiveDocument("Animation")
        else:
            FreeCAD.newDocument("Animation")
        animation_document = FreeCAD.ActiveDocument

        # Generate the list of bodies and
        # add their shapes to the animation_document
        list_of_bodies = []
        for body in body_objects:
            animation_object = animation_document.addObject("Part::Feature", body.Label)
            animation_document.getObject(
                animation_object.Name
            ).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)

        # Request the animation window zoom to be set to fit the bodies
        FreeCADGui.SendMsgToActiveView("ViewFit")

        # Display the Animation dialog
        FreeCADGui.Control.showDialog(
            _TaskPanelDapAnimate.TaskPanelDapAnimate(
                solver_object,
                solver_document,
                animation_document,
                solver_object.DapResults,  # results
                list_of_bodies,
                solver_object.global_rotation_matrix,  # rotation_matrix
                solver_object.Bodies_r,  # Bodies_r
                solver_object.Bodies_p,
            )
        )  # Bodies_p
