import datetime
from data_manager import DataManager

# --- Helper Function ---

def _get_next_id(items_list, id_key):
    """
    Generates the next unique ID for a list of dictionary items.

    Args:
        items_list (list): The list of items (dictionaries).
        id_key (str): The key for the ID in the dictionaries.

    Returns:
        int: The next available integer ID.
    """
    if not items_list:
        return 1
    return max(item.get(id_key, 0) for item in items_list) + 1

# --- Turbine Functions ---

def add_turbine(data_manager, serial_number, frame_type, location=''):
    """
    Adds a new turbine to the data.

    Args:
        data_manager (DataManager): An instance of the DataManager.
        serial_number (str): The serial number of the turbine.
        frame_type (str): The frame type of the turbine.
        location (str, optional): The location of the turbine. Defaults to ''.
    """
    turbines = data_manager.data['turbines']
    new_turbine = {
        'turbine_id': _get_next_id(turbines, 'turbine_id'),
        'serial_number': serial_number,
        'frame_type': frame_type,
        'location': location
    }
    turbines.append(new_turbine)
    data_manager.save_data()
    print(f"Added new turbine: {serial_number}")
    return new_turbine

def get_turbine_by_serial(data_manager, serial_number):
    """Finds a turbine by its serial number."""
    for turbine in data_manager.data.get('turbines', []):
        if turbine['serial_number'] == serial_number:
            return turbine
    return None

def get_all_turbines(data_manager):
    """Returns the list of all turbines."""
    return data_manager.data.get('turbines', [])

# --- Part Master Functions ---

def add_part_master(data_manager, part_number, description, manufacturer=''):
    """Adds a new part to the part master list."""
    parts = data_manager.data['part_master']
    new_part = {
        'part_number': part_number,
        'description': description,
        'manufacturer': manufacturer
    }
    parts.append(new_part)
    data_manager.save_data()
    print(f"Added new part master: {part_number}")
    return new_part

def get_all_part_masters(data_manager):
    """Returns the list of all part master records."""
    return data_manager.data.get('part_master', [])

# --- Part Instance Functions ---

def add_part_instance(data_manager, part_number, serial_number):
    """Adds a new part instance."""
    instances = data_manager.data['part_instances']
    new_instance = {
        'instance_id': _get_next_id(instances, 'instance_id'),
        'part_number': part_number,
        'serial_number': serial_number
    }
    instances.append(new_instance)
    data_manager.save_data()
    print(f"Added new part instance: {serial_number}")
    return new_instance

def get_all_part_instances(data_manager):
    """Returns the list of all part instances."""
    return data_manager.data.get('part_instances', [])

def get_part_by_serial(data_manager, serial_number):
    """Finds a part instance by its serial number."""
    for instance in data_manager.data.get('part_instances', []):
        if instance['serial_number'] == serial_number:
            return instance
    return None

# --- Installation History Functions ---

def add_installation_record(data_manager, instance_id, turbine_id, installation_date=None):
    """Adds an installation history record."""
    history = data_manager.data['installation_history']
    if installation_date is None:
        installation_date = datetime.date.today().isoformat()

    new_record = {
        'installation_id': _get_next_id(history, 'installation_id'),
        'instance_id': instance_id,
        'turbine_id': turbine_id,
        'installation_date': installation_date
    }
    history.append(new_record)
    data_manager.save_data()
    print(f"Added installation record for instance {instance_id} in turbine {turbine_id}.")
    return new_record

def get_all_installation_history(data_manager):
    """Returns the entire installation history."""
    return data_manager.data.get('installation_history', [])

# --- Maintenance Log Functions ---

def add_maintenance_log(data_manager, instance_id, description, log_date=None):
    """Adds a maintenance log entry."""
    logs = data_manager.data['maintenance_log']
    if log_date is None:
        log_date = datetime.datetime.now().isoformat()

    new_log = {
        'log_id': _get_next_id(logs, 'log_id'),
        'instance_id': instance_id,
        'description': description,
        'log_date': log_date
    }
    logs.append(new_log)
    data_manager.save_data()
    print(f"Added maintenance log for instance {instance_id}.")
    return new_log

def get_all_maintenance_logs(data_manager):
    """Returns all maintenance logs."""
    return data_manager.data.get('maintenance_log', [])

# --- Core Part Management Logic ---

