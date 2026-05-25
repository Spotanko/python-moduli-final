import sys
from pathlib import Path

# Dodavanje korijenskog direktorija u sys.path kako bi uvozi radili bez obzira na radni direktorij pokretanja
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from Frontend.app_gui import AppGUI

def main():
    """Glavna pokretačka funkcija aplikacije."""
    try:
        app = AppGUI()
        app.mainloop()
    except Exception as e:
        print(f"Došlo je do kritične pogreške prilikom pokretanja aplikacije: {e}")
        import traceback
        traceback.print_exc()
        input("\nPritisnite Enter za izlaz...")

if __name__ == "__main__":
    main()
