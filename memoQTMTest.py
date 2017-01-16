import unittest
import memoQTM
import json
import os


class MemoQTMTest(unittest.TestCase):
    """Tests for memoQTM module."""

    def __init__(self, *args, **kwargs):
        super(MemoQTMTest, self).__init__(*args, **kwargs)
        with open("testFiles/testConfig.json") as json_file:
            self.config = json.load(json_file)

    def test_get_tm_details(self):
        """Test for get_tm_details method."""
        test = memoQTM.MemoQTM()

        self.assertEqual(
            test.get_tm_details(self.config["wrong_tm_guid"]), None,
            "TM Info for wrong TM guid should be none!")

        self.assertNotEqual(
            test.get_tm_details(self.config["valid_tm_guid"]), None,
            "TM Info for wrong TM guid shouldn't be none!")

    def test_set_active_tm(self):
        """Test for set_active_tm method."""
        test = memoQTM.MemoQTM()

        test.set_active_tm(self.config["wrong_tm_guid"])
        self.assertEqual(
            test.tm.info, None, "TM Info for wrong TM guid should be none!")

        test.set_active_tm(self.config["valid_tm_guid"])
        self.assertNotEqual(
            test.tm.info, None, "TM Info for valid TM guid shouldn't be none!")

    def test_get_all_tms(self):
        """Test for get_all_tms method."""
        test = memoQTM.MemoQTM()
        self.assertTrue(len(test.get_all_tms()),
                        "List of TMs shouldn't be empty!")

    def test_download_tmx(self):
        """Test for download_tmx method."""
        test = memoQTM.MemoQTM()

        file_path = test.download_tmx(".", self.config["wrong_tm_guid"])
        self.assertEqual(file_path, None,
                         "Filepath for wrong guid should be none!")

        file_path = test.download_tmx(".", self.config["valid_tm_guid"])
        self.assertNotEqual(file_path, None,
                            "Filepath shouldn't be none! (argument)")
        self.assertTrue(os.path.isfile(file_path),
                        "File should exist! (argument)")
        os.remove(file_path)

        test = memoQTM.MemoQTM()
        test.set_active_tm(self.config["valid_tm_guid"])
        self.assertNotEqual(
            test.tm.info, None, "TM Info for valid TM guid shouldn't be none!")

        file_path = test.download_tmx(".")
        self.assertNotEqual(file_path, None,
                            "Filepath shouldn't be none! (field)")
        self.assertTrue(os.path.isfile(file_path),
                        "File should exist! (field)")
        os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
