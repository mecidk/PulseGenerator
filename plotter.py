import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os

class LegendColumnPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Plotter")
        self.root.geometry("800x600")
        
        self.files = []
        self.legend_labels = []
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(main_frame, columns=('File', 'Legend'), show='headings')
        self.tree.heading('File', text='File Name')
        self.tree.heading('Legend', text='Legend Label')
        self.tree.column('File', width=300, anchor=tk.W)
        self.tree.column('Legend', width=300, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit Legend", command=self.edit_legend).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Plot in New Window", command=self.plot_external).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
    
    def add_files(self):
        new_files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt")])
        if new_files:
            for f in new_files:
                self.files.append(f)
                base_name = os.path.splitext(os.path.basename(f))[0]
                self.legend_labels.append(base_name)
                self.tree.insert('', tk.END, values=(os.path.basename(f), base_name))
    
    def edit_legend(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to edit")
            return
            
        item = selection[0]
        current_values = self.tree.item(item, 'values')
        new_label = simpledialog.askstring(
            "Edit Legend Label",
            "Enter new legend label:",
            initialvalue=current_values[1]
        )
        
        if new_label:
            self.tree.set(item, 'Legend', new_label)
            index = self.tree.index(item)
            self.legend_labels[index] = new_label
    
    def remove_selected(self):
        selection = self.tree.selection()
        if not selection:
            return
            
        for item in reversed(selection):  # Reverse to prevent index shifting
            index = self.tree.index(item)
            del self.files[index]
            del self.legend_labels[index]
            self.tree.delete(item)
    
    def plot_external(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please add files first")
            return
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        for i, file in enumerate(self.files):
            try:
                data = np.loadtxt(file, delimiter=',')
                if len(data) >= 2:
                    ax.plot(
                        data[-1],  # Last row as X
                        data[-2],  # Second last row as Y
                        label=self.legend_labels[i],
                    )
            except Exception as e:
                print(f"Error plotting {file}: {e}")
        
        ax.set_xlabel("ns")
        ax.set_ylabel("a. u.")
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.show()
    
    def clear_all(self):
        self.files = []
        self.legend_labels = []
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = LegendColumnPlotter(root)
    root.mainloop()