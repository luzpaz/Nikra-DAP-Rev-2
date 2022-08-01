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
import DapTools
import numpy as np
import math

if FreeCAD.GuiUp:
    import FreeCADGui
    import PySide

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class TaskPanelDapAnimate:
    """Taskpanel for Running an animation"""

    #  -------------------------------------------------------------------------
    def __init__(
        self,
        solver_object,
        solver_document,
        animation_document,
        list_of_bodies,
    ):

        if Debug:
            FreeCAD.Console.PrintMessage("Opening TaskPanelDapAnimate\n")

        # Here we get the list of objects from the FreeCAD active document
        self.animation_body_objects = FreeCAD.ActiveDocument.Objects

        # Transfer the called parameters to the instance variables
        self.obj = solver_object
        self.solver_document = solver_document
        self.animation_document = animation_document
        self.results = np.array(solver_object.DapResults)
        self.list_of_bodies = list_of_bodies
        self.rotation_matrix = solver_object.global_rotation_matrix
        # The list of all the body locations for each clock tick
        self.Bodies_r = solver_object.Bodies_r
        # The list of all the body angles for each clock tick
        self.Bodies_p = solver_object.Bodies_p

        # Set the scale to convert from meters to mm
        self.scale = 1.0e3

        # Transfer the values from the obj object (i.e. solver_object) to instance variables
        self.t_initial = self.obj.StartTime
        self.t_final = self.obj.EndTime
        self.reporting_time_step = self.obj.ReportingTimeStep
        self.plane_norm = self.obj.UnitVector
        self.reportedTimes = self.obj.ReportedTimes

        # Set play back period to mid-range
        self.play_back_period = 100  # msec

        # Set up the timer parameters
        self.n_time_steps = len(self.Bodies_r) - 1
        self.timer = PySide.QtCore.QTimer()
        self.timer.setInterval(self.play_back_period)
        self.timer.timeout.connect(
            self.onTimerTimeout
        )  # callback function after each tick

        self.list_of_moving_bodies = DapTools.getListOfMovingBodies(
            self.list_of_bodies, self.solver_document
        )

        # Load the Dap Animate ui form
        ui_path = os.path.join(os.path.dirname(__file__), "TaskPanelDapAnimate.ui")
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)

        # Set up the values displayed on the dialog
        self.form.horizontalSlider.setRange(0, self.n_time_steps)
        self.form.timeStepLabel.setText(
            "{0:5.3f}s / {1:5.3f}s".format(self.t_initial, self.t_final)
        )

        # Define callback functions when changes are made in the dialog
        self.form.horizontalSlider.valueChanged.connect(self.moveObjects)
        self.form.startButton.clicked.connect(self.playStart)
        self.form.stopButton.clicked.connect(self.stopStop)
        self.form.playSpeed.valueChanged.connect(self.changePlaySpeed)

        self.current_pose = self.thisTick_Pose(0)

    #  -------------------------------------------------------------------------
    def thisTick_Pose(self, clock_tick):
        """Generate the list of poses for all the bodies at this clock_tick"""

        PoseAtThisTick = []
        for body_number in range(len(self.Bodies_p[clock_tick])):
            location = self.Bodies_r[clock_tick][body_number]
            angle = self.Bodies_p[clock_tick][body_number]
            PoseAtThisTick.append([location, angle])
        return PoseAtThisTick

    #  -------------------------------------------------------------------------
    def reject(self):
        """Closes document and sets the active document
        back to the solver document when the 'close' button is pressed"""

        if Debug:
            FreeCAD.Console.PrintMessage("Animate 'close' button pressed\n")

        FreeCADGui.Control.closeDialog()
        FreeCAD.closeDocument(self.animation_document.Name)
        FreeCAD.setActiveDocument(self.solver_document.Name)

    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """Set up button attributes for the dialog ui"""

        return 0x00200000

    #  -------------------------------------------------------------------------
    def playStart(self):
        """Start the Qt timer"""

        self.timer.start()

    #  -------------------------------------------------------------------------
    def stopStop(self):
        """Stop the Qt timer"""

        self.timer.stop()

    #  -------------------------------------------------------------------------
    def onTimerTimeout(self):
        """Increment the tick position in the player, looping, if requested"""

        tickPosition = self.form.horizontalSlider.value()
        tickPosition += 1
        if tickPosition >= self.n_time_steps:
            if self.form.loopCheckBox.isChecked():
                tickPosition = 0
            else:
                self.timer.stop()

        # Update the slider on the dialog
        self.form.horizontalSlider.setValue(tickPosition + 1)

    #  -------------------------------------------------------------------------
    def changePlaySpeed(self, newSpeed):
        """Alter the play back period by a factor of 1/newSpeed"""

        self.timer.setInterval(self.play_back_period * (1.0 / newSpeed))

    #  -------------------------------------------------------------------------
    def centerOfGravityOfCompound(self, compound):
        """Necessary because older versions of FreeCAD do not have centerOfGravity
            and compound shapes do not have centerOfMass
        The Centre of Mass of a compound object:
          The vector sum of the centre of mass of each solid,
          weighted by volume"""

        totVol = 0
        CoG = FreeCAD.Vector(0, 0, 0)
        for solid in compound.Shape.Solids:
            vol = solid.Volume
            totVol += vol
            CoG += solid.CenterOfMass * vol

        CoG /= totVol

        return CoG

    #  -------------------------------------------------------------------------
    def moveObjects(self, clock_tick):
        """Move all the bodies to their location at this clock tick"""

        # Remember the previous location, and step to the new value
        previous_pose = self.current_pose.copy()
        self.current_pose = self.thisTick_Pose(clock_tick)

        # Update the time label in the dialog
        # We add one step to the reported value so that the reported time, ends at exactly t_final
        self.form.timeStepLabel.setText(
            "{0:5.3f}s of {1:5.3f}s".format(
                self.reportedTimes[clock_tick] + self.reporting_time_step, self.t_final
            )
        )

        # Calculate rotation and translation for each body
        for body_number in range(len(self.list_of_moving_bodies)):
            body_index = self.list_of_bodies.index(
                self.list_of_moving_bodies[body_number]
            )
            animation_body_cog = self.centerOfGravityOfCompound(
                self.animation_body_objects[body_index]
            )
            axis_of_rotation = self.plane_norm
            current_pose = self.current_pose[body_number]

            # Calculate the position after ROTATION
            angular_displacement = math.degrees(
                current_pose[1] - previous_pose[body_number][1]
            )
            self.animation_body_objects[body_index].Placement.rotate(
                animation_body_cog, axis_of_rotation, angular_displacement
            )
            rotated_location = FreeCAD.Vector(current_pose[0][0], current_pose[0][1], 0)

            # Rotate the centre of gravity
            rotated_cog = self.centerOfGravityOfCompound(
                self.animation_body_objects[body_index]
            )
            projected_cog = DapTools.projectPointOntoPlane(self.plane_norm, rotated_cog)
            orthonormal_translation = (
                rotated_location * self.scale - self.rotation_matrix * projected_cog
            )

            # Calculate and apply the translation we require
            required_translation = self.rotation_matrix.transposed().multVec(
                orthonormal_translation
            )
            self.animation_body_objects[body_index].Placement.translate(
                required_translation
            )
