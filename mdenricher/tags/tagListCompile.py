#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def tagListCompile(self, details):

    # Create a list of tags for content that will show and a list of tags for content that will hidden

    # import json  # for sending data with and parsing data from requests
    # import os  # for running OS commands like changing directories or listing files in directory

    from mdenricher.errorHandling.errorHandling import addToWarnings
    from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    # self.log.debug('\n')
    # self.log.debug('----------------------------------')
    # self.log.debug('Tag list and display settings for ' + self.location_name + ':')
    # self.log.debug('----------------------------------')

    self.tags_show.append('all')
    self.tags_hide.append('hidden')

    if 'all' not in self.all_tags:
        self.all_tags.append('all')
    if 'hidden' not in self.all_tags:
        self.all_tags.append('hidden')

    # Get the feature flags and replace them with staging/prod tags to be dealt with later in this script
    if not details["featureFlags"] == 'None':

        for featureFlag in details["featureFlags"]:
            featureFlagName = featureFlag["name"]
            self.all_tags.append(featureFlagName)

            if details["featureFlags"].count(featureFlag) > 1:
                addToErrors('Check for duplicate "' + featureFlagName + '" flags in the feature flag file.', details["featureFlagFile"],
                            '', details, self.log, self.location_name, featureFlagName, str(details["featureFlags"]))

            if ' ' in featureFlagName:
                addToErrors('Feature flags cannot include spaces: ' + featureFlagName, details["featureFlagFile"],
                            '', details, self.log, self.location_name, featureFlagName, str(details["featureFlags"]))

            try:
                featureFlagDisplay = featureFlag['location']
            except Exception as e:
                addToWarnings('No location value for the ' + featureFlagName + ' feature flag to parse' +
                              str(e), details["featureFlagFile"], '', details, self.log, self.location_name,
                              featureFlagName, str(details["featureFlags"]))
            else:

                if type(featureFlagDisplay) is str:
                    self.log.debug('Location value for ' + featureFlagName + ': ' + featureFlagDisplay)

                    try:
                        featureFlagDisplay
                    except Exception:
                        addToErrors('No location value for the ' + featureFlagName, details["featureFlagFile"], '',
                                    details, self.log, self.location_name, featureFlagName, str(details["featureFlags"]))
                    else:
                        if ', ' in featureFlagDisplay:
                            featureFlagDisplay = featureFlagDisplay.replace(', ', ',')
                        if ',' in featureFlagDisplay:
                            featureFlagDisplayList = featureFlagDisplay.split(',')
                        else:
                            featureFlagDisplayList = [featureFlagDisplay]

                        # Get all of the show tags for each entry in the feature flag files
                        featureFlagShow = False
                        for featureFlagDisplayEntry in featureFlagDisplayList:

                            if (featureFlagDisplayEntry not in details['location_tags'] and
                                    not featureFlagDisplayEntry == 'hidden' and
                                    not featureFlagDisplayEntry == 'enabled' and
                                    not featureFlagDisplayEntry == 'unprocessed' and
                                    not featureFlagDisplayEntry == 'disabled' and
                                    not featureFlagDisplayEntry == 'all'):
                                addToErrors('The `' + featureFlagDisplayEntry + '` location specified for the `' + featureFlagName +
                                            '` feature flag does not exist in the locations file. The available locations are: `' +
                                            ', '.join(details['location_tags']) + '`', details["featureFlagFile"], '', details, self.log, self.location_name,
                                            featureFlagName, str(details["featureFlags"]))

                            if featureFlagDisplayEntry == 'unprocessed':
                                self.tags_ignore.append(featureFlagName)

                            elif featureFlagDisplayEntry == 'all' or featureFlagDisplayEntry == 'enabled':
                                if featureFlagName not in self.tags_show:
                                    self.tags_show.append(featureFlagName)
                                    featureFlagShow = True

                            elif featureFlagDisplayEntry == 'hidden' or featureFlagDisplayEntry == 'disabled':
                                if featureFlagName not in self.tags_hide:
                                    self.tags_hide.append(featureFlagName)

                            elif featureFlagName not in self.tags_show and featureFlagDisplayEntry == self.location_name:
                                if featureFlagName not in self.tags_show:
                                    self.tags_show.append(featureFlagName)
                                    featureFlagShow = True

                        if ((featureFlagShow is False) and
                                (not featureFlagName == self.location_name) and
                                (featureFlagName not in self.tags_hide) and
                                (featureFlagName not in self.tags_ignore)):
                            self.tags_hide.append(featureFlagName)
                else:
                    featureFlagDisplay = featureFlag['location'][self.location_name]
                    if featureFlagDisplay == 'hidden' or featureFlagDisplay == 'disabled':
                        if featureFlagName not in self.tags_hide:
                            self.tags_hide.append(featureFlagName)
                    else:
                        if featureFlagName not in self.tags_show:
                            self.tags_show.append(featureFlagName)

    else:
        self.log.debug('No feature flag to work with: ' + details["featureFlagFile"])

    # If there's special handling for a folder, append that as a tag name
    for directory in self.location_contents_folders_keep:
        directory = directory.replace('/', '')
        if directory != 'None':
            if directory not in self.tags_show:
                self.tags_show.append(directory)

    for directory in self.location_contents_folders_remove:
        directory = directory.replace('/', '')
        if directory != 'None':
            if ((directory not in self.tags_hide) and (directory not in self.tags_show)):
                self.tags_hide.append(directory)

    for location_tag in details['location_tags']:
        if (location_tag not in self.tags_show) and (location_tag not in self.tags_hide):
            if (location_tag == self.location_name):
                self.tags_show.append(self.location_name)
            else:
                self.tags_hide.append(location_tag)

    TAGS_SHOW_STRING = ", ".join(sorted(self.tags_show))
    self.log.debug(self.location_name + ' tags_show: ' + TAGS_SHOW_STRING)
    TAGS_HIDE_STRING = ", ".join(sorted(self.tags_hide))
    self.log.debug(self.location_name + ' tags_hide: ' + TAGS_HIDE_STRING)

    return (self)
