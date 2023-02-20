# aiVLE for Slurm

## aiVLE Web Backend
1. `cd aivle_web_slurm`
2. `python -m venv aivle_web`
3. `source aivle_web/bin/activate`
4. Follow "Setup" instructions at https://github.com/edu-ai/aivle-web 
5. Follow "Deploying Backend" instructions at https://github.com/edu-ai/aivle-docs/blob/master/docs/dev-guide/deployment-guide.md
6. Make sure "Participations" is filled in for object permissions for tasks
7. Set `debug=False` in `aiVLE/settings.py` for safe deployment
8. Run server with `python manage.py runserver 0.0.0.0:8000`

## aiVLE Worker
1. Download the appropriate grader and gym libraries
2. `cd aivle_worker_slurm`
3. `python -m venv aivle_worker`
4. `source aivle_worker/bin/activate`
5. `python -m pip install .`
6. Follow "Getting Started" instructions at https://github.com/edu-ai/aivle-worker
7. Add `TEMP_FOLDER_ROOT` to `.env` file and set it to be the directory to store the job submission files (make sure you have execute permissions in this directory to run `bootstrap.sh`)
8. Add `GRADER_GYM_LOCATION` (without trailing /) to `.env` file and set it to the directory containing BOTH the grader and gym libraries
9. Get `ACCESS_TOKEN` using the aivLE Web admin backend under "Tokens" (make sure the user with the token has admin role for "Participations" in all courses)
10. Run server with `python -m aivle_worker`

## aiVLE Web Frontend
1. `git clone https://github.com/le0tan/aivle-fe`
2. Follow "Deploy aiVLE Web" instructions at https://github.com/edu-ai/aivle-docs/blob/master/docs/dev-guide/deployment-guide.md