def install_part(data_manager, part_serial_number, turbine_serial_number, installation_date=None):
    """
    Installs a part into a turbine and creates an installation record.
    """
    part_instance = get_part_by_serial(data_manager, part_serial_number)
    if not part_instance:
        print(f"Error: Part with serial number '{part_serial_number}' not found.")
        return

    turbine = get_turbine_by_serial(data_manager, turbine_serial_number)
    if not turbine:
        print(f"Error: Turbine with serial number '{turbine_serial_number}' not found.")
        return

    # Check if the part is already installed
    for record in get_all_installation_history(data_manager):
        if record['instance_id'] == part_instance['instance_id'] and 'removal_date' not in record:
            print(f"Error: Part '{part_serial_number}' is already installed in a turbine.")
            return

    add_installation_record(data_manager, part_instance['instance_id'], turbine['turbine_id'], installation_date)

def remove_part(data_manager, part_serial_number, removal_date=None):
    """
    Removes a part from a turbine by updating its installation record.
    """
    part_instance = get_part_by_serial(data_manager, part_serial_number)
    if not part_instance:
        print(f"Error: Part with serial number '{part_serial_number}' not found.")
        return

    if removal_date is None:
        removal_date = datetime.date.today().isoformat()

    # Find the active installation record
    active_record = None
    for record in data_manager.data['installation_history']:
        if record['instance_id'] == part_instance['instance_id'] and 'removal_date' not in record:
            active_record = record
            break

    if active_record:
        active_record['removal_date'] = removal_date
        data_manager.save_data()
        print(f"Part '{part_serial_number}' removed on {removal_date}.")
    else:
        print(f"Error: Part '{part_serial_number}' has no active installation record to remove.")

def get_part_lifecycle(data_manager, instance_id):
    """
    Retrieves the complete history for a specific part instance.
    """
    part_instance = next((p for p in get_all_part_instances(data_manager) if p['instance_id'] == instance_id), None)
    if not part_instance:
        return "Part instance not found."

    installation_history = [r for r in get_all_installation_history(data_manager) if r['instance_id'] == instance_id]
    maintenance_history = [l for l in get_all_maintenance_logs(data_manager) if l['instance_id'] == instance_id]

    return {
        "part_details": part_instance,
        "installation_history": installation_history,
        "maintenance_log": maintenance_history
    }

def get_installed_parts(data_manager, turbine_id):
    """
    Returns a list of parts currently installed in a specific turbine.
    """
    installed_instance_ids = {
        rec['instance_id'] for rec in get_all_installation_history(data_manager)
        if rec['turbine_id'] == turbine_id and 'removal_date' not in rec
    }

    return [
        inst for inst in get_all_part_instances(data_manager)
        if inst['instance_id'] in installed_instance_ids
    ]

# --- Example Usage ---
if __name__ == '__main__':
    # Initialize the data manager
    dm = DataManager('data.json')

    print("\n--- Initial Data ---")
    # To ensure a clean slate for the example, we can re-initialize the data
    # dm._initialize_default_data()
    # dm.save_data()
    print(dm.data)

    print("\n--- Adding Base Data ---")
    add_part_master(dm, "PN-1001", "Main Bearing")
    add_part_master(dm, "PN-2050", "Gearbox Filter")
    turbine1 = add_turbine(dm, "T-SN-101", "GE 1.5sle", "Wind Farm Alpha")
    instance1 = add_part_instance(dm, "PN-1001", "PI-SN-001")
    instance2 = add_part_instance(dm, "PN-2050", "PI-SN-002")


    print("\n--- Testing Core Logic ---")
    # Install PI-SN-001 into T-SN-101
    install_part(dm, "PI-SN-001", "T-SN-101")
    
    # Add a maintenance log
    add_maintenance_log(dm, instance1['instance_id'], "Initial inspection complete.")

    # Check installed parts for turbine1
    print(f"\nParts installed in turbine {turbine1['serial_number']}:")
    print(get_installed_parts(dm, turbine1['turbine_id']))

    # Remove the part
    remove_part(dm, "PI-SN-001")

    # Check installed parts again
    print(f"\nParts installed in turbine {turbine1['serial_number']} after removal:")
    print(get_installed_parts(dm, turbine1['turbine_id']))

    # Get the full lifecycle of the part
    print(f"\nLifecycle for part instance {instance1['instance_id']}:")
    print(get_part_lifecycle(dm, instance1['instance_id']))

    print("\n--- Final Data in File ---")
    print(dm.data)
