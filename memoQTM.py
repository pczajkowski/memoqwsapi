from suds.client import Client
from base64 import b64decode, b64encode
import os
import json


class MemoQTM(object):
    """Client for memoQ Translation memory API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            apiURL = self.config["api_base_url"] + "/memoqservices/tm?wsdl"
            self.client = Client(apiURL)

        self.__guid = None
        self.info = None

    def get_guid(self):
        """Returns guid of active TM."""
        return self.__guid

    def get_tm_details(self, guid):
        """Returns TM Info for TM of given guid or none if no TM or connection problems."""
        try:
            info = self.client.service.GetTMInfo(guid)
            return info
        except:
            return None

    def set_active_tm(self, guid):
        """Sets guid and info if TM exists."""
        tm_info = self.get_tm_details(guid)
        if tm_info != None:
            self.__guid = guid
            self.info = tm_info

    def __repr__(self):
        if self.info != None:
            return "{} - {}\n{} - {}".format(self.info.Name, self.info.Guid, self.info.SourceLanguageCode, self.info.TargetLanguageCode)
        else:
            return "No TM!"

    def all_tms(self):
        return self.client.service.ListTMs()

    def download_tmx(self, path, guid=None):
        """Downloads TMX export of active or given TM to given path. Returns path to TMX file or none on any failure."""
        if guid != None:
            self.set_active_tm(guid)
        if self.info == None:
            return None

        session_id = self.client.service.BeginChunkedTMXExport(self.get_guid())
        output_filename = os.path.join(path, (self.info.Name + ".tmx"))
        output = open(output_filename, 'wb')
        while True:
            try:
                chunk = self.client.service.GetNextTMXChunk(session_id)
                if chunk is not None:
                    output.write(b64decode(chunk))
                else:
                    break
            except:
                self.client.service.EndChunkedTMXExport(session_id)
                output.close()
                return None

        output.close()
        self.client.service.EndChunkedTMXExport(session_id)

        return output_filename
