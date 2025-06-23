import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os

class RowSelectPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Row Data Plotter with Row Selection")
        self.root.geometry("900x700")
        self.files = []
        self.legend_labels = []
        self.x_row = tk.IntVar(value=-1) 
        self.y_row = tk.IntVar(value=-2)
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        settings_frame = ttk.LabelFrame(main_frame, text="Row Selection", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="X-axis row index:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.x_row, width=5).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(settings_frame, text="Y-axis row index:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.y_row, width=5).grid(row=1, column=1, sticky=tk.W)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, columns=('File', 'Legend'), show='headings')
        self.tree.heading('File', text='File Name')
        self.tree.heading('Legend', text='Legend Label')
        self.tree.column('File', width=400, anchor=tk.W)
        self.tree.column('Legend', width=300, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Edit Legend", command=self.edit_legend).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Plot in New Window", command=self.plot_external).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
    
    def add_files(self):
        new_files = filedialog.askopenfilenames(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
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
            
        for item in reversed(selection):
            index = self.tree.index(item)
            del self.files[index]
            del self.legend_labels[index]
            self.tree.delete(item)
    
    def plot_external(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please add files first")
            return
        
        try:
            x_idx = int(self.x_row.get())
            y_idx = int(self.y_row.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Row indices must be integers")
            return
        
        fig, ax = plt.subplots(figsize=(9, 6))
        
        for i, file in enumerate(self.files):
            try:
                data = np.loadtxt(file, delimiter=',')
            
                x_data = data[x_idx] if x_idx >= 0 else data[x_idx]
                y_data = data[y_idx] if y_idx >= 0 else data[y_idx]
                
                ax.plot(
                    x_data,
                    y_data,
                    label=self.legend_labels[i],
                )
            except Exception as e:
                print(f"Error plotting {file}: {e}")
                continue
        
        ax.set_xlabel("ns")
        ax.set_ylabel("Amplitude (a.u.)")
        ax.legend(loc='upper right')
        ax.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def clear_all(self):
        self.files = []
        self.legend_labels = []
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = RowSelectPlotter(root)
    root.mainloop()