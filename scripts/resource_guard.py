"""Resource containment for deterministic test and build runners.

Provides a system admission guard (free disk, available memory, commit
headroom), Windows Job Object containment for child process trees (kill on
close, low scheduling priority, job memory ceiling, peak memory reporting) and
a portable fallback that only lowers priority elsewhere. No model or network
calls. Thresholds are overridable through environment variables so a bounded
diagnostic run can relax them deliberately; the defaults refuse to start work
on a machine that is already short of disk or memory.
"""
import ctypes as C
import os
import pathlib
import shutil
import subprocess
import sys
import math

GB = 1024 ** 3
DEFAULTS = {
    # Free space required on the volume that receives build outputs.
    'FFTA_MIN_FREE_DISK_GB': 40,
    # Physical memory that must be available before a step starts.
    'FFTA_MIN_AVAILABLE_MEMORY_GB': 8,
    # Commit charge headroom (page file + RAM) that must remain.
    'FFTA_MIN_COMMIT_HEADROOM_GB': 16,
    # Ceiling for the committed memory of one step's whole process tree.
    'FFTA_STEP_MEMORY_LIMIT_GB': 24,
}


def setting(name):
    value = os.environ.get(name)
    result = float(value) if value else float(DEFAULTS[name])
    if not math.isfinite(result) or result <= 0:
        raise ValueError(name + ' must be a positive finite number')
    return result


class MEMORYSTATUSEX(C.Structure):
    _fields_ = [('dwLength', C.c_uint32), ('dwMemoryLoad', C.c_uint32),
                ('ullTotalPhys', C.c_uint64), ('ullAvailPhys', C.c_uint64),
                ('ullTotalPageFile', C.c_uint64), ('ullAvailPageFile', C.c_uint64),
                ('ullTotalVirtual', C.c_uint64), ('ullAvailVirtual', C.c_uint64),
                ('ullAvailExtendedVirtual', C.c_uint64)]


def memory_status():
    """Return available physical memory and commit headroom in bytes."""
    if os.name == 'nt':
        status = MEMORYSTATUSEX()
        status.dwLength = C.sizeof(status)
        if not C.windll.kernel32.GlobalMemoryStatusEx(C.byref(status)):
            raise OSError('GlobalMemoryStatusEx failed')
        return {'availablePhysical': status.ullAvailPhys, 'totalPhysical': status.ullTotalPhys,
                'commitAvailable': status.ullAvailPageFile, 'commitLimit': status.ullTotalPageFile}
    page = os.sysconf('SC_PAGE_SIZE')
    total = os.sysconf('SC_PHYS_PAGES') * page
    available = os.sysconf('SC_AVPHYS_PAGES') * page
    return {'availablePhysical': available, 'totalPhysical': total,
            'commitAvailable': available, 'commitLimit': total}


def snapshot(root):
    usage = shutil.disk_usage(root)
    memory = memory_status()
    return {'freeDiskGB': round(usage.free / GB, 2), 'totalDiskGB': round(usage.total / GB, 2),
            'availableMemoryGB': round(memory['availablePhysical'] / GB, 2),
            'commitHeadroomGB': round(memory['commitAvailable'] / GB, 2),
            'commitLimitGB': round(memory['commitLimit'] / GB, 2)}


def admission_problems(root):
    """List human-readable reasons the system should not accept heavy work."""
    state = snapshot(root)
    problems = []
    if state['freeDiskGB'] < setting('FFTA_MIN_FREE_DISK_GB'):
        problems.append(f"free disk {state['freeDiskGB']} GB is below "
                        f"{setting('FFTA_MIN_FREE_DISK_GB'):g} GB on {pathlib.Path(root).anchor}")
    if state['availableMemoryGB'] < setting('FFTA_MIN_AVAILABLE_MEMORY_GB'):
        problems.append(f"available memory {state['availableMemoryGB']} GB is below "
                        f"{setting('FFTA_MIN_AVAILABLE_MEMORY_GB'):g} GB")
    if state['commitHeadroomGB'] < setting('FFTA_MIN_COMMIT_HEADROOM_GB'):
        problems.append(f"commit headroom {state['commitHeadroomGB']} GB is below "
                        f"{setting('FFTA_MIN_COMMIT_HEADROOM_GB'):g} GB")
    return state, problems


class WorkspaceLock:
    """Exclusive lock shared by the runner and the pruner.

    The OS lock releases on process exit; a leftover file is not a live lock.
    """
    def __init__(self, path):
        self.path = pathlib.Path(path)

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.path.open('a+b')
        self.stream.seek(0)
        self.stream.write(b'0')
        self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise RuntimeError('Another expansion test runner owns this workspace') from None
        return self

    def __exit__(self, *args):
        self.stream.close()


def require_admission(root, label='run'):
    state, problems = admission_problems(root)
    if problems:
        raise SystemExit(f'Refusing to start {label}: ' + '; '.join(problems)
                         + '. Free space or memory first, or override FFTA_MIN_* deliberately.')
    return state


# --- Windows Job Object containment -----------------------------------------

JOB_OBJECT_LIMIT_PRIORITY_CLASS = 0x20
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_LIMIT_JOB_MEMORY = 0x200
JobObjectExtendedLimitInformation = 9
BELOW_NORMAL_PRIORITY_CLASS = 0x4000


