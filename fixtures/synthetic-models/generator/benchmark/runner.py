from enum import Enum
import subprocess
from subprocess import CompletedProcess
from types import Union
from typing import List

class ExecutableType(Enum):
    SCRAM = 'scram'
    XFTA = 'xfta'

RunnerTypes = {

}

class RunnerConfig(list):

    pass

class Result():
    pass

class Runner(object):

    def __init__(self, executable_type: ExecutableType):
        self.executable_type = executable_type

    # args, *, stdin = None, input = None, stdout = None, stderr = None, capture_output = False, shell = False, cwd = None, timeout = None, check = False, encoding = None, errors = None, text = None, env = None, universal_newlines = None, ** other_popen_kwargs)

    def run(self, config: RunnerConfig) -> any:
        args: List = config
        args.insert(0, self.executable_type)
        return subprocess.run(args=args)
