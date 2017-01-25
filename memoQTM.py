from suds.client import Client
from base64 import b64decode, b64encode
import os
import json


class TM(object):
    """Wrapper for TM."""

    def __init__(self, info=None):
        self.info = info

    def __repr__(self):
        if self.info != None:
            return "{} - {}\n{} - {}".format(
                self.info.Name, self.info.Guid,
                self.info.SourceLanguageCode, self.info.TargetLanguageCode)
        else:
            return "No TM!"

    def get_guid(self):
        """Returns guid of active TM."""
        return self.info.Guid


class MemoQTM(object):
    """Client for memoQ Translation memory API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            api_url = self.config["api_base_url"] + "/memoqservices/tm?wsdl"
            self.client = Client(api_url)

        self.tm = TM()

    def __repr__(self):
        return "{}".format(self.tm)

    def get_tm_details(self, guid):
        """Returns TM Info for TM of given guid or none if no TM or connection problems."""
        try:
            info = self.client.service.GetTMInfo(guid)
            return info
        except:
            return None

    def set_active_tm(self, guid):
        """Sets TM of given guid as active."""
        tm_info = self.get_tm_details(guid)
        if tm_info != None:
            self.tm = TM(tm_info)

    def get_all_tms(self):
        """Returns list of all TMs on server."""
        return [TM(x) for x in self.client.service.ListTMs()[0]]

    def download_tmx(self, path, guid=None):
        """Downloads TMX export of active or given TM to given path.
        Returns path to TMX file or none on any failure."""
        if guid != None:
            self.set_active_tm(guid)
        if self.tm.info == None:
            return None

        session_id = None
        try:
            session_id = self.client.service.BeginChunkedTMXExport(
                self.tm.get_guid())
        except Exception as e:
            print(e)
            return None

        output_filename = os.path.join(path, (self.tm.info.Name + ".tmx"))
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
