# gui_views.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import backend logic and reusable components
import app_logic as logic
from gui_components import FormPopup

class WelcomeScreen(ttk.Frame):
    """
    The initial welcome screen for the application.
    Shows a list of locations and main action buttons.
    """
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent)
        self.controller = controller
        self.data_manager = data_manager

        # Main layout frames
        left_frame = ttk.Frame(self, padding="10")
        left_frame.pack(side="left", fill="both", expand=True)
        right_frame = ttk.Frame(self, padding="20")
        right_frame.pack(side="right", fill="y")
        
        ttk.Separator(self, orient='vertical').pack(side="left", fill='y', padx=5)

        # --- Left Frame: Location List ---
        ttk.Label(left_frame, text="Turbine Locations", font=("", 14, "bold")).pack(pady=10)
        ttk.Label(left_frame, text="(Double-click a location to view its turbines)").pack(pady=(0, 10))

        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.pack(fill="both", expand=True)

        self.location_listbox = tk.Listbox(listbox_frame, font=("", 11))
        self.location_listbox.pack(side="left", fill="both", expand=True)
        self.location_listbox.bind("<Double-1>", self._on_location_select)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.location_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.location_listbox.config(yscrollcommand=scrollbar.set)
        
        self.populate_locations()

        # --- Right Frame: Action Buttons ---
        ttk.Label(right_frame, text="Actions", font=("", 14, "bold")).pack(anchor="center", pady=10)

        # Button factory
        def create_button(text, command):
            button = ttk.Button(right_frame, text=text, command=command, width=25)
            button.pack(pady=8, anchor="center")
            return button
        
        create_button("View All Turbines", lambda: controller.show_frame("TurbineView"))
        create_button("Search for a Part", controller.open_part_search)
        create_button("Add New Turbine", controller.open_add_turbine_form)
        create_button("Add Part Master", controller.open_add_part_master_form)
        create_button("Import from File", controller.open_import_dialog)
        create_button("Exit Application", controller.quit)

    def populate_locations(self):
        """Fetches and displays a unique list of turbine locations."""
        self.location_listbox.delete(0, tk.END)
        all_turbines = logic.get_all_turbines(self.data_manager)
        # Create a unique, sorted list of locations
        locations = sorted(list({turbine.get('location', 'N/A') for turbine in all_turbines}))
        for location in locations:
            self.location_listbox.insert(tk.END, location)

    def _on_location_select(self, event):
        """Handles double-clicking a location to filter the turbine view."""
        selected_indices = self.location_listbox.curselection()
        if not selected_indices:
            return
        selected_location = self.location_listbox.get(selected_indices[0])
        # Tell the controller to show the turbine view with a location filter
        self.controller.show_frame("TurbineView", location_filter=selected_location)


class TurbineView(ttk.Frame):
    """
    A frame that displays the list of turbines, either all or filtered by location.
    """
    def __init__(self, parent, controller, data_manager):
        super().__init__(parent)
        self.controller = controller
        self.data_manager = data_manager
        
        # --- Widgets for this View ---
        top_bar = ttk.Frame(self, padding="5")
        top_bar.pack(fill="x")
        
        back_button = ttk.Button(top_bar, text="< Back to Welcome", command=lambda: controller.show_frame("WelcomeScreen"))
        back_button.pack(side="left")
        
        self.title_label = ttk.Label(top_bar, text="All Turbines", font=("", 14, "bold"))
        self.title_label.pack(side="left", padx=20)
        
        tree_container = ttk.Frame(self)
        tree_container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ('serial_number', 'frame_type', 'location', 'current_hours', 'current_starts')
        self.turbine_tree = ttk.Treeview(tree_container, columns=columns, show='headings')
        self.turbine_tree.heading('serial_number', text='Serial Number')
        self.turbine_tree.heading('frame_type', text='Frame Type')
        self.turbine_tree.heading('location', text='Location')
        self.turbine_tree.heading('current_hours', text='Current Hours')
        self.turbine_tree.heading('current_starts', text='Current Starts')
        self.turbine_tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.turbine_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.turbine_tree.config(yscrollcommand=scrollbar.set)
        
        self.turbine_tree.bind("<Double-1>", self._on_turbine_double_click)

    def populate_turbine_list(self, location_filter=None):
        """Populates the turbine list, optionally filtering by location."""
        for i in self.turbine_tree.get_children():
            self.turbine_tree.delete(i)
            
        if location_filter:
            self.title_label.config(text=f"Turbines at: {location_filter}")
            all_turbines = [t for t in logic.get_all_turbines(self.data_manager) if t.get('location') == location_filter]
        else:
            self.title_label.config(text="All Turbines")
            all_turbines = logic.get_all_turbines(self.data_manager)

        for turbine in all_turbines:
            self.turbine_tree.insert('', tk.END, values=(
                turbine.get('serial_number', 'N/A'),
                turbine.get('frame_type', 'N/A'),
                turbine.get('location', 'N/A'),
                f"{turbine.get('current_total_hours', 0.0):.2f}",
                turbine.get('current_total_starts', 0)
            ), iid=turbine.get('serial_number'))

    def _on_turbine_double_click(self, event):
        """Launches the details window for the selected turbine."""
        selection = self.turbine_tree.focus()
        if not selection: return
        turbine_sn = self.turbine_tree.item(selection, "values")[0]
        # Launch the details Toplevel window
        TurbineDetailsWindow(self.controller.root, self.data_manager, turbine_sn, self.populate_turbine_list)

