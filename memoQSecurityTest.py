import unittest
import memoQSecurity
import json
import os


class MemoQSecurityTest(unittest.TestCase):
    """Tests for memoQSecurity module."""

    def __init__(self, *args, **kwargs):
        super(MemoQSecurityTest, self).__init__(*args, **kwargs)
        with open("testFiles/testConfig.json") as json_file:
            self.config = json.load(json_file)

    def test_set_active_user(self):
        """Test for set_active_user method."""
        test = memoQSecurity.MemoQSecurity()

        test.set_active_user(self.config["wrong_user_guid"])
        self.assertFalse(test.user.valid_user_info(),
                         "User info shouldn't be valid for wrong guid!")

        test.set_active_user(self.config["valid_user_guid"])
        self.assertTrue(test.user.valid_user_info(),
                        "User info should be valid for valid guid!")
        self.assertEqual(test.user.info.FullName,
                         self.config["valid_user_name"], "Names should match!")

    def test_get_users(self):
        """Test for get_users method."""
        test = memoQSecurity.MemoQSecurity()

        test.get_users()

        self.assertTrue(len(test.users), "List of users shouldn't be empty!")

    def test_user_by_name(self):
        """Test for user_by_name method."""
        test = memoQSecurity.MemoQSecurity()

        self.assertFalse(len(test.user_by_name(
            self.config["wrong_user_name"])), "List of users for wrong username should be empty!")

        self.assertTrue(len(test.user_by_name(
            self.config["valid_user_name"])), "List of users for valid username shouldn't be empty!")

    def test_set_password(self):
        """Test for set_password method."""
        test = memoQSecurity.MemoQSecurity()
        test.set_active_user(self.config["valid_user_guid"])

        password = test.user.info.Password

        test.set_password("")
        self.assertEqual(test.user.info.Password, password,
                         "Password shouldn't be changed to empty!")

        test.set_password("something")
        self.assertNotEqual(test.user.info.Password, password,
                            "Password should be changed!")

    def test_new_user(self):
        """Test for new_user method."""
        test = memoQSecurity.MemoQSecurity()
        test.new_user()

        self.assertNotEqual(test.user, None, "User shouldn't be none!")

        self.assertTrue(test.user.valid_user_info(),
                        "User info should be valid!")

        self.assertEqual(test.user.info.PackageWorkflowType.value,
                         "Online", "Package workflow should be set to online!")

    def test_create_update_delete_user(self):
        """Test for create_user, update_user and delete_user methods."""
        test = memoQSecurity.MemoQSecurity()

        # Create new user
        test.new_user()
        test.user.info.EmailAddress = "anon@anon.com"
        test.user.info.FullName = "Anonymous Mouse"
        test.set_password("something123")
        test.user.info.UserName = "anonymous"

        guid = test.create_user()
        self.assertNotEqual(guid, None, "Guid shouldn't be none!")

        # Update user
        new_fullname = "Anonymous Mouse2"
        test.user.info.FullName = new_fullname
        self.assertFalse(test.update_user(),
                         "Update should return false for password not set!")

        test.set_password("something123")
        self.assertTrue(test.update_user(), "Update should return true!")

        test.set_active_user(guid)
        self.assertEqual(test.user.info.FullName,
                         new_fullname, "Names should be equal!")

        # Delete user
        test = memoQSecurity.MemoQSecurity()
        self.assertFalse(test.delete_user(),
                         "Deletion should fail for no user!")

        test.set_active_user(guid)
        self.assertTrue(test.delete_user(), "Deletion should succeed!")

        test.set_active_user(guid)
        self.assertFalse(test.user.valid_user_info(),
                         "User info shouldn't be valid for deleted user!")

    def test_get_groups(self):
        """Test for get_groups method."""
        test = memoQSecurity.MemoQSecurity()

        test.get_groups()

        self.assertTrue(len(test.groups), "List of groups shouldn't be empty!")

    def test_group_by_name(self):
        """Test for group_by_name method."""
        test = memoQSecurity.MemoQSecurity()

        self.assertFalse(len(test.group_by_name(
            self.config["wrong_group_name"])), "List of groups for wrong group name should be empty!")

        self.assertTrue(len(test.group_by_name(
            self.config["valid_group_name"])), "List of groups for valid group name shouldn't be empty!")

    def test_get_subvendors(self):
        """Test for get_subvendors method."""
        test = memoQSecurity.MemoQSecurity()

        test.get_subvendors()

        self.assertTrue(len(test.subvendors),
                        "List of subvendors shouldn't be empty!")

    def test_users_of_group(self):
        """Test for users_of_group method."""
        test = memoQSecurity.MemoQSecurity()

        self.assertFalse(len(test.users_of_group(self.config[
                         "wrong_group_guid"])), "List of users should be empty for wrong guid!")

        self.assertFalse(len(test.users_of_group(None)),
                         "List of users should be empty for no guid!")

        self.assertTrue(len(test.users_of_group(self.config[
                        "valid_group_guid"])), "List of users shouldn't be empty for valid guid!")

    def test_add_remove_current_user_tofrom_group(self):
        """Test for add_current_user_to_group and remove_current_user_from_group methods."""
        test = memoQSecurity.MemoQSecurity()

        test.set_active_user(self.config["wrong_user_guid"])
        self.assertFalse(test.add_current_user_to_group(self.config["valid_group_guid"]),
                         "Should be false if wrong user but valid group guid! (adding)")
        self.assertFalse(test.remove_current_user_from_group(self.config["valid_group_guid"]),
                         "Should be false if wrong user but valid group guid! (deleting)")

        test.set_active_user(self.config["valid_user_guid"])
        self.assertFalse(test.add_current_user_to_group(self.config[
                         "wrong_group_guid"]),
                         "Should be false if valid user but wrong group guid! (adding)")
        self.assertFalse(test.remove_current_user_from_group(self.config[
                         "wrong_group_guid"]),
                         "Should be false if valid user but wrong group guid! (deleting)")

        # Adding valid user to valid group
        self.assertTrue(test.add_current_user_to_group(self.config["valid_group_guid"]),
                        "Should be true if valid user and group guid! (adding)")

        users = test.users_of_group(self.config[
            "valid_group_guid"])
        self.assertTrue(len([x for x in users if x.info.UserGuid ==
                             self.config[
                                 "valid_user_guid"]]),
                        "Valid user should be part of the group after adding!")

        # Removing valid user from valid group
        self.assertTrue(test.remove_current_user_from_group(self.config["valid_group_guid"]),
                        "Should be true if valid user and group guid! (deleting)")

        users = test.users_of_group(self.config[
            "valid_group_guid"])
        self.assertFalse(len([x for x in users if x.info.UserGuid ==
                              self.config["valid_user_guid"]]),
                         "Valid user shouldn't be part of the group after deleting!")

if __name__ == "__main__":
    unittest.main()
