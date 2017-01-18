from suds.client import Client
from base64 import b64decode, b64encode
import os
import json


class MemoQFile(object):
    """Client for memoQ File management API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            api_url = self.config["api_base_url"] + \
                "/memoqservices/filemanager?wdsl"
            self.client = Client(api_url)

    def download_file(self, path, guid):
        """Downloads file of given guid from memoQ Server to specified path. Returns full path of downloaded file."""
        chunk_size = 1000000
        start, filename, filesize = self.client.service.BeginChunkedFileDownload(
            guid, False)
        file_bytes_left = filesize[1]
        output_filename = os.path.join(path, filename[1])
        output = open(output_filename, 'wb')
        while file_bytes_left > 0:
            chunk = self.client.service.GetNextFileChunk(start[1], chunk_size)
            output.write(b64decode(chunk))
            file_bytes_left -= len(chunk)
        output.close()
        self.client.service.EndChunkedFileDownload(start[1])
        return output_filename

    def upload_file(self, file_path, chunk_size=1024):
        """Uploads given file to memoQ Server. Returns guid of uploaded file."""
        file_to_send = open(file_path, 'rb')
        file_guid = self.client.service.BeginChunkedFileUpload(
            file_path, False)
        while True:
            data = b64encode(file_to_send.read(chunk_size))
            if not data:
                break
            else:
                self.client.service.AddNextFileChunk(file_guid, data)

        self.client.service.EndChunkedFileUpload(file_guid)
        file_to_send.close()
        return file_guid
