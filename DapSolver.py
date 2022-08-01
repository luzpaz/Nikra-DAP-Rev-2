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
import sys
import numpy as np
from DapStructures import (
    Body_struct,
    Force_struct,
    Joint_struct,
    Point_struct,
    Unit_struct,
    Funct_struct,
)
from DapHelperfunctions import RotMatrix, RotMatrix90

# Select if we want to be in debug mode
global Debug
Debug = True


# =============================================================================
class DapSolver:

    #  -------------------------------------------------------------------------
    def __init__(self, folder):
        """ """
        self.folder = folder
        self.readInputFiles()
        self.initialize()
        return

    #  -------------------------------------------------------------------------
    def readInputFiles(self):
        """ """
        exec(open(os.path.join(self.folder, "inBodies.py")).read())
        exec(open(os.path.join(self.folder, "inForces.py")).read())
        exec(open(os.path.join(self.folder, "inFuncts.py")).read())
        exec(open(os.path.join(self.folder, "inJoints.py")).read())
        exec(open(os.path.join(self.folder, "inPoints.py")).read())
        exec(open(os.path.join(self.folder, "inUvectors.py")).read())
        self.Bodies = Bodies
        self.Forces = Forces
        self.Functs = Functs
        self.Joints = Joints
        self.Points = Points
        self.Uvectors = Uvectors

    #  -------------------------------------------------------------------------
    def initialize(self):
        """ """
        self.nB = len(self.Bodies)
        self.nB3 = 3 * (self.nB)
        self.nB6 = 6 * (self.nB)
        for Bi in range(self.nB):
            self.Bodies[Bi, 0].irc = 3 * Bi
            self.Bodies[Bi, 0].irv = self.nB3 + 3 * Bi
            self.Bodies[Bi, 0].m_inv = 1 / self.Bodies[Bi, 0].m
            self.Bodies[Bi, 0].J_inv = 1 / self.Bodies[Bi, 0].J
            self.Bodies[Bi, 0].A = RotMatrix(self.Bodies[Bi, 0].p)
            # self.Bodies[Bi, 0].color  = bodycolor[Bi]
        # %%% Mass (inertia) matrix as an array
        self.M_array = np.zeros((self.nB3, 1))
        self.M_inv_array = np.zeros((self.nB3, 1))
        for Bi in range(self.nB):
            is_ = 3 * Bi
            ie = is_ + 3
            self.M_array[is_:ie, 0] = [
                self.Bodies[Bi, 0].m,
                self.Bodies[Bi, 0].m,
                self.Bodies[Bi, 0].J,
            ]
            self.M_inv_array[is_:ie, 0] = [
                self.Bodies[Bi, 0].m_inv,
                self.Bodies[Bi, 0].m_inv,
                self.Bodies[Bi, 0].J_inv,
            ]
        # %%% self.Points
        self.nP = len(self.Points)
        self.nPtot = self.nP
        for Pi in range(self.nPtot):
            if self.Points[Pi, 0].Bindex == -1:
                self.Points[Pi, 0].sP = self.Points[Pi, 0].sPlocal
                self.Points[Pi, 0].sP_r = RotMatrix90(self.Points[Pi, 0].sP)
                self.Points[Pi, 0].rP = self.Points[Pi, 0].sP
            for Bi in range(self.nB):
                if int(self.Points[Pi, 0].Bindex) == int(Bi):
                    length = len(
                        self.Bodies[Bi, 0].pts
                    )  # current length of pts - Assigned but never used
                    self.Bodies[Bi, 0].pts = np.concatenate(
                        (self.Bodies[Bi, 0].pts, np.array([[Pi]])), axis=0
                    )
        # %%% Unit vectors
        self.nU = len(self.Uvectors)
        for Vi in range(self.nU):
            if self.Uvectors.size == 0:
                pass
            elif self.Uvectors[Vi, 0].Bindex == -1:
                self.Uvectors[Vi, 0].u = self.Uvectors[Vi, 0].ulocal
                self.Uvectors[Vi, 0].u_r = RotMatrix90(self.Uvectors[Vi, 0].u)
        # %%% Force elements
        self.nF = len(self.Forces)
        for Fi in range(self.nF):
            #  define switch
            if self.Forces[Fi, 0].type == "weight":
                ug = self.Forces[Fi, 0].gravity * self.Forces[Fi, 0].wgt
                for Bi in range(1, self.nB):
                    self.Bodies[Bi, 0].wgt = self.Bodies[Bi, 0].m * ug
            elif self.Forces[Fi, 0].type == "ptp":
                Pi = self.Forces[Fi, 0].iPindex
                Pj = self.Forces[Fi, 0].jPindex
                self.Forces[Fi, 0].iBindex = self.Points[Pi, 0].Bindex
                self.Forces[Fi, 0].jBindex = self.Points[Pj, 0].Bindex
        # %%% self.Joints
        self.nJ = len(self.Joints)
        cfriction = 0  # Assigned to but never used
        #  Assign number of constraints and number of bodies to each joint type
        for Ji in range(self.nJ):
            #  define switch
            if self.Joints[Ji, 0].type == "rev":
                self.Joints[Ji, 0].mrows = 2
                self.Joints[Ji, 0].nbody = 2
                Pi = self.Joints[Ji, 0].iPindex
                Pj = self.Joints[Ji, 0].jPindex
                Bi = self.Points[Pi, 0].Bindex
                self.Joints[Ji, 0].iBindex = Bi
                Bj = self.Points[Pj, 0].Bindex
                self.Joints[Ji, 0].jBindex = Bj
                if self.Joints[Ji, 0].fix == 1:
                    self.Joints[Ji, 0].mrows = 3
                    if Bi == -1:
                        self.Joints[Ji, 0].p0 = -self.Bodies[Bj, 0].p
                    elif Bj == -1:
                        self.Joints[Ji, 0].p0 = self.Bodies[Bi, 0].p
                    else:
                        self.Joints[Ji, 0].p0 = (
                            self.Bodies[Bi, 0].p - self.Bodies[Bj, 0].p
                        )
            elif self.Joints[Ji, 0].type == "tran":
                self.Joints[Ji, 0].mrows = 2
                self.Joints[Ji, 0].nbody = 2
                Pi = self.Joints[Ji, 0].iPindex
                Pj = self.Joints[Ji, 0].jPindex
                Bi = self.Points[Pi, 0].Bindex
                self.Joints[Ji, 0].iBindex = Bi
                Bj = self.Points[Pj, 0].Bindex
                self.Joints[Ji, 0].jBindex = Bj
                if self.Joints[Ji, 0].fix == 1:
                    self.Joints[Ji, 0].mrows = 3
                    if Bi == -1:
                        self.Joints[Ji, 0].p0 = np.linalg.norm(
                            self.Points[Pi, 0].rP
                            - self.Bodies[Bj, 0].r
                            - self.Bodies[Bj, 0].A @ self.Points[Pj, 0].sPlocal
                        )
                    elif Bj == -1:
                        self.Joints[Ji, 0].p0 = np.linalg.norm(
                            self.Bodies[Bi, 0].r
                            + self.Bodies[Bi, 0].A @ self.Points[Pi, 0].sPlocal
                            - self.Points[Pj, 0].rP
                        )
                    else:
                        self.Joints[Ji, 0].p0 = np.linalg.norm(
                            self.Bodies[Bi, 0].r
                            + self.Bodies[Bi, 0].A @ self.Points[Pi, 0].sPlocal
                            - self.Bodies[Bj, 0].r
                            - self.Bodies[Bj, 0].A @ self.Points[Pj, 0].sPlocal
                        )
            elif self.Joints[Ji, 0].type == "rev-rev":
                self.Joints[Ji, 0].mrows = 1
                self.Joints[Ji, 0].nbody = 2
                Pi = self.Joints[Ji, 0].iPindex
                Pj = self.Joints[Ji, 0].jPindex
                self.Joints[Ji, 0].iBindex = self.Points[Pi, 0].Bindex
                self.Joints[Ji, 0].jBindex = self.Points[Pj, 0].Bindex
            elif self.Joints[Ji, 0].type == "rev-tran":
                self.Joints[Ji, 0].mrows = 1
                self.Joints[Ji, 0].nbody = 2
                Pi = self.Joints[Ji, 0].iPindex
                Pj = self.Joints[Ji, 0].jPindex
                self.Joints[Ji, 0].iBindex = self.Points[Pi, 0].Bindex
                self.Joints[Ji, 0].jBindex = self.Points[Pj, 0].Bindex
            elif self.Joints[Ji, 0].type == "rel-rot":
                self.Joints[Ji, 0].mrows = 1
                self.Joints[Ji, 0].nbody = 1
            elif self.Joints[Ji, 0].type == "rel-tran":
                self.Joints[Ji, 0].mrows = 1
                self.Joints[Ji, 0].nbody = 1
            elif self.Joints[Ji, 0].type == "disc":
                self.Joints[Ji, 0].mrows = 2
                self.Joints[Ji, 0].nbody = 1
            elif self.Joints[Ji, 0].type == "rigid":
                self.Joints[Ji, 0].mrows = 3
                self.Joints[Ji, 0].nbody = 2
                Bi = self.Joints[Ji, 0].iBindex
                Bj = self.Joints[Ji, 0].jBindex
                if Bi == -1:
                    self.Joints[Ji, 0].d0 = (
                        -self.Bodies[Bj, 0].A.T @ self.Bodies[Bj, 0].r
                    )
                    self.Joints[Ji, 0].p0 = -self.Bodies[Bj, 0].p
                elif Bj == -1:
                    self.Joints[Ji, 0].d0 = self.Bodies[Bi, 0].r
                    self.Joints[Ji, 0].p0 = self.Bodies[Bi, 0].p
                else:
                    self.Joints[Ji, 0].d0 = self.Bodies[Bj, 0].A.T @ (
                        self.Bodies[Bi, 0].r - self.Bodies[Bj, 0].r
                    )
                    self.Joints[Ji, 0].p0 = self.Bodies[Bi, 0].p - self.Bodies[Bj, 0].p
        # %%% Functions
        # NOTE: TODO: Need to still properly port the functions
        # TODO TODO
        # #Requires defining FunctionData
        # self.nFc = len(self.Functs)
        # if self.Functs.size == 0:
        #    # pass
        # #else:
        #    # #for Ci in range(1,self.nFc):
        #        # #functionData(Ci)
        #  Compute number of constraints and determine row/column pointer
        self.nConst = 0
        # for Ji in range(1,self.nJ):
        #    # self.Joints[Ji, 0].rows = self.nConst
        #    # self.Joints[Ji, 0].rowe = self.nConst + self.Joints[Ji, 0].mrows
        #    # self.nConst = self.Joints[Ji, 0].rowe
        #    # Bi = self.Joints[Ji, 0].iBindex
        #    # if Bi != -1:
        #        # self.Joints[Ji, 0].colis = 3 * (Bi)
        #        # self.Joints[Ji, 0].colie = 3 * Bi + 1
        #    # Bj = self.Joints[Ji, 0].jBindex
        #    # if Bj != -1:
        #        # self.Joints[Ji, 0].coljs = 3 * (Bj)
        #        # self.Joints[Ji, 0].colje = 3 * Bj + 1

    #  -------------------------------------------------------------------------
    # def u_to_Bodies(self, u):
    #    # for Bi in range(1,self.nB):
    #        # ir  = self.Bodies[Bi, 0].irc
    #        # ird = self.Bodies[Bi, 0].irv
    #        # self.Bodies[Bi, 0].r  = np.atleast_2d( u[ir:ir +1 +1].flatten() ).T
    #        # self.Bodies[Bi, 0].p  = u[ir+2]
    #        # self.Bodies[Bi, 0].r_d = np.atleast_2d( u[ird:ird +1 +1].flatten() ).T
    #        # self.Bodies[Bi, 0].p_d = u[ird+2]
    #    # return None
    #  -------------------------------------------------------------------------
    # def Bodies_to_u(self, u):
    #    # u = np.zeros((self.nB6,1))
    #    # for Bi in range(1,self.nB):
    #        # ir  = self.Bodies[Bi, 0].irc
    #        # ird = self.Bodies[Bi, 0].irv
    #        # u[ir:ir+2+1]   = np.atleast_2d(np.concatenate((self.Bodies[Bi, 0].r, self.Bodies[Bi, 0].p),axis=None)).T
    #        # u[ird:ird+2+1] = np.atleast_2d(np.concatenate((self.Bodies[Bi, 0].r_d, self.Bodies[Bi, 0].p_d),axis=None)).T
    #    # return u
    # # Transfer self.Bodies to u
    #  -------------------------------------------------------------------------
    # def Bodies_to_u_d(self):
    #    # u_d = np.zeros((self.nB6, 1))
    #    # for Bi in range(1, self.nB):
    #        # ir = self.Bodies[Bi, 0].irc
    #        # ird = self.Bodies[Bi, 0].irv
    #        # u_d[ir:ir + 2+1] = np.atleast_2d(np.concatenate((self.Bodies[Bi, 0].r_d, self.Bodies[Bi, 0].p_d), axis=None)).T
    #        # u_d[ird:ird + 2+1] = np.atleast_2d(np.concatenate((self.Bodies[Bi, 0].r_dd, self.Bodies[Bi, 0].p_dd), axis=None)).T
    #    # return u_d
    #  -------------------------------------------------------------------------
    # def Update_Position(self):
    #    # # Compute A's
    #    # for Bi in range(1, self.nB):
    #        # B_A_ = np.concatenate( (RotMatrix(self.Bodies[Bi, 0].p)), axis=None)
    #        # B_A_1 = np.array([ [ B_A_[0],B_A_[1] ] ])
    #        # B_A_2 = np.array([ [ B_A_[2],B_A_[3] ] ])
    #        # self.Bodies[Bi, 0].A = np.concatenate( (B_A_1, B_A_2),axis=0)
    #    # # Compute sP = A  *  sP_prime; rP = r + sP
    #    # for Pi in range(1, self.nP):
    #        # Bi = self.Points[Pi, 0].Bindex
    #        # if Bi != 0:
    #            # self.Points[Pi, 0].sP = np.matmul(self.Bodies[Bi, 0].A, self.Points[Pi, 0].sPlocal)
    #            # self.Points[Pi, 0].sP_r = RotMatrix90(self.Points[Pi, 0].sP)
    #            # self.Points[Pi, 0].rP = self.Bodies[Bi, 0].r + self.Points[Pi, 0].sP
    #    # for Vi in range(1, self.nU):
    #        # Bi = self.Uvectors[Vi, 0].Bindex
    #        # if Bi != 0:
    #            # self.Uvectors[Vi, 0].u = np.matmul(self.Bodies[Bi, 0].A, self.Uvectors[Vi, 0].ulocal)
    #            # self.Uvectors[Vi, 0].u_r = RotMatrix90(self.Uvectors[Vi, 0].u)
    # #%%% Update_Velocity
    #  -------------------------------------------------------------------------
    # def Update_Velocity(self):
    #    # for Pi in range(1, self.nP):
    #        # Bi = self.Points[Pi, 0].Bindex
    #        # if Bi != 0:
    #            # self.Points[Pi, 0].sP_d = self.Points[Pi, 0].sP_r * self.Bodies[Bi, 0].p_d
    #            # self.Points[Pi, 0].rP_d = self.Bodies[Bi, 0].r_d + self.Points[Pi, 0].sP_d
    #    # # Compute u_dot vectors
    #    # for Vi in range(1, self.nU):
    #        # Bi = self.Uvectors[Vi, 0].Bindex
    #        # if Bi != 0:
    #            # self.Uvectors[Vi, 0].u_d = self.Uvectors[Vi, 0].u_r * self.Bodies[Bi, 0].p_d


