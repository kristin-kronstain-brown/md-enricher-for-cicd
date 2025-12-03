#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def metadata(self, details, file_name, firstAnchor, folderAndFile, folderPath, topicContents):

    # Replace the metadata variables
    # Retrieve the dates from the previous version of the file, if possible, to get an accurate changed file list

    # import os
    import re  # for doing finds within the topic content
    import yaml

    from mdenricher.errorHandling.errorHandling import addToErrors

    # Rather than us using our own metadata attributes list, we'll use the core team's. After everyone stops using this conref, remove this section.
    if '[{METADATA_ATTRIBUTES}]' in topicContents:
        topicContents = topicContents.replace('[{METADATA_ATTRIBUTES}]', '{{site.data.keyword.attribute-definition-list}}')
        self.log.debug(r'Replaced [{METADATA_ATTRIBUTES}] with {{site.data.keyword.attribute-definition-list}}.')

    # This is for Blockchain's version links at the beginning of each file
    if '{[FIRST_ANCHOR]}' in topicContents:
        topicContents = topicContents.replace('{[FIRST_ANCHOR]}', firstAnchor)
        self.log.debug(r'Replaced [{FIRST_ANCHOR}] with ' + firstAnchor + '.')

    if 'qna:' in topicContents and folderAndFile.endswith('.md'):
        try:
            # Get just the metadata from the topic contents
            metadataStringOriginal = str(topicContents).split('---')[1]
            # Escape the quotation marks to make sure they don't get lost in the conversion
            metadataString = metadataStringOriginal.replace('"', '\\"')
            # Load the string as YAML
            metadataYAML = yaml.safe_load(metadataString)
            self.log.debug(metadataYAML)

            # Validate qna ID match with context tag or anchor ID
            qnaSection = metadataYAML['qna']
            for qnaID in qnaSection:
                if '<qna:' + qnaID + '>' in topicContents or '{: #' + qnaID + '}' in topicContents:
                    self.log.debug('Valid qna ID: ' + qnaID)
                else:
                    addToErrors('A context section ID could not be found to match the qna ID: ' + qnaID,
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')

            qnaOpenIDs = re.findall('<qna:(.*?)>', topicContents)
            qnaOpenIDsUnique = list(dict.fromkeys(qnaOpenIDs))

            qnaClosingIDs = re.findall('</qna:(.*?)>', topicContents)
            qnaClosingIDsUnique = list(dict.fromkeys(qnaClosingIDs))

            for qnaID in qnaOpenIDsUnique:
                openCount = qnaOpenIDsUnique.count(qnaID)
                closedCount = qnaClosingIDsUnique.count(qnaID)

                if openCount > closedCount:
                    addToErrors('Missing closing qna tag: <qna:' + qnaID + '>',
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')
                elif openCount < closedCount:
                    addToErrors('Missing open qna tag: </qna:' + qnaID + '>',
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')

                if qnaID not in qnaSection:
                    addToErrors('qna context tag used but topic metadata does not include the qna key: <qna:' + qnaID + '>',
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')

            for qnaID in qnaClosingIDsUnique:
                if qnaID not in qnaOpenIDsUnique:
                    addToErrors('Missing open qna tag: </qna:' + qnaID + '>',
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')

                if qnaID not in qnaSection:
                    addToErrors('qna context tag used but topic metadata does not include the qna key: </qna:' + qnaID + '>',
                                folderAndFile,
                                folderPath + file_name, details, self.log,
                                self.location_name, '', '')

            # Remove the qna key
            del metadataYAML['qna']
            self.log.debug('Removed qna section from metadata.')
            # Load the YAML as a string
            metadataFinalString = yaml.dump(metadataYAML, sort_keys=False, indent=2, width=1000)
            # Add new lines back in between the keys since most people format metadata that way
            for newLineKey in metadataYAML:
                metadataFinalString = metadataFinalString.replace(newLineKey + ':', '\n' + newLineKey + ':')
            # Remove the escaping from the quotation marks
            metadataFinalString = metadataFinalString.replace('\\"', '"')
            # Replace the original metadata with this reformatted metadata
            topicContents = topicContents.replace(metadataStringOriginal, '\n' + metadataFinalString + '\n')
            self.log.debug('qna removed from metadata.')

            for qnaID in qnaSection:
                if '<qna:' + qnaID + '>' in topicContents:
                    topicContents = topicContents.replace('<qna:' + qnaID + '>', '<!--<qna:' + qnaID + '>-->')
                if '</qna:' + qnaID + '>' in topicContents:
                    topicContents = topicContents.replace('</qna:' + qnaID + '>', '<!--</qna:' + qnaID + '>-->')

        except Exception as e:
            self.log.debug(e)
            self.log.debug('qna section of the metadata could not be handled.')

    return (topicContents)
