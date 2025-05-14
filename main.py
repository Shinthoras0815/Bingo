# main.py

import os
import math
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from data_manager import DataManager
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(sys.argv[0])

DATA_FILE = os.path.join(BASE_DIR, "bingo_data.json")

class BingoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bingo App")
        self.geometry("600x400")
        self.dm = DataManager()
        self.create_widgets()
        # Save data at exit
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):

        # Configure the main window grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Create a frame for the category management on the left side
        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Configure row weights for the left frame
        left.rowconfigure(5, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Neue Kategorie:").grid(row=0, column=0, sticky="w")
        self.cat_var = tk.StringVar()
        self.cat_entry = ttk.Entry(left, textvariable=self.cat_var)
        self.cat_entry.grid(row=1, column=0, columnspan=2, sticky="we", pady=5)
        ttk.Button(left, text="Hinzufügen", command=self.add_category).grid(row=2, column=0, sticky="w", pady=5)
        ttk.Button(left, text="Entfernen", command=self.remove_category).grid(row=2, column=1, sticky="w", pady=5)

        self.cat_var.trace_add("write", self.on_cat_entry_text_change)

        # category listbox
        self.cat_listbox = tk.Listbox(left, exportselection=False)
        self.cat_listbox.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=0)
        self.cat_listbox.bind("<<ListboxSelect>>", self.on_cat_select)
        cat_scroll = ttk.Scrollbar(left, orient="vertical")
        cat_scroll.grid(row=5, column=2, sticky="ns")
        cat_scroll.config(command=self.cat_listbox.yview)
        self.cat_listbox.config(yscrollcommand=cat_scroll.set)

        # Create a frame for the word management on the right side
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Configure row weights for the right frame
        right.rowconfigure(5, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Wort hinzufügen:").grid(row=2, column=0, sticky="w")
        self.word_entry = ttk.Entry(right)
        self.word_entry.grid(row=3, column=0, columnspan=2, sticky="we", pady=5)

        ttk.Label(right, text="Kategorie Gewichtung:").grid(row=0, column=0, sticky="w")
        self.weight_spin = ttk.Spinbox(right, from_=1, to=10, width=5, command=self.on_weight_change)
        self.weight_spin.grid(row=1, column=0, sticky="w", pady=5)

        ttk.Label(right, text="Kategorie aktivieren:").grid(row=0, column=1, sticky="w")
        self.checkbox_var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(right, variable=self.checkbox_var, command=self.on_checkbox_toggle)
        self.checkbox.grid(row=1, column=1, sticky="w", pady=5)

        ttk.Button(right, text="Wort speichern", command=self.save_word).grid(row=4, column=0, sticky="w", pady=5)
        ttk.Button(right, text="Wort entfernen", command=self.remove_word).grid(row=4, column=1, sticky="w", pady=5)

        # word listbox
        self.word_listbox = tk.Listbox(right)
        self.word_listbox.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=0)
        word_scroll = ttk.Scrollbar(right, orient="vertical")
        word_scroll.grid(row=5, column=2, sticky="ns")
        word_scroll.config(command=self.word_listbox.yview)
        self.word_listbox.config(yscrollcommand=word_scroll.set)

        #bottom buttons
        bottom = ttk.Frame(self)
        bottom.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)
        ttk.Button(bottom, text="Bingo generieren", command=self.generate_bingo).grid(row=1, column=0, pady=5)
        ttk.Label(bottom, text="Karten Größe:").grid(row=1, column=1, sticky="w")
        self.size_spin = ttk.Spinbox(bottom,  from_=1, to=10, width=5)
        self.size_spin.grid(row=1, column=2, sticky="w", pady=5)
        self.size_spin.set(5)
        # loading message
        if self.dm.load_from_file(DATA_FILE):
            message = ("Loaded data from:")
            self.refresh_ui()
        else:
            message =(" Starting with empty lists. File not found:")
        self.label = ttk.Label(bottom, text=message)
        self.label.grid(row=0, column=3, columnspan=2, sticky="w")
        ttk.Label(bottom, text=(f"{DATA_FILE}")).grid(row=1, column=3, columnspan=2, sticky="we")

    # Method to save the word
    def save_word(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            messagebox.showwarning("Keine Kategorie", "Bitte zuerst eine Kategorie auswählten.")
            return
        cat = self.cat_listbox.get(sel[0])
        word = self.word_entry.get().strip()
        if word:
            self.dm.add_word(cat,word)
            self.on_cat_select(None) # Refresh the listbox to show the new word
            self.word_entry.delete(0, tk.END)

    def remove_word(self):
        sel = self.word_listbox.curselection()
        cat = self.cat_listbox.curselection()
        word = self.word_listbox.get(sel[0])
        if sel and cat and word:
            cat = self.cat_listbox.get(cat[0])
            self.dm.remove_word(cat, word)
            self.word_listbox.delete(sel[0])

    def add_category(self):
        name = self.cat_entry.get().strip()
        weight = int(self.weight_spin.get())
        if name:
            self.dm.add_category(name, weight=1)  # Default weight is 1
            self.cat_listbox.insert(tk.END, name)
            self.cat_entry.delete(0, tk.END)
            self.dm.set_weight(name, weight)
            self.dm.lists[name]['used'] = True
        self.on_cat_select(self)

    def on_cat_entry_text_change(self, name, index, mode):
        # Check if the entry is empty and set the weight to 1 if it is
        if self.cat_var.get().strip():
            self.weight_spin.set(1)
            self.cat_listbox.selection_clear(0,tk.END)
        else:
            self.weight_spin.set('')

    def on_cat_select(self, event):
        sel = self.cat_listbox.curselection()
        if not sel: return
        cat = self.cat_listbox.get(sel[0])
        self.word_listbox.delete(0, tk.END)
        for w in self.dm.lists[cat]['words']:
            self.word_listbox.insert(tk.END, w)
        current_weight = self.dm.lists[cat]['weight']
        self.checkbox_var.set(self.dm.lists[cat]['used'])
        self.weight_spin.delete(0, tk.END)
        self.weight_spin.insert(0, str(current_weight))

    def on_weight_change(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        cat = self.cat_listbox.get(sel[0])
        try:
            new_weight = int(self.weight_spin.get())
            self.dm.set_weight(cat, new_weight)
        except ValueError:
            pass  # Ignore invalid input

    def on_checkbox_toggle(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        cat = self.cat_listbox.get(sel[0])
        if self.checkbox_var.get():
            self.dm.lists[cat]['used'] = True
        else:
            self.dm.lists[cat]['used'] = False

    def remove_category(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            messagebox.showwarning("Keine Kategorie", "Bitte zuerst eine Kategorie auswählten.")
            return
        cat = self.cat_listbox.get(sel[0])
        while cat in self.dm.lists:
            self.dm.remove_category(cat)
            self.cat_listbox.delete(sel[0])
            self.word_listbox.delete(0, tk.END)
        self.on_cat_select(self)

    def generate_bingo(self):
        size = int(self.size_spin.get())
        card = self.dm.draw_unique(size*size)
        if len(card) < size * size:
            messagebox.showwarning("Nicht genug Wörter", "Nicht genug Wörter für die Karte.")
            return
        else:
            self.show_card_window(card)

    def wrap_text(self, text, font, max_width):
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            # check if word contains a "-"
            if '-' in word:
                # divide the word into parts at the "-"
                sub_words = word.split('-')
                for i, sub_word in enumerate(sub_words):
                    # add the sub-word to the current line
                    if i < len(sub_words) - 1:
                        sub_word += '-'
                    test_line = " ".join(current_line + [sub_word])
                    bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_line, font=font)
                    line_width = bbox[2] - bbox[0]

                    if line_width > max_width and not current_line:
                        # if the word is still too long, split it
                        split_word = ""
                        for char in sub_word:
                            test_split = split_word + char
                            bbox_split = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_split, font=font)
                            if bbox_split[2] - bbox_split[0] > max_width:
                                lines.append(split_word)
                                split_word = char
                            else:
                                split_word += char
                        if split_word:
                            lines.append(split_word)
                    elif line_width <= max_width:
                        current_line.append(sub_word)
                    else:
                        lines.append(" ".join(current_line))
                        current_line = [sub_word]
            else:
                # normal word processing
                test_line = " ".join(current_line + [word])
                bbox = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]

                if line_width > max_width and not current_line:
                    split_word = ""
                    for char in word:
                        test_split = split_word + char
                        bbox_split = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), test_split, font=font)
                        if bbox_split[2] - bbox_split[0] > max_width:
                            lines.append(split_word)
                            split_word = char
                        else:
                            split_word += char
                    if split_word:
                        lines.append(split_word)
                elif line_width <= max_width:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def show_card_window(self, card):
        win = tk.Toplevel(self)
        win.title("Bingo Karte")
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True)
        size = int(len(card) ** 0.5)
        for idx, word in enumerate(card):
            row = idx // size
            col = idx % size
            lbl = tk.Label(frame, text=word, borderwidth=2, relief="ridge", width=12, height=5, wraplength=80, anchor="center", justify="center")
            lbl.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            for i in range(size):
                frame.grid_rowconfigure(i, weight=1)
                frame.grid_columnconfigure(i, weight=1)
        # Create a button to save the card as an image
        btn_frame = ttk.Frame(win, padding=(0,5))
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Exportieren", command=lambda: self.export_card(card)).pack(side="right")

    def export_card(self, card):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
        if not file_path:
            return

        size = int(math.sqrt(len(card)))
        cell_w, cell_h = 200, 100
        img = Image.new("RGB", (cell_w * size, cell_h * size), "white")
        draw = ImageDraw.Draw(img)

        # loade a font
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        # draw the grid and words
        for idx, word in enumerate(card):
            row, col = divmod(idx, size)
            x0, y0 = col * cell_w, row * cell_h
            x1, y1 = x0 + cell_w, y0 + cell_h
            draw.rectangle([x0, y0, x1, y1], outline="black", width=2)

            # breake the word into lines
            lines = self.wrap_text(word, font, cell_w - 10)  # 10px padding
            if not lines:
                continue

            # calculating the height of the text block
            total_text_height = len(lines) * (font.size + 5) # 5px padding between lines
            y_offset = y0 + (cell_h - total_text_height) / 2  # vertical centering

            # draw the text
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x_offset = x0 + (cell_w - line_width) / 2  # horizontal centering
                draw.text((x_offset, y_offset), line, fill="black", font=font)
                y_offset += font.size + 5  # move down for the next line

        # save the image
        img.save(file_path)
        messagebox.showinfo("Erfolg", f"Karte gespeichert als {file_path}")

    def refresh_ui(self):
        # Refresh the UI elements based on the current state of the DataManager
        self.cat_listbox.delete(0, tk.END)
        for category in self.dm.lists.keys():
            self.cat_listbox.insert(tk.END, category)

    def on_closing(self):
        # Save data to file before closing
        self.dm.save_to_file(DATA_FILE)
        self.label.config(text=("Saved data to:"))
        self.after(1000, self.destroy)

if __name__ == "__main__":
    app = BingoApp()
    app.mainloop()



