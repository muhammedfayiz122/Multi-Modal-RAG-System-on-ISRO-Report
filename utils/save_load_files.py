import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from utils.paths import get_project_root
from typing import Callable, Any
import pickle
import json
from logger import logging


def save_as_pickle(save_obj:str, file_name:str):
    """
    To save object as pickle file
    """

    # Adding .pkl format if not available
    if file_name[-4:] != ".pkl":
        file_name += ".pkl"
    file_path = os.path.join(get_project_root(), "data", "pickle_files", file_name)
    # file_path = f"../data/pickle_files/{file_name}"

    # Creating path if not available and if file exists , returns
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        print(f"Warning: {file_path} already exists ")
        return False
    
    # Saving pickle file
    try:
        with open(file_path, 'wb') as file: 
            pickle.dump(save_obj, file)
        logging.info(f"{file_name} saved locally")
        print(f"{file_name} saved.")
    except Exception as e:
        print(f"Error while saving : {e}")
    return True

def load_pickle(load_file:str):
    """
    To load pickle objects
    """

    # Adding .pkl format if not available 
    if load_file[-4:] != ".pkl":
        load_file += ".pkl"
    file_path = os.path.join(get_project_root(), "data", "pickle_files", load_file)
    # file_path = f"../data/pickle_files/{load_file}"

    # Checking if file not exists
    if not os.path.exists(file_path):
        print(f"Warning: {load_file} not found!")
        return False
    
    # Loading pickle file
    try:
        with open(file_path, "rb") as f:
            pickle_file = pickle.load(f)
        logging.info(f"{load_file} loaded")
        print(f"{load_file} loaded.")
        return pickle_file
    except Exception as e:
        print("Error while loading pickle file : ",e)

    return pickle_file

def reload_pickle(pickle_file: str, func: Callable[[str], any], *args, **kwargs):
    """
    """
    # Loading pickle file
    load_obj = load_pickle(pickle_file)
    # If there is no pickle file , creating it by running function
    if not load_obj:
        if pickle_file[-4:] != ".pkl":
            pickle_file += ".pkl"
        print(f"{pickle_file} file not exists. \nCreating...")
        save_obj = func(*args, **kwargs)
        if save_obj:
            save_as_pickle(save_obj, pickle_file)
        else:
            print("Saving error : nothing returned by function {func.__name__}")
        return save_obj
    return load_obj


def load_json(load_file:str):
    """
    To load JSON files
    """

    #at last i have to solve this directory by getting whole directory locatn
    # Adding .json format if not available 
    if load_file[-5:] != ".json":
        load_file += ".json"
    file_path = os.path.join(get_project_root(), "data", load_file)

    # Checking if file not exists
    if not os.path.exists(file_path):
        print(f"Warning: {load_file} not found!")
        return False
    
    # Loading pickle file
    try:
        with open(file_path, "r") as file   :
            json_file = json.load(file)
        logging.info(f"{load_file} loaded")
        print(f"{load_file} loaded.")
        return json_file
    except Exception as e:
        print("Error while loading pickle file : ",e)

    return json_file


def save_as_json(save_obj:str, file_name:str):
    """
    To save object as json file
    """

    # Adding .pkl format if not available
    if file_name[-5:] != ".json":
        file_name += ".json"
    file_path = os.path.join(get_project_root(), "data", file_name)
    # file_path = f"../data/json_files/{file_name}"

    # Creating path if not available and if file exists , returns
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if os.path.exists(file_path):
        print(f"Warning: {file_path} already exists ")
        return False
    
    # Saving json file
    try:
        with open(file_path, 'w') as file: 
            json.dump(save_obj, file, indent=4)
        logging.info(f"{file_path} saved locally")
        print(f"{file_path} saved.")
    except Exception as e:
        print(f"Error while saving : {e}")
    return True

def reload_json(json_file: str, func: Callable[[str], any], *args, **kwargs):
    """
    """
    # Loading json file
    load_obj = load_json(json_file)
    # If there is no json file , creating it by running function
    if not load_obj:
        if json_file[-5:] != ".json":
            json_file += ".json"
        print(f"{json_file} file not exists. \nCreating...")
        save_obj = func(*args, **kwargs)
        if save_obj:
            save_as_json(save_obj, json_file)
        else:
            print("Saving error : nothing returned by function {func.__name__}")
        return save_obj
    return load_obj