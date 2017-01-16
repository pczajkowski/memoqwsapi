from suds.client import Client
import hashlib
import json


class Group(object):
    """Wrapper for group."""

    def __init__(self, group_info=None):
        self.info = group_info

    def __repr__(self):
        if self.info != None:
            return "{} - {}".format(self.info.GroupName, self.info.GroupGuid)
        else:
            return "No group!"


class User(object):
    """Wrapper for user."""

    def __init__(self, user_info=None):
        self.info = user_info

    def valid_user_info(self):
        """ Returns true if given user_info has all required attributes."""
        required_attributes = ["EmailAddress", "FullName",
                               "Password", "UserName", "PackageWorkflowType", "UserGuid"]

        for attribute in required_attributes:
            if not hasattr(self.info, attribute):
                return False
            return True

    def __repr__(self):
        if self.info != None:
            return "{} - {}".format(self.info.FullName, self.info.UserGuid)
        else:
            return "No user!"


class MemoQSecurity(object):
    """Client for memoQ Security API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            apiURL = self.config["api_base_url"] + \
                "/memoqservices/security?wsdl"
            self.client = Client(apiURL)

        self.user = User()
        self.users = []
        self.groups = None
        self.subvendors = None

    def __repr__(self):
        return "{}".format(self.user)

    def set_active_user(self, guid):
        """Sets user of given guid as active."""
        self.user = User(self.client.service.GetUser(guid))

    def get_users(self):
        """Gets list of users from the server into users field."""
        self.users = [User(x) for x in self.client.service.ListUsers()[0]]

    def user_by_name(self, username):
        """ Returns list of users of given fullname (can be partial) from users field."""
        if not len(self.users):
            self.get_users()

        return [x for x in self.users if username in x.info.FullName]

    def not_empty_user_info(self):
        """Validates user info of active user. Returns true on success."""
        if self.user.valid_user_info():
            if self.user.info.EmailAddress != None \
                    and self.user.info.FullName != None \
                    and self.user.info.Password != None \
                    and self.user.info.UserName != None \
                    and self.user.info.PackageWorkflowType != None:
                return True
        return False

    def set_password(self, password):
        """Hashes and sets password for active user."""
        if self.user.info != None and password != "":
            salt = 'fgad s d f sgds g  sdg gfdg'
            to_hash = (password + salt).encode('utf-8')
            self.user.info.Password = str(
                hashlib.sha1(to_hash).hexdigest()).upper()

    def new_user(self):
        """ Sets empty user info as active user (package workflow = online).
        For further user creation."""
        self.user = User(self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}UserInfo'))
        package_workflow = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}UserPackageWorkflowType')
        self.user.info.PackageWorkflowType.value = package_workflow.Online

    def create_user(self):
        """ Creates new user on server from active user. Returns guid."""
        if self.not_empty_user_info():
            guid = self.client.service.CreateUser(self.user.info)
            if guid != None:
                self.set_active_user(guid)
            return guid

    def update_user(self):
        """ Updates user info on server. Returns true on success."""
        if self.not_empty_user_info():
            self.client.service.UpdateUser(self.user.info)
            return True
        return False

    def delete_user(self):
        """ Deletes active user. Dangerous! Returns true on success."""
        if self.user != None and self.user.valid_user_info() and self.user.info.UserGuid != None:
            self.client.service.DeleteUser(self.user.info.UserGuid)
            return True
        return False

    def get_groups(self):
        """ Gets list of groups from the server into groups field."""
        self.groups = [Group(x) for x in self.client.service.ListGroups()[0]]

    def group_by_name(self, groupname):
        """ Returns list of groups of given group name (can be partial) from groups field."""
        if self.groups == None:
            self.get_groups()

        return [x for x in self.groups if groupname in x.info.GroupName]

    def get_subvendors(self):
        """ Gets list of subvendor groups from the server into subvendors field."""
        self.subvendors = [
            Group(x) for x in self.client.service.ListSubvendorGroups()[0]]

    def subvendor_by_name(self, groupname):
        """ Returns list of subvendor groups of given group name (can be partial) from subvendors field."""
        if self.subvendors == None:
            self.get_subvendors()

        return [x for x in self.subvendors if groupname in x.info.GroupName]

    def users_of_group(self, guid):
        """Returns list of users of group of given guid."""
        if guid == None:
            return []

        try:
            users = [User(x)
                     for x in self.client.service.ListUsersOfGroup(guid)[0]]
            return users
        except:
            return []

    def add_current_user_to_group(self, group_guid):
        """Adds current user to group of given guid. Returns true on success."""
        if self.user != None and self.user.valid_user_info() and group_guid != None:
            group_users = self.users_of_group(group_guid)
            if len(group_users):
                new_users_guids = self.client.factory.create(
                    '{http://kilgray.com/memoqservices/2007}userGuids')
                new_users_guids.guid = [
                    user.info.UserGuid for user in group_users]
                new_users_guids.guid.append(self.user.info.UserGuid)
                if len(new_users_guids):
                    try:
                        self.client.service.SetUsersOfGroup(
                            group_guid, new_users_guids)
                        return True
                    except:
                        return False
        return False

    def remove_current_user_from_group(self, group_guid):
        """Removes current user from group of given guid. Returns true on success."""
        if self.user != None and self.user.valid_user_info() and group_guid != None:
            group_users = self.users_of_group(group_guid)
            if len(group_users) and len([x for x in group_users if x.info.UserGuid == self.user.info.UserGuid]):
                new_users_guids = self.client.factory.create(
                    '{http://kilgray.com/memoqservices/2007}userGuids')
                new_users_guids.guid = [
                    user.info.UserGuid for user in group_users if user.info.UserGuid != self.user.info.UserGuid]
                if len(new_users_guids):
                    try:
                        self.client.service.SetUsersOfGroup(
                            group_guid, new_users_guids)
                        return True
                    except:
                        return False
        return False
