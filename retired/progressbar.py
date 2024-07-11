
def progressbar(step:int, length:int, time_elapsed:float,prefix :str= "Computing"):
    """
    Prints out a progressbar to see the progress of the current work.

    Parameters
    ----------
    step : int
        Current step.
    length : int
        Total number of steps.
    time_elapsed : float
        Total time from the start.
    prefix : str, optional
        Job name. The default is "Computing".

    Returns
    -------
    None.

    """    


    per = step/time_elapsed #performance
    remaining = length-step	#remaining steps

    #max bar length
    max_bar = 40
    step_norm = int(step/length*max_bar)
    remaining_norm = max_bar-step_norm

    eta = remaining/per

    unit = 's'
    if eta>60 and eta<3600:
        eta = eta/60
        unit = 'min'
    elif eta>3600:
        eta = eta/3600
        unit = 'h'

    ending = '\r'
    if step == length:
        ending = '\n'

    print(f'{prefix}: [{u"█"*step_norm}{" "*remaining_norm}]{step}/{length} -- Step/s:{per:.1f} -- ETA:{eta:.1f}{unit}     ',flush=True,end=ending)
