from suds.client import Client
import memoQFile
import json


class MemoQResource(object):
    """Client for memoQ Light Resource API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            api_url = self.config["api_base_url"] + \
                "/memoqservices/resource?wsdl"
            self.client = Client(api_url)

        self.types = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}ResourceType')
        self.__type = None
        self.info = None

    def __repr__(self):
        if self.info != None:
            return "{} - {} ({})".format(self.info.Name, self.info.Guid, self.get_type())
        else:
            return "No resource!"

    def get_guid(self):
        """Returns resource guid."""
        if self.info != None:
            return self.info.Guid

    def get_type(self):
        """Returns resource type."""
        return self.__type

    def set_type(self, value):
        """Sets resource type."""
        if self.valid_type(value):
            self.__type = self.types[value]

    def valid_type(self, value):
        """Returns true if type is valid."""
        if value in self.types:
            return True
        return False

    def set_active_resource(self, guid, resource_type):
        """Populates info basing on resource type and guid."""
        if guid != None and self.valid_type(resource_type):
            try:
                info = self.client.service.GetResourceInfo(
                    self.types[resource_type], guid)
                if info != None:
                    self.info = info
                    self.set_type(resource_type)
            except Exception:
                pass

    def get_resources_of_type(self, resource_type):
        """Returns all resources of given type from memoQ server."""
        if self.valid_type(resource_type):
            return self.client.service.ListResources(resource_type)

    def get_all_resources(self):
        """Returns all resources from memoQ server."""
        resources = []
        for name, value in self.types:
            for resource in self.get_resources_of_type(value):
                resources.extend([(value, x) for x in resource[1]])
        return resources

    def download_resource(self, path):
        """Downloads active resource to given path. Returns path to downloaded file."""
        if self.get_type() != None and self.get_guid() != None:
            file_client = memoQFile.MemoQFile()
            return file_client.download_file(
                path, self.client.service.ExportResource(self.get_type(), self.get_guid()))
