import unittest
import memoQResource
import json
import os


class MemoQResourceTest(unittest.TestCase):
    """Tests for memoQResource module."""

    def __init__(self, *args, **kwargs):
        super(MemoQResourceTest, self).__init__(*args, **kwargs)
        with open("testFiles/testConfig.json") as json_file:
            self.config = json.load(json_file)

    def test_valid_type(self):
        """ Test for valid_type method."""
        test = memoQResource.MemoQResource()

        self.assertFalse(
            test.valid_type(self.config["wrong_resource_type"]), "Wrong type should return false!")

        self.assertTrue(
            test.valid_type(self.config["valid_resource_type"]), "Valid type should return true!")

    def test_set_type(self):
        """ Test for set_type method."""
        test = memoQResource.MemoQResource()

        test.set_type(self.config["wrong_resource_type"])
        self.assertEqual(
            test.get_type(), None, "Setting wrong type succeeded!")

        test.set_type(self.config["valid_resource_type"])
        self.assertNotEqual(
            test.get_type(), None, "Setting valid type failed!")

    def test_set_active_resource(self):
        """ Test for get_project_by_domain method."""
        test = memoQResource.MemoQResource()

        test.set_active_resource(self.config["wrong_resource_guid"],
                                 self.config["valid_resource_type"])
        self.assertEqual(
            test.info, None, "Setting active resource with wrong guid \
            and valid type should return none!")

        test.set_active_resource(self.config["valid_resource_guid"],
                                 self.config["wrong_resource_type"])
        self.assertEqual(
            test.info, None, "Setting active resource with valid guid \
            and wrong type should return none!")

        test.set_active_resource(self.config["valid_resource_guid"],
                                 self.config["valid_resource_type"])
        self.assertNotEqual(
            test.info, None, "Setting active resource with valid guid \
            and type shouldn't return none!")

    def test_get_resources_of_type(self):
        """ Test for get_resources_of_type method."""
        test = memoQResource.MemoQResource()

        self.assertEqual(
            test.get_resources_of_type(self.config["wrong_resource_type"]), None, "Lookup for wrong type should return none!")

        self.assertNotEqual(test.get_resources_of_type(
            self.config["valid_resource_type"]), None, "Lookup for valid type shouldn't return none!")

    def test_get_all_resources(self):
        """ Test for get_all_resources method."""
        test = memoQResource.MemoQResource()
        test.set_active_resource(self.config["valid_resource_guid"],
                                 self.config["valid_resource_type"])

        resources = test.get_all_resources()
        self.assertTrue(len(resources),
                        "List of resources shouldn't be empty!")

        self.assertTrue(len([x for x in resources if x[1].Guid == test.info.Guid and x[1].Name == test.info.Name]),
                        "List should contain our valid resource!")

    def test_download_resource(self):
        """ Test for download_resource method."""
        test = memoQResource.MemoQResource()
        test.set_active_resource(self.config["valid_resource_guid"],
                                 self.config["valid_resource_type"])

        file_path = test.download_resource(".")
        self.assertTrue(os.path.isfile(file_path), "File should exist!")

        os.remove(file_path)

if __name__ == "__main__":
    unittest.main()
