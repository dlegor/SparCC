import math
import os
import sys
from pathlib import Path
from shutil import rmtree
from typing import Any

import numpy as np
from pandas import Series

try:
    import psutil
except ImportError:
    psutil = None

__all__ = ["CPU_COUNT",
           "check_memory_available",
           "clean_data_folder",
           "cpu_count",
           "system_sanity_check"]


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


def check_memory_available() -> dict[str, Any] | None:
    """
    If the psutil package is available, return a dictionary with information
    about the memory (total, available, percentage used) and the CPU count.
    Returns None when psutil is not installed.
    """
    if psutil is None:
        return None

    mem = psutil.virtual_memory()
    return {
        'Total Memory': str(round(mem.total / 1e9, 2)) + ' GB',
        'Available Memory': str(round(mem.available / 1e9, 2)) + ' GB',
        'Percent': str(mem.percent) + '%',
        'Num Core': CPU_COUNT,
    }


def system_sanity_check(size: tuple[int, ...] | None = None) -> dict[str, Any] | None:
    """
    Report the memory available for the SparCC algorithm.

    If ``size`` (the shape of a matrix to process) is given, try to allocate an
    integer matrix of that shape and add its size in GB to the report under
    'Size_Matrix'. A MemoryError is reported and re-raised.
    """
    info_memory = check_memory_available()

    if size is None:
        print('No matrix size was given. The information available in your system is:\n')
        if info_memory is not None:
            print(Series(info_memory, name='Information').to_string())
        return info_memory

    try:
        size_gb = np.zeros(size, dtype=np.int64).nbytes / 1e9
    except MemoryError:
        print('The memory overflows. The information available in your system is:\n')
        if info_memory is not None:
            print(Series(info_memory, name='Information').to_string())
        raise

    if info_memory is not None:
        info_memory['Size_Matrix'] = size_gb
    return info_memory


def clean_data_folder(path_folder: str | Path) -> None:
    """Recursively delete ``path_folder``, which must be a directory."""
    path_folder = Path(path_folder)

    if path_folder.is_dir():
        rmtree(path_folder.resolve())
    else:
        raise NotADirectoryError(f'"{path_folder}" is not a directory')