class TurbineDetailsWindow(tk.Toplevel):
    """
    A Toplevel window to display details for a single turbine,
    including its currently installed parts.
    """
    def __init__(self, parent, data_manager, turbine_serial_number, main_app_refresh_callback):
        super().__init__(parent)
        self.title(f"Details for Turbine: {turbine_serial_number}")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        self.data_manager = data_manager
        self.turbine = logic.get_turbine_by_serial(self.data_manager, turbine_serial_number)
        self.main_app_refresh_callback = main_app_refresh_callback

        if not self.turbine:
            messagebox.showerror("Error", "Could not find details for the selected turbine.", parent=parent)
            self.destroy()
            return

        self._create_widgets()
        self._refresh_installed_parts_list()

    def _create_widgets(self):
        # Display turbine information at the top
        info_frame = ttk.Frame(self, padding="10")
        info_frame.pack(fill="x")
        info_text = (f"Serial Number: {self.turbine['serial_number']} | "
                     f"Frame: {self.turbine['frame_type']} | "
                     f"Location: {self.turbine['location']} | "
                     f"Hours: {self.turbine.get('current_total_hours', 0.0):.2f} | "
                     f"Starts: {self.turbine.get('current_total_starts', 0)}")
        ttk.Label(info_frame, text=info_text, font=("", 10, "bold")).pack(anchor="w")

        # TreeView for installed parts
        parts_frame = ttk.Frame(self, padding="10")
        parts_frame.pack(fill="both", expand=True)
        part_cols = ('part_name', 'part_sn', 'manufacturer', 'install_date')
        self.parts_tree = ttk.Treeview(parts_frame, columns=part_cols, show='headings')
        self.parts_tree.heading('part_name', text='Part Name')
        self.parts_tree.heading('part_sn', text='Part S/N')
        self.parts_tree.heading('manufacturer', text='Manufacturer')
        self.parts_tree.heading('install_date', text='Installation Date')
        self.parts_tree.pack(fill="both", expand=True, side="left")
        
        parts_scrollbar = ttk.Scrollbar(parts_frame, orient=tk.VERTICAL, command=self.parts_tree.yview)
        self.parts_tree.configure(yscroll=parts_scrollbar.set)
        parts_scrollbar.pack(side='right', fill='y')

        # Add buttons for interactivity
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Install Part", command=self._show_install_part_form).pack(side="left")
        ttk.Button(button_frame, text="Remove Part", command=self._show_remove_part_form).pack(side="left", padx=5)

    def _refresh_installed_parts_list(self):
        """Helper to populate the installed parts list for this turbine."""
        for i in self.parts_tree.get_children():
            self.parts_tree.delete(i)
        
        installed_parts = logic.get_installed_parts(self.data_manager, self.turbine['turbine_id'])
        for part_instance in installed_parts:
            lifecycle = logic.get_part_lifecycle(self.data_manager, part_instance['instance_id'])
            if lifecycle and lifecycle['part_master'] and lifecycle['installation_history']:
                master = lifecycle['part_master']
                active_record = next((r for r in lifecycle['installation_history'] if r['removal_date'] is None), None)
                install_date = active_record['installation_date'] if active_record else "N/A"
                self.parts_tree.insert('', tk.END, values=(
                    master.get('part_name', 'N/A'),
                    part_instance.get('serial_number', 'N/A'),
                    master.get('manufacturer', 'N/A'),
                    install_date
                ), iid=part_instance.get('serial_number'))

    def _show_install_part_form(self):
        """Shows a form to install a part on the given turbine."""
        fields = ['part_serial_number']
        def save_logic(part_serial_number):
            logic.install_part(
                data_manager=self.data_manager,
                part_serial_number=part_serial_number,
                turbine_serial_number=self.turbine['serial_number'],
                installation_date=datetime.now().strftime('%Y-%m-%d')
            )
            self._refresh_installed_parts_list()
        
        FormPopup(self, f"Install Part on {self.turbine['serial_number']}", fields, save_logic)

    def _show_remove_part_form(self):
        """Shows a form to remove a selected part."""
        selection = self.parts_tree.focus()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a part from the list to remove.", parent=self)
            return
        
        part_sn = self.parts_tree.item(selection)['values'][1]
        fields = ['removal_date', 'new_turbine_hours', 'new_turbine_starts']
        def save_logic(**kwargs):
            logic.remove_part(
                data_manager=self.data_manager,
                part_serial_number=part_sn,
                turbine_serial_number_removed_from=self.turbine['serial_number'],
                removal_date=kwargs['removal_date'],
                new_turbine_hours=float(kwargs['new_turbine_hours']),
                new_turbine_starts=int(kwargs['new_turbine_starts'])
            )
            self._refresh_installed_parts_list()
            self.main_app_refresh_callback() # Refresh main list to show updated hours

        popup = FormPopup(self, f"Remove {part_sn}", fields, save_logic)
        popup.entries['removal_date'].insert(0, datetime.now().strftime('%Y-%m-%d'))
        popup.entries['new_turbine_hours'].insert(0, str(self.turbine['current_total_hours']))
        popup.entries['new_turbine_starts'].insert(0, str(self.turbine['current_total_starts']))


