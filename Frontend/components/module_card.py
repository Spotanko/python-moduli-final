import customtkinter as ctk
import pyperclip
from typing import Callable
from Backend.model import PythonModule

class ModuleCard(ctk.CTkFrame):
    """
    UI komponenta za prikaz pojedinog Python modula u obliku kartice.
    Sadrži hover animacije, kopiranje import naredbe i gumb za otvaranje detalja.
    """
    def __init__(self, master, modul: PythonModule, detalji_callback: Callable[[PythonModule], None], **kwargs):
        # Postavljanje standardnih boja kartice za tamnu i svijetlu temu
        self.normal_color = ("#e2e8f0", "#2b2b2b")  # Svijetlo siva / Tamno siva
        self.hover_color = ("#cbd5e1", "#373737")   # Lighter siva / Svjetlija tamna
        
        super().__init__(master, fg_color=self.normal_color, corner_radius=12, **kwargs)
        
        self.modul = modul
        self.detalji_callback = detalji_callback

        # Raspored unutar kartice
        self.grid_columnconfigure(0, weight=1)
        
        # 1. Gornji red: Naziv modula i oznaka Builtin/Pip
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 2))
        header_frame.columnconfigure(0, weight=1)

        # Naziv modula
        self.label_name = ctk.CTkLabel(
            header_frame, 
            text=self.modul.name, 
            font=("Segoe UI", 18, "bold"),
            anchor="w"
        )
        self.label_name.grid(row=0, column=0, sticky="w")

        # Oznaka (Built-in / External)
        if self.modul.builtin:
            badge_text = "Ugrađen"
            badge_fg = "#0f172a"
            badge_bg = "#10b981" # Zelena za ugrađene
        else:
            badge_text = "Vanjski"
            badge_fg = "#ffffff"
            badge_bg = "#f59e0b" # Narančasta za vanjske
            
        self.badge = ctk.CTkLabel(
            header_frame,
            text=badge_text,
            font=("Segoe UI", 10, "bold"),
            text_color=badge_fg,
            fg_color=badge_bg,
            corner_radius=6,
            height=18,
            width=55
        )
        self.badge.grid(row=0, column=1, sticky="e", padx=(5, 0))

        # 2. Kategorija
        self.label_category = ctk.CTkLabel(
            self,
            text=self.modul.category.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=("#1e3a8a", "#0ea5e9"), # Tamno plava / Svijetlo plava
            anchor="w"
        )
        self.label_category.pack(fill="x", padx=15, pady=(0, 6))

        # 3. Kratak opis
        opis_skraceni = self._skrati_tekst(self.modul.description, 110)
        self.label_desc = ctk.CTkLabel(
            self,
            text=opis_skraceni,
            font=("Segoe UI", 13),
            text_color=("#475569", "#cbd5e1"),
            justify="left",
            anchor="nw",
            wraplength=200,
            height=60
        )
        self.label_desc.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # 4. Import linija i brzi gumb za kopiranje
        import_frame = ctk.CTkFrame(self, fg_color=("#cbd5e1", "#1e1e1e"), corner_radius=6, height=32)
        import_frame.pack(fill="x", padx=15, pady=(0, 12))
        import_frame.grid_propagate(False)
        import_frame.columnconfigure(0, weight=1)
        import_frame.rowconfigure(0, weight=1)

        self.label_import = ctk.CTkLabel(
            import_frame,
            text=self.modul.import_stmt,
            font=("Consolas", 11),
            text_color=("#0f172a", "#38bdf8"), # Tamna / Svijetlo plava
            anchor="w"
        )
        self.label_import.grid(row=0, column=0, sticky="ew", padx=(10, 5))

        self.btn_copy = ctk.CTkButton(
            import_frame,
            text="📋",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=("#94a3b8", "#334155"),
            text_color=("#000000", "#ffffff"),
            command=self._kopiraj_import
        )
        self.btn_copy.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # 5. Gumb za otvaranje detalja
        self.btn_details = ctk.CTkButton(
            self,
            text="Prikaži detalje →",
            font=("Segoe UI", 13, "bold"),
            fg_color=("#0284c7", "#0369a1"),
            hover_color=("#0369a1", "#0284c7"),
            text_color="#ffffff",
            corner_radius=8,
            height=32,
            command=lambda: self.detalji_callback(self.modul)
        )
        self.btn_details.pack(fill="x", padx=15, pady=(0, 15))

        # Povezivanje hover efekata
        self._vezi_hover_rekurzivno(self)

    def _skrati_tekst(self, tekst: str, limit: int = 110) -> str:
        """Skraćuje tekst na određeni broj znakova i dodaje tri točkice."""
        if not tekst:
            return ""
        if len(tekst) <= limit:
            return tekst
        return tekst[:limit].strip() + "..."

    def _kopiraj_import(self):
        """Kopira import naredbu u međuspremnik i daje povratnu informaciju."""
        pyperclip.copy(self.modul.import_stmt)
        staro_tekst = self.btn_copy.cget("text")
        self.btn_copy.configure(text="✔", text_color="#10b981")
        # Vraćanje gumba na staro nakon 1.5 sekundi
        self.after(1500, lambda: self.btn_copy.configure(text="📋", text_color=("#000000", "#ffffff")))

    def _on_enter(self, event):
        """Aktivira se kada miš uđe u područje kartice."""
        self.configure(fg_color=self.hover_color)

    def _on_leave(self, event):
        """Aktivira se kada miš napusti područje kartice."""
        # Provjera nalazi li se pokazivač miša i dalje unutar okvira kartice
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget is not None:
            # Idemo uz stablo widgeta da vidimo je li trenutni widget dio ove kartice
            parent = widget
            while parent:
                if parent == self:
                    return
                parent = parent.master
        self.configure(fg_color=self.normal_color)

    def _vezi_hover_rekurzivno(self, widget):
        """Rekurzivno povezuje događe ulaza i izlaza miša na sve pod-widgete."""
        # Ne želimo povezati hover na gumbe i interaktivne elemente jer oni imaju svoj hover
        if widget not in [self.btn_details, self.btn_copy]:
            widget.bind("<Enter>", self._on_enter, add="+")
            widget.bind("<Leave>", self._on_leave, add="+")
        
        # Poveži za svu djecu widgeta
        for child in widget.winfo_children():
            self._vezi_hover_rekurzivno(child)
        
        # Posebna iznimka: klik na samu karticu (bilo gdje osim gumba) može također otvoriti detalje
        if widget not in [self.btn_details, self.btn_copy]:
            widget.bind("<Button-1>", lambda e: self.detalji_callback(self.modul))
