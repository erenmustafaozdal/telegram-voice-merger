import os


def create_directory(directory):
    if not path_is_exists(directory):
        os.mkdir(directory)


def path_is_exists(os_path):
    return os.path.exists(os_path)


def format_date(date):
    return date.strftime("%Y-%m-%d")
