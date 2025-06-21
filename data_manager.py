import json
import os

class DataManager:
    """
    Manages all data persistence by reading from and writing to a JSON file.
    """
    def __init__(self, filepath: str = 'data.json'):
        """
        Initializes the DataManager.

        Args:
            filepath (str): The path to the JSON data file.
        """
        self.filepath = filepath
        self.data = None
        self.load_data()

    def load_data(self):
        """
        Loads data from the JSON file. If the file doesn't exist,
        it initializes a default data structure and creates the file.
        """
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'turbines': [],
                'part_masters': [],
                'part_instances': [],
                'installation_records': []
            }
            self.save_data()

    def save_data(self):
        """
        Saves the current state of self.data to the JSON file in a
        pretty-printed format.
        """
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=4)

if __name__ == '__main__':
    # This block demonstrates the DataManager class functionality.
    
    # Define the schemas for clarity, as described in the prompt.
    # Note: These are for documentation; the actual data is managed in the class.
    schemas = {
        "turbines": {
            'turbine_id': 'unique_int',
            'serial_number': 'string',
            'frame_type': 'string',
            'location': 'string',
            'current_total_hours': 'float',
            'current_total_starts': 'int'
        },
        "part_masters": {
            'part_number': 'string',
            'part_name': 'string',
            'description': 'string',
            'manufacturer': 'string'
        },
        "part_instances": {
            'instance_id': 'unique_int',
            'part_number': 'string',
            'serial_number': 'string',
            'manufacture_date': 'string'
        },
        "installation_records": {
            'record_id': 'unique_int',
            'instance_id': 'int',
            'turbine_id': 'int',
            'installation_date': 'string',
            'turbine_hours_at_install': 'float',
            'turbine_starts_at_install': 'int',
            'removal_date': 'string or None',
            'turbine_hours_at_removal': 'float or None',
            'turbine_starts_at_removal': 'int or None'
        }
    }

    print("Initializing DataManager...")
    # Create an instance of the DataManager.
    # If data.json exists, it will be loaded. If not, it will be created.
    data_manager = DataManager('data.json')
    
    print(f"DataManager initialized. Data loaded from '{data_manager.filepath}'.")
    
    # Display the loaded data.
    print("\nInitial data:")
    print(json.dumps(data_manager.data, indent=4))
    
    # Example of how you might add data (though this logic will be in app_logic.py)
    # This is for demonstration only.
    if not data_manager.data['turbines']:
        print("\nAdding a sample turbine for demonstration...")
        sample_turbine = {
            'turbine_id': 1,
            'serial_number': '123-ABC',
            'frame_type': '7FA',
            'location': 'Power Plant A',
            'current_total_hours': 50000.5,
            'current_total_starts': 1200
        }
        data_manager.data['turbines'].append(sample_turbine)
        data_manager.save_data()
        print("Sample turbine added and data saved.")

        print("\nData after modification:")
        print(json.dumps(data_manager.data, indent=4))

        # Clean up the demonstration data by reloading the original empty structure
        print("\nCleaning up demonstration data...")
        os.remove(data_manager.filepath)
        clean_manager = DataManager('data.json')
        print("data.json has been reset to its default empty state.")
        print("\nFinal clean data:")
        print(json.dumps(clean_manager.data, indent=4))
    else:
        print("\n'data.json' already contains data. No sample data added.")