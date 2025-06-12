from typing import Callable, Any
import pickle
import os

def save_as_pickle(save_obj:str, file_name:str):
    """
    To save object as pickle file
    """

    # Adding .pkl format if not available
    if file_name[-4:] != ".pkl":
        file_name += ".pkl"
    file_name = f"../data/pickle_files/{file_name}"

    # Creating path if not available and if file exists , returns
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    if os.path.exists(file_name):
        print(f"Warning: {file_name} already exists ")
        return False
    
    # Saving pickle file
    try:
        with open(file_name, 'wb') as file: 
            pickle.dump(save_obj, file)
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
    load_file = f"../data/pickle_files/{load_file}"

    # Checking if file not exists
    if not os.path.exists(load_file):
        print(f"Warning: {load_file} not found!")
        return False
    
    # Loading pickle file
    try:
        with open(load_file, "rb") as f:
            pickle_file = pickle.load(f)
        print(f"{load_file} loaded.")
        return pickle_file
    except Exception as e:
        print("Error while loading pickle file : ",e)

    return pickle_file

def reload(pickle_file: str, func: Callable[[str], any], parameter: str):
    """
    """
    # Loading pickle file
    load_obj = load_pickle(pickle_file)
    # If there is no pickle file , creating it by running function
    if not load_obj:
        if pickle_file[-4:] != ".pkl":
            pickle_file += ".pkl"
        print(f"{pickle_file} file not exists. \nCreating...")
        save_obj = func(parameter)
        if save_obj:
            save_as_pickle(save_obj, pickle_file)
        else:
            print("Saving error : nothing returned by function {func.__name__}")
        return save_obj
    return load_obj


