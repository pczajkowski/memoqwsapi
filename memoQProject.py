from suds.client import Client
import datetime
import os
import memoQFile
from base64 import b64decode, b64encode
import json


class Languages(object):
    """Encapsulates project languages."""

    def __init__(self):
        self.target = []
        self.source = None


class Project(object):
    """Encapsulates basic project information."""

    def __init__(self):
        self.__guid = None
        now = datetime.datetime.now()
        self.name = 'Test_{}'.format(str(now).replace(":", "-"))
        self.domain = "Python"
        self.documents = None
        self.languages = Languages()
        self.deadline = now + datetime.timedelta(days=2)

    def get_project_guid(self):
        return self.__guid

    def set_project_guid(self, value):
        self.__guid = value

    def populate_project_info(self, projectInfo):
        """Populates name, domain, languages, deadline from project information as received
        from memoQ server."""
        if projectInfo != None:
            self.name = projectInfo['Name']
            self.domain = projectInfo['Domain']
            self.languages.target = [
                x for x in projectInfo['TargetLanguageCodes'].string]
            self.languages.source = projectInfo['SourceLanguageCode']
            self.deadline = projectInfo['Deadline']


class MemoQProject(object):
    """Client for memoQ Server projects API."""

    def __init__(self):
        with open("config.json") as json_file:
            self.config = json.load(json_file)

        if self.config["api_base_url"] != "":
            api_url = self.config["api_base_url"] + \
                "/memoqservices/ServerProject?wsdl"
            self.client = Client(api_url)

        self.project = Project()

    def __repr__(self):
        if self.project.get_project_guid() != None:
            return "{} - {}\n{} - {}\n{}".format(self.project.name, self.project.get_project_guid(), self.project.languages.source, (", ").join([x for x in self.project.languages.target]), str(self.project.deadline))
        else:
            return "No project!"

    def get_project_by_domain(self, domain):
        """Gets first project of given domain name."""
        filter = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}ServerProjectListFilter')
        filter.Domain = domain

        projects = self.client.service.ListProjects(filter)
        if projects:
            self.project.set_project_guid(projects[0][0]['ServerProjectGuid'])
            self.project.populate_project_info(projects[0][0])
        else:
            self.project.set_project_guid(None)

    def get_project_by_guid(self, guid):
        """Gets project information for project of given guid."""
        project_info = self.client.service.GetProject(guid)
        if project_info != None:
            self.project.set_project_guid(guid)
            self.project.populate_project_info(project_info)
        else:
            self.project.set_project_guid(None)

    def template_project_options(self, template_guid):
        """Needs guid of memoQ project template. project.languages.source must be set.
        Returns options needed for creating memoQ project from template."""
        if self.project.languages.source != None:
            options = self.client.factory.create(
                '{http://kilgray.com/memoqservices/2007}TemplateBasedProjectCreateInfo')
            options.TemplateGuid = template_guid
            options.Name = self.project.name

            if self.project.languages.source != "":
                options.SourceLanguageCode = self.project.languages.source
            else:
                print("project.languages.source must be set!")
                return None

            if len(self.project.languages.target):
                options.TargetLanguageCodes.string = self.project.languages.target

            options.Domain = self.project.domain
            options.CreatorUser = self.config["creator_guid"]

            return options
        else:
            return None

    def create_project_from_template(self, template_guid=None, options=None):
        """Creates memoQ project using predefined options when
        provided with template_guid or using provided options.
        Sets new project as active project on success."""
        if template_guid != None:
            options = self.template_project_options(template_guid)

        if options != None:
            result = self.client.service.CreateProjectFromTemplate(options)
            if result.ResultStatus == "Success":
                self.get_project_by_guid(result.ProjectGuid)
            else:
                self.project.set_project_guid(None)

    def project_options(self):
        """Returns options needed for creating memoQ project. project.languages.source and project.languages.target must be set."""
        if len(self.project.languages.target) and self.project.languages.source != None:
            options = self.client.factory.create(
                '{http://kilgray.com/memoqservices/2007}ServerProjectDesktopDocsCreateInfo')
            options.Name = self.project.name

            if self.project.languages.source != "":
                options.SourceLanguageCode = self.project.languages.source
            else:
                print("project.languages.source must be set!")
                return None

            if len(self.project.languages.target):
                options.TargetLanguageCodes.string = self.project.languages.target
            else:
                print("project.languages.target must be set!")
                return None

            options.Deadline = self.project.deadline
            options.RecordVersionHistory = True
            options.CreatorUser = self.config["creator_guid"]

            resources = self.client.factory.create(
                '{http://schemas.datacontract.org/2004/07/MemoQServices}ServerProjectResourcesInPackages')
            options.PackageResourceHandling.value = resources.LinkRemote
            return options
        else:
            return None

    def create_project(self, options=None):
        """Creates memoQ project using predefined or provided options.
        Sets new project as active project on success."""
        if options == None:
            options = self.project_options()

        if options != None:
            project_guid = self.client.service.CreateProject2(options)
            if project_guid != None:
                self.get_project_by_guid(project_guid)
            else:
                self.project.set_project_guid(None)

    def import_document(self, path):
        """Uploads and then imports given file to active project for all target languages.
        Returns true on success."""
        file_client = memoQFile.MemoQFile()
        file_guid = file_client.upload_file(path)
        if file_guid == None:
            return False

        langs = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}targetLangCodes')
        langs.string = self.project.languages.target

        result = self.client.service.ImportTranslationDocument(
            self.project.get_project_guid(), file_guid, langs)
        if result != None:
            return True
        else:
            return False

    def get_project_documents(self):
        """Gets list of documents from active project."""
        options = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}ListServerProjectTranslationDocument2Options')
        options.FillInAssignmentInformation = True

        if self.project.get_project_guid() != None:
            self.documents = self.client.service.ListProjectTranslationDocuments2(
                self.project.get_project_guid(), options)

    def document_guids(self):
        """Returns guids of documents from active project."""
        if self.documents == None:
            self.get_project_documents()

        return [x.DocumentGuid for x in self.documents[0]]

    def print_documents(self):
        """Prints basic information on documents from active project."""
        if self.documents == None:
            self.get_project_documents()

        for document in self.documents[0]:
            print("{} ({}) - {}\n".format(document.DocumentName,
                                          document.TargetLangCode, document.DocumentGuid))

    def export_documents(self, path):
        """Exports all documents from active project to given path.
        Prints path to each file on success and returns true."""
        if self.project.get_project_guid() == None:
            return "No project!"

        export_results = []
        for guid in self.document_guids():
            export_results.append(
                self.client.service.ExportTranslationDocument(self.project.get_project_guid(), guid))

        file_client = memoQFile.MemoQFile()
        if len(export_results):
            for document in export_results:
                print(file_client.download_file(path, document.FileGuid))
            return True
        else:
            return False

    def export_documents2(self, path):
        """Exports all documents from active project to given path using extended method.
        Prints path to each file on success and returns true."""
        if self.project.get_project_guid() == None:
            return "No project!"

        options = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}DocumentExportOptions')
        options.CopySourceToEmptyTarget = True

        export_results = []
        for guid in self.document_guids():
            export_results.append(self.client.service.ExportTranslationDocument2(
                self.project.get_project_guid(), guid, options))

        file_client = memoQFile.MemoQFile()
        if len(export_results):
            for document in export_results:
                print(file_client.download_file(path, document.FileGuid))
            return True
        else:
            return False

    def statistics_options(self):
        """Returns options for statistics."""
        options = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}StatisticsOptions')
        options.Analysis_ProjectTMs = True
        options.Analysis_Homogenity = True
        options.ShowResultsPerFile = True
        options.RepetitionPreferenceOver100 = True
        statistics_algorithm = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}StatisticsAlgorithm')
        options.Algorithm.value = statistics_algorithm.MemoQ

        return options

    def run_statistics(self, options=None):
        """Returns statistics (memoQ CSV) for all documents and language
        combinations of active project using predefined or provided options,
         returns none on failure."""
        if options == None:
            options = self.statistics_options()

        statistics_format = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}StatisticsResultFormat')
        languages = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}targetLangCodes')
        languages.string = self.project.languages.target

        try:
            stats = self.client.service.GetStatisticsOnProject(
                self.project.get_project_guid(), languages, options, statistics_format.CSV_MemoQ)
            if stats.ResultStatus == "Success":
                return stats
            else:
                return None
        except Exception as e:
            print(str(e))

    def save_statistics(self, path, statistics=None, options=None):
        """Saves provided statistics (generates them using provided options
        if none) to given path (one file per language combination).
        Prints path to statistics file(s)."""
        if statistics == None:
            statistics = self.run_statistics(options=options)

        for stat in statistics.ResultsForTargetLangs.StatisticsResultForLang:
            filename = '{}_{}.csv'.format(
                stat.TargetLangCode, self.project.name)
            output_file = os.path.join(path, filename)
            with open(output_file, 'wb') as target:
                # Statistics are base64 and utf-16 encoded, so we need to
                # decode first
                stat_data = b64decode(stat.ResultData).decode("utf-16")
                # Changing delimiter to ,
                stat_data = stat_data.replace(";", ",")
                target.write(stat_data.encode("utf-8"))
            print(output_file)

    def pretranslate_options(self):
        """Returns options for pre-translation."""
        options = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}PretranslateOptions')
        lookup_behavior = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}PretranslateLookupBehavior')
        options.PretranslateLookupBehavior.value = lookup_behavior.GoodMatch
        options.GoodMatchRate = 80

        # Options for locking 100% matches
        options.LockPretranslated = True
        pretranslate_state = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}PretranslateStateToConfirmAndLock')
        options.ConfirmLockPretranslated.value = pretranslate_state.ExactMatch
        final_state = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}PretranslateExpectedFinalTranslationState')
        options.FinalTranslationState = final_state.Confirmed

        copy_source_options = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}PretranslateCopySourceToTargetBehavior')
        copy_condition = self.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}PretranslateCopySourceToTargetConditions')
        copy_source_options.Condition.value = copy_condition.SegmentsWithOnlyTagsAndWhitespace
        copy_source_options.Lock = True
        options.CopySourceToTarget = copy_source_options

        return options

    def pretranslate_project(self, options=None):
        """Pretranslate active project using predefined or provided options. Returns true on success."""
        if options == None:
            options = self.pretranslate_options()

        languages = self.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}targetLangCodes')
        languages.string = self.project.languages.target

        result = self.client.service.PretranslateProject(
            self.project.get_project_guid(), languages, options)
        if result.ResultStatus == "Success":
            return True
        return False

    def delete(self):
        """Deletes active project permanently. WARNING! Not possible to recover!"""
        self.client.service.DeleteProject(self.project.get_project_guid())
