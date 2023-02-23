import os
import pickle
import shutil
import zipfile
from ast import literal_eval

import requests

from .apis import get_task_info, ERROR_RUNTIME_ERROR, ERROR_MEMORY_LIMIT_EXCEEDED, ERROR_TIME_LIMIT_EXCEEDED
from .models import Submission, ExecutionOutput
from .sandbox import create_venv, run_with_venv
from .settings import LOCAL_FILE, TEMP_GRADING_FOLDER
from .util import LocalFileAdapter, download_and_save


def _download_submission(s: Submission) -> str:
    temp_grading_folder = os.path.join(TEMP_GRADING_FOLDER, str(s.sid))
    if not os.path.exists(temp_grading_folder):
        os.mkdir(temp_grading_folder)
    session = requests.Session()
    if LOCAL_FILE:
        session.mount("file://", LocalFileAdapter())
    task_zip_path = os.path.join(temp_grading_folder, "task.zip")
    download_and_save(session, s.task_url, task_zip_path)
    with zipfile.ZipFile(task_zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_grading_folder)
    agent_zip_path = os.path.join(temp_grading_folder, "agent.zip")
    download_and_save(session, s.agent_url, agent_zip_path)
    with zipfile.ZipFile(agent_zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_grading_folder)
    return temp_grading_folder


def run_submission(s: Submission, job_id: int, celery_task_id: str, force: bool = False) -> ExecutionOutput:
    temp_grading_folder = _download_submission(s)
    task_info = get_task_info(s.task_id)
    env_name = task_info["name"]
    # env_name = create_venv(os.path.join(temp_grading_folder, "requirements.txt"), force=force)
    # error_type = run_with_venv(env_name=env_name,
    return_code = run_with_venv(env_name=env_name,
                            command=["sbatch", "./bootstrap.sh"],
                            home=temp_grading_folder,
                            rlimit=task_info["ram_limit"],
                            vram_limit=task_info["vram_limit"],
                            time_limit=task_info["run_time_limit"],
                            task_id=s.task_id,
                            job_id=job_id,
                            celery_task_id=celery_task_id)
    # with open(os.path.join(temp_grading_folder, "stdout.log"), "r") as f:
    with open(os.path.join(temp_grading_folder, "log.out"), "r") as f:
        try:
            # raw_log = f.read()
            stdout_log = f.readlines()
            # check if results are returned properly
            result = literal_eval(stdout_log[-1])
            # pickle.loads(literal_eval(result))
            ok = True
            f.close()
        except Exception as e:
            # too much in log, may be because student printed too much in the code
            f.close()
            if type(e).__name__ == "MemoryError":
                return ExecutionOutput(ok=False, raw=[""], result=None, error=ERROR_MEMORY_LIMIT_EXCEEDED)
            ok = False
    error_type = None
    if return_code != 0:
        ok = False
    # delete files after grading
    shutil.rmtree(temp_grading_folder)
    if ok:
        return ExecutionOutput(ok=True, raw=stdout_log, result=result, error=None)
    else:
        if "TIME LIMIT" in stdout_log[0]:
            return ExecutionOutput(ok=False, raw=stdout_log, result=None, error=ERROR_TIME_LIMIT_EXCEEDED)
        elif "oom-kill" in stdout_log[-1]:
            return ExecutionOutput(ok=False, raw=stdout_log, result=None, error=ERROR_MEMORY_LIMIT_EXCEEDED)
        if error_type is not None:
            return ExecutionOutput(ok=False, raw=stdout_log, result=None, error=error_type)
        else:
            return ExecutionOutput(ok=False, raw=stdout_log, result=None, error=ERROR_RUNTIME_ERROR)
