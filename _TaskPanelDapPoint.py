# *        -  Varnu Govender (UP) <govender.v@tuks.co.za>                            *
import FreeCAD

import os
import os.path
import numpy
import DapTools
import DapPointSelection
import _DapBodySelector
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class TaskPanelDapPoint:
    """ Taskpanel for adding DAP Point """

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        self.obj = obj
        self.Point = self.obj.Point
        self.PointCoord = self.obj.PointCoord
        self.doc_name = self.obj.Document.Name
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapPoint.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        self.bodySelector = _DapBodySelector.DapBodySelector(self.form.bodySelection_1, self.obj)
        self.bodySelector.Page3()
        self.rebuildInputs()
        return

    #  -------------------------------------------------------------------------
    def rebuildInputs(self):
        """ """
        self.Point = self.obj.Point
        self.PointCoord = self.obj.PointCoord
        self.bodySelector.rebuildInputs(2)

    #  -------------------------------------------------------------------------
    def accept(self):
        """ """
        """If this is missing, there won't be an OK button"""
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.Point = self.Point
        self.obj.PointCoord = self.PointCoord
        self.bodySelector.accept(2)
        self.bodySelector.closing()
        #  Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        #  self.obj.recompute()
        return

    #  -------------------------------------------------------------------------
    def reject(self):
        """ """
        """IF this is missing, there won't be a Cancel button"""
        FreeCADGui.Selection.removeObserver(self)
        #  Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        self.bodySelector.reject()
        self.bodySelector.closing()
        return True
