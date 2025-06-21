# gui_components.py

import tkinter as tk
from tkinter import ttk, messagebox

class FormPopup(tk.Toplevel):
    """
    A generic Toplevel window for creating data entry forms.
    This is a reusable component with no specific application logic.
    """
    def __init__(self, parent, title, fields, save_callback):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.fields = fields
        self.save_callback = save_callback
        self.entries = {}

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill="both", expand=True)

        # Create a label and entry for each field passed in
        for i, field in enumerate(self.fields):
            label_text = field.replace('_', ' ').title()
            ttk.Label(form_frame, text=label_text).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            self.entries[field] = entry
        
        form_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Save", command=self._on_save).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")

    def _on_save(self):
        """Gathers data from entries and calls the provided save callback function."""
        data = {field: entry.get() for field, entry in self.entries.items()}
        try:
            self.save_callback(**data)
            self.destroy()
        except (ValueError, TypeError, KeyError) as e:
            messagebox.showerror("Error", f"Could not save the data:\n{e}", parent=self)