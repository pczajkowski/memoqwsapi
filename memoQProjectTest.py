import unittest
import memoQProject
import json
import os


class MemoQProjectTest(unittest.TestCase):
    """Tests for memoQProject module."""

    def __init__(self, *args, **kwargs):
        super(MemoQProjectTest, self).__init__(*args, **kwargs)
        with open("testFiles/testConfig.json") as json_file:
            self.config = json.load(json_file)

    def test_get_project_by_domain(self):
        """ Test for get_project_by_domain method."""
        test = memoQProject.MemoQProject()

        test.get_project_by_domain(self.config["valid_domain"])
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        test.get_project_by_domain(self.config["wrong_domain"])
        self.assertEqual(test.project.get_project_guid(),
                         None, "Guid should be none!")

    def test_get_project_by_guid(self):
        """ Test for get_project_by_guid method."""
        test = memoQProject.MemoQProject()

        valid_guid = "27e14066-0b73-44fc-a5ea-a828fed42e7f"
        wrong_guid = "00000000-0000-0000-0000-000000000001"

        test.get_project_by_guid(valid_guid)
        self.assertEqual(test.project.get_project_guid(),
                         valid_guid, "Guids don't match!")

        test.get_project_by_guid(wrong_guid)
        self.assertEqual(test.project.get_project_guid(),
                         None, "Guid should be none!")

    def test_template_project_options(self):
        """ Test for template_project_options method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]

        options = test.template_project_options(
            self.config["project_template_guid"])

        fake_options = test.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}TemplateBasedProjectCreateInfo')
        fake_options.TemplateGuid = self.config["project_template_guid"]
        fake_options.Name = test.project.name
        fake_options.SourceLanguageCode = test.project.languages.source
        fake_options.Domain = test.project.domain
        fake_options.CreatorUser = self.config["creator_guid"]

        self.assertEqual(options.Name, fake_options.Name,
                         "Names should be equal!")
        self.assertEqual(options.TemplateGuid, fake_options.TemplateGuid,
                         "Template guids should be equal!")
        self.assertEqual(options.Domain, fake_options.Domain,
                         "Domains should be equal!")
        self.assertEqual(options.SourceLanguageCode, fake_options.SourceLanguageCode,
                         "Source language codes should be equal!")

    def test_create_project_from_template(self):
        """ Test for create_project_from_template method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]

        test.create_project_from_template(self.config["project_template_guid"])

        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        test.delete()

    def test_project_options(self):
        """ Test for project_options method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        options = test.project_options()

        fake_options = test.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}ServerProjectDesktopDocsCreateInfo')
        fake_options.Name = test.project.name
        fake_options.SourceLanguageCode = test.project.languages.source
        fake_options.TargetLanguageCodes.string = test.project.languages.target
        fake_options.Deadline = test.project.deadline
        fake_options.RecordVersionHistory = True
        fake_options.CreatorUser = self.config["creator_guid"]

        self.assertEqual(options.Name, fake_options.Name,
                         "Names should be equal!")
        self.assertEqual(options.TargetLanguageCodes.string, fake_options.TargetLanguageCodes.string,
                         "Target languages should be equal!")
        self.assertEqual(options.Deadline, fake_options.Deadline,
                         "Deadlines should be equal!")
        self.assertEqual(options.SourceLanguageCode, fake_options.SourceLanguageCode,
                         "Source language codes should be equal!")
        self.assertEqual(options.CreatorUser, fake_options.CreatorUser,
                         "Creators should be equal!")

    def test_create_project(self):
        """ Test for create_project method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()

        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        test.delete()

    def test_import_document(self):
        """ Test for import_document method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        test.delete()

    def test_get_project_documents(self):
        """ Test for get_project_documents method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        filename = os.path.basename(self.config["test_file_path"])
        test.get_project_documents()
        self.assertEqual(test.documents[0][0].DocumentName,
                         filename, "Name of document doesn't match test filename!")

        test.delete()

    def test_export_documents(self):
        """ Test for export_documents method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        filename = os.path.basename(self.config["test_file_path"])
        test.get_project_documents()
        self.assertEqual(test.documents[0][0].DocumentName,
                         filename, "Name of document doesn't match test filename!")

        export_result = test.export_documents(".")
        self.assertTrue(export_result, "Export result should be true!")

        test.delete()

    def test_export_documents2(self):
        """ Test for export_documents2 method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        filename = os.path.basename(self.config["test_file_path"])
        test.get_project_documents()
        self.assertEqual(test.documents[0][0].DocumentName,
                         filename, "Name of document doesn't match test filename!")

        export_result = test.export_documents2(".")
        self.assertTrue(export_result, "Export result should be true!")

        test.delete()

    def test_statistics_options(self):
        """ Test for statistics_options method."""
        test = memoQProject.MemoQProject()

        fake_options = test.client.factory.create(
            '{http://kilgray.com/memoqservices/2007}StatisticsOptions')
        fake_options.Analysis_ProjectTMs = True
        fake_options.Analysis_Homogenity = True
        fake_options.ShowResultsPerFile = True
        fake_options.RepetitionPreferenceOver100 = True
        statistics_algorithm = test.client.factory.create(
            '{http://schemas.datacontract.org/2004/07/MemoQServices}StatisticsAlgorithm')
        fake_options.Algorithm.value = statistics_algorithm.MemoQ

        options = test.statistics_options()
        self.assertEqual(fake_options.Analysis_ProjectTMs, options.Analysis_ProjectTMs,
                         "Project TMs option shouldn't be different!")
        self.assertEqual(fake_options.Analysis_Homogenity, options.Analysis_Homogenity,
                         "Analysis Homogenity option shouldn't be different!")
        self.assertEqual(fake_options.Algorithm.value, options.Algorithm.value,
                         "Algorithm value shouldn't be different!")

    def test_run_statistics(self):
        """ Test for run_statistics method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        statistics = test.run_statistics()
        self.assertNotEqual(statistics, None, "Statistics shouldn't be none!")

        test.delete()

    def test_save_statistics(self):
        """ Test for save_statistics method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        result = test.import_document(self.config["test_file_path"])
        self.assertTrue(result, "Result should be true!")

        file_path = test.save_statistics(".")
        self.assertTrue(os.path.isfile(file_path), "File should exist!")

        os.remove(file_path)
        test.delete()

    def test_delete(self):
        """ Test for delete method."""
        test = memoQProject.MemoQProject()
        test.project.languages.source = self.config["source_language"]
        test.project.languages.target = self.config["target_languages"]

        test.create_project()
        self.assertNotEqual(test.project.get_project_guid(),
                            None, "Guid shouldn't be none!")

        guid = test.project.get_project_guid()

        test.delete()
        test.get_project_by_guid(guid)
        self.assertNotEqual(test.project.get_project_guid(),
                            guid, "Guids don't match!")


if __name__ == "__main__":
    unittest.main()
