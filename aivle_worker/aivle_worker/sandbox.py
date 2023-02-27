import hashlib
import logging
import os
import subprocess
from typing import List
import time

# import zmq

from .apis import ERROR_TIME_LIMIT_EXCEEDED, ERROR_RUNTIME_ERROR, ERROR_MEMORY_LIMIT_EXCEEDED
from .constants import SANDBOX_ONLY_TASK_ID
from .settings import PROFILE_PATH, TEMP_VENV_FOLDER, CREATE_VENV_PATH, ZMQ_PORT

logger = logging.getLogger("root")


def create_venv(req_path: str, force: bool = False) -> str:
    """
    Create virtual environment (NOTE: this step happens outside of any security sandbox)

    :param req_path: path to the requirements.txt file
    :param force: if True, the cached environment will be overwritten
    :return: venv name
    """
    with open(req_path, "r") as f:
        req_str = f.read()
        f.close()
    env_name = hashlib.md5(req_str.encode("ascii")).hexdigest()
    dst_path = os.path.join(TEMP_VENV_FOLDER, env_name)
    if os.path.exists(dst_path) and not force:
        return env_name
    subprocess.call(["chmod", "u+x", CREATE_VENV_PATH], stderr=subprocess.DEVNULL)
    # cmd = ["srun", "--time=10", CREATE_VENV_PATH, dst_path, req_path, GRADER_GYM_LOCATION]
    cmd = ["srun", "--time=10", CREATE_VENV_PATH, dst_path, req_path]
    # Reference: https://stackoverflow.com/a/4417735
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line, end="")
    for stderr_line in iter(popen.stderr.readline, ""):
        print(stderr_line, end="")
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    return env_name


def run_with_venv(env_name: str, command: List[str], task_id: int, job_id: int, celery_task_id: str, home: str = "",
                  rlimit: int = 0, vram_limit: int = 256, time_limit: int = 0) -> str:
    """
    Run `command` within venv named `env_name`

    :param celery_task_id:
    :param job_id: ID of Job model in aiVLE Web
    :param env_name: venv name
    :param command:
    :param home: path to the home directory (check --private={HOME} in Firejail doc)
    :param rlimit: RAM limit in MiB (<=0 means no limit,
    :param task_id: aiVLE task ID (NOT evaluation job/task ID)
    :param vram_limit: VRAM limit in MiB
    :param time_limit:

    :return: error type (defined as constants in api)
    """
    # if task_id is -1, then we're running with sandbox only, no need to communicate with warden
    # sandbox_only = task_id == SANDBOX_ONLY_TASK_ID
    # create bash file for Slurm job
    # TODO: vram_limit for Slurm
    bash_file_name = command[-1]
    # NOTE: make sure resource limits set for the task are below the resource limits specified in the Slurm server!
    with open(os.path.join(home, bash_file_name), "w") as fh:
        fh.writelines("#!/bin/bash\n")
        fh.writelines("#SBATCH --job-name=%s_%s\n" % (env_name.replace(' ', '_'), str(job_id)))
        fh.writelines("#SBATCH --output=%s\n" % os.path.join(home, "log.out"))
        fh.writelines("#SBATCH --partition=medium\n")
        fh.writelines("#SBATCH --time=%s:%s\n" % (str(int(time_limit / 60)), str(time_limit % 60)))
        fh.writelines("#SBATCH --ntasks=1\n")
        fh.writelines("#SBATCH --cpus-per-task=1\n")
        fh.writelines("#SBATCH --mem=%s\n" % (str(rlimit)))
        fh.writelines("#SBATCH --qos=normal\n")
        fh.writelines("#SBATCH --mail-type=ALL\n")
        fh.writelines("source %s/bin/activate\n" % os.path.join(TEMP_VENV_FOLDER, env_name.replace(' ', '\ ')))
        fh.writelines("python %s" % (os.path.join(home, "grader.py")))
        fh.close()
    #logger.debug(f"[SANDBOX | run_with_venv] command: {' '.join(full_cmd)}")
    # add log to follow Firejail
    # logfile = open(os.path.join(home, "stdout.log"), "w")
    subprocess.call(["chmod", "u+x", os.path.join(home, "bootstrap.sh")], stderr=subprocess.DEVNULL)
    full_cmd = [command[0], "-W", os.path.join(home, "bootstrap.sh")]
    # proc = subprocess.Popen(full_cmd, stdout=logfile, stderr=logfile, universal_newlines=True)
    return_code = subprocess.call(full_cmd, stderr=subprocess.DEVNULL)
    # NOTE: remove need for warden process communication
    # context = zmq.Context()
    # socket = context.socket(zmq.REQ)
    # if not sandbox_only:
    #     socket.connect(f"tcp://localhost:{ZMQ_PORT}")
    #     socket.send_pyobj({
    #         "message_type": "sandbox-start",
    #         "payload": {
    #             "job_id": job_id,
    #             "celery_task_id": celery_task_id,
    #             "pid": proc.pid,
    #             "vram_limit": vram_limit,
    #         },
    #     })
    #     _ = socket.recv()
    # error_type = None
    #if time_limit > 0:
    #    try:
    #        proc.wait(time_limit + 30)  # wait 30 more seconds
    #    except subprocess.TimeoutExpired:
    #        error_type = ERROR_TIME_LIMIT_EXCEEDED
    #else:
    # return_code = proc.wait()
    # if return_code != 0:
    #    error_type = ERROR_RUNTIME_ERROR
    # result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    # print(result.returncode, result.stderr, result.stdout)
    # if not sandbox_only:
    #     socket.send_pyobj({
    #         "message_type": "sandbox-finish",
    #         "payload": {
    #             "task_id": task_id,
    #             "pid": proc.pid,
    #             "vram_limit": vram_limit,
    #         },
    #     })
    #     _ = socket.recv()
    # logfile.close()
    # return error_type
    return return_code
