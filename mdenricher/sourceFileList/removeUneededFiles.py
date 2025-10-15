#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def removeUneededFiles(self, details):

    import os
    import shutil
    # from mdenricher.errorHandling.errorHandling import addToWarnings

    # Check for these directories and delete them to avoid accidental pushes
    directories_to_delete = ['/source']
    for folder in self.location_contents_folders_remove:
        directories_to_delete.append(folder)

    # Should these be within the location_dir or the output_dir
    for directory_to_delete in directories_to_delete:
        if not directory_to_delete.startswith('/') and not directory_to_delete.startswith('includes'):
            directory_to_delete = '/' + directory_to_delete
        if os.path.isdir(self.location_dir + directory_to_delete):
            self.log.debug('Deleted: ' + self.location_dir + directory_to_delete)
            shutil.rmtree(self.location_dir + directory_to_delete)

    if details['ibm_cloud_docs'] is True and self.location_tag_processing == 'on':

        try:
            self.all_files_dict['/toc.yaml']['fileContents_output']
            testExistenceInTOC = True
        except Exception:
            testExistenceInTOC = False
        ignoredFileList = ['/.build.yaml', '/.pre-commit-config.yaml', '/.travis.yml',
                           '/CODEOWNERS', '/conref.md',
                           '/ignoreLinks.txt', '/glossary/glossary.json', 'Jenkinsfile', '/keyref.yaml',
                           '/landing.json', '/readme.md', '/README.md', '/toc.yaml', '/user-mapping.json']
        ignoredFolderList = ['/.github/', '/_include-segments/']

        if not self.location_tag_processing == "on":
            ignoredFileList.append(details["featureFlagFile"])

        for (path, dirs, files) in os.walk(self.location_dir):
            if self.location_dir == path:
                folder = '/'
            else:
                folder = path.split(self.location_dir)[1]
                if not folder.endswith('/'):
                    folder = folder + '/'
                if not folder.startswith('/'):
                    folder = '/' + folder
            for file in sorted(files):
                # folderAndFile = folder + file
                try:
                    if (('.git' not in path) and
                            ('.git' not in file) and
                            ((file) not in self.expected_output_files) and
                            ((folder + file) not in self.expected_output_files) and
                            ((folder[1:] + file) not in self.expected_output_files) and
                            ((file.endswith(tuple(details["filetypes"]))) or ((file.endswith(tuple(details["img_output_filetypes"]))))) and
                            (self.location_tag_processing == "on") and
                            (os.path.isfile(path + '/' + file)) and
                            (not folder + file in ignoredFileList) and
                            (not (folder.startswith(tuple(ignoredFolderList))))):
                        os.remove(path + '/' + file)
                        self.log.info('Removing unused file from ' + self.location_name + ': ' + folder + file)

                    elif ((testExistenceInTOC is True) and
                            ('.git' not in path) and
                            ('.git' not in file) and
                            (not (path + '/' + file) == details['locations_file']) and
                            file.endswith(tuple(details["filetypes"])) and
                            (not (' ' + folder + file) in self.all_files_dict['/toc.yaml']['fileContents_output']) and
                            (not (' ' + folder[1:] + file) in self.all_files_dict['/toc.yaml']['fileContents_output']) and
                            (details['reuse_snippets_folder'] not in folder) and
                            (not '/' + file in ignoredFileList) and
                            ('conref' not in file and not file.endswith('.yaml') and not file.endswith('.yml')) and
                            (not folder + file in ignoredFileList) and
                            (not (folder.startswith(tuple(ignoredFolderList))))):
                        self.log.info('The file is not used in the ' + self.location_name +
                                      ' toc.yaml so it is not included downstream: ' + folder + file)
                        if os.path.isfile(path + '/' + file):
                            # Most likely removing a file that was generated this build, but not pushed before
                            os.remove(path + '/' + file)
                            self.log.debug('Removing undefined file from ' + self.location_name + ': ' + folder + file)
                    elif ((not file.endswith(tuple(details["filetypes"]))) and
                            ((not file.endswith(tuple(details["img_output_filetypes"])))) and
                            ('.git' not in path) and
                            (not '/' + file not in ignoredFileList) and
                            ('.git' not in file) and
                            (not folder + file in ignoredFileList) and
                            (not (folder.startswith(tuple(ignoredFolderList))))):
                        if os.path.isfile(path + '/' + file):
                            os.remove(path + '/' + file)
                            self.log.info('Removing file of unsupported type from ' + self.location_name + ': ' + folder + file)
                except Exception as e:
                    self.log.error('Traceback')
                    self.log.error('Could not issue warning for or remove: ' + folder + file)
                    self.log.error(e)

            if details['rebuild_all_files'] is True or details['builder'] == 'local':
                if (('.git' not in path) and
                        (not folder.startswith(tuple(self.expected_output_files))) and
                        (not folder.startswith(tuple(ignoredFolderList)))):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                        self.log.info('Removing old folder from ' + self.location_name + ': ' + folder)
