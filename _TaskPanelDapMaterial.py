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

import os
import os.path
import DapTools
import DapBodySelection

if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtGui
    from PySide import QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class TaskPanelDapMaterial:
    """Taskpanel for adding DAP Bodies"""

    #  -------------------------------------------------------------------------
    def __init__(self, obj):
        """ """
        self.obj = obj
        self.MaterialDictionary = self.obj.MaterialDictionary
        self.default_density = "1 kg/m^3"
        self.fetchFreeCADMaterials()
        self.doc_name = self.obj.Document.Name
        self.doc = FreeCAD.getDocument(self.doc_name)
        (
            self.parts_shape_list_all,
            self.parent_assembly_all,
        ) = DapTools.getSolidsFromAllShapes(self.doc)
        # FreeCAD.Console.PrintMessage("all parts shape " + str(self.parts_shape_list_all) + "\n")
        # FreeCAD.Console.PrintMessage("all parent assembly " + str(self.parent_assembly_all) + "\n")
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapMaterials.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        self.body_labels = DapTools.getListOfBodyLabels()
        self.form.bodyCombo.addItems(self.body_labels)
        self.form.bodyCombo.currentIndexChanged.connect(self.bodyComboSelectionChanged)
        self.bodyComboSelectionChanged()
        self.form.tableWidget.cellClicked.connect(self.tableWidgetCellClicked)
        # self.form.tableWidget.cellChanged.connect(self.valueInCellChanged)
        self.defaultAssignmentOnCreate()

    #  -------------------------------------------------------------------------
    def accept(self):
        """ """
        self.obj.MaterialDictionary = self.MaterialDictionary
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    #  -------------------------------------------------------------------------
    def reject(self):
        """ """
        FreeCADGui.Selection.removeObserver(self)
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return True

    #  -------------------------------------------------------------------------
    def valueInCellChanged(self):
        """ """
        row = self.form.tableWidget.currentRow()
        col = self.form.tableWidget.currentColumn()
        #  Only interested atm in changes that happen when user enters a custom density value
        if col == 2:
            part_label = self.form.tableWidget.item(row, 0).text()
            combo_box_object = self.form.tableWidget.cellWidget(row, 1)
            mat_index = combo_box_object.currentIndex()
            current_mat_choice = self.card_name_list[mat_index]
            density_quantity = DapTools.getQuantity(
                self.form.tableWidget.cellWidget(row, col)
            )
            self.MaterialDictionary[part_label] = {
                "matName": current_mat_choice[0],
                "density": density_quantity,
            }

    #  -------------------------------------------------------------------------
    def fetchFreeCADMaterials(self):
        """ """
        #  Prepulate list of available material properties in FreeCAD
        #  The following snippet of code comes from MaterialEditor.py by Yorik van Havre, Bernd Hahnebach
        from materialtools.cardutils import import_materials as getmats

        self.materials, self.cards, self.icons = getmats()
        self.card_name_list = []  # [ [card_name, card_path, icon_path], ... ]
        self.card_name_labels = []
        for a_path in sorted(self.materials.keys()):
            self.card_name_list.append([self.cards[a_path], a_path, self.icons[a_path]])
            self.card_name_labels.append(self.cards[a_path])
        self.card_name_list.insert(0, ["Manual Definition", "", ""])
        self.card_name_labels.insert(0, "Manual Definition")

    #  -------------------------------------------------------------------------
    def defaultAssignmentOnCreate(self):
        """ """
        # docName = str(self.doc_name)
        # doc = FreeCAD.getDocument(docName)
        if len(self.body_labels):
            for i in range(len(self.body_labels)):
                selection_object = self.doc.getObjectsByLabel(self.body_labels[i])[0]
                list_of_parts = selection_object.References
                for current_body_label in list_of_parts:
                    obj = self.doc.getObjectsByLabel(current_body_label)[0]
                    # shape_label_list = DapTools.getListOfSolidsFromShape(obj, [])
                    shape_label_list = self.parts_shape_list_all[obj.Label]
                    for sub_shape_label in shape_label_list:
                        if not (sub_shape_label in self.MaterialDictionary.keys()):
                            mat_name = self.card_name_labels[0]
                            density = self.default_density
                            self.MaterialDictionary[sub_shape_label] = {}
                            self.MaterialDictionary[sub_shape_label][
                                "matName"
                            ] = mat_name
                            self.MaterialDictionary[sub_shape_label][
                                "density"
                            ] = density

    #  -------------------------------------------------------------------------
    def bodyComboSelectionChanged(self):
        """ """
        ci = self.form.bodyCombo.currentIndex()
        table_row = 0
        docName = str(self.doc_name)  # Never used
        # doc = FreeCAD.getDocument(docName)
        self.form.tableWidget.clearContents()
        self.form.tableWidget.setRowCount(0)
        self.form.tableWidget.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.ResizeToContents
        )
        if len(self.body_labels):
            selection_object = self.doc.getObjectsByLabel(self.body_labels[ci])[0]
            list_of_parts = selection_object.References
            for current_body_label in list_of_parts:
                self.form.tableWidget.insertRow(table_row)
                # current_body_label = list_of_parts[i]
                obj = self.doc.getObjectsByLabel(current_body_label)[0]
                # shape_label_list = DapTools.getListOfSolidsFromShape(obj, [])
                shape_label_list = self.parts_shape_list_all[obj.Label]
                if len(shape_label_list) > 1:
                    partName = QtGui.QTableWidgetItem(current_body_label)
                    partName.setFlags(QtCore.Qt.ItemIsEnabled)
                    font = QtGui.QFont()
                    font.setBold(True)
                    partName.setFont(font)
                    self.form.tableWidget.setItem(table_row, 0, partName)
                    table_row += 1
                for sub_shape_label in shape_label_list:
                    self.form.tableWidget.insertRow(table_row)
                    partName = QtGui.QTableWidgetItem(sub_shape_label)
                    partName.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.form.tableWidget.setItem(table_row, 0, partName)
                    combo = QtGui.QComboBox()
                    for mat in self.card_name_list:
                        combo.addItem(QtGui.QIcon(mat[2]), mat[0], mat[1])
                    self.form.tableWidget.setCellWidget(table_row, 1, combo)
                    # TODO: a lot of code duplication between the various functions.
                    if sub_shape_label in self.MaterialDictionary.keys():
                        mat_name = self.MaterialDictionary[sub_shape_label]["matName"]
                        density = self.MaterialDictionary[sub_shape_label]["density"]
                        mi = DapTools.indexOrDefault(self.card_name_labels, mat_name, 0)
                    else:
                        mat_name = self.card_name_labels[0]
                        density = self.default_density
                        self.MaterialDictionary[sub_shape_label] = {}
                        self.MaterialDictionary[sub_shape_label]["matName"] = mat_name
                        self.MaterialDictionary[sub_shape_label]["density"] = density
                        mi = 0
                    combo.setCurrentIndex(mi)
                    self.addDensityItemToTable(density, table_row, mi)
                    combo.currentIndexChanged.connect(self.materialComboChanged)
                    table_row += 1

    #  -------------------------------------------------------------------------
    def materialComboChanged(self, index):
        """ """
        current_row = self.form.tableWidget.currentRow()
        current_mat_choice = self.card_name_list[index]
        if index == 0:
            density = self.default_density
        else:
            density = self.materials[current_mat_choice[1]]["Density"]
        self.addDensityItemToTable(density, current_row, index)
        part_label = self.form.tableWidget.item(current_row, 0).text()
        self.form.tableWidget.resizeColumnsToContents()
        self.MaterialDictionary[part_label] = {
            "matName": current_mat_choice[0],
            "density": density,
        }

    #  -------------------------------------------------------------------------
    def addDensityItemToTable(self, density, current_row, mat_index):
        """ """
        density = FreeCAD.Units.Quantity(density)
        ui = FreeCADGui.UiLoader()
        density_item = ui.createWidget("Gui::InputField")
        DapTools.setQuantity(density_item, density)
        if mat_index != 0:
            # NOTE TODO This disables editing of the density value if it is selected from
            # available freeCAD materials. Not sure we should really force this?
            # density_item.setFlags(QtCore.Qt.ItemIsEnabled)
            density_item.setEnabled(False)
        # self.form.tableWidget.setItem(current_row, 2, density_item)
        density_item.editingFinished.connect(self.valueInCellChanged)
        self.form.tableWidget.setCellWidget(current_row, 2, density_item)

    #  -------------------------------------------------------------------------
    def tableWidgetCellClicked(self, row, column):
        """ """
        #  select the object to make it visible
        if column == 0:
            docName = str(self.doc_name)
            doc = FreeCAD.getDocument(docName)
            selection_object_label = self.form.tableWidget.item(row, column).text()
            # NOTE: Because the underlying subshapes that make up subassemblies can be contained in a different
            # document, getObject won't work and cannot be added to the selection list. If it was it would
            # switch documents. To circumvent this, if the subpart is part of a subassemlby then the subassemlby
            # will be added to the selection list.
            if self.parent_assembly_all[selection_object_label] != None:
                selection_object = doc.getObjectsByLabel(
                    self.parent_assembly_all[selection_object_label]
                )[0]
            else:
                selection_object = doc.getObjectsByLabel(selection_object_label)[0]
            # selection_object = doc.findObjects(Label = selection_object_label)[0]
            # selection_object = doc.getObjectsByLabel(selection_object_label)[0]
            FreeCADGui.Selection.clearSelection()
            FreeCADGui.Selection.addSelection(selection_object)
