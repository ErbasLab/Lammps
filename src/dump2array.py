import time
import numpy as np
import os

"""
Code for converting dumpfile into 3D Numpy Array for lower storage requirements
and for acquiring a more usable data format. By Zafer Kosar 2022.

______________________________________________________________________________
Sample use:
    
    
if __name__ == '__main__':
    arr = txt2arr(ftoread:'path/to/my/dumpfile') #
    np.save('dump.npy',arr) #note that generated array should be stored in a file.

"""


def txt2arr(ftoread: str = "dump.main", ignore: int = 0)->np.ndarray:
    """
    Transfers dump data into two 3D numpy array. 
    Each row is for an atom, atom index is not stored but the index of the row
    i == atom-index-1.
    Same for other dimension as index in python starts from 0.
    
    Sample 2D Array looks like the following...
    
    |atom-type|x-coor|y-coor|z-coor|
    ________________________________
         2    | 3.13 | 4.32 | -2.11|
    --------------------------------
                    ...
                    ...  
                    ...
    --------------------------------
                    
    3rd dimenion is Time or Step.
    Only the types and coordinates preserved.

    Parameters
    ----------
    ftoread : str, optional
        path/to/dumpfile. The default is "dump.main".
        
    ignore : int, optional
        First 'ignore' number of timestep will ignored or discarded. 
        The default is 0.

    Returns
    -------
    arr : np.ndarray
        3D Numpy Array generated from dumpfile.

    """
    
    tos = time.perf_counter() #start time

    ignore_num = ignore
    #reading dump file line-by-line--------------------------------------------
    dump = open(ftoread, "r")
    size = os.stat(ftoread).st_size #checking the file size
    lines = dump.readlines()
    dump.close()

    #finding number of atoms
    number_atom = int(lines[3]) #dumpfile declares number of atoms in the line4
    batch = number_atom + 9 #in every batch 9 lines are description lines
    
    atom_types = list()
    for a in lines[9:batch]:
        atom_types.append(int(a.split()[1]))
    
    atom_types = np.sort(np.array(atom_types))
    types, counts = np.unique(atom_types, return_counts=True)

    types_str = ''
    for typ,count in zip(types,counts):
        types_str += f'Number of atoms of type {typ}:\t{count}\n'

    
    #number of the timesteps---------------------------------------------------
    time_num = int(len(lines)/batch)
    #creating an array of zeros with intented size-----------------------------
    time_interval = time_num-ignore_num
    arr =  np.zeros([time_interval,number_atom,4],dtype=np.float32)
    
    #for loop to browse through time of array from the dump file---------------
    for i in range(ignore_num,time_num):
        
        #for loop to make the 3D array-----------------------------------------
        for k in range(number_atom):

            values = lines[i*batch+k+9].split()
            atomID = int(values[0])
            
            #polymer atoms
            if True:
                arr[i-ignore,atomID-1,0] = float(values[1])
                arr[i-ignore,atomID-1,1] = float(values[2])
                arr[i-ignore,atomID-1,2] = float(values[3])
                arr[i-ignore,atomID-1,3] = float(values[4])
    
    tof = time.perf_counter() #finish time
    '''retired progressbar

    
        if (i>ignore_num and i%int(time_interval/100)==0) or i == time_num-1 :
            progressbar(i-ignore_num, time_interval, tof-tos, prefix = "progress")
    '''
        
    with open('summary.txt','w') as summary:
        summary.write(types_str)
        summary.write(f'Dump file size: \t\t\t{size/(2**30):.2f} GB\n')
        summary.write(f'Numpy Array Size: \t\t{arr.size*arr.itemsize/2**30:.2f} GB\n')
        summary.write(f'Compression level: \t\t{100-arr.size*arr.itemsize/size*100:.2f}%\n')
        summary.write(f'Conversion Time: \t\t\t{tof-tos:.1f} seconds\n')
        
    
    print(f'DONE in {tof-tos:.1f} Seconds')
    return arr

if __name__ == '__main__':
    arr = txt2arr() #
    np.save('dump.npy',arr) #note that generated array should be stored in a file
    
    #if wanted for testing small portion of timestep can also be stored in a different file
    arr_small = arr[-1000:]
    np.save('small.npy',arr_small)