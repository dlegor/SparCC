from typing import Dict,Text,Tuple,Union,Any
from pathlib import Path
from shutil import rmtree
import math
import os

import sys
from pandas import Series
from numpy.random import RandomState

try:
    import psutil
except ImportError:
    psutil = None

__all__ = ["cpu_count",
           "CPU_COUNT",
           "check_memory_available",
           "system_sanity_check",
           "clean_data_folder"]


def cpu_count():
    """Get the available CPU count for this system.
    Takes the minimum value from the following locations:
    - Total system cpus available on the host.
    - CPU Affinity (if set)
    - Cgroups limit (if set)
    """
    count = os.cpu_count()

    # Check CPU affinity if available
    if psutil is not None:
        try:
            affinity_count = len(psutil.Process().cpu_affinity())
            if affinity_count > 0:
                count = min(count, affinity_count)
        except Exception:
            pass

    # Check cgroups if available
    if sys.platform == "linux":
        # The directory name isn't standardized across linux distros, check both
        for dirname in ["cpuacct,cpu", "cpu,cpuacct"]:
            try:
                with open("/sys/fs/cgroup/%s/cpu.cfs_quota_us" % dirname) as f:
                    quota = int(f.read())
                with open("/sys/fs/cgroup/%s/cpu.cfs_period_us" % dirname) as f:
                    period = int(f.read())
                # We round up on fractional CPUs
                cgroups_count = math.ceil(quota / period)
                if cgroups_count > 0:
                    count = min(count, cgroups_count)
                break
            except Exception:
                pass

    return count


CPU_COUNT = cpu_count()

def check_memory_available()->Dict[Text,float]:
    """
    If the  psutil packages is available, return a dictionary 
    with information about the memory: total, available and percentage of memory.
    """
    
    MemoryD=dict()

    if psutil==None:
        return None
    
    if psutil != None:
        mem=psutil.virtual_memory()
        MemoryD['Total Memory']=str(round(mem.total/1e9,2))+' GB'
        MemoryD['Available Memory']=str(round(mem.available/1e9,2))+' GB'
        MemoryD['Percent']=str(mem.percent)+'%'
        MemoryD['Num Core']=CPU_COUNT
        return MemoryD

def system_sanity_check(size:Tuple=None):
    """
    Check the memory required for the SparCC algorithm, 
    if your memory is insufficient, then the function raises an exception.

    """
    message1='You do not give information about some matrix to processing.'\
        'But the information available in your system is:\n'
    
    message1='You do not give information about some matrix to processing.'\
        'But the information available in your system is:\n'

    message2='The memory overflows, but the information of your systems is:\n'

    if size==None:
        print(message1)
        Info_Memory=check_memory_available()
        print(Series(Info_Memory,name='Information ').to_markdown())


    else:
         rs=RandomState()
         try:
             a=rs.randint(0,100,size=size)
             Size_a=a.nbytes/1e9
             Info_Memory=check_memory_available()
             Info_Memory['Size_Matrix']=Size_a
             #print(Series(Info_Memory,name='Information ').to_markdown())
             return Info_Memory

         except MemoryError as error:
            print("{}".format(error))
         else:
            
            print(message2)
            Info_Memory=check_memory_available()
            #print(Series(Info_Memory,name='Information ').to_markdown())
            return Info_Memory
        
def clean_data_folder(path_folder:Union[str,Path])->Any:
    
    path_folder=Path(path_folder)

    if path_folder.is_dir():
        rmtree(path_folder.resolve())
    else:
        raise EOFError("This is not a directory")







