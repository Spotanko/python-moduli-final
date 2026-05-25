import customtkinter as ctk
from pathlib import Path
from typing import List
from Backend.catalog import ModuleCatalog
from Backend.model import PythonModule
from Frontend.components.module_card import ModuleCard
from Frontend.components.detail_window import DetailWindow

class AppGUI(ctk.CTk):
    """
    Glavni prozor aplikacije Katalog Python Modula.
    Sadrži sidebar za navigaciju po kategorijama, zaglavlje s naprednim filtrima i
    pretragom, responzivni grid s karticama i footer sa statistikom.
    """
    def __init__(self):
        super().__init__()

        # Inicijalizacija baze podataka
        self.catalog = ModuleCatalog()

        # Osnovne postavke glavnog prozora
        self.title("Preglednik Python Modula")
        self.geometry("1024x720")
        self.minsize(950, 650)
        
        # Postavljanje zadane teme na tamnu
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Trenutno stanje filtara
        self.trenutna_kategorija = "Sve"
        self.trenutna_razina = "Sve"
        self.samo_ugradeni = False
        self.pojam_pretrage = ""
        
        # Evidencija stvorenih kartica za lakšu reorganizaciju grida
        self.aktivne_kartice: List[ModuleCard] = []
        self.kartice_cache = {}  # Cache za ponovno korištenje kartica (brže filtriranje)
        self.search_timer_id = None  # Timer ID za debounce pretrage
        self._zadnja_sirina_grida = 0
        
        # Izrada sučelja
        self._kreiraj_layout()
        
        # Početno učitavanje podataka
        self._osvjezi_kategorije()
        self._filtriraj_i_prikazi()

    def _kreiraj_layout(self):
        """Kreira osnovnu mrežnu strukturu i panele."""
        self.grid_columnconfigure(0, weight=0) # Sidebar - fiksna širina
        self.grid_columnconfigure(1, weight=1) # Glavni sadržaj - rastezljiv
        self.grid_rowconfigure(0, weight=1)

        # --- LIJEVI SIDEBAR (IZBORNIK) ---
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.rowconfigure(2, weight=1) # Popis kategorija raste

        # Logotip i naziv aplikacije
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        logo_icon = ctk.CTkLabel(logo_frame, text="🐍", font=("Segoe UI", 36))
        logo_icon.pack(side="left", padx=(0, 10))
        
        logo_text_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_text_frame.pack(side="left")
        
        ctk.CTkLabel(
            logo_text_frame, 
            text="PYTHON", 
            font=("Segoe UI", 20, "bold"),
            text_color=("#1e3a8a", "#38bdf8")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            logo_text_frame, 
            text="Katalog Modula", 
            font=("Segoe UI", 12, "italic"),
            text_color=("#475569", "#94a3b8")
        ).pack(anchor="w")

        # Separator linija
        ctk.CTkFrame(self.sidebar, height=2, fg_color=("#cbd5e1", "#334155")).grid(row=1, column=0, sticky="ew", padx=15, pady=5)

        # Scrollable Frame za gumbe kategorija
        self.sidebar_categories = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent", 
            label_text="KATEGORIJE",
            label_font=("Segoe UI", 11, "bold"),
            label_text_color=("#475569", "#94a3b8")
        )
        self.sidebar_categories.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # Donji dio sidebara - Prekidač za temu
        theme_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        theme_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        
        self.switch_theme = ctk.CTkSwitch(
            theme_frame, 
            text="Svijetla tema", 
            font=("Segoe UI", 12),
            command=self._promijeni_temu
        )
        self.switch_theme.pack(anchor="w")

        # --- DESNI PANEL (GLAVNI SADRŽAJ) ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=(20, 10))
        self.main_content.columnconfigure(0, weight=1)
        self.main_content.rowconfigure(1, weight=1) # Grid kartica raste

        # 1. ZAGLAVLJE (Search i Filtri)
        topbar = ctk.CTkFrame(self.main_content, fg_color="transparent")
        topbar.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        topbar.columnconfigure(0, weight=1) # Search bar se širi

        # Tražilica
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._na_promjenu_pretrage)
        
        self.search_entry = ctk.CTkEntry(
            topbar,
            placeholder_text="Pretraži module po nazivu, opisu ili importu...",
            font=("Segoe UI", 13),
            textvariable=self.search_var,
            height=38,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        # Filter: Težina (OptionMenu)
        self.filter_level = ctk.CTkOptionMenu(
            topbar,
            values=["Sve razine", "Osnovno", "Srednje", "Napredno"],
            font=("Segoe UI", 12),
            height=38,
            width=130,
            fg_color=("#475569", "#2b2b2b"),
            button_color=("#334155", "#1e1e1e"),
            button_hover_color=("#1e293b", "#373737"),
            command=self._promijeni_razinu
        )
        self.filter_level.grid(row=0, column=1, sticky="e", padx=(0, 15))

        # Filter: Ugrađeni (Switch)
        self.filter_builtin = ctk.CTkSwitch(
            topbar,
            text="Samo ugrađeni",
            font=("Segoe UI", 12),
            height=38,
            command=self._promijeni_builtin
        )
        self.filter_builtin.grid(row=0, column=2, sticky="e")

        # 2. GLAVNO PODRUČJE S KARTICAMA (Scrollable Grid)
        self.cards_scrollable = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        self.cards_scrollable.grid(row=1, column=0, sticky="nsew")
        
        # Povezivanje resize događaja za responzivni grid (koristimo add="+" kako ne bismo prebrisali unutarnji scrollregion bind)
        self.cards_scrollable.bind("<Configure>", self._na_resize_grida, add="+")

        # 3. FOOTER (Status Bar)
        self.footer = ctk.CTkFrame(self, height=30, corner_radius=0, fg_color=("#cbd5e1", "#1e1e1e"))
        self.footer.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.footer.grid_propagate(False)

        self.lbl_stats = ctk.CTkLabel(
            self.footer,
            text="",
            font=("Segoe UI", 11),
            text_color=("#475569", "#94a3b8")
        )
        self.lbl_stats.pack(side="left", padx=20, pady=2)

        self.lbl_footer_info = ctk.CTkLabel(
            self.footer,
            text="Preglednik Python Modula",
            font=("Segoe UI", 11, "bold"),
            text_color=("#475569", "#94a3b8")
        )
        self.lbl_footer_info.pack(side="right", padx=20, pady=2)

    def _osvjezi_kategorije(self):
        """Dohvaća kategorije iz baze podataka i generira navigacijske gumbe."""
        # Brisanje starih gumba
        for widget in self.sidebar_categories.winfo_children():
            widget.destroy()

        # Dohvaćanje svih kategorija i ukupnog broja
        kategorije = self.catalog.dohvati_sve_kategorije()
        ukupno_modula = self.catalog.dohvati_statistiku()["ukupno"]

        # Generiranje popisa s opcijom "Sve" na vrhu
        sve_kategorije = [("Sve", ukupno_modula)] + kategorije
        self.category_buttons: List[ctk.CTkButton] = []

        for naziv, broj in sve_kategorije:
            btn_tekst = f"{naziv} ({broj})"
            
            # Stvaranje gumba za kategoriju
            btn = ctk.CTkButton(
                self.sidebar_categories,
                text=btn_tekst,
                font=("Segoe UI", 12),
                anchor="w",
                fg_color="transparent",
                text_color=("#0f172a", "#f1f5f9"),
                hover_color=("#cbd5e1", "#2b2b2b"),
                height=32,
                command=lambda k=naziv: self._promijeni_kategoriju(k)
            )
            btn.pack(fill="x", pady=2, padx=5)
            self.category_buttons.append(btn)

        # Početno označavanje gumba "Sve"
        self._oznaci_aktivnu_kategoriju("Sve")

    def _oznaci_aktivnu_kategoriju(self, kategorija: str):
        """Označava odabranu kategoriju u sidebar-u (daje joj boju, ostali su prozirni)."""
        for btn in self.category_buttons:
            btn_kat = btn.cget("text").split(" (")[0]
            if btn_kat == kategorija:
                # Plavi aktivni gumb
                btn.configure(
                    fg_color=("#0284c7", "#0ea5e9"), 
                    hover_color=("#0369a1", "#0284c7"),
                    text_color="#ffffff"
                )
            else:
                # Obični transparentni gumb
                btn.configure(
                    fg_color="transparent", 
                    hover_color=("#cbd5e1", "#2b2b2b"),
                    text_color=("#0f172a", "#f1f5f9")
                )

    def _promijeni_temu(self):
        """Prebacuje između tamne i svijetle teme."""
        if self.switch_theme.cget("text") == "Svijetla tema":
            ctk.set_appearance_mode("light")
            self.switch_theme.configure(text="Tamna tema")
        else:
            ctk.set_appearance_mode("dark")
            self.switch_theme.configure(text="Svijetla tema")

    def _promijeni_kategoriju(self, kategorija: str):
        """Filtar callback za promjenu kategorije."""
        self.trenutna_kategorija = kategorija
        self._oznaci_aktivnu_kategoriju(kategorija)
        self._filtriraj_i_prikazi()

    def _promijeni_razinu(self, razina: str):
        """Filtar callback za promjenu razine težine."""
        self.trenutna_razina = razina if razina != "Sve razine" else "Sve"
        self._filtriraj_i_prikazi()

    def _promijeni_builtin(self):
        """Filtar callback za ugrađenost modula."""
        self.samo_ugradeni = self.filter_builtin.get()
        self._filtriraj_i_prikazi()

    def _na_promjenu_pretrage(self, *args):
        """Filtar callback za pretragu u realnom vremenu s debounce odgodom."""
        self.pojam_pretrage = self.search_var.get()
        
        # Otkazivanje prethodnog timera za debounce pretrage
        if self.search_timer_id is not None:
            self.after_cancel(self.search_timer_id)
            
        # Pokretanje novog timera s odgodom od 150 ms
        self.search_timer_id = self.after(150, self._filtriraj_i_prikazi)

    def _filtriraj_i_prikazi(self):
        """Filtrira module iz kataloga i stvara/prikazuje kartice u gridu."""
        # 1. Sakrij trenutno aktivne kartice (koristimo grid_forget umjesto destroy radi performansi)
        for kartica in self.aktivne_kartice:
            if isinstance(kartica, ctk.CTkLabel):
                kartica.destroy()  # Uništavamo samo privremene labele ("Nema modula...")
            else:
                kartica.grid_forget()
        self.aktivne_kartice.clear()

        # 2. Dohvaćanje filtriranih modula
        filtrirani = self.catalog.filtriraj(
            kategorija=self.trenutna_kategorija,
            razina=self.trenutna_razina,
            samo_ugradeni=self.samo_ugradeni,
            upit=self.pojam_pretrage
        )

        # 3. Dohvaćanje iz cachea ili stvaranje novih kartica
        if not filtrirani:
            # Prikaz obavijesti ako nema rezultata
            lbl_no_results = ctk.CTkLabel(
                self.cards_scrollable,
                text="Nema modula koji odgovaraju odabranim filtrima.",
                font=("Segoe UI", 16, "italic"),
                text_color=("#475569", "#94a3b8")
            )
            lbl_no_results.grid(row=0, column=0, columnspan=5, pady=40, sticky="ew")
            self.aktivne_kartice.append(lbl_no_results)
        else:
            for modul in filtrirani:
                if modul.name not in self.kartice_cache:
                    kartica = ModuleCard(
                        self.cards_scrollable,
                        modul=modul,
                        detalji_callback=self._otvori_detalje_modula
                    )
                    self.kartice_cache[modul.name] = kartica
                else:
                    kartica = self.kartice_cache[modul.name]
                
                self.aktivne_kartice.append(kartica)

        # 4. Raspoređivanje kartica u grid (responzivno)
        self._reorganiziraj_grid()

        # 5. Ažuriranje statusne trake (footer)
        stat = self.catalog.dohvati_statistiku()
        ukupno_filter = len(filtrirani) if filtrirani else 0
        stat_tekst = f"Ukupno modula u bazi: {stat['ukupno']} (Ugrađenih: {stat['ugradeni']}, Vanjskih: {stat['vanjski']})  |  Prikazano nakon filtriranja: {ukupno_filter}"
        self.lbl_stats.configure(text=stat_tekst)

    def _na_resize_grida(self, event):
        """Događaj koji prati promjenu veličine prozora i prilagođava broj kolona."""
        current_width = event.width
        # Pokrećemo reorganizaciju samo ako se širina promijenila za više od 30 piksela da spriječimo lag
        if abs(current_width - self._zadnja_sirina_grida) > 30:
            self._zadnja_sirina_grida = current_width
            self._reorganiziraj_grid(current_width)

    def _reorganiziraj_grid(self, width: int = None):
        """Raspoređuje kartice u grid na temelju trenutne širine okvira."""
        if not self.aktivne_kartice:
            return

        # Ako je širina nepoznata ili premala (prilikom pokretanja), koristimo winfo_width()
        if width is None:
            width = self.cards_scrollable.winfo_width()
        
        # Početni fallback ako je prozor tek inicijaliziran (winfo_width vraća 1)
        if width <= 10:
            width = 700  # Očekivana prosječna širina desnog panela pri pokretanju

        # Određivanje broja kolona (svaka kartica je široka 270px, a s marginama kolona iznosi 295px)
        # Odbijamo 40px sigurnosnog prostora za scrollbar i desne margine
        sirina_kolone = 295
        dostupna_sirina = width - 40
        broj_kolona = max(1, dostupna_sirina // sirina_kolone)

        # Ograničavamo maksimalan broj kolona radi čitljivosti
        broj_kolona = min(broj_kolona, 4)

        # Konfiguracija kolona da se šire ravnomjerno i budu savršeno simetrične (uniform)
        for i in range(10):  # Resetiramo stare stupce
            self.cards_scrollable.grid_columnconfigure(i, weight=0, uniform="")
            
        for i in range(broj_kolona):
            self.cards_scrollable.grid_columnconfigure(i, weight=1, uniform="stupac")

        # Raspoređivanje kartica
        for idx, kartica in enumerate(self.aktivne_kartice):
            # Ako je kartica labela za "nema rezultata", stavljamo je preko svih kolona
            if isinstance(kartica, ctk.CTkLabel):
                kartica.grid(row=0, column=0, columnspan=broj_kolona, pady=50, sticky="ew")
                return

            red = idx // broj_kolona
            stupac = idx % broj_kolona
            kartica.grid(row=red, column=stupac, padx=10, pady=10, sticky="nsew")

    def _otvori_detalje_modula(self, modul: PythonModule):
        """Otvara modalni prozor s detaljnim prikazom za odabrani modul."""
        # Provjera postoji li već otvoren prozor, ako da zatvaramo ga
        if hasattr(self, "detail_window") and self.detail_window.winfo_exists():
            self.detail_window.destroy()
            
        self.detail_window = DetailWindow(self, modul=modul)
