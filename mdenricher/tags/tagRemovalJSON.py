#
# Copyright 2015, 2024 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def tagRemovalJSON(self, details, folderAndFile, topicContents):

    import json
    import yaml

    from mdenricher.errorHandling.errorHandling import addToErrors

    self.log.debug('Handling tags in JSON/YAML.')

    def remove_by_key_value(obj, key_name):

        # self.log.info('Object:')
        # self.log.info(type(obj))
        # self.log.info(obj)

        if isinstance(obj, dict):

            # Otherwise, recurse into each key
            new_obj = {}

            for k, v in obj.items():

                try:
                    key_value = str(obj[k][key_name])
                    if (key_value in self.tags_hide):
                        try:
                            self.log.debug('Hiding dictionary: ' + k)
                        except Exception:
                            pass
                        cleaned = None
                        # self.log.info('Hiding section: ' + key_value)
                        return cleaned
                    elif key_value not in self.all_tags:
                        addToErrors(key_value + ' is not a valid value for ' + key_name + ' in ' +
                                    self.location_name + ' ' + folderAndFile + '.',
                                    folderAndFile, folderAndFile, details, self.log, self.location_name,
                                    '', '')
                except Exception:
                    pass

                try:
                    key_value = str(obj[key_name])
                    if (key_value in self.tags_hide):
                        try:
                            self.log.debug('Hiding topic: ' + obj['topic'])
                        except Exception:
                            try:
                                self.log.debug('Hiding link: ' + obj['link'])
                            except Exception:
                                try:
                                    self.log.debug('Hiding link: ' + obj['include'])
                                except Exception:
                                    pass
                        cleaned = None
                        return cleaned
                    elif key_value not in self.all_tags:
                        addToErrors(key_value + ' is not a valid value for ' + key_name + ' in ' +
                                    self.location_name + ' ' + folderAndFile + '.',
                                    folderAndFile, folderAndFile, details, self.log, self.location_name,
                                    '', '')
                except Exception:
                    pass

                try:
                    key_value = str(k[key_name])
                    if key_value not in self.all_tags:
                        addToErrors(key_value + ' is not a valid value for ' + key_name + ' in ' +
                                    self.location_name + ' ' + folderAndFile + '.',
                                    folderAndFile, folderAndFile, details, self.log, self.location_name,
                                    '', '')
                    # self.log.info('Found: ' + key_value)
                except Exception:
                    # self.log.info('dict exception')
                    cleaned = remove_by_key_value(v, key_name)
                else:
                    if (key_value in self.tags_hide):
                        cleaned = None
                    elif key_value not in self.all_tags:
                        addToErrors(key_value + ' is not a valid value for ' + key_name + ' in ' +
                                    self.location_name + ' ' + folderAndFile + '.',
                                    folderAndFile, folderAndFile, details, self.log, self.location_name,
                                    '', '')
                    else:
                        cleaned = remove_by_key_value(v, key_name)

                if cleaned is not None and cleaned is not {}:
                    if not self.location_tag_processing == 'off' and not k == key_name:
                        new_obj[k] = cleaned

            if not new_obj == {}:
                return new_obj

        elif isinstance(obj, list):
            # Recurse through list items and remove any that match
            new_list = []
            for item in obj:
                try:
                    # Look for a parent like a topic group with a tag that makes the whole section hidden
                    for topicGroup in item:
                        key_value = str(item[topicGroup][key_name])
                        if (key_value in self.tags_hide):
                            try:
                                self.log.debug('Hiding topicgroup: ' + item[topicGroup]['label'])
                            except Exception:
                                try:
                                    self.log.debug('Hiding navgroup: ' + item[topicGroup]['id'])
                                except Exception:
                                    self.log.debug('Hiding list: ' + topicGroup)
                            cleaned = None
                        elif key_value not in self.all_tags:
                            addToErrors(key_value + ' is not a valid value for ' + key_name + ' in ' +
                                        self.location_name + ' ' + folderAndFile + '.',
                                        folderAndFile, folderAndFile, details, self.log, self.location_name,
                                        '', '')
                        else:
                            cleaned = remove_by_key_value(item, key_name)
                except Exception:
                    cleaned = remove_by_key_value(item, key_name)

                if cleaned is not None and cleaned is not []:
                    if (not self.location_tag_processing == 'off'):
                        new_list.append(cleaned)
            if not new_list == []:
                return new_list
        return obj

    try:
        topicContentsJSON = topicContents
        if folderAndFile.endswith('.json'):
            topicContentsJSON = json.loads(topicContents)
            topicContentsJSON = json.dumps(topicContentsJSON, sort_keys=False, indent=2, ensure_ascii=False)
        elif folderAndFile.endswith('.yaml') or folderAndFile.endswith('.yml'):
            flagNames = ['flag', 'tag', 'x-visible-environment']
            # Single TOC
            try:
                topicContentsJSON = yaml.safe_load(topicContents)
                for flagName in flagNames:
                    if '\'' + flagName + '\'' in str(topicContentsJSON):
                        topicContentsJSON = remove_by_key_value(topicContentsJSON, flagName)
            # Multi-document TOC with tags on entire toc keys
            except Exception:
                topicContentsJSONMulti = yaml.safe_load_all(topicContents)
                for topicContentsJSON in topicContentsJSONMulti:
                    for flagName in flagNames:
                        if '\'' + flagName + '\'' in str(topicContentsJSON):
                            topicContentsJSON = remove_by_key_value(topicContentsJSON, flagName)
                            break
                    if topicContentsJSON is not None:
                        break
                    topicContentsJSON = remove_by_key_value(topicContentsJSON, flagName)
            topicContentsJSON = yaml.dump(topicContentsJSON, default_flow_style=False, sort_keys=False, width=1000, allow_unicode=True)

    except Exception as e:
        if self.location_tag_processing == 'on':
            error = str(e)
            if ':' in error:
                error = error.split(':')[0]
            addToErrors('Formatting error: ' + str(e),
                        folderAndFile, folderAndFile, details, self.log, self.location_name,
                        '', '')

    return (str(topicContentsJSON), self.all_files_dict)
