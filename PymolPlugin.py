from pymol import cmd


class PymolPlug:
    def __init__(self):
        cmd.set_color("MissingAtoms", [221, 25, 29])
        cmd.set_color("ChiralityMismatches", [189, 164, 41])
        cmd.set_color("ForeignAtoms", [96, 125, 139])
        cmd.set_color("Substitutions", [96, 125, 139])
        cmd.set_color("NameMismatches", [120, 144, 156])
        cmd.show("sticks")
        cmd.color("gray")
        cmd.do("set ignore_case, off")

    @staticmethod
    def set_representation(property_color, pdb_id, res_id, chain, issue):
        """
        Focus on given residue. Color fault atoms.
        :param property_color:
        :param pdb_id:
        :param res_id:
        :param chain:
        :param issue:
        :param i:
        :return:
        """
        if property_color == "MissingAtoms":
            rsd = str(pdb_id + " and resi " + res_id + " and chain " + chain)
            cmd.color(property_color, rsd)

        for j in range(len(issue[property_color])):
            atom_id = str(pdb_id + " and resi " + res_id + " and chain " + chain + " and name " +
                          str(issue[property_color][j]))
            cmd.show("spheres", atom_id)
            print atom_id
            cmd.color(property_color, atom_id)
            cmd.label(selection=atom_id, expression="'" + issue[property_color][j] + "'")
            cmd.set("sphere_scale", 0.25, selection=atom_id)
            cmd.deselect()

    def show_res(self, pdb_id, res_id, chain, model_number=None, downloaded=None, issue=None):
        """
        Fetch molecule, show residue, color residue, orient residue, show issues
        :param downloaded: help argument
        :param model_number: help argument - for chimera plugin, same number of plugins
        :param pdb_id:
        :param res_id:
        :param chain:
        :param issue: dict of issues
        :return:
        """
        if pdb_id.lower() not in cmd.get_object_list():
            cmd.fetch(pdb_id)

        if issue is not None:
            cmd.deselect()
            identificator = str(pdb_id + "_" + res_id + chain)
            identificator.encode('ascii')
            cmd.select(identificator, pdb_id + " and resi " + res_id + " and chain " + chain)
            cmd.color("gray", identificator)
            cmd.hide("all")
            cmd.show("sticks", identificator)

            map(lambda x: self.set_representation(x, pdb_id, res_id, chain, issue), issue.keys())

            cmd.orient(identificator)
