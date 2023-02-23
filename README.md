# aiVLE for Slurm

## aiVLE Web Backend
### Deployment
1. `cd aivle_web`
2. `python -m venv aivle_web_venv`
3. `source aivle_web_venv/bin/activate`
4. `python -m pip install wheel`
5. Follow "Setup" instructions at https://github.com/edu-ai/aivle-web but `python manage.py makemigrations app scheduler` under Step 4
6. Follow "Deploying Backend" instructions at https://github.com/edu-ai/aivle-docs/blob/master/docs/dev-guide/deployment-guide.md
7. Set `debug=False` in `aiVLE/settings.py` for safe deployment
8. Run server with `python manage.py runserver 0.0.0.0:8000`

### Usage
1. Create Courses
2. Set Participations
3. Add Tasks


## aiVLE Worker
### Deployment
1. Download the appropriate grader and gym libraries
2. `cd aivle_worker`
3. `python -m venv aivle_worker_venv`
4. `source aivle_worker_venv/bin/activate`
5. `python -m pip install .`
6. Follow "Getting Started" instructions at https://github.com/edu-ai/aivle-worker
7. Add `TEMP_FOLDER_ROOT` to `.env` file and set it to be the directory to store the job submission files (make sure you have execute permissions in this directory to run `bootstrap.sh`)
7. Add `MAX_PROCESS_NUM` and `PROCESS_BUFFER` to `.env` file and set them to be the process limit for your user on the Slurm login node and the buffer between that and the max number of processes you will allow respectively
8. Get `ACCESS_TOKEN` using the aivLE Web admin backend under "Tokens" (make sure the user with the token has admin role for "Participations" in intended "Courses")
9. Run server with `python -m aivle_worker`

### New Task Setup
1. Add new task to "Tasks" with task_name in the aiVLE Web Backend
2. `cd TEMP_FOLDER_ROOT/venvs/`
3. `python -m venv <task_name>`
4. `source <task_name>/bin/activate`
5. Install aiVLE Grader, aiVLE Gym and their required dependencies (locally with `--use-pep517`)
6. Add task function to `aivle_worker/aivle_worker/tasks.py`


## aiVLE Web Frontend
1. `git clone https://github.com/le0tan/aivle-fe`
2. Follow "Deploy Frontend (aiVLE FE)" instructions at https://yuanhong.larksuite.com/docx/doxusHWd5rNVi1qjvgw611wB3de