#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def cleanupEachFile(self, details):

    try:

        # Loop through every file in the files for this location and do the tag and reuse replacements

        import json
        import os  # for running OS commands like changing directories or listing files in directory
        import re
        import shutil
        import time

        from mdenricher.errorHandling.errorHandling import addToWarnings
        from mdenricher.errorHandling.errorHandling import addToErrors
        from mdenricher.cleanupEachFile.writeResult import writeResult
        from mdenricher.sitemap.sitemapOLD import sitemapOLD
        from mdenricher.sitemap.sitemapYML import sitemapYML
        from mdenricher.sitemap.sitemapSUMMARY import sitemapSUMMARY
        from mdenricher.sourceFileList.tocTagHandling import tocTagHandling
        # from mdenricher.setup.exitBuild import exitBuild

        def fileHandlingDecisions(self, source_file, source_files):
            if self.all_files_dict[source_file]['locationHandling'] == 'remove':
                if os.path.isfile(self.location_dir + source_files[source_file]['folderPath'] + source_files[source_file]['file_name']):
                    os.remove(self.location_dir + source_files[source_file]['folderPath'] + source_files[source_file]['file_name'])
                    self.log.debug('Removing ' + source_file + ' from the ' +
                                   self.location_name + ' location.')
                else:
                    self.log.debug(source_file + ' is set to be removed from the ' +
                                   self.location_name + ' location, but it already did not exist downstream.')
            else:
                try:

                    if details['debug'] is True:
                        startTimeFile = time.time()

                    folderAndFile = source_files[source_file]['folderAndFile']
                    file_name = source_files[source_file]['file_name']
                    folderPath = source_files[source_file]['folderPath']
                    fileStatus = source_files[source_file]['fileStatus']
                    fileNamePrevious = source_files[source_file]['fileNamePrevious']
                    locationHandling = source_files[source_file]['locationHandling']
                    try:
                        topicContents = self.all_files_dict[source_file]['fileContents']
                    except Exception:
                        try:
                            topicContents = source_files[source_file]['fileContents']
                        except Exception:
                            topicContents = ''
                            self.log.debug('No topic contents.')

                    if ((self.location_tag_processing == "off") and
                            (not file_name.endswith(tuple(details["img_output_filetypes"])))):

                        if not os.path.isdir(self.location_dir + folderPath):
                            os.makedirs(self.location_dir + folderPath)

                        self.log.debug('\n\n')
                        self.log.debug('----------------------------------')
                        self.log.debug(folderAndFile)
                        self.log.debug('(' + self.location_name + ')')
                        self.log.debug('----------------------------------')
                        self.log.debug('(folderAndFile=' + folderAndFile + ',folderPath=' + folderPath + ',file_name=' + file_name +
                                       ',fileStatus=' + fileStatus + ',fileNamePrevious=' + fileNamePrevious +
                                       ',locationHandling=' + locationHandling + ')')
                        if os.path.isfile(self.location_dir + folderPath + file_name):
                            os.remove(self.location_dir + folderPath + file_name)
                            self.log.debug('Removing previous version of the file.')

                        if folderAndFile == details['featureFlagFile']:
                            featureFlagContents = json.loads(source_files[source_file]['fileContents'])
                            newFeatureFlagContents = []
                            for entry in featureFlagContents:
                                try:
                                    entryName = entry['name']
                                    try:
                                        locationJSON = entry['location'][self.location_name]
                                    except Exception:
                                        locationJSON = entry['location']
                                    newFeatureFlagContents.append({
                                        "name": entryName,
                                        "location": locationJSON
                                    })
                                except Exception as e:
                                    self.log.debug(e)
                                    addToErrors('Could not revise unprocessed feature flag file: ' + entryName,
                                                folderAndFile,
                                                folderPath + file_name, details, self.log,
                                                self.location_name, '', '')
                                    break
                            topicContentsJSON = json.dumps(newFeatureFlagContents, indent=2)
                            writeResult(self, details, file_name, folderAndFile, folderPath, topicContentsJSON)

                        else:
                            if os.path.isfile(details['source_dir'] + folderAndFile):
                                shutil.copyfile(details['source_dir'] + folderAndFile, self.location_dir + folderPath + file_name)
                                self.log.debug('Copied downstream without processing.')
                            else:
                                self.log.debug('Upstream version was deleted, so downstream version was deleted.')

                    elif file_name.endswith(tuple(details["img_output_filetypes"])):
                        self.log.debug('\n\n')
                        self.log.debug('----------------------------------')
                        self.log.debug(folderAndFile)
                        self.log.debug('(' + self.location_name + ')')
                        self.log.debug('----------------------------------')
                        self.log.debug('(folderAndFile=' + folderAndFile + ',folderPath=' + folderPath + ',file_name=' + file_name +
                                       ',fileStatus=' + fileStatus + ',fileNamePrevious=' + fileNamePrevious + ')')
                        if fileStatus == 'renamed':
                            if os.path.isfile(self.location_dir + fileNamePrevious):
                                os.remove(self.location_dir + fileNamePrevious)
                                self.log.debug(source_file + ' was renamed in the upstream repo. Deleting ' +
                                               fileNamePrevious + ' from ' + self.location_name + ' as well.')
                        elif fileStatus == 'deleted':
                            if os.path.isfile(self.location_dir + folderPath + file_name):
                                os.remove(self.location_dir + folderPath + file_name)
                                self.log.debug(source_file + ' was removed in the upstream repo. Deleting ' +
                                               folderPath + file_name + ' from ' + self.location_name + ' as well.')
                        elif details['images_include_always'] is True or (details['ibm_cloud_docs'] is True and details['source_github_repo'] == 'icons'):
                            if os.path.isfile(self.location_dir + folderPath + file_name):
                                os.remove(self.location_dir + folderPath + file_name)
                            if 'keep' in self.all_files_dict[folderAndFile]['locationHandling']:
                                if not os.path.isdir(self.location_dir + folderPath):
                                    os.makedirs(self.location_dir + folderPath)
                                shutil.copyfile(details['source_dir'] + folderAndFile, self.location_dir + folderPath + file_name)
                            self.log.debug('Copying image downstream.')
                        elif details['images_include_always'] is False:
                            self.log.debug('Images handled at the end of the build.')

                    elif file_name.endswith(tuple(details["filetypes"])):

                        self.log.debug('\n\n')
                        self.log.debug('----------------------------------')
                        self.log.debug(folderAndFile)
                        self.log.debug('(' + self.location_name + ')')
                        self.log.debug('----------------------------------')
                        self.log.debug('(folderAndFile=' + folderAndFile + ',folderPath=' + folderPath + ',file_name=' + file_name +
                                       ',fileStatus=' + fileStatus + ',fileNamePrevious=' + fileNamePrevious + ')')

                        if details["reuse_snippets_folder"] in folderAndFile:
                            self.log.debug('Not handling ' + details["reuse_snippets_folder"] + ' individually.')
                        else:

                            # Check the file status for 'renamed' and if so, use the fileNamePrevious to remove the old version of
                            # the file from the downstream repo. This can't be a part of the following if/elif because the new
                            # file still should be handled.
                            if 'renamed' in fileStatus:
                                self.log.debug('Rename detected in the file status for ' + source_file + '.')
                                if fileNamePrevious == 'None':
                                    addToWarnings(source_file + ' was renamed, but the previous file name could not be found, so the ' +
                                                  'previous version of the file could not be removed from the downstream repo.',
                                                  folderAndFile, folderPath + file_name, details, self.log, self.location_name, '', '')
                                else:
                                    try:
                                        if os.path.isfile(self.location_dir + fileNamePrevious):
                                            os.remove(self.location_dir + fileNamePrevious)
                                            self.log.debug(source_file + ' was renamed in the upstream repo. Deleting ' +
                                                           fileNamePrevious + ' from ' + self.location_name + ' as well.')
                                    except Exception:
                                        addToWarnings(fileNamePrevious + ' could not be found, so the previous version of the file ' +
                                                      'could not be removed from the downstream repo.', folderAndFile,
                                                      folderPath + file_name, details, self.log,
                                                      self.location_name, '', '')

                            # Check the file status for 'removed'.
                            # If the file was removed from upsteam or set to be removed by the locations file, remove it from this location too
                            if 'removed' in fileStatus:
                                if os.path.isfile(self.location_dir + folderPath + file_name):
                                    os.remove(self.location_dir + folderPath + file_name)
                                    self.log.debug('Removing ' + source_file + ' from the ' +
                                                   self.location_name + ' location.')
                                else:
                                    self.log.debug(source_file + ' is set to be removed from the ' +
                                                   self.location_name + ' location, but it already did not exist downstream.')

                            # If the file is a text file in the supported text file list, then run the filecleanup loop at the top of the file over it
                            elif file_name.endswith(tuple(details["filetypes"])):

                                # The filepaths are the differences between these two sections
                                # If the subdirectory, doesn't exist in the downstream repo, create it
                                if not os.path.isdir(self.location_dir + folderPath):
                                    try:
                                        os.makedirs(self.location_dir + folderPath)
                                    except Exception:
                                        if os.path.isfile(self.location_dir + folderPath):
                                            os.remove(self.location_dir + folderPath)
                                            os.makedirs(self.location_dir + folderPath)
                                        if not os.path.isdir(self.location_dir + folderPath):
                                            addToErrors('Could not create directory: ' + self.location_dir + folderPath,
                                                        folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                                                        '', '')

                                if not os.path.isdir(self.location_dir + folderPath):
                                    self.log.debug('Folder does not exist in working dir: ' + self.location_dir + folderPath)
                                try:
                                    self.all_files_dict = fileCleanUpLoop(self, details, conrefJSON, file_name, folderAndFile, folderPath, topicContents)
                                except Exception as e:
                                    self.log.debug(str(e))
                                    self.log.debug('folderAndFile = ' + folderAndFile)
                                    self.log.debug('file_name = ' + file_name)
                                    self.log.debug('folderPath = ' + folderPath)
                                    self.log.debug('fileNamePrevious = ' + fileNamePrevious)

                    if details['debug'] is True:
                        endTime = time.time()
                        totalTime = endTime - startTimeFile
                        wholeFileTime = str(round(totalTime, 2))
                        self.log.info(source_file + ': ' + wholeFileTime)

                except Exception as e:
                    addToErrors('Could not complete processing for ' + folderAndFile + ': ' + str(e),
                                folderAndFile, folderPath + file_name, details, self.log, self.location_name,
                                '', '')
            return (self.all_files_dict)

        def fileCleanUpLoop(self, details, conrefJSON, file_name, folderAndFile, folderPath, topicContents):

            # Get first topic ID
            try:
                allAnchors = re.findall('{: #(.*)}', topicContents)
                firstAnchor = allAnchors[0]
                # self.log.debug('First anchor: ' + firstAnchor)
            except Exception:
                # self.log.debug('No anchors in the page.')
                firstAnchor = '{[FIRST_ANCHOR]}'

            if details['debug'] is True:
                startTime = time.time()

            # Replace all of the conrefs in this file
            if os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/'):
                # Replace the conref files first
                if '.md]}' in topicContents:
                    # If they exist, replace all of the .md conrefs in the conref file
                    from mdenricher.conrefs.wholeFileConrefs import wholeFileConrefs
                    topicContents = wholeFileConrefs(self, details, file_name, folderAndFile, folderPath, topicContents)
                # Replace the conref phrases
                if not str(details["reuse_phrases_file"]) in file_name:
                    # Don't look for conref phrases in the conref phrases file or else it will replace the IDs that we need!!!
                    if ((']}' in topicContents) or ('{[' in topicContents)):
                        from mdenricher.conrefs.inlineConrefs import inlineConrefs
                        topicContents = inlineConrefs(self, details, conrefJSON,
                                                      file_name, folderAndFile, folderPath, topicContents)
                    else:
                        self.log.debug('No inline snippets to handle.')

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                reuseTime = str(round(totalTime, 2))

            if details['debug'] is True:
                startTime = time.time()

            from mdenricher.tags.tagRemoval import tagRemoval
            topicContents, self.all_files_dict = tagRemoval(self, details, folderAndFile, topicContents)

            if (('/toc.yaml' in self.all_files_dict) and
                    ('toc.yaml' in folderAndFile) and
                    (details['ibm_cloud_docs'] is True) and
                    ('<' in self.all_files_dict['/toc.yaml']['fileContents'])):  # type: ignore
                self.log.debug('Found tags in toc.yaml')
                self.all_files_dict = tocTagHandling(self, details, topicContents)

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                tagRemovalTime = str(round(totalTime, 2))

            if details['debug'] is True:
                startTime = time.time()

            if (('{{' in topicContents) and (details["ibm_cloud_docs_keyref_check"] is True)):
                from mdenricher.errorHandling.keyrefCheck import keyrefCheck
                keyrefCheck(self, details, file_name, folderAndFile, folderPath, topicContents)

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                keyrefCheckTime = str(round(totalTime, 2))

            if details['debug'] is True:
                startTime = time.time()
            if '```\n    ```' in topicContents:
                # Tested 1/6/21
                addToWarnings('Empty codeblock. This issue can fail the markdown processor and prevent this file and any ' +
                              'file after it from being handled by the markdown processor. Verify that the removal of tags in ' +
                              'the codeblock aren\'t leaving behind the empty codeblock.', folderAndFile, folderPath + file_name, details, self.log,
                              self.location_name, '```\n    ```', topicContents)

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                codeblockTime = str(round(totalTime, 2))

            if details['debug'] is True:
                startTime = time.time()
            if os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"]):
                from mdenricher.images.imagesCheckRelativePaths import imagesCheckRelativePaths
                topicContents = imagesCheckRelativePaths(self, details, file_name, folderAndFile, folderPath, topicContents)
            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                imagesCheckRelativePathsTime = str(round(totalTime, 2))

            if details['debug'] is True:
                startTime = time.time()
            from mdenricher.cleanupEachFile.metadata import metadata
            topicContents = metadata(self, details, file_name, firstAnchor, folderAndFile, folderPath, topicContents)

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                metadataTime = str(round(totalTime, 2))

            if file_name == 'toc.yaml':
                topicContentsList = topicContents.split('\n')
                for line in topicContentsList:
                    if (line.isspace() is True) or (line == ''):
                        topicContentsList.remove(line)
                topicContents = "\n".join(topicContentsList)

            if folderPath + file_name == self.sitemap_file:

                if details['debug'] is True:
                    startTime = time.time()

                # If there is a sitemap.md, populate it with links
                # This needs to happen after comments are handled
                if (not details["ibm_cloud_docs_sitemap_depth"] == 'off') and self.location_tag_processing == "on":
                    if 'toc.yaml' in str(self.all_files_dict) and self.location_ibm_cloud_docs is True:
                        topicContents = sitemapYML(self, details, topicContents)

                    elif 'SUMMARY.md' in str(self.all_files_dict):
                        topicContents = sitemapSUMMARY(self, details, topicContents)

                    elif (('toc' in str(self.all_files_dict)) and ('toc.yaml' not in str(self.all_files_dict))):
                        topicContents = sitemapOLD(self, details, topicContents)

                    else:
                        addToWarnings('A toc.yaml file does not exist, so the sitemap could not be built.',
                                      'toc.yaml', '', details, self.log, 'pre-build', '', '')

                if details['debug'] is True:
                    endTime = time.time()
                    totalTime = endTime - startTime
                    sectionTime = str(round(totalTime, 2))
                    self.log.info(self.location_name + ' sitemap: ' + sectionTime)

            if details['debug'] is True:
                startTime = time.time()
            writeResult(self, details, file_name, folderAndFile, folderPath, topicContents)
            if folderAndFile == '/toc.yaml':
                self.all_files_dict['/toc.yaml']['fileContents_output'] = topicContents

            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                writeTime = str(round(totalTime, 2))

            if folderAndFile.endswith('.json'):
                from mdenricher.errorHandling.jsonCheck import jsonCheck
                jsonCheck(details, self.log, 'True', [folderPath + file_name], self.location_dir)

            if (folderAndFile.endswith('.yaml')) or (folderAndFile.endswith('.yml')):
                from mdenricher.errorHandling.ymlCheck import ymlCheck
                ymlCheck(self, details, 'True', [folderPath + file_name], [folderAndFile], self.location_dir, self.location_name)

            if details['debug'] is True:
                startTime = time.time()
            if '.json' not in folderAndFile:
                # Tag validation happens no matter what the value is for the --validation flag because tag errors impact output
                from mdenricher.tags.htmlValidator import htmlValidator
                htmlValidator(self, details, file_name, folderAndFile, folderPath, topicContents)
            if details['debug'] is True:
                endTime = time.time()
                totalTime = endTime - startTime
                htmlValidatorTime = str(round(totalTime, 2))

            if details['debug'] is True:
                self.log.debug('reuseTime: ' + reuseTime)
                self.log.debug('keyrefCheckTime: ' + keyrefCheckTime)
                self.log.debug('tagRemovalTime: ' + tagRemovalTime)
                self.log.debug('codeblockTime: ' + codeblockTime)
                self.log.debug('imagesCheckRelativePathsTime: ' + imagesCheckRelativePathsTime)
                self.log.debug('metadataTime: ' + metadataTime)
                self.log.debug('writeTime: ' + writeTime)
                self.log.debug('htmlValidatorTime: ' + htmlValidatorTime)

            return (self.all_files_dict)

        if self.source_files == {}:
            self.log.debug('No files to process for ' + self.location_name + '.')
        else:

            if os.path.isfile(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + str(details["reuse_phrases_file"])):
                # Open the conrefs file
                with open(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/' + details["reuse_phrases_file"],
                          'r', encoding="utf8", errors="ignore") as conrefTxtFile:
                    # Load the conrefs file as json
                    conrefTxt = conrefTxtFile.read()
                    conrefJSON = json.loads(conrefTxt)
            else:
                conrefJSON = ''

            # Start handling each file individually from the source_files dictionary
            sortedList = sorted(self.source_files.items())
            source_files = dict(sortedList)

            # Handle things like keyref and files to remove first
            for first_file in self.location_build_first:
                if first_file in source_files:
                    self.all_files_dict = fileHandlingDecisions(self, self.all_files_dict[first_file]['folderAndFile'], source_files)

            # Handle the majority of files
            for source_file, source_file_info in source_files.items():
                if (not self.all_files_dict[source_file]['folderAndFile'] in self.location_build_first and
                        not self.all_files_dict[source_file]['folderAndFile'] in self.location_build_last):
                    try:
                        fileToHandle = self.all_files_dict[source_file]['folderAndFile']
                    except Exception:
                        self.log.debug('Not cleaning up: ' + source_file)
                    else:
                        self.all_files_dict = fileHandlingDecisions(self, fileToHandle, source_files)

            # Handle things like the sitemap last
            for last_file in self.location_build_last:
                if last_file in source_files:
                    self.all_files_dict = fileHandlingDecisions(self, self.all_files_dict[last_file]['folderAndFile'], source_files)

    except Exception as e:
        addToErrors('Could not complete the file cleanup steps for ' + self.location_name + ': ' + str(e),
                    '', '', details, self.log, self.location_name, '', '')
        self.log.debug(e)
