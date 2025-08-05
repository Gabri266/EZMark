import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import re

CONFIG_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "ezcad_config.json")


class EZCADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EZCAD Laser Manager")
        self.root.geometry("500x250")

        self.setup_config = self.load_config()

        # Etichette e campo input
        tk.Label(root, text="DATAMATRIX RILEVATO").pack(pady=5)
        self.dm_entry = tk.Entry(root, width=60)
        self.dm_entry.pack(pady=5)
        self.dm_entry.focus()

        # Pulsanti
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="SETUP", command=self.setup_window).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="REFRESH", command=self.refresh_files).grid(row=0, column=1, padx=10)

        # Avviso
        tk.Label(root, text="⚠️ Assicurati che il lettore invii il codice completo (attenzione a spazi o newline)", fg="red").pack(pady=5)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return self.initial_setup()

    def save_config(self):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.setup_config, f, indent=2)

    def initial_setup(self):
        messagebox.showinfo("Setup Iniziale", "Seleziona la cartella dove salvare i file.")
        folder = filedialog.askdirectory(title="Scegli cartella di destinazione")

        if not folder:
            messagebox.showerror("Errore", "Cartella non selezionata. Riavvia il programma.")
            exit()

        # Richiedi i nomi dei 2 o 3 file
        def ask_filename(title, default):
            name = tk.simpledialog.askstring("Nome File", f"Inserisci il nome per {title} (senza estensione):")
            return name.strip() + ".txt" if name else default

        data_file = ask_filename("DATA (grezzo)", "DATA.txt")
        info_file = ask_filename("INFO (elaborato)", "INFO.txt")
        extra_file = ask_filename("TERZO FILE (opzionale)", "ALTRO.txt")

        config = {
            "folder": folder,
            "data_file": data_file,
            "info_file": info_file,
            "extra_file": extra_file
        }

        self.setup_config = config
        self.save_config()
        return config

    def setup_window(self):
        win = tk.Toplevel(self.root)
        win.title("Setup Avanzato")
        win.geometry("400x150")

        tk.Label(win, text="Cartella corrente:").pack()
        tk.Label(win, text=self.setup_config["folder"], fg="blue").pack()

        def cambia_cartella():
            nuova = filedialog.askdirectory(title="Nuova cartella")
            if nuova:
                self.setup_config["folder"] = nuova
                self.save_config()
                messagebox.showinfo("Ok", "Cartella aggiornata.")
                win.destroy()

        tk.Button(win, text="Cambia cartella di salvataggio", command=cambia_cartella).pack(pady=10)

    def refresh_files(self):
        datamatrix = self.dm_entry.get().strip()

        if not datamatrix:
            messagebox.showerror("Errore", "Campo vuoto.")
            return

        folder = self.setup_config["folder"]
        data_path = os.path.join(folder, self.setup_config["data_file"])
        info_path = os.path.join(folder, self.setup_config["info_file"])
        extra_path = os.path.join(folder, self.setup_config["extra_file"])

        # Scrive il file DATA (grezzo)
        with open(data_path, "w", encoding="utf-8") as f:
            f.write(datamatrix)

        # Parsing smart (espandibile)
        info_lines = self.parse_datamatrix(datamatrix)

        with open(info_path, "w", encoding="utf-8") as f:
            for line in info_lines:
                f.write(line + "\n")

        # Terzo file (opzionale, stesso contenuto o espandibile)
        with open(extra_path, "w", encoding="utf-8") as f:
            f.write("File extra generato.\n")

        # Pulisce il campo input
        self.dm_entry.delete(0, tk.END)

    def parse_datamatrix(self, text):
        # Parsing intelligente per SN, SuN, HW, SW
        parsed = []
        tags = ['SuN', 'SN', 'HW', 'SW']
        for tag in tags:
            match = re.search(rf'{tag}(\w+)', text)
            if match:
                parsed.append(f"{tag}: {match.group(1)}")
        return parsed if parsed else ["Nessun dato riconosciuto"]

# Avvio programma
if __name__ == "__main__":
    import tkinter.simpledialog  # Necessario per input testuali
    root = tk.Tk()
    app = EZCADApp(root)
    root.mainloop()
