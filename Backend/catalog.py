import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from .model import PythonModule

class ModuleCatalog:
    """
    Upravlja učitavanjem, pretraživanjem i filtriranjem kataloga Python modula.
    """
    def __init__(self, json_path: Path = None):
        if json_path is None:
            # Automatsko određivanje relativne putanje u odnosu na ovu datoteku
            # catalog.py je u Katalog_Python_Modula/Backend/
            # JSON je u Katalog_Python_Modula/Json/
            base_dir = Path(__file__).resolve().parent.parent
            json_path = base_dir / "Json" / "python_modules_catalog.json"

        self.json_path = json_path
        self.modules: List[PythonModule] = []
        self._ucitaj_iz_datoteke()

    def _ucitaj_iz_datoteke(self):
        """Učitava JSON podatke i pretvara ih u objekte klase PythonModule."""
        if not self.json_path.exists():
            raise FileNotFoundError(f"JSON datoteka nije pronađena na putanji: {self.json_path}")
        
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.modules = [PythonModule.from_dict(item) for item in data]
        except json.JSONDecodeError as e:
            print(f"Greška prilikom čitanja JSON datoteke: {e}")
            self.modules = []

    def dohvati_sve_kategorije(self) -> List[Tuple[str, int]]:
        """
        Vraća sortiranu listu svih kategorija i broj modula u svakoj od njih.
        Format: [("Naziv Kategorije", broj_modula), ...]
        """
        brojac: Dict[str, int] = {}
        for modul in self.modules:
            cat = modul.category
            brojac[cat] = brojac.get(cat, 0) + 1
        
        sortirane = sorted(brojac.items())
        return sortirane

    def filtriraj(self, 
                  kategorija: str = "Sve", 
                  razina: str = "Sve", 
                  samo_ugradeni: bool = False, 
                  upit: str = "") -> List[PythonModule]:
        """
        Filtrira i pretražuje module na temelju parametara.
        """
        filtrirani = self.modules

        # 1. Filtriranje po kategoriji
        if kategorija != "Sve":
            filtrirani = [m for m in filtrirani if m.category == kategorija]

        # 2. Filtriranje po razini težine
        if razina != "Sve":
            razina_lower = razina.lower()
            filtrirani = [m for m in filtrirani if razina_lower in [lvl.lower() for lvl in m.levels]]

        # 3. Filtriranje po ugrađenosti (Built-in)
        if samo_ugradeni:
            filtrirani = [m for m in filtrirani if m.builtin]

        # 4. Pretraživanje po tekstualnom upitu (ime, opis, import, kategorija)
        if upit:
            upit_lower = upit.lower().strip()
            filtrirani = [
                m for m in filtrirani 
                if upit_lower in m.name.lower() or 
                   upit_lower in m.description.lower() or 
                   upit_lower in m.import_stmt.lower() or
                   upit_lower in m.category.lower()
            ]

        # Sortiranje po imenu modula abecedno
        return sorted(filtrirani, key=lambda m: m.name)

    def dohvati_statistiku(self) -> Dict[str, int]:
        """Vraća osnovne statističke podatke o katalogu."""
        ukupno = len(self.modules)
        ugradeni = sum(1 for m in self.modules if m.builtin)
        vanjski = ukupno - ugradeni
        kategorije_broj = len(set(m.category for m in self.modules))
        
        return {
            "ukupno": ukupno,
            "ugradeni": ugradeni,
            "vanjski": vanjski,
            "kategorije": kategorije_broj
        }
