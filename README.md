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
1. Download the appropriate grader and gym libraries
2. `cd aivle_worker`
3. `python -m venv aivle_worker_venv`
4. `source aivle_worker_venv/bin/activate`
5. `python -m pip install .`
6. Follow "Getting Started" instructions at https://github.com/edu-ai/aivle-worker
7. Add `TEMP_FOLDER_ROOT` to `.env` file and set it to be the directory to store the job submission files (make sure you have execute permissions in this directory to run `bootstrap.sh`)
8. Add `GRADER_GYM_LOCATION` (without trailing /) to `.env` file and set it to the directory containing BOTH the grader and gym libraries
9. Get `ACCESS_TOKEN` using the aivLE Web admin backend under "Tokens" (make sure the user with the token has admin role for "Participations" in intended "Courses")
10. Run server with `python -m aivle_worker`

## aiVLE Web Frontend
1. `git clone https://github.com/le0tan/aivle-fe`
2. Follow "Deploy aiVLE Web" instructions at https://github.com/edu-ai/aivle-docs/blob/master/docs/dev-guide/deployment-guide.md