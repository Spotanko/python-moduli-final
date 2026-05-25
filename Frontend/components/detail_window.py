import customtkinter as ctk
import webbrowser
import pyperclip
from Backend.model import PythonModule, Example

class DetailWindow(ctk.CTkToplevel):
    """
    Popup prozor za prikaz detaljnih informacija o modulu.
    Sadrži kartice (Tabview) za opis i interaktivni pregled primjera koda.
    """
    def __init__(self, master, modul: PythonModule, **kwargs):
        super().__init__(master, **kwargs)
        
        self.modul = modul
        
        # Postavke prozora
        self.title(f"Detalji modula: {self.modul.name}")
        self.geometry("750x620")
        self.minsize(700, 550)
        
        # Osiguravamo da popup bude u prvom planu i modalan
        self.after(10, self._postavi_modalnost)

        # Glavni kontejner s marginama
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # --- ZAGLAVLJE POPUPA ---
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)

        # Naslov modula
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.modul.name,
            font=("Segoe UI", 28, "bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Kategorija i ugrađenost
        meta_text = f"Kategorija: {self.modul.category}  |  Instalacija: {self.modul.dohvati_install_tekst()}"
        meta_label = ctk.CTkLabel(
            header_frame,
            text=meta_text,
            font=("Segoe UI", 12),
            text_color=("#475569", "#94a3b8"),
            anchor="w"
        )
        meta_label.grid(row=1, column=0, sticky="w", pady=(2, 5))

        # Gumb za službenu dokumentaciju
        btn_docs = ctk.CTkButton(
            header_frame,
            text="Službena dokumentacija 🌐",
            font=("Segoe UI", 12, "bold"),
            fg_color=("#475569", "#334155"),
            hover_color=("#334155", "#475569"),
            width=170,
            command=self._otvori_dokumentaciju
        )
        btn_docs.grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))

        # --- RAZINE TEŽINE (BADGES) ---
        levels_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        levels_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            levels_frame,
            text="Razine težine: ",
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")
        
        level_colors = {
            "osnovno": ("#dcfce7", "#14532d", "#22c55e"),      # Zelena (bg, fg_light, fg_dark)
            "srednje": ("#fef3c7", "#78350f", "#eab308"),      # Žuta
            "napredno": ("#fee2e2", "#7f1d1d", "#ef4444")      # Crvena
        }

        for lvl in self.modul.levels:
            lvl_lower = lvl.lower()
            colors = level_colors.get(lvl_lower, ("#e2e8f0", "#1e293b", "#94a3b8"))
            
            lbl = ctk.CTkLabel(
                levels_frame,
                text=lvl.capitalize(),
                font=("Segoe UI", 11, "bold"),
                text_color=(colors[1], "#ffffff"),
                fg_color=(colors[0], colors[2]),
                corner_radius=6,
                width=75,
                height=20
            )
            lbl.pack(side="left", padx=5)

        # --- TABVIEW (OPIS I PRIMJERI) ---
        self.tabview = ctk.CTkTabview(
            main_container,
            segmented_button_selected_color=("#0284c7", "#0ea5e9"),
            segmented_button_selected_hover_color=("#0369a1", "#0284c7")
        )
        self.tabview.pack(fill="both", expand=True)

        self.tab_desc = self.tabview.add("Opis modula")
        self.tab_examples = self.tabview.add("Primjeri koda")

        self._kreiraj_tab_opis()
        self._kreiraj_tab_primjeri()

    def _postavi_modalnost(self):
        """Osigurava fokus i modalnost prozora."""
        self.grab_set()
        self.focus_force()

    def _otvori_dokumentaciju(self):
        """Otvara službeni URL dokumentacije u web pregledniku."""
        if self.modul.docs:
            webbrowser.open(self.modul.docs)

    def _kreiraj_tab_opis(self):
        """Kreira sadržaj taba za opis."""
        self.tab_desc.grid_rowconfigure(0, weight=1)
        self.tab_desc.grid_columnconfigure(0, weight=1)
        
        # Koristimo onemogućen Textbox za selektabilni tekst opisa
        desc_box = ctk.CTkTextbox(
            self.tab_desc, 
            font=("Segoe UI", 14), 
            wrap="word",
            fg_color="transparent",
            text_color=("#1e293b", "#f1f5f9")
        )
        desc_box.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # Upisivanje opisa
        opis_tekst = self.modul.description if self.modul.description else "Nema dostupnog opisa."
        desc_box.insert("1.0", opis_tekst)
        desc_box.configure(state="disabled")

    def _kreiraj_tab_primjeri(self):
        """Kreira sadržaj taba s primjerima koda (sidebar s lijeve strane, detalji s desne)."""
        if not self.modul.examples:
            lbl = ctk.CTkLabel(
                self.tab_examples,
                text="Za ovaj modul trenutno nema unesenih primjera.",
                font=("Segoe UI", 14, "italic")
            )
            lbl.pack(pady=50)
            return

        self.tab_examples.grid_columnconfigure(0, weight=1) # Lijevi popis (širi se manje)
        self.tab_examples.grid_columnconfigure(1, weight=3) # Desni detalji (širi se više)
        self.tab_examples.grid_rowconfigure(0, weight=1)

        # 1. Lijevi dio: popis primjera (Scrollable Frame)
        self.sidebar_examples = ctk.CTkScrollableFrame(
            self.tab_examples, 
            width=180, 
            label_text="Popis primjera",
            label_font=("Segoe UI", 12, "bold")
        )
        self.sidebar_examples.grid(row=0, column=0, sticky="nsew", padx=(5, 10), pady=10)
        
        # 2. Desni dio: detalji odabranog primjera
        self.detail_frame = ctk.CTkFrame(self.tab_examples, fg_color="transparent")
        self.detail_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        self.detail_frame.columnconfigure(0, weight=1)
        self.detail_frame.rowconfigure(2, weight=1) # Code box raste

        # Naziv primjera i razina
        self.ex_title_lbl = ctk.CTkLabel(self.detail_frame, text="", font=("Segoe UI", 16, "bold"), anchor="w")
        self.ex_title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.ex_desc_lbl = ctk.CTkLabel(self.detail_frame, text="", font=("Segoe UI", 12, "italic"), text_color="gray", justify="left", anchor="w", wraplength=400)
        self.ex_desc_lbl.grid(row=1, column=0, sticky="w", pady=(0, 10))

        # Code Viewer Frame (Toolbar + Textbox)
        code_viewer = ctk.CTkFrame(self.detail_frame, fg_color=("#cbd5e1", "#1e1e1e"), corner_radius=8)
        code_viewer.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        code_viewer.columnconfigure(0, weight=1)
        code_viewer.rowconfigure(1, weight=1)

        # Toolbar koda s gumbom za kopiranje
        code_toolbar = ctk.CTkFrame(code_viewer, fg_color=("#94a3b8", "#121212"), height=30, corner_radius=0)
        code_toolbar.grid(row=0, column=0, sticky="ew")
        code_toolbar.grid_propagate(False)
        
        lbl_code = ctk.CTkLabel(code_toolbar, text="PYTHON KOD", font=("Segoe UI", 10, "bold"), text_color=("#0f172a", "#94a3b8"))
        lbl_code.pack(side="left", padx=10)
        
        self.btn_copy_code = ctk.CTkButton(
            code_toolbar, 
            text="📋 Kopiraj kod", 
            font=("Segoe UI", 11),
            width=100,
            fg_color="transparent",
            hover_color=("#cbd5e1", "#2b2b2b"),
            text_color=("#0f172a", "#38bdf8"),
            command=self._kopiraj_kod
        )
        self.btn_copy_code.pack(side="right", padx=5)

        # Monospace Textbox za kod
        self.code_text = ctk.CTkTextbox(
            code_viewer, 
            font=("Consolas", 12), 
            fg_color="transparent",
            text_color=("#0f172a", "#38bdf8")
        )
        self.code_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Očekivani izlaz (Output)
        self.output_frame = ctk.CTkFrame(self.detail_frame, fg_color=("#cbd5e1", "#111827"), height=100, corner_radius=8)
        self.output_frame.grid(row=3, column=0, sticky="ew")
        self.output_frame.columnconfigure(0, weight=1)
        self.output_frame.rowconfigure(1, weight=1)
        
        lbl_out = ctk.CTkLabel(self.output_frame, text="Očekivani izlaz (Output):", font=("Segoe UI", 10, "bold"), text_color=("#475569", "#94a3b8"), anchor="w")
        lbl_out.grid(row=0, column=0, sticky="w", padx=10, pady=(4, 0))
        
        self.output_text = ctk.CTkTextbox(
            self.output_frame, 
            font=("Consolas", 11), 
            fg_color="transparent",
            text_color=("#0f172a", "#10b981"), # Zeleni output
            height=60
        )
        self.output_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Popunjavanje sidebara gumbima za primjere
        self.buttons: List[ctk.CTkButton] = []
        for idx, ex in enumerate(self.modul.examples):
            btn = ctk.CTkButton(
                self.sidebar_examples,
                text=ex.title,
                font=("Segoe UI", 12),
                anchor="w",
                fg_color="transparent",
                text_color=("#0f172a", "#f1f5f9"),
                hover_color=("#cbd5e1", "#2b2b2b"),
                height=30,
                command=lambda e=ex, i=idx: self._prikazi_primjer(e, i)
            )
            btn.pack(fill="x", pady=2, padx=2)
            self.buttons.append(btn)

        # Početno prikaži prvi primjer
        self._prikazi_primjer(self.modul.examples[0], 0)

    def _prikazi_primjer(self, primjer: Example, index: int):
        """Prikazuje detalje odabranog primjera u desnom panelu."""
        # Oznaci aktivni gumb u sidebar-u
        for idx, btn in enumerate(self.buttons):
            if idx == index:
                btn.configure(fg_color=("#0284c7", "#0ea5e9"), text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=("#0f172a", "#f1f5f9"))

        # Postavljanje podataka
        self.trenutni_primjer = primjer
        self.ex_title_lbl.configure(text=f"{primjer.title} ({primjer.level.capitalize()})")
        
        # Postavljanje opisa primjera (ako postoji opis ili koristimo parametre)
        desc_parts = []
        if primjer.description:
            desc_parts.append(primjer.description)
        if primjer.parameters:
            desc_parts.append(f"Parametri: {primjer.parameters}")
        
        self.ex_desc_lbl.configure(text="\n".join(desc_parts))

        # Kod
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", primjer.code)
        self.code_text.configure(state="disabled")

        # Output
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        if primjer.output:
            self.output_text.insert("1.0", primjer.output)
            self.output_frame.grid() # Prikaži output frame
        else:
            self.output_frame.grid_remove() # Sakrij output frame ako ga nema
        self.output_text.configure(state="disabled")

    def _kopiraj_kod(self):
        """Kopira kod trenutnog primjera u međuspremnik."""
        if hasattr(self, 'trenutni_primjer'):
            pyperclip.copy(self.trenutni_primjer.code)
            self.btn_copy_code.configure(text="✔ Kopirano!", text_color="#10b981")
            self.after(1500, lambda: self.btn_copy_code.configure(text="📋 Kopiraj kod", text_color=("#0f172a", "#38bdf8")))
Class_Name = "DetailWindow"
