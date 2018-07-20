import json
import urllib2
import Model
import time
import random
import socket
import httplib
# Global variable, used for display values in treeview #


class ValidatorManager:
    # Manage validation, Checks internet connection, checks for errors in PDBs #

    def __init__(self):
        self.error = ""
        self.protein_model_list = []
        # self.downloaded_json = json.load(open('3d11.json', mode='r'))             # uncomment when internet connection
        self.downloaded_json = {}
        self.validation_report = {}
        self.all_reports = {}


    def url_response(self, pdb_id):
        """
        Checks internet connection and download validation report
        :param pdb_id:
        :return: validation report
        """
        data_response = False
        tries = 0
        limit = 5
        self.downloaded_json = {}

        while tries < limit:

            try:

                auto_handler = urllib2.HTTPSHandler()
                opener = urllib2.build_opener(auto_handler)
                urllib2.install_opener(opener)
                #req = urllib2.Request("http://webchemdev.ncbr.muni.cz/API/Validation/Protein/" + pdb_id)
                #response = urllib2.HTTPSHandler.https_open(req)
                response = urllib2.urlopen("https://webchemdev.ncbr.muni.cz/API/Validation/Protein/" + pdb_id, None, 5)

            except urllib2.HTTPError, e:
                if e.code == 404:
                    time.sleep(random.randint(1, 5))  # sleep 1-5 seconds
                    tries += 1
                    data_response = False

                else:
                    time.sleep(random.randint(1, 5))  # sleep 1-5 seconds
                    tries += 1

            except urllib2.URLError, e:
                time.sleep(random.randint(1, 5))  # sleep 1-5 seconds
                tries += 1

            except socket.timeout, e:
                time.sleep(random.randint(1, 5))  # sleep 1-5 seconds
                tries += 1

            else:
                self.downloaded_json = json.load(response)
                data_response = True
                break

        if not data_response:
            return data_response

        return data_response

    def error_check(self, pdb_id):
        """
        check for errors; motivecount == 0
        :param pdb_id: PDBid which will be downloaded
        :return: bool, True for Error, False for warning, False for succes
        """
        validation_report = self.url_response(pdb_id)

        if not validation_report:
            self.error = "Could not load page. Check your internet connection"
            return False

        if 'Error' in self.downloaded_json:
            self.error = self.downloaded_json['Error']
            return False

        elif self.downloaded_json['MotiveCount'] == 0:
            self.error = "No models to validate! Please use another molecule."
            return True

        else:
            return True

    def scan_json(self, pdb_id):
        """
        Scan the JSON file, add PDB to global variable validation_report and split PDB to models.
        :param pdb_id: PDBid which will be downloaded
        :return: List of models of given PDBid
        """

        self.all_reports[pdb_id] = self.downloaded_json
        self.protein_model_list = []

        for item, value in enumerate(self.all_reports[pdb_id]["Models"]):
            pdb_entry = self.all_reports[pdb_id]["Models"][item]
            self.protein_model_list.append(pdb_entry)
            Model.Model(pdb_entry)

        return self.protein_model_list

    def find_report(self, pdb_id, model_counter, property):

        return self.all_reports[pdb_id]["Models"][model_counter][property]

    def delete_report(self, pdb_id, model_count = None, property = None, entry_count = None):

        if entry_count is None:
            self.all_reports.pop(pdb_id)

        else:
            self.find_report(pdb_id, model_count, property).pop(entry_count)
