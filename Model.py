import Entry


class Model:
    # Stores information about individual model #

    entry_count = 0
    model_names_list = []
    entries_list = []
    model_atom_names = []

    def __init__(self, model):
        self.model_names_list.append(model["ModelName"])

        self.model_atom_names = model["ModelNames"]
        self.model_atom_names = {int(k): v for k, v in self.model_atom_names.items()}

        for entry in model["Entries"]:
            self.entries_list.append(entry)
            self.entry_count += 1
            Entry.Entry(entry)
