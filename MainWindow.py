import Tkinter as Tk
import ttk
import tkMessageBox
import ValidatorManager
import threading
import os
from Pmw import Balloon as Balloon

try:
    from PymolPlugin import PymolPlug as plugin
    PLUGIN = "pymol"

except:
    import chimera
    from ChimeraPlugin import ChimeraPlugin as plugin
    PLUGIN = "chimera"


class MainWindow:
    # Tkinter Window class #
    name = "ValidatorDB"

    def __init__(self):
        # Mainwindow #
        self.plugin_type = PLUGIN
        self.master = Tk.Tk()
        self.master.wm_title("ValidatorDB")
        self.master.resizable(width=False, height=False)

        if self.plugin_type == "pymol":
            self.master.geometry("648x480")

        else:
            self.master.geometry("770x492")
        self.frame = Tk.Frame(self.master, borderwidth=0)
        balloon = Balloon(self.master)

        # Table of models #
        self.model_table = ttk.Treeview(self.master, height=10)
        self.model_table.grid(row=0, column=0, sticky="nw", padx=[3, 0], pady=5, rowspan=2, columnspan=3)
        self.model_table.heading('#0', text="PDBid")
        self.model_table.bind("<<TreeviewSelect>>", self.on_select_model_table)
        self.model_table.bind("<Delete>", lambda event, table=self.model_table: self.delete_option(table))
        #self.model_table.bind("<Enter>", lambda message='model_table': self.display(message))
        #self.model_table.bind("<Leave>", self.remove)
        self.model_table.column('#0', width=77, stretch=Tk.NO, minwidth=80)
        balloon.bind(self.model_table, "Table of PDB entries and it's models. ")

        # Table of entries #
        self.entries_table_columns = ["Entry", "Missing Atoms", "Substitutions", "Chirality Mismatches",
                                      "Name Mismatches", "Foreign Atoms"]
        self.entries_table = ttk.Treeview(self.master, height=10,
                                          columns=self.entries_table_columns)
        self.entries_table.grid(row=0, column=3, sticky="NW", padx=[3, 0], pady=[5, 0], columnspan=10)
        self.entries_table['show'] = 'headings'

        self.entries_table.heading('#1', text=self.entries_table_columns[0])
        self.entries_table.heading('#2', text=self.entries_table_columns[1])
        self.entries_table.heading('#3', text=self.entries_table_columns[2])
        self.entries_table.heading('#4', text=self.entries_table_columns[3])
        self.entries_table.heading('#5', text=self.entries_table_columns[4])
        self.entries_table.heading('#6', text=self.entries_table_columns[5])


        if self.plugin_type == "pymol":
            self.entries_table.column('#1', width=49, anchor=Tk.W)
            self.entries_table.column('#2', width=87, anchor="center")
            self.entries_table.column('#3', width=77, anchor="center")
            self.entries_table.column('#4', width=119, anchor="center")
            self.entries_table.column('#5', width=109, anchor="center")
            self.entries_table.column('#6', width=89, anchor="center")

        else:
            self.entries_table.column('#1', width=60, anchor=Tk.W)
            self.entries_table.column('#2', width=110, anchor="center")
            self.entries_table.column('#3', width=96, anchor="center")
            self.entries_table.column('#4', width=145, anchor="center")
            self.entries_table.column('#5', width=132, anchor="center")
            self.entries_table.column('#6', width=105, anchor="center")

        self.entries_table.bind("<<TreeviewSelect>>", self.on_select_entries_table)
        self.entries_table.bind("<Delete>", lambda event, table=self.entries_table: self.delete_option(table))
        self.entries_table.bind("<Double-1>", self.call_plugin)
        balloon.bind(self.entries_table, "Table showing entreies of selected model from left table. Double click the"
                                         "entry to visualize main residue of selected entry")

        # Enntries table scrollbar #
        self.entries_scrollbar = ttk.Scrollbar(self.master, orient=Tk.VERTICAL, command=self.entries_table.yview)
        self.entries_table['yscroll'] = self.entries_scrollbar.set
        self.entries_scrollbar.grid(row=0, column=14, sticky=Tk.NSEW, padx=[2, 0], pady=0)
        self.entries_table.bind("<<TreeviewSelect>>", self.on_select_entries_table)

        # Notebook, used for tabs #
        self.notebook = ttk.Notebook(self.master, width=350, height=180)
        self.notebook.grid(row=1, column=0, sticky="NW", columnspan=6, pady=[5, 5], padx=5)
        balloon.bind(self.notebook, "Detail information about selected  entry")

        # Tabs, each tab has one table #
        self.tab_names = ['Entries', 'Missing', 'Substitutions', 'Name Mismatches', 'Chirality Mismatches',
                          'Foreign Atoms']

        self.missing_table = self.tab_maker(self.tab_names[1], ["Atoms"])
        self.substitution_table = self.tab_maker(self.tab_names[2], ["Model", "Motif"])
        self.name_mismatches_table = self.tab_maker(self.tab_names[3], ["Model", "Motif"])
        self.chirality_mismatches_table = self.tab_maker(self.tab_names[4], ["Model", "Motif"])
        self.foreign_atoms_table = self.tab_maker(self.tab_names[5], ["Model", "Motif"])
        self.hide_tabs()

        # Help Tab #
        if self.plugin_type == "pymol":
            self.help_notebook = ttk.Notebook(self.master, width=250, height=180)

        else:
            self.help_notebook = ttk.Notebook(self.master, width=350, height=180)
        self.help_notebook.grid(row=1, column=6, columnspan=10, pady=5, padx=5)

        self.help_tab = Tk.Frame(self.master)
        self.help_notebook.add(self.help_tab, text="About")
        self.help_text = Tk.Label(self.help_tab, relief='sunken', anchor=Tk.NW, justify=Tk.LEFT, bg='#52A300', fg='white',
                                  font=("Helvetica", 13), padx=10, pady=10, text="(c) 2017 CEITEC & NCBR "
                                                                                 "MU\nValidatorDB\nhttp://ncbr.muni"
                                                                                 ".cz/ValidatorDB\n"
                                                                                 "plugin by Ondrej Balcarek 2017\n"
                                                                                 "ondra.balcarek@gmail.com\n\n\n"
                                                                                 "                            v    17.05.8")

        self.help_text.config(width=38, height=9)
        self.help_text.grid(row=0, column=0)

        # Entry label #
        self.entry_label = Tk.Label(self.master, text="PDBid", anchor=Tk.W)
        self.entry_label.grid(row=2, column=0, sticky=Tk.NW, padx=(5, 0), pady=5)

        # String length control #
        self.input_text = Tk.StringVar()
        # self.input_text.trace("w", lambda name, index, mode, sv=self.input_text: self.validatecommand(sv))
        self.input_text.trace("w", lambda name, index, mode, sv=self.input_text: self.str_length())

        # Entry widget #
        self.entry = Tk.Entry(self.master, width=23, textvariable=self.input_text)
        self.entry.grid(row=2, column=1, sticky=Tk.NE, padx=(0, 5), columnspan=3, pady=5)
        self.entry.bind("<Return>", lambda event, pdb_id=self.entry.get().lower(): self.start_button_click())
        balloon.bind(self.entry, 'Write PDB structure to validate here')

        # Start button #
        self.start_button = Tk.Button(self.master, text="Validate!", command=lambda: self.start_button_click(),
                                      height=1)
        self.start_button.grid(row=2, column=4, sticky=Tk.NW, padx=0, columnspan=2, pady=3)

        # Download label #
        self.downloaded_label = Tk.Label(self.master, text="")
        self.downloaded_label.grid(row=2, column=6)
        self.downloaded_in_chimera = []     # Used for molecule identification in chimera #
        self.report = ValidatorManager.ValidatorManager()
        self.master.mainloop()

    def validate_command(self, input_text):
        """
        Prepared for input validation, did not work in PyMOL.
        :param input_text: entry widget input
        :return:
        """
        if len(input_text.get()) != 4:
            self.start_button.config(state='disabled')

        else:
            print len(self.input_text.get())
            self.start_button.config(state='active')

    def str_length(self):
        """
        Control length of given string.
        :return: True, if it has right length
        """
        string = self.input_text.get()[0:4]
        self.input_text.set(string)
        return True

    def add_option(self, pdb_id):
        """
        Method, makes a PDBid option in model_table + makes it's children (Models)
        :param pdb_id: given PDBid
        :return:
        """
        try:
            self.model_table.insert("", 1, pdb_id.lower(), text=pdb_id.lower())
            for i in self.report.protein_model_list:
                self.model_table.insert(pdb_id, 1, text=i["ModelName"])
            self.downloaded_label.config(text="")

        except Tk.TclError:
            self.downloaded_label.config(text="PDB allready downloaded.")
            self.model_table.selection_set(pdb_id)
            return

    def tab_maker(self, tab, column_names):
        """
        Method, makes tabs with given name
        :param tab: name of tab
        :param column_names: name of columns for table
        :return:
        """

        self.tab = Tk.Frame(self.master)

        self.tree = ttk.Treeview(self.tab, columns=column_names, height=8)

        self.tree['show'] = 'headings'
        for i in range(len(column_names)):
            self.tree.heading(i, text=column_names[i])
            self.tree.column(i, stretch=Tk.NO, width=350 / (len(column_names)))

        self.tree.column('#0', width=610 / (len(column_names)))

        self.tree.grid(row=0, columnspan=4, sticky="nsew", padx=2, pady=2)
        self.treeview = self.tree

        self.notebook.add(self.tab, text=tab)
        return self.treeview

    def on_select_model_table(self, event):
        """
        Method, called when is clicked on left table. Fills Entries table.
        :param event:
        :return:
        """
        clicked_item = self.model_table.focus()
        if self.model_table.parent(clicked_item) == '':
            return

        counter = 0
        degenerate = False

        pdb_id = self.model_table.parent(clicked_item)
        model_name = self.model_table.item(clicked_item, "text")
        self.entries_table.delete(*self.entries_table.get_children())

        while model_name not in self.report.find_report(pdb_id, counter, "ModelName"):
            counter += 1

        if model_name in self.report.find_report(pdb_id, counter, "ModelName"):
            current_model = self.report.find_report(pdb_id, counter, "Entries")

            for entry, properties in enumerate(current_model):

                if current_model[entry]["MissingAtomCount"] != 0:
                    self.entries_table.insert('', 1, text=current_model[entry]["MainResidue"],
                                              values=(self.entries_table_fill(current_model, entry)),
                                              tags=('missing'))

                    self.entries_table.tag_configure('missing', background='red')

                elif current_model[entry]["ChiralityMismatchCount"] != 0:
                    self.entries_table.insert('', 1, text=current_model[entry]["MainResidue"],
                                              values=(self.entries_table_fill(current_model, entry)),
                                              tags=('chiralitymismatch'))

                    self.entries_table.tag_configure('chiralitymismatch', background='#BDA429')

                elif current_model[entry]["MissingAtomCount"] == 0 \
                        and current_model[entry]["SubstitutionCount"] == 0 \
                        and current_model[entry]["ChiralityMismatchCount"] == 0 \
                        and current_model[entry]["NameMismatchCount"] == 0 \
                        and current_model[entry]["ForeignAtomCount"] == 0\
                        and current_model[entry]["State"] != "Degenerate":

                    self.entries_table.insert('', 1, text=current_model[entry]["MainResidue"],
                                              values=(self.entries_table_fill(current_model, entry)),
                                              tags=('ok'))

                    self.entries_table.tag_configure('ok', foreground='green')

                elif current_model[entry]["State"] == "Degenerate":

                    self.entries_table.insert('', 1, text="! Null", values = (self.entries_table_fill(current_model,
                                                                                                      entry)),
                                              tags='degenerate')
                    self.entries_table.tag_configure('degenerate', foreground='red')
                    degenerate = True

                else:
                    self.entries_table.insert('', 1, text=current_model[entry]["MainResidue"],
                                              values=(self.entries_table_fill(current_model, entry)))

        if degenerate is True:
            tkMessageBox.showwarning("Degenerate", "Degenerated entry in selected model!")

    @staticmethod
    def entries_table_fill(current_model, entry):
        """
        Fill the entries table with given model
        :param current_model: clicked model
        :param entry:
        :return:
        """
        try:
            entry_name, res_id, chain = current_model[entry]["MainResidue"].split(" ")
            return (res_id.encode('ascii', 'ignore') + " " + chain.encode('ascii', 'ignore')), \
                   current_model[entry]["MissingAtomCount"],\
                   current_model[entry]["SubstitutionCount"],\
                   current_model[entry]["ChiralityMismatchCount"], \
                   current_model[entry]["NameMismatchCount"], \
                    current_model[entry]["ForeignAtomCount"]

        except AttributeError:
            res_id = "! Null"
            return (res_id), \
                   current_model[entry]["MissingAtomCount"], \
                   current_model[entry]["SubstitutionCount"], \
                   current_model[entry]["ChiralityMismatchCount"], \
                   current_model[entry]["NameMismatchCount"], \
                   current_model[entry]["ForeignAtomCount"]

    def hide_tabs(self):
        """
        Hide all tabs.
        :return:
        """
        self.notebook.hide(0)
        self.notebook.hide(1)
        self.notebook.hide(2)
        self.notebook.hide(3)
        self.notebook.hide(4)

    def on_select_entries_table(self, event):
        """
        Method, is called when is clicked on entries table, fill properties tables.
        :param event:
        :return:
        """
        res_name = self.entries_table.item(self.entries_table.focus(), 'text')
        entry_count = 0
        pdb_id = self.model_table.parent(self.model_table.focus())
        model_name_id = self.model_table.focus()
        model_name = self.model_table.item(model_name_id, 'text')

        property_names = ["Substitutions", "ChiralityMismatches", "NameMismatches", "ForeignAtoms"]
        tab_names = ["Substitutions", "Chirality Mismatches", "Name Mismatches", "Foreign Atoms"]
        list_of_tables = [self.substitution_table, self.chirality_mismatches_table, self.name_mismatches_table,
                          self.foreign_atoms_table]
        values = self.entries_table.item(self.entries_table.focus(), 'values')[2:]

        counter = 0
        index = 0  # used for indexing in interactive table maker

        for i in range(self.notebook.index("end")):
            self.notebook.hide(i)

        while model_name not in self.report.find_report(pdb_id, counter, "ModelName"):
            counter += 1

        try:
            while res_name not in (self.report.find_report(pdb_id, counter, "Entries")[entry_count]
                               ["MainResidue"]):
                entry_count += 1

        except TypeError:
            pass

        # if model_name in ValidatorManager.validation_report[pdb_id]["Models"][counter]["ModelName"]:
        current_entry = self.report.find_report(pdb_id, counter, "Entries")[entry_count]

        # Missing atom tab maker, out of cycle because have just 1 column #

        if current_entry["MissingAtomCount"] != 0:
            self.missing_table = self.tab_maker(self.tab_names[1], ["Atoms"])

            for atom_index in current_entry["MissingAtoms"]:
                self.missing_table.insert('', 1, text=(
                    self.report.find_report(pdb_id, counter, "ModelNames")[str(atom_index)]),
                                          values=(self.report.find_report(pdb_id, counter, "ModelNames")[str(atom_index)]))

        # Interactive tab make cycle #
        for i in values:

            if int(i) != 0:  # If prop_count != --> make tab, table and fill it
                list_of_tables[index] = self.tab_maker(tab_names[index], ["Model", "Motif"])
                self.table_fill(list_of_tables[index], property_names[index])
                index += 1

            elif int(i) == 0:
                index += 1
                pass

    def delete_option(self, table):
        """
        Delete option from tables
        :param table: table, form which will be option deleted
        :return:
        """
        model_count = 0
        entry_count = 0
        model_name_id = self.model_table.focus()
        model_name = self.model_table.item(model_name_id, 'text')
        res_name = self.entries_table.item(self.entries_table.focus(), 'text')
        pdb_id = self.model_table.parent(self.model_table.focus())

        for i in range(self.notebook.index("end")):
            self.notebook.hide(i)

        if pdb_id == '':

            pdb_id = str(self.model_table.item(model_name_id, 'text'))
            table.delete(table.selection())
            self.report.delete_report(pdb_id)
            self.entries_table.delete(*self.entries_table.get_children())
            return

        try:
            while model_name not in self.report.find_report(pdb_id, model_count, "ModelName"):
                model_count += 1

        except KeyError:
            pass


        if len(self.report.find_report(pdb_id, model_count, "Entries")) == 0:
            return

        while res_name not in self.report.find_report(pdb_id, model_count, "Entries")[entry_count][
            "MainResidue"]:
            entry_count += 1

        selected_item = table.selection()
        table.delete(selected_item)
        self.report.delete_report(pdb_id, model_count, "Entries", entry_count)
        #ValidatorManager.ValidatorManager().find_report(pdb_id, model_count, "Entries").pop(entry_count)

    def table_fill(self, table, property):
        """
        Fill given table with given properties
        :param table: Table, wchich will be filled
        :param property:
        :return:
        """
        table.delete(*table.get_children())
        list_of_index = self.pointer()
        current_entry = list_of_index[0]
        pdb_id = list_of_index[1]
        counter = list_of_index[2]

        for atom_index, motiff in enumerate(current_entry[property]):
            table.insert('', 1, text=self.report.find_report(pdb_id, counter, "ModelNames")
            [str(motiff)], values=(self.report.find_report(pdb_id, counter, "ModelNames")
                                   [str(motiff)], current_entry[property][str(motiff)]))

    def pointer(self):
        """
        Method, goes through json structure and return pointers wanted validation report, pdb_id from model table and model count
        :return:
        """
        counter = 0
        res_name = self.entries_table.item(self.entries_table.focus(), 'text')
        entry_count = 0
        pdb_id = self.model_table.parent(self.model_table.focus())
        model_name_id = self.model_table.focus()
        model_name = self.model_table.item(model_name_id, 'text')


        while model_name not in self.report.find_report(pdb_id, counter, "ModelName"):
            counter += 1

        if self.report.find_report(pdb_id, counter, "Entries")[entry_count]["MainResidue"] == None:
            entry_count +=1

        while res_name not in self.report.find_report(pdb_id, counter, "Entries")[entry_count][
                "MainResidue"]:
                entry_count += 1

        # if model_name in ValidatorManager.validation_report[pdb_id]["Models"][counter]["ModelName"]:

        current_entry = self.report.find_report(pdb_id, counter, "Entries")[entry_count]
        return current_entry, pdb_id, counter

    def call_download(self):
        """
        Method, calls validation from ValidatorManager class
        :return:
        """

        self.downloaded_object = self.report

    def start_button_click(self):
        """
        Start new thread, update mainwindow, block button
        :return:
        """

        if self.entry.get() == "":
            tkMessageBox.showerror("Error", "No molecule to validate! Please write PDB id of molecule,"
                                            "you want to validate to entry area.")
            return

        self.start_button.configure(state='disabled')
        self.downloading_label = Tk.Label(self.master, text="Downloading validation report...")
        self.downloading_label.grid(row=2, column=6)
        self.master.config(cursor="wait")
        self.master.update()
        self.thread = threading.Thread(target=self.call_download)
        self.thread.start()

        self.master.after(10, self.check_completed())
        error = self.downloaded_object.error_check(self.entry.get().lower())

        if not error:
            tkMessageBox.showerror("Error", self.downloaded_object.error)
            return

        elif error and self.downloaded_object.error != "":
            tkMessageBox.showwarning("Warning", self.downloaded_object.error)

        else:
            self.downloaded_object.scan_json(self.entry.get().lower())
            self.add_option(self.entry.get().lower())

        self.entry.delete('0', 'end')
        self.master.update()

    def check_completed(self):
        """
        Checks, if thread is completed.
        :return:
        """
        if self.thread.is_alive():
            self.master.after(50, self.check_completed)

        else:
            self.start_button.configure(state='active')
            self.downloading_label.grid_forget()
            self.master.config(cursor="")

    def return_fault_atoms(self, property, issue_dict):
        """
        Return list of fault atoms
        :param property: name of prorp, for example "MissingAtoms"
        :return: name of atoms
        """
        atom_list = []
        list_of_index = self.pointer()
        current_entry = list_of_index[0]
        pdb_id = list_of_index[1]
        counter = list_of_index[2]

        for atom_index, motiff in enumerate(current_entry[property]):
            atom_list.append(self.report.find_report(pdb_id, counter, "ModelNames")
                             [str(motiff)])

        issue_dict[property] = atom_list
        return atom_list

    def call_plugin(self, event):
        """
        Method gets residues with issues, issues types and damaged atoms and calls pymol plugin
        :param event:
        :return:
        """
        # List of issue types #
        issue_list = ["MissingAtoms", "Substitutions", "ChiralityMismatches", "NameMismatches", "ForeignAtoms"]

        # Empty list for issues #
        issue_dict = {}

        try:
            clicked_item = self.entries_table.item(self.entries_table.focus(), 'values')[0].split(' ')
            res_name = self.entries_table.item(self.entries_table.focus(), 'text')
            if res_name == "! Null":
                tkMessageBox.showwarning("Degenerate", "Degenerated entry")
                return

        except IndexError:
            pass



        # Values from entries table #
        issues = self.entries_table.item(self.entries_table.focus(), 'values')[1:]

        # Get the values into named dict; if issue count > 0, makes key to dict and add value #
        for i, j in enumerate(issues):

            if int(j) != 0:
                issue_dict[issue_list[i]] = j

        # list of index --> 0 index = validation report; 1 index = pdb_id; 2 index = model_counter #
        list_of_index = self.pointer()

        try:
            pdb_id = list_of_index[1]

        except TypeError:
            return

        # Get atom names into dictionary #

        map(lambda x: self.return_fault_atoms(x, issue_dict), issue_dict.keys())


        try:
            model_number = self.downloaded_in_chimera.index(pdb_id)
            downloaded = True
        except:
            self.downloaded_in_chimera.append(pdb_id)
            model_number = len(self.downloaded_in_chimera) - 1
            downloaded = False
        plugin().show_res(pdb_id, str(clicked_item[0]), str(clicked_item[1]), downloaded,model_number,issue_dict)


if PLUGIN == "chimera":
    chimera.dialogs.register(MainWindow.name, MainWindow)
    dir, file = os.path.split(__file__)
    icon = os.path.join(dir, 'Webchem.tiff')
    chimera.tkgui.app.toolbar.add(icon, lambda d=chimera.dialogs.display, n=MainWindow.name: d(n), 'ValidatorDb', None)

if __name__ == '__main__':
    app = MainWindow()
