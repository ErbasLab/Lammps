import numpy as np
from typing import Optional
import datetime

"""
Code for making a LAMMPS data file from arrays. By Zafer Kosar 2022.

Arrays must be 2-dimensional Numpy Arrays in the following format.

Number of Rows = Particle or Atoms Number
Number of Columns = Depends on the Atoms # {Style}

| atom-id | atom-type | mol-type |  x-coor  |  y-coor  |  z-coor  |
___________________________________________________________________
|    1    |     2     |    2     | 33.54612 | -34.1297 | 6.121313 |
-------------------------------------------------------------------
                                ...
                                ...
                                ...
                                ...
-------------------------------------------------------------------
|   1071  |     1     |    1     | 66.54612 | 44.21379 | 120.0987 |
-------------------------------------------------------------------

Note that this is Atoms array in the 'angles' style which requires 6 columns.
Other style may employ different numbers of columns. Check the LAMMPS manual.
_____________________________________________________________________________


Arrays can be:
    1- Atoms(Must) :
        -> |atom-id|atom-type|mol-type|x-coor|y-coor|z-coor|
        
    2- Bonds       :
        -> |bond-id|bond-type|atom-id_1|atom-id_2|
        
    3- Angles      :
        -> |angle-id|angle-type|atom-id_1|atom-id_2|atom-id_3|
        
    4- Dihedrals   :
        -> |angle-id|angle-type|atom-id_1|atom-id_2|atom-id_3|atom-id_4|
        
    ...etc.,

_____________________________________________________________________________
function 'make_up_arrays' just creates sample arrays (i.e., atoms,bonds,angles)
for testing also giving an idea of the array structures.

_____________________________________________________________________________
function 'arr2str' generates a string from array in a file-writable format.

_____________________________________________________________________________
function 'describe' generates a string required in the beginning of data file.

e.g.,
-----------------------------------------
LAMMPS Data file -- Created in:2022-11-07

20000 atoms
3 atom types
20000 bonds
3 bond types
20000 angles
3 angle types
-----------------------------------------
_____________________________________________________________________________
function 'simulation_box' generates a string containing boundary information 
for the data file.

e.g.,
----------------------
-60.123 60.123 xlo xhi
-60.123 60.123 ylo yhi
-60.123 60.123 zlo zhi
----------------------
_____________________________________________________________________________
function 'unite_strings' unites the strings to form a complete string to be
written to a file.

Note that the order here is important and should be in the following order.
-------------------------------------------------------------
whole_str = unite_strings(description, #from 'describe'
                         box_str,      #from 'simulation_box'
                         atoms_str,    #from 'arr2str'
                         bonds_str,    #from 'arr2str'
                         angles_str,   #from 'arr2str'
                         .
                         .
                         .
                         )
-------------------------------------------------------------
_____________________________________________________________________________

Sample use of the complete code is as follows.

--------------------------------------------------------------
if __name__ ==  '__main__':
    
    #some arrays 
    atoms,bonds,angles = make_up_arrays(size=20000)
    
    #initial text describing component
    description = describe((atoms,'atoms'),
                           (bonds,'bonds'),
                           (angles,'angles'))
    
    #simulation box boundaries
    box_str = simulation_box(60.123,60.123,60.123,mirror=1,
                             xlo=55,ylo=31,zlo=15)
    
    #strings of arrays
    atoms_str = arr2str(arr=atoms,name='Atoms',style='angle')
    bonds_str = arr2str(arr=bonds,name='Bonds')
    angles_str = arr2str(arr=angles,name='Angles')
    
    #arrays united --note that order is important
    whole_str = unite_strings(description,
                             box_str,
                             atoms_str,
                             bonds_str,
                             angles_str)
    
    with open('deneme.data','w') as f:
        f.write(whole_str)

----------------------------------------------------------------
______________________________________________________________________________

"""

def make_up_arrays(size:int=260):
    """
    Just making up some arrays for testing

    Parameters
    ----------
    size : int, optional
        Number of atoms. The default is 260.

    Returns
    -------
    atoms : np.ndarray
        2D atoms Array.
    bonds : np.ndarray
        2D bonds Array.
    angles : np.ndarray
        2D angles Array.

    """
    #arrays
    atoms = np.random.rand(size,6).astype(np.float32)
    atoms =atoms*120-60
    bonds = np.ones([size,4]).astype(int)
    angles = np.ones([size,5]).astype(int)
    
    #setting their ids
    atoms[:,0] = np.arange(len(atoms))+1
    bonds[:,0] = np.arange(len(bonds))+1
    angles[:,0] = np.arange(len(angles))+1
    
    #setting the types
    #for atoms
    atoms[:,1] = 1
    atoms[:100,1] = 2
    atoms[-100:,1] = 3
    atoms[:,2] = atoms[:,1]
    
    #for bonds
    bonds[:,1] = 1
    bonds[:100,1] = 2
    bonds[-100:,1] = 3
    
    #for angles
    angles[:,1] = 1
    angles[:100,1] = 2
    angles[-100:,1] = 3
    
    return atoms,bonds,angles

