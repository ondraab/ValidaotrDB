class Entry:
    # Stores information about individual entry #

    main_res = []
    foreign_atoms = []
    missing_atoms = []
    chirality_mismatches = []
    substitutions = []
    name_mismatches = []
    state = False

    def __init__(self, model_entry):
        self.state = not model_entry["State"] == "Degenerate"
        try:
            self.main_res = (model_entry["MainResidue"].split(" ", 3))
        except AttributeError:
            self.state = False
        self.substitutions = model_entry["Substitutions"]
        self.chirality_mismatches = model_entry["ChiralityMismatches"]
        self.foreign_atoms = model_entry["ForeignAtoms"]
        self.name_mismatches = model_entry["NameMismatches"]