folder = sys.argv[1]
solver = DapSolver(folder)
solver.initialize()
for i in range(solver.nB):
    print("Bodies", i)
    print(solver.Bodies[i, 0])
for i in range(Points.shape[0]):
    print("Points", i)
    print(solver.Points[i, 0])
for i in range(Forces.shape[0]):
    print("Forces", i)
    print(solver.Forces[i, 0])
for i in range(Functs.shape[0]):
    print("Functs", i)
    print(solver.Functs[i, 0])
for i in range(Joints.shape[0]):
    print("Joints", i)
    print(solver.Joints[i, 0])
for i in range(Uvectors.shape[0]):
    print("Uvectors", i)
    print(solver.Uvectors[i, 0])
    # print(solver.Bodies[i, 0]     )
    # print(solver.Bodies[i, 0].J     )
    # print(solver.Bodies[i, 0].r     )
    # print(solver.Bodies[i, 0].p     )
    # print(solver.Bodies[i, 0].r_d   )
    # print(solver.Bodies[i, 0].p_d   )
    # print(solver.Bodies[i, 0].A     )
    # print(solver.Bodies[i, 0].r_dd  )
    # print(solver.Bodies[i, 0].p_dd  )
    # print(solver.Bodies[i, 0].irc   )
    # print(solver.Bodies[i, 0].irv   )
    # print(solver.Bodies[i, 0].ira   )
    # #print(solver.Bodies[, 0i])
    # print(solver.Bodies[i, 0].m_inv )
    # print(solver.Bodies[i, 0].J_inv )
    # print(solver.Bodies[i])
    # print(solver.Bodies[i])
    # #print(solver.Bodies[i])
    # print(solver.Bodies[i])
# print(solver.Forces  )
# print(solver.Functs  )
# print(solver.Joints  )
# print(solver.Points  )
# print(solver.Uvectors)