def arr2str(arr:np.ndarray,name:str,style:Optional[str]=None)->str:
    """
    Turn array into str with the LAMMPS data file format.

    Parameters
    ----------
    arr : np.ndarray
        Array to be t.
    name : str
        Name of the array (Atoms, Angles, Bonds,...)
    style : str
        Style of the given array.

    Returns
    -------
    str
        String version of the array with the title of 'name # style'.

    """
    
    name = name.capitalize() #a precaution for format req.
    #initing strimng with the title 
    if style:
        style = style.lower()#another precuation for format req.
        string = f'{name} # {style}\n\n'
    else:
        string = f'{name}\n\n'
    
    #browsing through every value
    for row in arr:
        for val in row:
            #if the value is integer they are removed off their decimals
            if int(val) == val:
                string+= f'{int(val)} '
            else:
                string+= f'{val} '
        
        #go next line after every row        
        string+='\n'
    
    #leaving a gap for the next array to be written
    string+='\n'
    
    return string #final str is returned


def describe(*arr_tup:tuple)->str:
    """
    Description part of the data file.
    e.g.,
    1234 atoms
    12 atom type
    ...

    Parameters
    ----------
    *arr_tup : tuple
        Array itself and its Name as such (arr,tuple) e.g. (atoms,'atoms')

    Returns
    -------
    str
        Description of the simulation components.

    """
    date = datetime.datetime.now().date()
    text = f'LAMMPS Data file -- Created in:{date}\n\n'
    for tup in arr_tup:
        #seperating array and its name
        arr = tup[0]
        name = tup[1].lower()
        
        #forming the count line e.g., 1234 atoms
        count = len(arr) #size
        number_line = f'{count} {name}\n'
        
        #forming the type number line 
        type_column = arr[:,1]
        type_num = len(np.unique(type_column))
        type_line = f'{type_num} {name[:-1]} types\n'
        
        text+=number_line+type_line
    
    text += '\n\n'
    
    return  text
        

def simulation_box(xhi:float,yhi:float,zhi:float,
                   mirror:bool=True,**xyz_lows)->str:
    """
    

    Parameters
    ----------
    xhi : float
        x high boundary.
    yhi : float
        y high boundary.
    zhi : float
        z high boundary.
    mirror : bool, optional
        When True, mirrors the high boundaries as their negatives.
        The default is True.
    **xyz_lows : kwargs
        xlo,ylo,zlo.

    Raises
    ------
    ValueError
        if mirror==False and no xlo,ylo,zlo value given.

    Returns
    -------
    str
        Simulation box description text.

    """
    
    text = ''
    err = 'if mirror=False Keyword values of xlo,ylo,zlo must be given --> '
    eg =  'e.g xlo=value1,ylo=value2,zlo=value3'
    if mirror:
        xline=f'{-xhi} {xhi} xlo xhi\n'
        yline=f'{-yhi} {yhi} ylo yhi\n'
        zline=f'{-zhi} {zhi} zlo zhi\n'
        text+=xline+yline+zline
    else:
        if xyz_lows == dict():
            raise ValueError(err+eg)
        xlo = xyz_lows['xlo']
        ylo = xyz_lows['ylo']
        zlo = xyz_lows['zlo']    
            
        xline=f'{xlo} {xhi} xlo xhi\n'
        yline=f'{ylo} {yhi} ylo yhi\n'
        zline=f'{zlo} {zhi} zlo zhi\n'
        text+=xline+yline+zline
            
    text+='\n\n'
            
    return text

def unite_strings(*strings)->str:
    """
    Takes strings and unites them in input order.
    

    Parameters
    ----------
    *strings : str
        String parts.

    Returns
    -------
    str
        United string.

    """
    
    full_str = ''
    
    for string in strings:
        full_str+=string
    
    return full_str

        
if __name__ ==  '__main__':
    
    #some arrays 
    atoms,bonds,angles = make_up_arrays(size=20000)
    
    #initial text describing component
    description = describe((atoms,'atoms'),
                           (bonds,'bonds'),
                           (angles,'angles'))
    
    #simulation box boundaries
    box_str = simulation_box(60.123,60.123,60.123,mirror=1,
                             xlo=55,ylo=31,zlo=15)
    
    #strings of arrays
    atoms_str = arr2str(arr=atoms,name='Atoms',style='angle')
    bonds_str = arr2str(arr=bonds,name='Bonds')
    angles_str = arr2str(arr=angles,name='Angles')
    
    #arrays united --note that order is important
    whole_str = unite_strings(description,
                             box_str,
                             atoms_str,
                             bonds_str,
                             angles_str)
    
    with open('deneme.data','w') as f:
        f.write(whole_str)
