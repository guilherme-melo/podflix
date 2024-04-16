# Podflix

## Repository Structure

### Web Application
- *[app](app)*: Django project. Container folder for `podcasts` application.
- *[utils](utils)*: notebooks that are used to reorganizing the data to database.

The code of the PyVespa models is in [app/podcasts/application.py](app/podcasts/application.py).

### Analysis and Evaluations
- *[data](data)*: the database in .csv format that is used in the models (side note: it's a TODO for the team to use the `app/db.sqlite3` instead).
- *[evaluation.ipynb](evaluation.ipynb)*: notebook that contains the evaluation to compare the models.
- *[performance.ipynb](performance.ipynb)*: notebook that contains the analysis of some classic metrics for the models.
- *[results](results)*: some results of the [performance notebook](performance.ipynb).

## Run the project
First of all, you need to upload the database file into the project (it's not in GitHub because of the size).

You must download the file [in this link](https://drive.google.com/file/d/1q8IAfZoq8wYoPlrfFHaVlnCo6iMSX0ff/view?usp=drive_link) and then move it to the `app` folder.

Finally, to run this project, you need to navigate to `app` folder and run
```
python3 manage.py runserver
```

Obs:
- You need to have docker installed on your computer.
 
