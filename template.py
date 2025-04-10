import os 
from pathlib import Path 
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name="datascience"

list_of_files=[
    ".gthub/workflows/.gitkeep", # Responsible for doing the deplyment (github actions).
    f"src/{project_name}/__init__.py", # all classes we need can be imported anywhere in the project
    f"src/{project_name}/components/__init__.py", # data ingestion, data transformation, model training, model evaluation --> all this should be developed inform of pipelines
    f"src/{project_name}/utils/__init__.py", # we have generic functionality defined.
    f"src/{project_name}/utils/common.py", # all functionality common to most of the compnents being defined
    f"src/{project_name}/cofig/__init__.py", # contains all constructor.
    f"src/{project_name}/cofig/configuration.py", 
    f"src/{project_name}/pipeline/__init__.py",  # Gove the different pipelines created
    f"src/{project_name}/entity/__init__.py",
    f"src/{project_name}/entity/config_entity.py",
    f"src/{project_name}/constants/__init__.py",
    "config/config.yaml",
    "params.yaml",
    "schema.yaml",
    "main.py"
    "Dockerfile",
    "setup.py",
    "research/research.ipynb",
    "templates/index.html",
    "app.py" 
]

for filepath in list_of_files:
    filepath=Path(filepath)
    filedir,filename=os.path.split(filepath)

    if filedir!="":
        os.makedirs(filedir,exist_ok=True)
        logging.info(f"Creating directory {filedir} for the file : {filename}")
    
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,"w") as f:

            pass
            logging.info(f"Creating empty file: {filepath}")

    else:
        logging.info(f"{filename} is already exists")