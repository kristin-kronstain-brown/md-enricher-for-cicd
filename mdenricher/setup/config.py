#
# Copyright 2022 IBM Inc. All rights reserved
# SPDX-License-Identifier: Apache2.0
#

def config(log, details, locations_config):

    # Parse and validate the values in the config section of the locations file

    # from mdenricher.errorHandling.errorHandling import addToWarnings
    # from mdenricher.errorHandling.errorHandling import addToErrors
    # from mdenricher.setup.exitBuild import exitBuild

    import os
    import subprocess

    # Get the source branch from the config info
    try:
        source_github_branch = locations_config["source_github_branch"]
    except KeyError:
        source_github_branch = 'None'

    try:
        # If the clone happens without auth, then this command won't work.
        os.chdir(details['source_dir'])
        branches = []
        branchResponse = subprocess.check_output(['git ls-remote --heads --quiet'], stderr=subprocess.STDOUT, shell=True)
        branchResponseDecoded = branchResponse.decode("utf-8")
        if '\n' in branchResponseDecoded:
            branchesList = branchResponseDecoded.split('\n')
            for line in branchesList:
                if 'refs/heads/' in line:
                    branches.append(line.rsplit('refs/heads/', 1)[1])
    except Exception:
        branches = []
    details.update({"branches": branches})
    details.update({"source_github_branch": str(source_github_branch)})

    # If there isn't a source branch specified, don't set the log branch or last commit ID file either
    if source_github_branch == 'None':
        log_branch = 'None'
        last_commit_id_file = 'None'
    else:
        try:
            log_branch = locations_config["log_branch"]
        except KeyError:
            log_branch = source_github_branch + '-logs'

        try:
            last_commit_id_file = locations_config["last_commit_id_file"]
        except KeyError:
            last_commit_id_file = '.' + source_github_branch + '_commit.txt'

    details.update({"log_branch": str(log_branch)})
    details.update({"last_commit_id_file": str(last_commit_id_file)})

    # Get everything else from the config info
    try:
        log_file_name = locations_config["log_file_name"]
    except KeyError:
        log_file_name = '.md-enricher-for-cicd.log'
    finally:
        details.update({"log_file_name": log_file_name})

    try:
        img_src_filetypes = locations_config["img_src_filetypes"]
    except KeyError:
        img_src_filetypes = '.ai, .AI, .drawio, .eps, .psd, .PSD, .sketch'
    finally:
        img_src_filetypes_list = img_src_filetypes.split(', ')
        details.update({"img_src_filetypes": img_src_filetypes_list})

    try:
        img_output_filetypes = locations_config["img_output_filetypes"]
    except KeyError:
        img_output_filetypes = '.bmp, .BMP, .gif, .GIF, .jpg, .JPG, .jpeg, .JPEG, .mp4, .MP4, .png, .PNG, .svg, .SVG'
    finally:
        img_output_filetypes_list = img_output_filetypes.split(', ')
        details.update({"img_output_filetypes": img_output_filetypes_list})

    try:
        filetypes = locations_config["filetypes"]
    except KeyError:
        filetypes = '.html, .json, .md, .nojekyll, .yml, .yaml, .txt, toc'
    finally:
        filetypes_list = filetypes.split(', ')
        details.update({"filetypes": filetypes_list})

    try:
        reuse_snippets_folder = locations_config["reuse_snippets_folder"]
        if reuse_snippets_folder.startswith('/'):
            reuse_snippets_folder = reuse_snippets_folder[1:]
        elif reuse_snippets_folder.endswith('/'):
            reuse_snippets_folder = reuse_snippets_folder[:-1]
        # if not os.path.isdir(details["source_dir"] + '/' + details["reuse_snippets_folder"] + '/'):
    except KeyError:
        reuse_snippets_folder = 'reuse-snippets'
    finally:
        details.update({"reuse_snippets_folder": reuse_snippets_folder})

    try:
        reuse_phrases_file = locations_config["reuse_phrases_file"]
    except KeyError:
        reuse_phrases_file = 'phrases.json'
    finally:
        details.update({"reuse_phrases_file": reuse_phrases_file})

    return (details)
