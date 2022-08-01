# Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>
# Cecil Churms <churms@gmail.com>

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
        """ Set up the menu text, the icon, and the tooltip """

        return {'Pixmap': os.path.join(DapTools.get_module_path(),
                                       "icons",
                                       "Icon8.png"),
                'MenuText': QtCore.QT_TRANSLATE_NOOP("Dap_Animation",
                                                     "Animate solution"),
                'ToolTip': QtCore.QT_TRANSLATE_NOOP("Dap_Animation",
                                                    "Animates the motion of the moving bodies")}

    #  -------------------------------------------------------------------------
    def IsActive(self):
        """ Determine if the command/icon must be active or greyed out """

        return DapTools.getSolverObject().DapResults is not None

    #  -------------------------------------------------------------------------
    def Activated(self):
        """ Called when the Animation command is run """

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
            animation_document.getObject(animation_object.Name).Shape = body.Shape.copy()
            list_of_bodies.append(body.Label)

        # Request the animation window zoom to be set to fit the bodies
        FreeCADGui.SendMsgToActiveView("ViewFit")

        # Display the Animation dialog
        FreeCADGui.Control.showDialog(
            _TaskPanelDapAnimate.TaskPanelDapAnimate(solver_object,
                                                     solver_document,
                                                     animation_document,
                                                     solver_object.DapResults,              # results
                                                     list_of_bodies,
                                                     solver_object.global_rotation_matrix,  # rotation_matrix
                                                     solver_object.Bodies_r,                # Bodies_r
                                                     solver_object.Bodies_p))               # Bodies_p
