import numpy as np
import datetime
from time import perf_counter_ns as pns
import polars as pl


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

-------------------------------------------------------------
_____________________________________________________________________________

Sample use of the complete code is as follows.

--------------------------------------------------------------
if __name__ ==  '__main__':
    
    #some arrays 
    atoms,bonds,angles,dihedrals = make_up_arrays(size=20000)
    
    #create DataFile object
    datafile = DataFile(atoms,
                        bonds,
                        angles,
                        dihedrals,
                        atoms_style='angle',
                        min_boundaries=True,)

    #write to file
    #this will write the data file in the LAMMPS compatible format
    datafile.to_file('example.data')


    #print the object	
    print(datafile)
    

----------------------------------------------------------------
______________________________________________________________________________

"""

# additional functions for utilities
def timer(func):
    def wrapper(*args,**kwargs):
        start = pns()
        func(*args,**kwargs)
        time_diff = pns()-start
        print(f'{(time_diff*1e-6):.2f}ms')
        return
    return wrapper

def blue(text:str)->str:
    '''Converts the text to blue color in the terminal.'''
    return f'\033[94m{text}\033[0m'

def red(text:str)->str:
    '''Converts the text to red color in the terminal.'''
    return f'\033[91m{text}\033[0m'

def make_up_arrays(size:int=260):
    """
    Just making up some arrays for testing

    Parameters
    ----------
    size : int, optional
        Number of atoms. The default is 260.

    Returns
    -------
    atoms : pl.DataFrame
        2D atoms Array.
    bonds : np.ndarray
        2D bonds Array.
    angles : np.ndarray
        2D angles Array.

    """
    #arrays
    atoms = np.random.rand(size,6).astype(np.float32)
    atoms = atoms*120-60
    atoms = atoms**2/10 # for test only
    bonds = np.ones([size,4]).astype(int)
    angles = np.ones([size,5]).astype(int)
    dihedrals = np.ones([size,6]).astype(int)
    
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

    atoms = pl.DataFrame(atoms,schema=['atom-id','atom-type','mol-type','x-coor','y-coor','z-coor'])
    
    #for bonds
    bonds[:,1] = 1
    bonds[:100,1] = 2
    bonds[-100:,1] = 3
    
    #for angles
    angles[:,1] = 1
    angles[:100,1] = 2
    angles[-100:,1] = 3

    #for dihedrals
    dihedrals[:,1] = 1
    dihedrals[:100,1] = 2
    dihedrals[-100:,1] = 3
    
    return atoms,bonds,angles,dihedrals

def arr2str(arr:np.ndarray|None,name:str,style:str|None=None)->str:
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
    
    # guard clause in case of None, returns empty str
    if arr is None:
        return ""
    
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
    text = f'LAMMPS Data file -- Created in:{date:%D}\n\n'
    for tup in arr_tup:

        if tup[0] is None:
            continue
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

def min_simulation_box(atoms:pl.DataFrame, extra_margin=1)->str:
    """
    Find the minimum boundaries for the simulation box.

    Parameters
    ----------
    atoms : np.ndarray
        Atoms array.

    Returns
    -------
    str
        Simulation box description text.

    """

    maxs = atoms.select(['x-coor','y-coor','z-coor']).max().to_numpy().flatten()+extra_margin
    mins = atoms.select(['x-coor','y-coor','z-coor']).min().to_numpy().flatten()-extra_margin
    xhi,yhi,zhi = np.ceil(maxs)
    xlo,ylo,zlo = np.floor(mins)
    
    return simulation_box(xhi=xhi,yhi=yhi,zhi=zhi,mirror=False,xlo=xlo,ylo=ylo,zlo=zlo)


class DataFile:
    def __init__(self,
                 atoms:pl.DataFrame,
                 bonds:np.ndarray|None=None,
                 angles:np.ndarray|None=None,
                 dihedrals:np.ndarray|None=None,
                 *,
                 min_boundaries:bool=True,
                 atoms_style:str='angle',
                 xhi:float=30,
                 yhi:float=30,
                 zhi:float=30,
                 mirror_box:bool=True
                 ) -> None:
        #numpy array forms
        self.atoms = atoms.to_numpy()
        self.bonds = bonds
        self.angles = angles
        self.dihedrals = dihedrals
        #string forms
        self.atoms_str = arr2str(atoms.to_numpy(),'Atoms',style=atoms_style) #cannot be None
        self.bonds_str = arr2str(bonds,'Bonds') # if bonds is not None else ""
        self.angles_str = arr2str(angles,'Angles') # if angles is not None else ""
        self.dihedrals_str= arr2str(dihedrals,'Dihedrals') # if dihedrals is not None else ""
        #description
        self.description = describe(
            (atoms,'atoms'),
            (bonds,'bonds'),
            (angles,'angles'),
            (dihedrals,'dihedrals')
        )
        #simulation box
        if not min_boundaries:
            self.simulation_box = simulation_box(xhi,yhi,zhi,mirror=mirror_box)
        elif min_boundaries:
            self.simulation_box = min_simulation_box(atoms)

    def __repr__(self)->str:
        """        
        Merges the strings to create the full data file text.
        Such as description, simulation box, atoms_str, bonds_str, angles_str, dihedrals_str.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Merged string 
            OR
            The full data file text.

        """

        strings = [self.description,
                   self.simulation_box,
                   self.atoms_str,
                   self.bonds_str,
                   self.angles_str,
                   self.dihedrals_str]

        # create DataFile text by appending the strings
        full_str = ''
        for string in strings:
            if string != "":
                full_str+=string
        
        return full_str
    
    def __len__(self)->int:
        '''Number of lines in the data file.'''
        return self.__repr__().count('\n')+1
    
    def __str__(self)->str:
        '''String representation of the object. Will be used for print() function.'''
        class_name = self.__class__.__name__
        description = self.description # removing the last two newlines
        return f'{red(class_name)} Object\n{blue(description+self.simulation_box)}'
    
    def to_file(self,fname:str)->None:
        '''Write the datafile to a file with given name (fname).'''
        with open(fname,'w') as f:
            f.write(self.__repr__())
        return

    # END OF CLASS                


@timer
def main():
    atoms,bonds,angles,dihedrals = make_up_arrays(size=20000)
    datafile = DataFile(atoms,
                        bonds,
                        None,
                        dihedrals,
                        atoms_style='angle',
                        min_boundaries=True,)
    datafile.to_file('example.data')
    print(datafile)
    return

if __name__ ==  '__main__':
    main()


    """
    #some arrays 
    atoms,bonds,angles,dihedrals = make_up_arrays(size=20000)
    
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
    
    """
