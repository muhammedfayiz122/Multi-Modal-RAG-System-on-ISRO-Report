import os

def get_project_root() -> str:
    """
    Returns the absolute path to the project root.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))