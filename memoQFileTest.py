import unittest
import memoQFile
import os


class memoQFileTest(unittest.TestCase):

    def test_upload_download_file(self):
        test = memoQFile.MemoQFile()

        file_guid = test.upload_file("testFiles/test.txt")
        self.assertNotEqual(file_guid, None, "Guid shouldn't equal none!")

        file_path = test.download_file(".", file_guid)
        self.assertTrue(os.path.isfile(file_path), "File should exist!")

        os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
