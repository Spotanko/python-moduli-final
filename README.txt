# Preglednik Python Modula (Katalog Modula)

Preglednik Python Modula je moderna desktop aplikacija razvijena u **Pythonu** koristeći **CustomTkinter** biblioteku. Aplikacija služi kao interaktivni katalog i edukacijski alat za pretraživanje i učenje o najpopularnijim Python modulima (kako ugrađenima u sam Python, tako i vanjskim paketima).

Ovaj projekt je dizajniran i strukturiran kao praktični dio završnog rada, s naglaskom na modularnost koda, čisto grafičko sučelje (GUI)

---

## 🌟 Ključne Funkcionalnosti

* **Moderan GUI (Rich Aesthetics)**: Prilagodljiv izgled s podrškom za tamnu i svijetlu temu (Dark/Light mode).
* **Pretraga u realnom vremenu**: Pretraživanje modula po nazivu, opisu ili import naredbi dok tipkate.
* **Napredno filtriranje**:
  * Po kategorijama (npr. Matematika, Tekst, Baze podataka, GUI, itd.) uz prikaz broja modula.
  * Po razinama težine (Osnovno, Srednje, Napredno).
  * Prekidač za prikaz samo ugrađenih (*built-in*) modula.
* **Responzivan Grid (Grid Adaptability)**: Broj kolona kartica automatski se prilagođava širini prozora prilikom promjene veličine (responsive design).
* **Interaktivne kartice modula**: 
  * Glatke hover animacije (isticanje kartice pri prelasku mišem).
  * Brza kopija `import` naredbe u međuspremnik (clipboard) s vizualnom potvrdom.
* **Detaljan popup prozor s tabovima**:
  * Prikaz cjelovitog opisa modula koji se može selektirati i kopirati.
  * Gumb za direktno otvaranje službene Python dokumentacije u pregledniku.
  * **Interaktivni preglednik primjera**: Lijevi izbornik s popisom primjera za odabrani modul, desni dio s prikazom koda u monospace fontu (Consolas), gumbom za kopiranje koda i prikazom očekivanog izlaza (*Output*).

---

## 📁 Struktura Projekta (MVC pristup)

Projekt je podijeljen na logičke cjeline kako bi se osigurala lakša nadogradnja i čistoća koda:

```text
Katalog_Python_Modula/
│
├── app.py                      # Glavna ulazna točka (pokretač aplikacije)
├── requirements.txt            # Popis potrebnih Python paketa
├── README.md                   # Dokumentacija projekta (ovaj dokument)
│
├── Json/
│   └── python_modules_catalog.json   # JSON baza podataka svih modula
│
├── Backend/
│   ├── __init__.py
│   ├── model.py                # Definicije klasa modela (Example, PythonModule)
│   └── catalog.py              # Logika učitavanja, pretraživanja i filtriranja
│
└── Frontend/
    ├── __init__.py
    ├── app_gui.py              # Glavni prozor aplikacije (Layout i upravljanje stanjima)
    └── components/
        ├── __init__.py
        ├── module_card.py      # Widget za pojedinačnu karticu modula (s hover efektom)
        └── detail_window.py    # Modalni popup prozor s detaljima i primjerima
```

---

## 🛠️ Tehnologije i Biblioteke

* **Python 3.8+** - programski jezik
* **CustomTkinter** - moderna nadogradnja na standardnu Tkinter biblioteku za moderan izgled widgeta
* **Pyperclip** - biblioteka za upravljanje međuspremnikom (clipboard) za jednostavno kopiranje koda i naredbi

---

## 🚀 Instalacija i Pokretanje

Kako biste pokrenuli aplikaciju na svom računalu, slijedite ove korake:

### 1. Kloniranje ili preuzimanje projekta
Preuzmite projekt s GitHuba ili ga klonirajte naredbom:
```bash
git clone https://github.com/korisnicko-ime/Katalog_Python_Modula.git
cd Katalog_Python_Modula
```

### 2. Kreiranje i aktivacija virtualnog okruženja (Preporučeno)
U mapi projekta kreirajte virtualno okruženje kako ne biste utjecali na globalne pakete sustava:

* **Windows**:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Instalacija zavisnosti
Instalirajte potrebne pakete pomoću `pip`-a:
```bash
pip install -r requirements.txt
```

### 4. Pokretanje aplikacije
Pokrenite glavnu skriptu:
```bash
python app.py
```