class IO_COUNTERS(C.Structure):
    _fields_ = [(name, C.c_uint64) for name in
                ('ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
                 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(C.Structure):
    _fields_ = [('PerProcessUserTimeLimit', C.c_int64), ('PerJobUserTimeLimit', C.c_int64),
                ('LimitFlags', C.c_uint32), ('MinimumWorkingSetSize', C.c_size_t),
                ('MaximumWorkingSetSize', C.c_size_t), ('ActiveProcessLimit', C.c_uint32),
                ('Affinity', C.c_size_t), ('PriorityClass', C.c_uint32),
                ('SchedulingClass', C.c_uint32)]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(C.Structure):
    _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION),
                ('IoInfo', IO_COUNTERS), ('ProcessMemoryLimit', C.c_size_t),
                ('JobMemoryLimit', C.c_size_t), ('PeakProcessMemoryUsed', C.c_size_t),
                ('PeakJobMemoryUsed', C.c_size_t)]


class ContainedProcess:
    """Run one command as a contained process tree.

    On Windows the child and every descendant join a Job Object that dies with
    this handle, runs at below-normal priority and cannot commit more than the
    configured ceiling. Peak job memory is reported after completion. On other
    systems only the priority is lowered; descendants are killed by process
    group on timeout.
    """

    def __init__(self, command, memory_limit_bytes=None, **popen_arguments):
        self.command = command
        self.job = None
        self.peak_bytes = None
        self.limit_bytes = memory_limit_bytes
        if os.name == 'nt':
            popen_arguments.setdefault('creationflags', 0)
            # Suspend before any user code can create descendants. Assignment
            # after ordinary Popen races the child's first process creation.
            popen_arguments['creationflags'] |= BELOW_NORMAL_PRIORITY_CLASS | 0x4
            self.job = self._create_job()
            try:
                self.process = subprocess.Popen(command, **popen_arguments)
                handle = C.c_void_p(int(self.process._handle))
                if not C.windll.kernel32.AssignProcessToJobObject(self.job, handle):
                    raise OSError('AssignProcessToJobObject failed: ' + str(C.GetLastError()))
                resume = C.windll.ntdll.NtResumeProcess
                resume.argtypes = [C.c_void_p]
                resume.restype = C.c_long
                status = resume(handle)
                if status != 0:
                    raise OSError('NtResumeProcess failed: ' + hex(status & 0xffffffff))
            except BaseException:
                if hasattr(self, 'process'):
                    self.process.kill()
                    self.process.wait()
                self.close()
                raise
        else:
            popen_arguments.setdefault('start_new_session', True)
            self.process = subprocess.Popen(command, preexec_fn=lambda: os.nice(10), **popen_arguments)

    def _create_job(self):
        kernel = C.windll.kernel32
        kernel.CreateJobObjectW.restype = C.c_void_p
        job = kernel.CreateJobObjectW(None, None)
        if not job:
            raise OSError('CreateJobObjectW failed')
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        info.BasicLimitInformation.LimitFlags = (JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
                                                 | JOB_OBJECT_LIMIT_PRIORITY_CLASS)
        info.BasicLimitInformation.PriorityClass = BELOW_NORMAL_PRIORITY_CLASS
        if self.limit_bytes:
            info.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_JOB_MEMORY
            info.JobMemoryLimit = int(self.limit_bytes)
        if not kernel.SetInformationJobObject(C.c_void_p(job), JobObjectExtendedLimitInformation,
                                              C.byref(info), C.sizeof(info)):
            kernel.CloseHandle(C.c_void_p(job))
            raise OSError('SetInformationJobObject failed')
        return C.c_void_p(job)

    def wait(self, timeout=None):
        try:
            return self.process.wait(timeout=timeout)
        finally:
            self._read_peak()

    def _read_peak(self):
        if self.job is None:
            return
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        if C.windll.kernel32.QueryInformationJobObject(self.job, JobObjectExtendedLimitInformation,
                                                       C.byref(info), C.sizeof(info), None):
            self.peak_bytes = int(info.PeakJobMemoryUsed)

    def terminate_tree(self):
        if self.job is not None:
            C.windll.kernel32.TerminateJobObject(self.job, 1)
        else:
            import signal
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            pass

    def close(self):
        if self.job is not None:
            self._read_peak()
            C.windll.kernel32.CloseHandle(self.job)
            self.job = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.process.poll() is None:
            self.terminate_tree()
        self.close()


def run_contained(command, timeout, **popen_arguments):
    """Run to completion. Returns (returncode or None on timeout, peak bytes)."""
    limit = setting('FFTA_STEP_MEMORY_LIMIT_GB') * GB
    with ContainedProcess(command, memory_limit_bytes=limit, **popen_arguments) as child:
        try:
            code = child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            child.terminate_tree()
            child._read_peak()
            return None, child.peak_bytes
        return code, child.peak_bytes


if __name__ == '__main__':
    import json
    state, problems = admission_problems(pathlib.Path(__file__).resolve().parents[1])
    print(json.dumps({'state': state, 'problems': problems, 'settings':
                      {k: setting(k) for k in DEFAULTS}}, indent=2))
    sys.exit(1 if problems else 0)
