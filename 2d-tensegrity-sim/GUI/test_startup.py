#!/usr/bin/env python3
"""Test script to verify startup dialog works"""

import tkinter as tk
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simple test that creates just the startup dialog
class TestStartupDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Test Startup Dialog")
        self.geometry("400x200")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        
        self.selected_mode = None
        
        # Center on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (self.winfo_width() // 2)
        y = (screen_height // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(self, text="Test Dialog", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Buttons
        btn_2d = tk.Button(self, text="2D Mode", command=lambda: self.select("2d"), width=15)
        btn_2d.pack(pady=5)
        
        btn_3d = tk.Button(self, text="3D Mode", command=lambda: self.select("3d"), width=15)
        btn_3d.pack(pady=5)
        
        btn_cancel = tk.Button(self, text="Cancel", command=self.cancel, width=15)
        btn_cancel.pack(pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def select(self, mode):
        self.selected_mode = mode
        print(f"Selected: {mode}")
        self.destroy()
    
    def cancel(self):
        self.selected_mode = None
        print("Cancelled")
        self.destroy()

if __name__ == "__main__":
    print("Creating startup root...")
    startup_root = tk.Tk()
    startup_root.withdraw()
    
    print("Creating dialog...")
    dialog = TestStartupDialog(startup_root)
    
    print("Waiting for dialog...")
    startup_root.wait_window(dialog)
    
    print(f"Dialog closed. Selected mode: {dialog.selected_mode}")
    startup_root.destroy()
    
    if dialog.selected_mode:
        print(f"Would now launch {dialog.selected_mode} mode")
    else:
        print("User cancelled")
