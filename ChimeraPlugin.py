from chimera import runCommand


class ChimeraPlugin():
    def __init__(self):
        runCommand("colordef MissingAtoms #dd191d")
        runCommand("colordef ChiralityMismatches #BDA429")
        runCommand("colordef ForeignAtoms #607d8b")
        runCommand("colordef Substitutions #607d8b")
        runCommand("colordef NameMismatches #78909c")

    @staticmethod
    def set_representation(property_color, model_number, res_id, chain, issue):
        """
        Focus on given residue. Color fault atoms.
        :param property_color:
        :param model_number:
        :param res_id:
        :param chain:
        :param issue:
        :param i:
        :return:
        """
        model_number = str(model_number)
        res_id = str(res_id)
        chain = str(chain)

        if property_color == "MissingAtoms":
            runCommand(str("color " + property_color + " #" + model_number + ":" + res_id + "." + chain))

        for j in range(len(issue[property_color])):
            atom = str(issue[property_color][j])
            runCommand(str("represent bs " + "#" + model_number + ":" + res_id + "." + chain + "@" + atom))
            runCommand(str("color " + property_color + " #" + model_number + ":" + res_id + "." + chain + "@" + atom))
            runCommand(str("label " + "#" + model_number + ":" + res_id + "." + chain + "@" + atom))
        runCommand(str("show #" + model_number + ":" + res_id + "." + chain))
        runCommand(str("~ribbon :#" + model_number))
        runCommand(str("focus #" + model_number + ":" + res_id + "." + chain))

    def show_res(self, pdb_id, res_id, chain, downloaded, model_number, issue=None):
        """
        Download molecule, color grey, calls set representation method
        :param pdb_id:
        :param res_id:
        :param chain:
        :param downloaded:
        :param model_number:
        :param issue:
        :return:
        """
        if not downloaded:
            runCommand(str("open cifID:" + pdb_id))
        runCommand(str("color dim gray"))

        if issue is not None:

            map(lambda x: self.set_representation(x, model_number, res_id, chain, issue), issue.keys())

