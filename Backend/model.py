from typing import List, Optional, Dict, Any

class Example:
    """
    Predstavlja jedan primjer koda za Python modul.
    """
    def __init__(self, level: str, title: str, description: str, 
                 parameters: Optional[str], code: str, output: str):
        self.level = level
        self.title = title
        self.description = description
        self.parameters = parameters
        self.code = code
        self.output = output

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Example':
        return cls(
            level=data.get("level", "osnovno"),
            title=data.get("title", "Primjer"),
            description=data.get("description", ""),
            parameters=data.get("parameters"),
            code=data.get("code", ""),
            output=data.get("output", "")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "title": self.title,
            "description": self.description,
            "parameters": self.parameters,
            "code": self.code,
            "output": self.output
        }


class PythonModule:
    """
    Predstavlja Python modul sa svim pripadajućim metapodacima i primjerima.
    """
    def __init__(self, name: str, category: str, levels: List[str], 
                 builtin: bool, pip_install: Optional[str], import_stmt: str, 
                 description: str, docs: str, examples: List[Example]):
        self.name = name
        self.category = category
        self.levels = levels  # npr. ["osnovno", "srednje"]
        self.builtin = builtin
        self.pip_install = pip_install
        self.import_stmt = import_stmt
        self.description = description
        self.docs = docs
        self.examples = examples

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PythonModule':
        examples_data = data.get("example", [])
        examples = [Example.from_dict(ex) for ex in examples_data]
        
        # Prilagodba instalacijskog teksta
        pip_inst = data.get("pip_install")
        if not pip_inst and not data.get("builtin"):
            pip_inst = f"pip install {data.get('name')}"

        return cls(
            name=data.get("name", "Nepoznat"),
            category=data.get("category", "Ostalo"),
            levels=data.get("level", ["osnovno"]),
            builtin=data.get("builtin", False),
            pip_install=pip_inst,
            import_stmt=data.get("import", f"import {data.get('name')}"),
            description=data.get("description", ""),
            docs=data.get("docs", "https://docs.python.org/3/"),
            examples=examples
        )

    def dohvati_install_tekst(self) -> str:
        """Vraća tekst za instalaciju ovisno o tome je li modul ugrađen."""
        if self.builtin:
            return "Ugrađen u Python (Built-in)"
        return self.pip_install or f"pip install {self.name}"