class PartLifecycleWindow(tk.Toplevel):
    """
    A Toplevel window to display the complete installation history of a single part.
    """
    def __init__(self, parent, data_manager, lifecycle_data):
        super().__init__(parent)
        self.data_manager = data_manager
        self.lifecycle_data = lifecycle_data
        
        serial_number = self.lifecycle_data['part_instance'].get('serial_number', 'N/A')
        self.title(f"Lifecycle for Part S/N: {serial_number}")
        self.geometry("900x500")
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        part_instance = self.lifecycle_data['part_instance']
        part_master = self.lifecycle_data['part_master']
        history = self.lifecycle_data['installation_history']

        info_frame = ttk.Frame(self, padding="10")
        info_frame.pack(fill="x")
        master_text = f"Part: {part_master.get('part_name', 'N/A')} ({part_master.get('part_number', 'N/A')}) | Manufacturer: {part_master.get('manufacturer', 'N/A')}"
        instance_text = f"Serial Number: {part_instance.get('serial_number', 'N/A')} | Manufacture Date: {part_instance.get('manufacture_date', 'N/A')}"
        ttk.Label(info_frame, text=master_text, font=("", 10, "bold")).pack(anchor="w")
        ttk.Label(info_frame, text=instance_text).pack(anchor="w")

        history_frame = ttk.Frame(self, padding="10")
        history_frame.pack(fill="both", expand=True)

        hist_cols = ('turbine', 'install_date', 'hours_install', 'starts_install', 'removal_date', 'hours_removal', 'starts_removal')
        hist_tree = ttk.Treeview(history_frame, columns=hist_cols, show='headings')
        for col in hist_cols:
            hist_tree.heading(col, text=col.replace('_', ' ').title())
            hist_tree.column(col, width=120, anchor='center')
        hist_tree.pack(fill="both", expand=True, side="left")
        
        hist_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=hist_tree.yview)
        hist_tree.configure(yscroll=hist_scrollbar.set)
        hist_scrollbar.pack(side='right', fill='y')

        for record in history:
            turbine = logic.get_turbine_by_id(self.data_manager, record['turbine_id'])
            turbine_sn = turbine['serial_number'] if turbine else 'N/A'
            hist_tree.insert('', tk.END, values=(
                turbine_sn, record.get('installation_date', ''),
                record.get('turbine_hours_at_install', ''), record.get('turbine_starts_at_install', ''),
                record.get('removal_date', 'Installed'), record.get('turbine_hours_at_removal', ''),
                record.get('turbine_starts_at_removal', '')
            ))