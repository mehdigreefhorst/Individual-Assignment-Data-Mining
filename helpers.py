import os
import json


def save_json_data(json_data, relative_path='json/data.json'):
    """
    Save JSON data to a file in a directory relative to the package.
    """
    # Get the path to the package directory
    file_path = relative_path
    for index in range(100):
        if index == 0:

            # uses the filepath as is given
            if not os.path.exists(file_path):
                break
        file_name = os.path.splitext(file_path)[0]
        extension = os.path.splitext(file_path)[1]

        # creates a filepath with index append if path already exists
        if not os.path.exists(f"{file_name}_{index}{extension}"):
            file_name = os.path.splitext(relative_path)[0]
            extension = os.path.splitext(relative_path)[1]
            file_path = f"{file_name}_{index}{extension}"
            break
    print("save_file_path = ", file_path)
    print("save_file_path = ", file_path)

    # Ensure the directory exists
    if not os.path.dirname(file_path):
        os.makedirs(os.path.dirname(file_path))

    # Write the JSON data to the file
    with open(file_path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)

    return f"Data saved successfully in {file_path}"