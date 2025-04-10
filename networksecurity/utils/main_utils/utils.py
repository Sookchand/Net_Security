import yaml
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import os,sys
import numpy as np
#import dill
import pickle

from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV

def read_yaml_file(file_path: str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    

def save_numpy_array_data(file_path: str, array: np.array):
    """
    Save numpy array data to a file
    file_path: str: file path to save the numpy array data
    array: np.array: numpy array data to save
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def save_object(file_path: str, obj: object) -> None:
    """
    Save object to a file
    file_path: str: file path to save the object
    obj: object: object to save
    """
    try:
        logging.info("Entered into save_object method of MainUtils class")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)
        logging.info("Object saved successfully. Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path: str) -> object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f"The file: {file_path} is not exists")
        with open(file_path, "rb") as file_obj:
            print(file_obj)
            return pickle.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def load_numpy_array_data(file_path: str) -> np.array:
    """
    Load numpy array data from a file
    file_path: str: file path to load the numpy array data
    """
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def evaluate_models(x_train, y_train, x_test, y_test, models: dict, param: dict) -> dict:
    """
    Evaluate the models
    x_train: np.array: training data
    y_train: np.array: training target
    x_test: np.array: testing data
    y_test: np.array: testing target
    models: dict: models to evaluate
    param: dict: parameters for the models
    """
    try:
        model_report = {}  # model report
        for i in range(len(list(models))):  # iterate through the models
            model = list(models.values())[i]  # get the model
            model_name = list(models.keys())[i]  # get the model name
            
            logging.info(f"Evaluating model: {model_name}")  # log the model name
            
            grid_search = GridSearchCV(model, param[model_name], cv=3)  # grid search
            grid_search.fit(x_train, y_train)  # fit the model
            
            model.set_params(**grid_search.best_params_)  # set the best parameters
            model.fit(x_train, y_train)  # fit the model
            
            y_train_pred = model.predict(x_train)  # predict the training data
            
            y_test_pred = model.predict(x_test)  # predict the testing data
            
            train_model_score = r2_score(y_train, y_train_pred)  # get the training model score
            
            test_model_score = r2_score(y_test, y_test_pred)  # get the testing model score
            
            model_report[model_name] = test_model_score  # add the model score to the model report
        return model_report  # return the model report
     
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e