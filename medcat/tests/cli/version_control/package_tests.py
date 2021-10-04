from medcat import vocab
import os
import unittest
import shutil
import requests
import zipfile
from tqdm import tqdm
from unittest import mock

from medcat.cli.system_utils import force_delete_path, get_local_model_storage_path
from medcat.cli.config import *
from medcat.cli.package import package
from medcat.cli.download import download

from medcat.cat import CAT

unittest.defaultTestLoader.sortTestMethodsUsing = lambda *args: -1

def make_orderer():
    order = {}

    def ordered(f):
        order[f.__name__] = len(order)
        return f

    def compare(a, b):
        return [1, -1][order[a] < order[b]]

    return ordered, compare

ordered, compare = make_orderer()
unittest.defaultTestLoader.sortTestMethodsUsing = compare

class PackageTests(unittest.TestCase):
    

    """
        Unit tests for git & utils, tests if folders can be created & accessed, as well as if the git credentials work etc.
    """
    set_git_global_git_credentials()

    def setUp(self):
        self.tmp_full_model_tag_name = "unit_test_model-1.0"
        self.unit_testing_model_path_origin = os.path.join(get_local_model_storage_path(), "_unit_test_model_tmp_")
        self.unit_testing_model_path_download_location = os.path.join(get_local_model_storage_path(), "_unit_test_model_")
        self.unit_test_specialist_model_name = "unit_test_specialist_model"
        self.unit_test_specialist_model_tag_name = "unit_test_specialist_model-1.0"

        if not os.path.exists(self.unit_testing_model_path_origin):
            os.mkdir(self.unit_testing_model_path_origin)

    def get_input(text):
        return input(text)
   
    def get_test_model_name(test):
        return input(test)

    @ordered
    def test_download_files(self):
        logging.info("Attempting to download initial base models from the MedCAT repo with NO version history.")
        if not os.path.exists(self.unit_testing_model_path_download_location):
            os.mkdir(self.unit_testing_model_path_download_location)
            os.chdir(self.unit_testing_model_path_download_location)

        url_cdb = "https://medcat.rosalind.kcl.ac.uk/media/cdb-medmen-v1.dat"
        url_vocab = "https://medcat.rosalind.kcl.ac.uk/media/vocab.dat"
        url_medcat_export_json = "https://raw.githubusercontent.com/CogStack/MedCAT/legacy/tutorial/data/MedCAT_Export.json"
        url_mc_status = "https://medcat.rosalind.kcl.ac.uk/media/mc_status.zip"
        
        cdb_file_name = url_cdb.split("/")[-1]
        vocab_file_name = url_vocab.split("/")[-1]
        medcat_export_file_name = url_medcat_export_json.split("/")[-1]
        url_mc_status_file_name = url_mc_status.split("/")[-1]

        r_get_cdb = requests.get(url_cdb, stream=True, allow_redirects=True)
        r_get_vocab = requests.get(url_vocab, stream=True, allow_redirects=True)
        r_get_medcat_export = requests.get(url_medcat_export_json, stream=True, allow_redirects=True)
        r_get_mc_status = requests.get(url_mc_status, stream=True, allow_redirects=True)

        cdb_fsize = int(r_get_cdb.headers.get('content-length'))
        vocab_fsize = int(r_get_vocab.headers.get('content-length'))
        medcat_export_fsize = int(r_get_medcat_export.headers.get('content-length'))
        r_get_mc_status_fsize = int(r_get_mc_status.headers.get('content-length'))

        cdb_f_path = os.path.join(self.unit_testing_model_path_download_location, cdb_file_name)
        vocab_f_path = os.path.join(self.unit_testing_model_path_download_location, vocab_file_name)
        medcat_export_f_path = os.path.join(self.unit_testing_model_path_download_location, medcat_export_file_name)
        r_get_mc_status_f_path = os.path.join(self.unit_testing_model_path_download_location, url_mc_status_file_name)

        if (os.path.exists(cdb_f_path) and os.path.isfile(cdb_f_path) and os.path.getsize(cdb_f_path) >= cdb_fsize) is False:
            with open(cdb_f_path, "wb") as cdb_file:
                with tqdm(total=cdb_fsize, unit_scale=True, desc=url_cdb.split("/")[-1], initial=0, ascii=True) as pbar:
                    for kbyte in r_get_cdb.iter_content(chunk_size=1024):
                        if kbyte:
                            cdb_file.write(kbyte)
                            pbar.update(len(kbyte))
        else:
            logging.info("File already exists:" + cdb_f_path + ". No need to redownload.")

        shutil.copy(cdb_f_path, os.path.join(self.unit_testing_model_path_download_location, "cdb.dat"))

        if (os.path.exists(vocab_f_path) and os.path.isfile(vocab_f_path) and os.path.getsize(vocab_f_path) >= vocab_fsize) is False:
            with open(vocab_f_path , "wb") as vocab_file:
                with tqdm(total=vocab_fsize, unit_scale=True, desc=url_vocab.split("/")[-1], initial=0, ascii=True) as pbar:
                    for kbyte in r_get_vocab.iter_content(chunk_size=1024):
                        if kbyte:
                            vocab_file.write(kbyte)
                            pbar.update(len(kbyte))
        else:
            logging.info("File already exists:" + vocab_f_path + ". No need to redownload.")

        if (os.path.exists(medcat_export_f_path) and os.path.isfile(medcat_export_f_path) and os.path.getsize(medcat_export_f_path) >= medcat_export_fsize) is False:
            with open(medcat_export_f_path , "wb") as medcat_export_file_name:
                with tqdm(total=medcat_export_fsize, unit_scale=True, desc=url_medcat_export_json.split("/")[-1], initial=0, ascii=True) as pbar:
                    for kbyte in r_get_medcat_export.iter_content(chunk_size=1024):
                        if kbyte:
                            medcat_export_file_name.write(kbyte)
                            pbar.update(len(kbyte))
        else:
            logging.info("File already exists:" + medcat_export_f_path + ". No need to redownload.")

        # MC STATUS FILE
        if (os.path.exists(r_get_mc_status_f_path) and os.path.isfile(r_get_mc_status_f_path) and os.path.getsize(r_get_mc_status_f_path) >= r_get_mc_status_fsize) is False:
            with open(r_get_mc_status_f_path , "wb") as url_mc_status_file_name:
                with tqdm(total=r_get_mc_status_fsize, unit_scale=True, desc=url_medcat_export_json.split("/")[-1], initial=0, ascii=True) as pbar:
                    for kbyte in r_get_mc_status.iter_content(chunk_size=1024):
                        if kbyte:
                            url_mc_status_file_name.write(kbyte)
                            pbar.update(len(kbyte))
            archive = zipfile.ZipFile(r_get_mc_status_f_path, 'r')
            for file in archive.namelist():
                archive.extract(file, self.unit_testing_model_path_origin)
        else:
            logging.info("File already exists:" + r_get_mc_status_f_path + ". No need to redownload.")
   
    @ordered
    def test_standardize_model_files(self):
        os.chdir(self.unit_testing_model_path_download_location)

        if os.path.exists(self.unit_testing_model_path_origin):
            if not os.path.exists(os.path.join(self.unit_testing_model_path_origin, "vocab.dat")) and \
               not os.path.exists(os.path.join(self.unit_testing_model_path_origin, "cdb.dat")) and \
               not os.path.exists(os.path.join(self.unit_testing_model_path_origin, "MedCAT_Export.json")):

                cat = CAT.load_model(model_full_tag_name="", vocab_input_file_name = "./vocab.dat", cdb_input_file_name = "./cdb.dat", trainer_data_file_name = "./MedCAT_Export.json", bypass_model_path=True)
                os.chdir(self.unit_testing_model_path_origin)
                cat.save_model(vocab_output_file_name="vocab.dat", cdb_output_file_name="cdb.dat", trainer_data_file_name="MedCAT_Export.json")
    
    @ordered   
    def test_package_model_default(self):
        os.chdir(self.unit_testing_model_path_origin)
        with unittest.mock.patch('builtins.input', side_effect=["yes", "yes", "no", "yes"]):
            self.assertEqual(package(self.tmp_full_model_tag_name), True)

    @ordered     
    def test_package_model_default_improvement(self):
        new_release_tmp_path = os.path.join(get_local_model_storage_path(), "_unit_test_new_release_tmp_")

        if not os.path.exists(new_release_tmp_path):
            os.mkdir(new_release_tmp_path)
            
        os.chdir(new_release_tmp_path)

        cat = CAT.load_model(self.tmp_full_model_tag_name)
        text = ["My patient has kidney failure, bowel cancer and heart failure",
                "She was evaluated by an ophthalmologist and diagnosed with conjunctivitis. She was given eye drops that did not relieve her eye symptoms."]
                
        cat.train = True

        for sentence in text:
            doc_spacy = cat(sentence)

        cat.train = False

        print("AFTER TRAINING: ")

        #cat.cdb.print_stats()
        cat.save_model()

        with unittest.mock.patch('builtins.input', side_effect=["yes", "yes", "yes", "yes"]):
            self.assertEqual(package(), True)
   
    @ordered   
    def test_download_base_unit_test_model(self):
        os.chdir(get_local_model_storage_path())
        with unittest.mock.patch('builtins.input', side_effect=["yes", "yes", "yes"]):
            self.assertEqual(download(self.tmp_full_model_tag_name), True)
     
    
    @ordered
    def test_x_package_model_specialist(self):

        new_release_tmp_path =  os.path.join(get_local_model_storage_path(), "_unit_test_new_release_tmp_")

        if not os.path.exists(new_release_tmp_path):
            os.mkdir(new_release_tmp_path)
        os.chdir(new_release_tmp_path)

        cat = CAT.load_model(self.tmp_full_model_tag_name)

        text = ["My patient has pancreatitis, and liver disease.", "Patient has nausea, symptoms appeared, vomiting.",
                "Patient has coronavirus, symptoms appeared 2 weeks ago."]
        cat.train = True

        for sentence in text:
            doc_spacy = cat(sentence)

        cat.save_model()

        with unittest.mock.patch('builtins.input', side_effect=["No", "Yes", self.unit_test_specialist_model_name, "y"]):
            self.assertEqual(package(), True)
  
    @ordered
    def test_x_package_model_specialist_improved(self):
        
        new_release_tmp_path = os.path.join(get_local_model_storage_path(), "_unit_test_new_release_tmp_")

        force_delete_path(new_release_tmp_path)

        if not os.path.exists(new_release_tmp_path):
            os.mkdir(new_release_tmp_path)

        os.chdir(new_release_tmp_path)

        cat = CAT.load_model(self.unit_test_specialist_model_tag_name)

        print(cat.cdb.vc_model_tag_data)

        text = ["My patient has Tuberculosis",
                "She was evaluated by an Tuberculosis , ulcer and gastroentritis + ToF."]
        cat.train = True
  
        for sentence in text:
            doc_spacy = cat(sentence)
  
        cat.train = False
  
        print("AFTER TRAINING:")
  
        #cat.cdb.print_stats()
        cat.save_model()

        with unittest.mock.patch('builtins.input', side_effect=["Yes", "y", "y"]):
            self.assertEqual(package(), True)
   
   

    @ordered
    def test_x_package_model_specialist_improved_print(self):
        cat = CAT.load_model("unit_test_specialist_model-1.0")
        print(cat.cdb.vc_model_tag_data)

    @ordered
    def test_x_package_model_specialist_improveda_print_improved(self):
        cat = CAT.load_model("unit_test_specialist_model-1.1")
        print(cat.cdb.vc_model_tag_data)