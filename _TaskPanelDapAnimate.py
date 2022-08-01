# Alfred Bogaers (EX-MENTE) <alfred.bogaers@ex-mente.co.za>              *
# Cecil Churms <churms@gmail.com>

import FreeCAD

from os import path
import DapTools
import numpy as np
from math import degrees

if FreeCAD.GuiUp:
    from FreeCADGui import Control, PySideUic
    from PySide import QtGui, QtCore

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class TaskPanelDapAnimate:
    """ Taskpanel for Running an animation """

    #  -------------------------------------------------------------------------
    def __init__(self,
                 solver_object,
                 solver_document,
                 animation_document,
                 results,
                 list_of_bodies,
                 rotation_matrix,
                 Bodies_r,            # The list of all the body locations for each clock tick
                 Bodies_p):           # The list of all the body angles for each clock tick

        if Debug:
            FreeCAD.Console.PrintMessage("Running: TaskPanelDapAnimate  ->  __init__\n")

        # Here we get the list of objects from the FreeCAD active document
        self.animation_body_objects = FreeCAD.ActiveDocument.Objects

        # Transfer the called parameters to the instance variables
        self.obj = solver_object
        self.solver_document = solver_document
        self.animation_document = animation_document
        self.results = np.array(results)
        self.list_of_bodies = list_of_bodies
        self.rotation_matrix = rotation_matrix
        self.Bodies_r = Bodies_r
        self.Bodies_p = Bodies_p

        self.scale = 1e3  # convert from meters to mm

        # Transfer the values from the obj object (i.e. solver_object) to instance variables
        self.t_initial = self.obj.StartTime
        self.t_final = self.obj.EndTime
        self.reporting_time_step = self.obj.ReportingTimeStep
        self.plane_norm = self.obj.UnitVector
        self.reportedTimes = self.obj.ReportedTimes

        # Set play back speed to mid-range
        self.play_back_speed = 100  # msec

        # Set up the timer parameters
        self.n_time_steps = len(self.Bodies_r) - 1
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.play_back_speed)
        self.timer.timeout.connect(self.onTimerTimeout)  # callback function after each tick

        self.list_of_moving_bodies = DapTools.getListOfMovingBodies(self.list_of_bodies, self.solver_document)

        # Load the Dap Animate ui form
        ui_path = path.join(path.dirname(__file__), "TaskPanelDapAnimate.ui")
        self.form = PySideUic.loadUi(ui_path)

        # Set up values displayed on the form
        self.form.horizontalSlider.setRange(0, self.n_time_steps)
        self.form.timeStepLabel.setText("{0:5.3f}s / {1:5.3f}s".format(self.t_initial, self.t_final))

        # Define callback functions when changes are made to the form
        self.form.horizontalSlider.valueChanged.connect(self.moveObjects)
        self.form.startButton.clicked.connect(self.playStart)
        self.form.stopButton.clicked.connect(self.stopStop)
        self.form.playSpeed.valueChanged.connect(self.changePlaySpeed)

        self.current_pose = self.thisTick_Pose(0)

    #  -------------------------------------------------------------------------
    def thisTick_Pose(self, clock_tick):
        """ Generate the list of poses for all the bodies at this clock_tick """

        PoseAtThisTick = []
        for body_number in range(len(self.Bodies_p[clock_tick])):
            location = self.Bodies_r[clock_tick][body_number]
            angle = self.Bodies_p[clock_tick][body_number]
            PoseAtThisTick.append([location, angle])
        return PoseAtThisTick

    #  -------------------------------------------------------------------------
    def reject(self):
        """ Closes document and sets the active document
        back to the solver document when the 'close' button is pressed """

        if Debug:
            FreeCAD.Console.PrintMessage("Animate 'close' button pressed\n")

        Control.closeDialog()
        FreeCAD.closeDocument(self.animation_document.Name)
        FreeCAD.setActiveDocument(self.solver_document.Name)

    #  -------------------------------------------------------------------------
    def getStandardButtons(self):
        """ Set up button attributes for the dialog ui """

        return 0x00200000

    #  -------------------------------------------------------------------------
    def playStart(self):
        """ Start the Qt timer """

        self.timer.start()

    #  -------------------------------------------------------------------------
    def stopStop(self):
        """ Stop the Qt timer """

        self.timer.stop()

    #  -------------------------------------------------------------------------
    def onTimerTimeout(self):
        """ Increment the tick position in the player, looping, if requested """

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
        """ Alter the play back speed by a factor of 1/newSpeed """

        self.timer.setInterval(self.play_back_speed * (1.0 / newSpeed))

    #  -------------------------------------------------------------------------
    def centerOfGravityOfCompound(self, compound):
        """ Necessary because older versions of FreeCAD do not have centerOfGravity
            and compound shapes do not have centerOfMass
        The Centre of Mass of a compound object:
          The vector sum of the centre of mass of each solid,
          weighted by volume """

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
        """ Move all the bodies to their location at this clock tick """

        # Remember the previous location, and step to the new value
        previous_pose = self.current_pose.copy()
        self.current_pose = self.thisTick_Pose(clock_tick)

        # Update the time label in the dialog
        # We add one step to the reported value so that the reported time, ends at exactly t_final
        self.form.timeStepLabel.setText("{0:5.3f}s of {1:5.3f}s".format(self.reportedTimes[clock_tick] + self.reporting_time_step, self.t_final))

        # Calculate rotation and translation for each body
        for body_number in range(len(self.list_of_moving_bodies)):
            body_index = self.list_of_bodies.index(self.list_of_moving_bodies[body_number])
            animation_body_cog = self.centerOfGravityOfCompound(self.animation_body_objects[body_index])
            axis_of_rotation = self.plane_norm
            current_pose = self.current_pose[body_number]

            # Calculate the position after ROTATION
            angular_displacement = degrees(current_pose[1] - previous_pose[body_number][1])
            self.animation_body_objects[body_index].Placement.rotate(animation_body_cog,
                                                                     axis_of_rotation,
                                                                     angular_displacement)
            rotated_location = FreeCAD.Vector(current_pose[0][0], current_pose[0][1], 0)

            # Rotate the centre of gravity
            rotated_cog = self.centerOfGravityOfCompound(self.animation_body_objects[body_index])
            projected_cog = DapTools.projectPointOntoPlane(self.plane_norm, rotated_cog)
            orthonormal_translation = rotated_location * self.scale - self.rotation_matrix * projected_cog

            # Calculate and apply the translation we require
            required_translation = self.rotation_matrix.transposed().multVec(orthonormal_translation)
            self.animation_body_objects[body_index].Placement.translate(required_translation)
