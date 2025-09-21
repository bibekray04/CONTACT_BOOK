
import json
import os
import uuid
import re
import csv
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

DATA_FILE = "contacts.json"

# ------------------ Themes ------------------
LIGHT_THEME = {
    "bg": "#F0F0F0",
    "frame_bg": "#E8E8E8",
    "entry_bg": "#FFFFFF",
    "entry_fg": "#000000",
    "btn_bg": "#4CAF50",
    "btn_fg": "#FFFFFF",
    "btn_hover": "#45A049",
    "tree_bg": "#FFFFFF",
    "tree_fg": "#000000",
    "tree_alt": "#F7F7F7",
    "highlight": "#FFD700"
}

DARK_THEME = {
    "bg": "#2E2E2E",
    "frame_bg": "#3C3F41",
    "entry_bg": "#5A5A5A",
    "entry_fg": "#FFFFFF",
    "btn_bg": "#1E90FF",
    "btn_fg": "#FFFFFF",
    "btn_hover": "#187bcd",
    "tree_bg": "#3C3F41",
    "tree_fg": "#FFFFFF",
    "tree_alt": "#4A4D4F",
    "highlight": "#FFA500"
}


class ContactBookApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Book")
        self.geometry("950x550")
        self.minsize(900, 500)

        self.contacts = []
        self.selected_contact_id = None
        self.theme = DARK_THEME  # default dark mode

        self.create_widgets()
        self.apply_theme()
        self.load_contacts()
        self.refresh_treeview()

    # ------------------ Theme ------------------
    def apply_theme(self):
        self.configure(bg=self.theme["bg"])
        for child in self.winfo_children():
            self.set_widget_theme(child)
        self.refresh_treeview()

    def set_widget_theme(self, widget):
        if isinstance(widget, (tk.Frame, ttk.Frame)):
            widget.configure(bg=self.theme["frame_bg"])
            for c in widget.winfo_children():
                self.set_widget_theme(c)
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], insertbackground=self.theme["entry_fg"])
        elif isinstance(widget, scrolledtext.ScrolledText):
            widget.configure(bg=self.theme["entry_bg"], fg=self.theme["entry_fg"], insertbackground=self.theme["entry_fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=self.theme["btn_bg"], fg=self.theme["btn_fg"], activebackground=self.theme["btn_hover"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=self.theme["frame_bg"], fg=self.theme["entry_fg"])
        elif isinstance(widget, ttk.Treeview):
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Treeview",
                            background=self.theme["tree_bg"],
                            foreground=self.theme["tree_fg"],
                            fieldbackground=self.theme["tree_bg"],
                            rowheight=30)
            style.map("Treeview", background=[("selected", self.theme["highlight"])])
        elif isinstance(widget, ttk.Scrollbar):
            pass

    def toggle_theme(self):
        self.theme = LIGHT_THEME if self.theme == DARK_THEME else DARK_THEME
        self.apply_theme()
        # Update hover tag color
        self.tree.tag_configure('hover', background=self.theme["highlight"], foreground=self.theme["tree_fg"])

    # ------------------ UI ------------------
    def create_widgets(self):
        pad = 10
        font_label = ("Arial", 12, "bold")
        font_entry = ("Arial", 12)
        
        frm_top = tk.Frame(self)
        frm_top.pack(fill=tk.X, padx=pad, pady=(pad, 0))

        # Labels & entries
        lbl_name = tk.Label(frm_top, text="Name:", font=font_label)
        lbl_name.grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        self.ent_name = tk.Entry(frm_top, width=35, font=font_entry)
        self.ent_name.grid(row=0, column=1, sticky=tk.W)

        lbl_phone = tk.Label(frm_top, text="Phone:", font=font_label)
        lbl_phone.grid(row=0, column=2, sticky=tk.W, padx=(12, 6))
        self.ent_phone = tk.Entry(frm_top, width=25, font=font_entry)
        self.ent_phone.grid(row=0, column=3, sticky=tk.W)

        lbl_email = tk.Label(frm_top, text="Email:", font=font_label)
        lbl_email.grid(row=1, column=0, sticky=tk.W, padx=(0, 6), pady=(8, 0))
        self.ent_email = tk.Entry(frm_top, width=35, font=font_entry)
        self.ent_email.grid(row=1, column=1, sticky=tk.W, pady=(8, 0))

        lbl_address = tk.Label(frm_top, text="Address:", font=font_label)
        lbl_address.grid(row=1, column=2, sticky=tk.NW, padx=(12, 6), pady=(8, 0))
        self.txt_address = scrolledtext.ScrolledText(frm_top, width=30, height=3, font=font_entry)
        self.txt_address.grid(row=1, column=3, sticky=tk.W, pady=(8, 0))

        # Buttons frame on far right
        frm_buttons = tk.Frame(frm_top)
        frm_buttons.grid(row=0, column=4, rowspan=2, sticky=tk.NE, padx=(20, 0))
        
        self.buttons = {}
        btn_texts = ["Add", "Update", "Delete", "Import CSV", "Export CSV", "Toggle Theme"]
        btn_cmds = [self.add_contact, self.update_contact, self.delete_contact,
                    self.import_csv, self.export_csv, self.toggle_theme]

        for txt, cmd in zip(btn_texts, btn_cmds):
            b = tk.Button(frm_buttons, text=txt, width=16, font=("Arial", 11, "bold"), command=cmd)
            b.pack(pady=6)
            b.bind("<Enter>", lambda e, b=b: b.config(bg=self.theme["btn_hover"]))
            b.bind("<Leave>", lambda e, b=b: b.config(bg=self.theme["btn_bg"]))
            self.buttons[txt] = b

        # Search
        frm_search = tk.Frame(self)
        frm_search.pack(fill=tk.X, padx=pad, pady=(pad, 0))
        lbl_search = tk.Label(frm_search, text="Search (name or phone):", font=("Arial", 11, "bold"))
        lbl_search.pack(side=tk.LEFT)
        self.ent_search = tk.Entry(frm_search, font=("Arial", 12))
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
        self.ent_search.bind("<KeyRelease>", lambda e: self.search_contacts())
        btn_show_all = tk.Button(frm_search, text="Show All", font=("Arial", 11, "bold"), command=self.show_all)
        btn_show_all.pack(side=tk.LEFT, padx=(6, 0))

        # Treeview
        frm_table = tk.Frame(self)
        frm_table.pack(fill=tk.BOTH, expand=True, padx=pad, pady=(pad, 0))
        columns = ("name", "phone", "email", "address")
        self.tree = ttk.Treeview(frm_table, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=col.title(), anchor="center",
                              command=lambda c=col: self.treeview_sort_column(c, False))
            self.tree.column(col, anchor="center", width=200)

        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frm_table.rowconfigure(0, weight=1)
        frm_table.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right-click context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Edit", command=self.edit_selected_contact)
        self.menu.add_command(label="Delete", command=self.delete_selected_contact)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Hover effect
        self.tree.tag_configure('hover', background=self.theme["highlight"], foreground=self.theme["tree_fg"])
        self.tree.bind("<Motion>", self.on_tree_hover)

    # ------------------ Treeview Hover ------------------
    def on_tree_hover(self, event):
        row_id = self.tree.identify_row(event.y)
        for item in self.tree.get_children():
            if item == row_id:
                self.tree.item(item, tags=('hover',))
            else:
                self.tree.item(item, tags=('row',))

    # ------------------ Context Menu ------------------
    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.menu.tk_popup(event.x_root, event.y_root)

    def edit_selected_contact(self):
        sel = self.tree.selection()
        if sel:
            cid = sel[0]
            contact = next((c for c in self.contacts if c["id"] == cid), None)
            if contact:
                self.selected_contact_id = cid
                self.ent_name.delete(0, tk.END)
                self.ent_name.insert(0, contact["name"])
                self.ent_phone.delete(0, tk.END)
                self.ent_phone.insert(0, contact["phone"])
                self.ent_email.delete(0, tk.END)
                self.ent_email.insert(0, contact["email"])
                self.txt_address.delete("1.0", tk.END)
                self.txt_address.insert("1.0", contact["address"])

    def delete_selected_contact(self):
        sel = self.tree.selection()
        if sel:
            self.selected_contact_id = sel[0]
            self.delete_contact()

    # ------------------ Persistence & Utilities ------------------
    def load_contacts(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.contacts = json.load(f)
            except:
                self.contacts = []

    def save_contacts(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.contacts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showwarning("Save Error", str(e))

    def clear_inputs(self):
        self.ent_name.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.txt_address.delete("1.0", tk.END)
        self.selected_contact_id = None
        self.tree.selection_remove(self.tree.selection())

    def get_inputs(self):
        return (self.ent_name.get().strip(),
                self.ent_phone.get().strip(),
                self.ent_email.get().strip(),
                self.txt_address.get("1.0", tk.END).strip())

    def auto_resize_columns(self):
        for col in self.tree["columns"]:
            max_width = max(
                [len(str(self.tree.set(k, col))) for k in self.tree.get_children()] + [len(col)]
            )
            self.tree.column(col, width=max_width*10)

    def refresh_treeview(self, contacts=None, highlight_query=""):
        for r in self.tree.get_children():
            self.tree.delete(r)
        to_show = contacts if contacts is not None else self.contacts
        q = highlight_query.lower()
        for idx, c in enumerate(to_show):
            if q and (q in c["name"].lower() or q in c["phone"].lower()):
                bg = self.theme["highlight"]
            else:
                bg = self.theme["tree_alt"] if idx % 2 == 0 else self.theme["tree_bg"]
            self.tree.insert("", tk.END, iid=c["id"],
                             values=(c["name"], c["phone"], c["email"], c["address"]),
                             tags=('row',))
            self.tree.tag_configure('row', background=bg, foreground=self.theme["tree_fg"])
        self.auto_resize_columns()

    # ------------------ Validation & Phone ------------------
    def validate_contact(self, name, phone, email):
        if not name or not phone:
            messagebox.showinfo("Validation", "Name and Phone cannot be empty.")
            return False
        if email and "@" not in email:
            messagebox.showinfo("Validation", "Invalid email.")
            return False
        return True

    def normalize_phone(self, phone):
        return re.sub(r'\D', '', phone)

    # ------------------ Add/Update/Delete ------------------
    def add_contact(self):
        name, phone, email, address = self.get_inputs()
        if not self.validate_contact(name, phone, email):
            return
        for c in self.contacts:
            if self.normalize_phone(c["phone"]) == self.normalize_phone(phone):
                messagebox.showinfo("Duplicate", "Phone number exists.")
                return
        new_contact = {"id": str(uuid.uuid4()), "name": name, "phone": phone, "email": email, "address": address}
        self.contacts.append(new_contact)
        self.save_contacts()
        self.refresh_treeview()
        self.clear_inputs()

    def update_contact(self):
        if not self.selected_contact_id:
            messagebox.showinfo("Select", "Select a contact to update.")
            return
        name, phone, email, address = self.get_inputs()
        if not self.validate_contact(name, phone, email):
            return
        for c in self.contacts:
            if self.normalize_phone(c["phone"]) == self.normalize_phone(phone) and c["id"] != self.selected_contact_id:
                messagebox.showinfo("Duplicate", "Another contact has this phone number.")
                return
        for c in self.contacts:
            if c["id"] == self.selected_contact_id:
                c.update({"name": name, "phone": phone, "email": email, "address": address})
                break
        self.save_contacts()
        self.refresh_treeview()
        self.clear_inputs()

    def delete_contact(self):
        if not self.selected_contact_id:
            messagebox.showinfo("Select", "Select a contact to delete.")
            return
        if not messagebox.askyesno("Delete", "Are you sure?"):
            return
        self.contacts = [c for c in self.contacts if c["id"] != self.selected_contact_id]
        self.save_contacts()
        self.refresh_treeview()
        self.clear_inputs()

    # ------------------ Search ------------------
    def search_contacts(self):
        q = self.ent_search.get().strip().lower()
        if not q:
            self.refresh_treeview()
            return
        filtered = [c for c in self.contacts if q in c["name"].lower() or q in c["phone"].lower()]
        self.refresh_treeview(filtered, highlight_query=q)

    def show_all(self):
        self.ent_search.delete(0, tk.END)
        self.refresh_treeview()

    # ------------------ Treeview selection ------------------
    def on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            cid = sel[0]
            contact = next((c for c in self.contacts if c["id"] == cid), None)
            if contact:
                self.selected_contact_id = cid
                self.ent_name.delete(0, tk.END)
                self.ent_name.insert(0, contact["name"])
                self.ent_phone.delete(0, tk.END)
                self.ent_phone.insert(0, contact["phone"])
                self.ent_email.delete(0, tk.END)
                self.ent_email.insert(0, contact["email"])
                self.txt_address.delete("1.0", tk.END)
                self.txt_address.insert("1.0", contact["address"])

    # ------------------ CSV ------------------
    def export_csv(self):
        if not self.contacts:
            messagebox.showinfo("Export CSV", "No contacts to export.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        with open(file_path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "phone", "email", "address"])
            writer.writeheader()
            for c in self.contacts:
                writer.writerow(c)
        messagebox.showinfo("Export CSV", "Contacts exported successfully.")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if "name" in row and "phone" in row:
                    row["id"] = str(uuid.uuid4())
                    self.contacts.append(row)
                    count += 1
        self.save_contacts()
        self.refresh_treeview()
        messagebox.showinfo("Import CSV", f"{count} contacts imported.")

    # ------------------ Sorting ------------------
    def treeview_sort_column(self, col, reverse):
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        try:
            data_list.sort(key=lambda t: int(re.sub(r'\D','',t[0])), reverse=reverse)
        except:
            data_list.sort(key=lambda t: t[0].lower(), reverse=reverse)
        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, not reverse))


if __name__ == "__main__":
    app = ContactBookApp()
    app.mainloop()

