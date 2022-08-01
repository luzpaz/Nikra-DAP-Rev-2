# Cecil Churms <churms@gmail.com>

import numpy as np

# Select if we want to be in debug mode
global Debug
Debug = True

#  -------------------------------------------------------------------------
def RotMatrix(p):
    """ This function sets up a rotational transformation matrix """
    
    c = np.cos(p)
    s = np.sin(p)
    A = np.array([[c, -s],
                  [s,  c]])
    return A


#  -------------------------------------------------------------------------
def RotMatrix90(s):
    """ This function rotates an array 90degrees positively """

    s_r = np.array([[-s[1, 0]],
                    [ s[0, 0]]])  # //??????????????????????????????????????????/
    return s_r
