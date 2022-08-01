# Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>
# Dewald Hattingh (UP) <u17082006@tuks.co.za>
# Varnu Govender (UP) <govender.v@tuks.co.za>
# Cecil Churms <churms@gmail.com>

import FreeCAD

import os
import os.path
import DapTools
import DapBodySelection

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class TaskPanelDapBody:
    """ Taskpanel for adding DAP Bodies """

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ Run on first instantiation of a TaskPanelDapBody """

        # Pass all the parameters from obj into the TaskPanelDapBody object
        self.obj = obj
        self.References = self.obj.References
        self.BodyType = self.obj.BodyType
        self.doc_name = self.obj.Document.Name
        self.initHorizontal = self.obj.InitialHorizontal
        self.initVertical = self.obj.InitialVertical
        self.initAngular = self.obj.InitialAngular
        self.default_velocity = "1 m/s"
        self.default_angVelocity = "1 rad/s"

        # Set up the form we will use to create the dialog box
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapBodies.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        self.form.comboBodyType.addItems(DapBodySelection.BODY_TYPES)
       
        # On reload, check to see if item already exists, and set dropbox item appropriately
        bi = DapTools.indexOrDefault(DapBodySelection.BODY_TYPES, self.obj.BodyType, 0)
        self.form.comboBodyType.setCurrentIndex(bi)
        self.bodyType()
        self.form.buttonRemovePart.clicked.connect(self.buttonRemovePartClicked)
        self.form.partList.currentRowChanged.connect(self.partListRowChanged)
        self.form.comboBodyType.currentIndexChanged.connect(self.comboTypeChanged)
        self.form.comboBodyType.currentIndexChanged.connect(self.bodyType)
        self.comboTypeChanged()
        self.form.buttonAddPart.clicked.connect(self.buttonAddPartClicked)
        self.form.pbResetInitialConditions.clicked.connect(self.resetInitialConditionsValues)

        # Set up the default velocity and angular velocity
        velocity = FreeCAD.Units.Quantity(self.default_velocity)
        angVelocity = FreeCAD.Units.Quantity(self.default_angVelocity)
        DapTools.setQuantity(self.form.velocityAngular, angVelocity)
        DapTools.setQuantity(self.form.velocityHorizontal, velocity)
        DapTools.setQuantity(self.form.velocityVertical, velocity)

        # Rebuild the dialog box accordingly
        self.rebuildReferenceList()
        self.rebuildInitialConditions()

    #  -------------------------------------------------------------------------
    def accept(self):
        """ """
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        self.obj.References = self.References
        self.obj.BodyType = self.BodyType
        self.obj.InitialHorizontal = DapTools.getQuantity(self.form.velocityHorizontal)
        self.obj.InitialVertical = DapTools.getQuantity(self.form.velocityVertical)
        self.obj.InitialAngular = DapTools.getQuantity(self.form.velocityAngular)
        #  Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        return  # self.obj.InitialHorizontal, self.obj.InitialVertical, self.obj.InitialAngular

    #  -------------------------------------------------------------------------
    def reject(self):
        """ """
        FreeCADGui.Selection.removeObserver(self)
        #  Recompute document to update viewprovider based on the shapes
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc_name = str(self.obj.Document.Name)
        FreeCAD.getDocument(doc_name).recompute()
        doc.resetEdit()
        return True

    #  -------------------------------------------------------------------------
    def comboTypeChanged(self):
        """ """
        type_index = self.form.comboBodyType.currentIndex()
        self.form.labelBodyDescription.setText(DapBodySelection.BODY_TYPE_HELPER_TEXT[type_index])
        self.BodyType = DapBodySelection.BODY_TYPES[type_index]
        if self.form.comboBodyType.currentIndex() == 0:
            self.obj.InitialHorizontal = "0 m/s"
            self.obj.InitialVertical = "0 m/s"
            self.obj.InitialAngular = "0 rad/s"
        self.rebuildInitialConditions()

    #  -------------------------------------------------------------------------
    def buttonAddPartClicked(self):
        """ """
        sel = FreeCADGui.Selection.getSelection()
        for item in sel:
            # check to see if part is not of Type DapBody
            DapBodyFound = False
            if hasattr(item, "Proxy"):
                if hasattr(item.Proxy, "Type"):
                    if item.Proxy.Type == 'DapBody':
                        DapBodyFound = True
            if hasattr(item, "Shape") and (not DapBodyFound):
                label = item.Label
                if label not in self.References:
                    self.References.append(label)
            else:
                if DapBodyFound:
                    FreeCAD.Console.PrintError("Selected object is a DAP container body. Cannot be added.")
                else:
                    FreeCAD.Console.PrintError("Selected object does not have a shape \n")
        self.rebuildReferenceList()
        return

    #  -------------------------------------------------------------------------
    def buttonRemovePartClicked(self):
        """ """
        if not self.References:
            FreeCAD.Console.PrintMessage("Here 1")
            return
        if not self.form.partList.currentItem():
            FreeCAD.Console.PrintMessage("Here 2")
            return
        row = self.form.partList.currentRow()
        self.References.pop(row)
        self.rebuildReferenceList()
        self.rebuildInitialConditions()  # Mod

    #  -------------------------------------------------------------------------
    def rebuildReferenceList(self):
        """ """
        self.form.partList.clear()
        for i in range(len(self.References)):
            self.form.partList.addItem(self.References[i])

    #  -------------------------------------------------------------------------
    def rebuildInitialConditions(self):
        """ """
        DapTools.setQuantity(self.form.velocityHorizontal, self.obj.InitialHorizontal)
        DapTools.setQuantity(self.form.velocityVertical, self.obj.InitialVertical)
        DapTools.setQuantity(self.form.velocityAngular, self.obj.InitialAngular)

    #  -------------------------------------------------------------------------
    def partListRowChanged(self, row):
        """ """
        """ Actively select the part to make it visible when viewing parts already in list """
        if len(self.References) > 0:
            item = self.References[row]
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)
            selection_object = doc.getObjectsByLabel(item)[0]
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(selection_object)

    #  -------------------------------------------------------------------------
    def bodyType(self):
        """ """
        if self.form.comboBodyType.currentIndex() == 0:
            self.form.lblInitialConditions.setHidden(True)
            self.form.labelInitConditionDescription.setHidden(True)
            self.form.lblVelocityHorizontal.setHidden(True)
            self.form.lblVelocityVertical.setHidden(True)
            self.form.lblVelocityAngular.setHidden(True)
            self.form.velocityHorizontal.setHidden(True)
            self.form.velocityVertical.setHidden(True)
            self.form.velocityAngular.setHidden(True)
            self.form.pbResetInitialConditions.setHidden(True)
            self.initHorizontal = "0.0 m/s"
            self.initVertical = "0.0 m/s"
            self.initAngular = "0.0 rad/s"
        else:
            self.form.lblInitialConditions.setHidden(False)
            self.form.labelInitConditionDescription.setHidden(False)
            self.form.lblVelocityHorizontal.setHidden(False)
            self.form.lblVelocityVertical.setHidden(False)
            self.form.lblVelocityAngular.setHidden(False)
            self.form.velocityHorizontal.setHidden(False)
            self.form.velocityVertical.setHidden(False)
            self.form.velocityAngular.setHidden(False)
            self.form.pbResetInitialConditions.setHidden(False)

    #  -------------------------------------------------------------------------
    def resetInitialConditionsValues(self):
        """ Resets the body's initial conditions to zero if the reset button is pushed """
        
        DapTools.setQuantity(self.form.velocityAngular, "0.0 rad/s")
        DapTools.setQuantity(self.form.velocityHorizontal, "0.0 m/s")
        DapTools.setQuantity(self.form.velocityVertical, "0.0 m/s")