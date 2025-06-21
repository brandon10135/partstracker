import os
import pandas as pd
from data_manager import DataManager
from app_logic import add_part_instance, add_part_master

# Note: To run this file, you will need to install the pandas and openpyxl libraries.
# You can install them using pip:
# pip install pandas
# pip install openpyxl

def import_from_file(data_manager: DataManager, file_path: str) -> dict:
    """
    Reads data from a CSV or Excel file and adds new part instances to the system.

    Args:
        data_manager: The DataManager instance for data operations.
        file_path: The full path to the CSV or Excel file.

    Returns:
        A dictionary summarizing the import results.
    """
    if not os.path.exists(file_path):
        return {"added": 0, "failed": 0, "error": "File not found."}

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            return {"added": 0, "failed": 0, "error": "Unsupported file type."}
    except Exception as e:
        return {"added": 0, "failed": 0, "error": f"Failed to read file: {e}"}

    added_count = 0
    failed_count = 0
    
    # Ensure required columns are present
    required_columns = ['part_number', 'serial_number', 'manufacture_date']
    for col in required_columns:
        if col not in df.columns:
            return {"added": 0, "failed": 0, "error": f"Missing required column: {col}"}

    for index, row in df.iterrows():
        try:
            # Extract data from the row
            part_number = str(row['part_number'])
            serial_number = str(row['serial_number'])
            # Pandas can sometimes read dates as datetime objects, convert to string
            manufacture_date = str(row['manufacture_date'])

            # Call the app_logic function to add the part instance
            add_part_instance(
                data_manager=data_manager,
                part_number=part_number,
                serial_number=serial_number,
                manufacture_date=manufacture_date
            )
            added_count += 1
        except Exception as e:
            print(f"Failed to process row {index + 2}: {e}") # Row index is 0-based, Excel is 1-based + header
            failed_count += 1
            
    return {"added": added_count, "failed": failed_count, "error": None}

if __name__ == '__main__':
    # --- Test Execution ---
    TEST_FILE = 'import_test_data.json'
    CSV_FILE = 'parts_to_import.csv'
    EXCEL_FILE = 'parts_to_import.xlsx'

    # Clean up previous test files if they exist
    for f in [TEST_FILE, CSV_FILE, EXCEL_FILE]:
        if os.path.exists(f):
            os.remove(f)

    print("--- Running Import Test Scenario ---")
    dm = DataManager(TEST_FILE)

    # Add master parts so the imported instances have a valid part_number
    print("\n--- Pre-loading Master Parts ---")
    add_part_master(dm, 'PN-IMPORT-1', 'Imported Blade', 'Blade from file', 'VendorA')
    add_part_master(dm, 'PN-IMPORT-2', 'Imported Nozzle', 'Nozzle from file', 'VendorB')

    # 1. Create a sample CSV file
    print("\n--- Creating Sample CSV File ---")
    csv_data = {
        'part_number': ['PN-IMPORT-1', 'PN-IMPORT-2', 'PN-IMPORT-1'],
        'serial_number': ['SN-CSV-001', 'SN-CSV-002', 'SN-CSV-003'],
        'manufacture_date': ['2024-05-10', '2024-05-11', '2024-05-12']
    }
    pd.DataFrame(csv_data).to_csv(CSV_FILE, index=False)
    print(f"'{CSV_FILE}' created.")

    # 2. Test importing from the CSV file
    print("\n--- Testing CSV Import ---")
    csv_summary = import_from_file(dm, CSV_FILE)
    print(f"CSV Import Summary: {csv_summary}")

    # 3. Create a sample Excel file
    print("\n--- Creating Sample Excel File ---")
    excel_data = {
        'part_number': ['PN-IMPORT-2', 'PN-IMPORT-2'],
        'serial_number': ['SN-XLS-001', 'SN-XLS-002'],
        'manufacture_date': ['2024-06-01', '2024-06-02'],
        'extra_column': ['ignore', 'this']
    }
    pd.DataFrame(excel_data).to_excel(EXCEL_FILE, index=False)
    print(f"'{EXCEL_FILE}' created.")

    # 4. Test importing from the Excel file
    print("\n--- Testing Excel Import ---")
    excel_summary = import_from_file(dm, EXCEL_FILE)
    print(f"Excel Import Summary: {excel_summary}")
    
    # 5. Verify the data was added
    print("\n--- Verifying Imported Data ---")
    print(f"Total part instances in data manager: {len(dm.data['part_instances'])}")
    for part in dm.data['part_instances']:
        print(part)

    # 6. Clean up test files
    print("\n--- Test Complete, Cleaning Up ---")
    for f in [TEST_FILE, CSV_FILE, EXCEL_FILE]:
        if os.path.exists(f):
            os.remove(f)
            print(f"Deleted '{f}'.")