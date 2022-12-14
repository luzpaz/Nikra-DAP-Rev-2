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
# *          Varnu Govender (UP) <govender.v@tuks.co.za>                             *
# *          Lukas du Plessis (UP) <lukas.duplessis@up.ac.za>                        *
# *          Cecil Churms <churms@gmail.com>                                         *
# *                                                                                  *
# ************************************************************************************

import FreeCAD

import os
import DapTools
import DapForceSelection
import _TaskPanelDapForce

# Select if we want to be in debug mode
global Debug
Debug = True


if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide
    import Part


# =============================================================================
class DapForceDriver:

    #  -------------------------------------------------------------------------
    def __init__(self, parent_widget, obj):
        """ """
        ui_path = os.path.join(os.path.dirname(__file__), "DapForceDriver.ui")
        self.parent_widget = parent_widget
        self.form = FreeCADGui.PySideUic.loadUi(ui_path, self.parent_widget)
        self.parent_widget.layout().addWidget(self.form)
        self.obj = obj
        self.doc_name = self.obj.Document.Name
        self.view_object = self.obj.ViewObject
        self.emptyunit = ""
        self.form.radtype_a.toggled.connect(lambda: self.funcChanged(0))
        self.form.radtype_b.toggled.connect(lambda: self.funcChanged(1))
        self.form.radtype_c.toggled.connect(lambda: self.funcChanged(2))
        self.unitFunc()
        self.rebuildInputs()
        self.propertyEditor()

    #  -------------------------------------------------------------------------
    def accept(self):
        """ """
        if self.form.radtype_a.isChecked():
            self.obj.a_Checker = True
            self.obj.b_Checker = False
            self.obj.c_Checker = False
            self.obj.tEndDriverFuncTypeA = DapTools.getQuantity(self.form.tEndFuncA)
            self.obj.coefC1DriverFuncTypeA = DapTools.getQuantity(self.form.FuncACoefC1)
            self.obj.coefC2DriverFuncTypeA = DapTools.getQuantity(self.form.FuncACoefC2)
            self.obj.coefC3DriverFuncTypeA = DapTools.getQuantity(self.form.FuncACoefC3)
            DapTools.setQuantity(self.form.tStartFuncB, 0.0)
            DapTools.setQuantity(self.form.tEndFuncB, 0.0)
            DapTools.setQuantity(self.form.startValueFuncB, 0.0)
            DapTools.setQuantity(self.form.endValueFuncB, 0.0)
            DapTools.setQuantity(self.form.tStartFuncC, 0.0)
            DapTools.setQuantity(self.form.tEndFuncC, 0.0)
            DapTools.setQuantity(self.form.startValueFuncC, 0.0)
            DapTools.setQuantity(self.form.endDerivativeFuncC, 0.0)
        if self.form.radtype_b.isChecked():
            self.obj.b_Checker = True
            self.obj.a_Checker = False
            self.obj.c_Checker = False
            self.obj.tStartDriverFuncTypeB = DapTools.getQuantity(self.form.tStartFuncB)
            self.obj.tEndDriverFuncTypeB = DapTools.getQuantity(self.form.tEndFuncB)
            self.obj.initialValueDriverFuncTypeB = DapTools.getQuantity(
                self.form.startValueFuncB
            )
            self.obj.endValueDriverFuncTypeB = DapTools.getQuantity(
                self.form.endValueFuncB
            )
            DapTools.setQuantity(self.form.tEndFuncA, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC1, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC2, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC3, 0.0)
            DapTools.setQuantity(self.form.tStartFuncC, 0.0)
            DapTools.setQuantity(self.form.tEndFuncC, 0.0)
            DapTools.setQuantity(self.form.startValueFuncC, 0.0)
            DapTools.setQuantity(self.form.endDerivativeFuncC, 0.0)
        if self.form.radtype_c.isChecked():
            self.obj.c_Checker = True
            self.obj.a_Checker = False
            self.obj.b_Checker = False
            self.obj.tStartDriverFuncTypeC = DapTools.getQuantity(self.form.tStartFuncC)
            self.obj.tEndDriverFuncTypeC = DapTools.getQuantity(self.form.tEndFuncC)
            self.obj.initialValueDriverFuncTypeC = DapTools.getQuantity(
                self.form.startValueFuncC
            )
            self.obj.endDerivativeDriverFuncTypeC = DapTools.getQuantity(
                self.form.endDerivativeFuncC
            )
            DapTools.setQuantity(self.form.tEndFuncA, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC1, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC2, 0.0)
            DapTools.setQuantity(self.form.FuncACoefC3, 0.0)
            DapTools.setQuantity(self.form.tStartFuncB, 0.0)
            DapTools.setQuantity(self.form.tEndFuncB, 0.0)
            DapTools.setQuantity(self.form.startValueFuncB, 0.0)
            DapTools.setQuantity(self.form.endValueFuncB, 0.0)
        self.propertyEditor()
        doc = FreeCADGui.getDocument(self.obj.Document)
        doc.resetEdit()
        return

    #  -------------------------------------------------------------------------
    def unitFunc(self):
        """ """
        emptyunit = FreeCAD.Units.Quantity(self.emptyunit)
        DapTools.setQuantity(self.form.tEndFuncA, emptyunit)
        DapTools.setQuantity(self.form.FuncACoefC1, emptyunit)
        DapTools.setQuantity(self.form.FuncACoefC2, emptyunit)
        DapTools.setQuantity(self.form.FuncACoefC3, emptyunit)
        DapTools.setQuantity(self.form.tStartFuncB, emptyunit)
        DapTools.setQuantity(self.form.tEndFuncB, emptyunit)
        DapTools.setQuantity(self.form.startValueFuncB, emptyunit)
        DapTools.setQuantity(self.form.endValueFuncB, emptyunit)
        DapTools.setQuantity(self.form.tStartFuncC, emptyunit)
        DapTools.setQuantity(self.form.tEndFuncC, emptyunit)
        DapTools.setQuantity(self.form.startValueFuncC, emptyunit)
        DapTools.setQuantity(self.form.endDerivativeFuncC, emptyunit)
        return

    #  -------------------------------------------------------------------------
    def rebuildInputs(self):
        """ """
        DapTools.setQuantity(self.form.tEndFuncA, self.obj.tEndDriverFuncTypeA)
        DapTools.setQuantity(self.form.FuncACoefC1, self.obj.coefC1DriverFuncTypeA)
        DapTools.setQuantity(self.form.FuncACoefC2, self.obj.coefC2DriverFuncTypeA)
        DapTools.setQuantity(self.form.FuncACoefC3, self.obj.coefC3DriverFuncTypeA)
        DapTools.setQuantity(self.form.tStartFuncB, self.obj.tStartDriverFuncTypeB)
        DapTools.setQuantity(self.form.tEndFuncB, self.obj.tEndDriverFuncTypeB)
        DapTools.setQuantity(
            self.form.startValueFuncB, self.obj.initialValueDriverFuncTypeB
        )
        DapTools.setQuantity(self.form.endValueFuncB, self.obj.endValueDriverFuncTypeB)
        DapTools.setQuantity(self.form.tStartFuncC, self.obj.tStartDriverFuncTypeC)
        DapTools.setQuantity(self.form.tEndFuncC, self.obj.tEndDriverFuncTypeC)
        DapTools.setQuantity(
            self.form.startValueFuncC, self.obj.initialValueDriverFuncTypeC
        )
        DapTools.setQuantity(
            self.form.endDerivativeFuncC, self.obj.endDerivativeDriverFuncTypeC
        )
        if self.obj.a_Checker:
            self.form.radtype_a.setChecked(True)
        if self.obj.b_Checker:
            self.form.radtype_b.setChecked(True)
        if self.obj.c_Checker:
            self.form.radtype_c.setChecked(True)

    #  -------------------------------------------------------------------------
    def funcChanged(self, index):
        """ """
        self.form.typeInput.setCurrentIndex(index + 1)

    #  -------------------------------------------------------------------------
    def propertyEditor(self):
        """ """
        if self.obj.a_Checker:
            self.obj.setEditorMode("tEndDriverFuncTypeA", 0)
            self.obj.setEditorMode("coefC1DriverFuncTypeA", 0)
            self.obj.setEditorMode("coefC2DriverFuncTypeA", 0)
            self.obj.setEditorMode("coefC3DriverFuncTypeA", 0)
            self.obj.setEditorMode("tStartDriverFuncTypeB", 2)
            self.obj.setEditorMode("tEndDriverFuncTypeB", 2)
            self.obj.setEditorMode("initialValueDriverFuncTypeB", 2)
            self.obj.setEditorMode("endValueDriverFuncTypeB", 2)
            self.obj.setEditorMode("tStartDriverFuncTypeC", 2)
            self.obj.setEditorMode("tEndDriverFuncTypeC", 2)
            self.obj.setEditorMode("initialValueDriverFuncTypeC", 2)
            self.obj.setEditorMode("endDerivativeDriverFuncTypeC", 2)
        if self.obj.b_Checker:
            self.obj.setEditorMode("tEndDriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC1DriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC2DriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC3DriverFuncTypeA", 2)
            self.obj.setEditorMode("tStartDriverFuncTypeB", 0)
            self.obj.setEditorMode("tEndDriverFuncTypeB", 0)
            self.obj.setEditorMode("initialValueDriverFuncTypeB", 0)
            self.obj.setEditorMode("endValueDriverFuncTypeB", 0)
            self.obj.setEditorMode("tStartDriverFuncTypeC", 2)
            self.obj.setEditorMode("tEndDriverFuncTypeC", 2)
            self.obj.setEditorMode("initialValueDriverFuncTypeC", 2)
            self.obj.setEditorMode("endDerivativeDriverFuncTypeC", 2)
        if self.obj.c_Checker:
            self.obj.setEditorMode("tEndDriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC1DriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC2DriverFuncTypeA", 2)
            self.obj.setEditorMode("coefC3DriverFuncTypeA", 2)
            self.obj.setEditorMode("tStartDriverFuncTypeB", 2)
            self.obj.setEditorMode("tEndDriverFuncTypeB", 2)
            self.obj.setEditorMode("initialValueDriverFuncTypeB", 2)
            self.obj.setEditorMode("endValueDriverFuncTypeB", 2)
            self.obj.setEditorMode("tStartDriverFuncTypeC", 0)
            self.obj.setEditorMode("tEndDriverFuncTypeC", 0)
            self.obj.setEditorMode("initialValueDriverFuncTypeC", 0)
            self.obj.setEditorMode("endDerivativeDriverFuncTypeC", 0)
