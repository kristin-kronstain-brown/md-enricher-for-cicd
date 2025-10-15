def tocTagHandling(self, details, topicContentsNoTags):

    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.errorHandling.errorHandling import addToWarnings
    import copy

    all_files_revised = copy.deepcopy(self.all_files_dict)

    for source_file in self.all_files_dict:
        if (('_include-segments' not in source_file) and
                ('reuse-snippets' not in source_file) and
                ('README' not in source_file) and
                ('conref.md' not in source_file) and
                (source_file.endswith('.md'))):
            try:
                downstreamFolderAndFile = self.all_files_dict[source_file]['folderPath'][1:] + self.all_files_dict[source_file]['file_name']
                if ('- ' + downstreamFolderAndFile in topicContentsNoTags) or ('topic: ' + downstreamFolderAndFile in topicContentsNoTags):
                    self.log.debug(self.location_name + ' show: ' + self.all_files_dict[source_file]['folderAndFile'])
                else:
                    self.log.debug(self.location_name + ' hide: ' + self.all_files_dict[source_file]['folderAndFile'])
                    originalFileContents = all_files_revised[source_file]['fileContents']
                    all_files_revised[source_file]['fileContents'] = '<hidden>' + originalFileContents + '</hidden>'
            except Exception as e:
                self.log.debug(e)
                self.log.debug('Failed: ' + source_file)

    return (all_files_revised)
