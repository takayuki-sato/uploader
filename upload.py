#!/usr/bin/env python3

import argparse
import logging
import pandas
import mintlabs
import os
import threading
import queue

DESCRIPTION = "Upload subjects data & metadata to the mintlabs platform."

LOGGER = logging.getLogger('root')
LOGGER.setLevel(logging.DEBUG)

def get_project_id(account, project):
    projects = account.projects
    for proj in projects:
        if proj['name'] == project:
            return proj['id']

def add_metadata_parameters(project, dataframe):
    # First col is file, second col is subject name, then come the
    # metadata parameters.
    # Second row contains the type of each parameter
    parameters = dataframe.columns[2:]
    for parameter in parameters:
        if parameter == 'gender':
            continue
        param_type = dataframe[parameter][0]
        project.add_metadata_parameter(parameter, param_type=param_type, visible=True)
        LOGGER.info('Added parameter: {} of type {}'.format(parameter, param_type))

def add_subjects(project, dataframe):
    parameters = dataframe.columns[2:]
    existing_subjects = project.subjects
    for index in range(1, dataframe.shape[0]):
        subject_name = dataframe['Subject'][index]
        if subject_name in existing_subjects:
            subject = project.get_subject(subject_name)
            LOGGER.info('Retrieved existing subject: {}'.format(subject_name))
        else:
            subject = mintlabs.Subject(subject_name)
            project.add_subject(subject)
            LOGGER.info('Added subject: {}'.format(subject_name))
        # fill dictionary with the subject metadata
        param_dict = subject.parameters
        for parameter in parameters:
            param_dict[parameter] = dataframe[parameter][index]
        subject.parameters = param_dict
        LOGGER.info('Updated subject metadata: {}'.format(subject_name))

def worker(q, data_type):
    while True:
        data = q.get()
        subject_name = data["subject_name"]
        data_file = data["file"]
        subject = data["subject"]
        if data_type == "gametection":
            target = subject.upload_gametection
        else:
            target = subject.upload_mri
        LOGGER.info('Uploading data for subject {}: {}'.format(subject_name, data_file))
        target(data_file)
        LOGGER.info('Finished upload for subject {}: {}'.format(subject_name, data_file))
        q.task_done()

def start_n_workers(n, *args):
    for i in range(n):
        t = threading.Thread(target=worker, args=args)
        t.daemon = True
        t.start()

def upload_subjects_data(project, dataframe, basedir, data_type, n):
    parameters = dataframe.columns[2:]
    q = queue.Queue()
    # fill queue with all the tasks
    for index in range(1, dataframe.shape[0]):
        subject_name = dataframe['Subject'][index]
        data_file = os.path.join(basedir, dataframe['File'][index])
        subject = project.get_subject(subject_name)
        data = {"subject_name": subject_name, "file": data_file, "subject": subject}
        q.put(data)
    # start n workers
    start_n_workers(5, q, data_type)
    q.join()


def main(options):
    if not options.user:
        LOGGER.error('No user provided')
        return
    if not options.password:
        LOGGER.error('No password provided')
        return
    if not options.project:
        LOGGER.error('No project provided')
        return
    acc = mintlabs.Account(options.user, options.password)
    # id (integer) of the project to which the subjects will
    # be uploaded
    project_id = get_project_id(acc, options.project)
    # select project
    project = mintlabs.Project(acc, project_id)

    # dataframe containing the data needed to upload the files
    df = pandas.read_csv(options.info_file)
    # if there is a column called gender, rename it to be lowercase
    df.columns = [col.lower() if col.lower() == 'gender' else col for col in df.columns]
    ### Add parameters ###
    # add_metadata_parameters(project, df)
    # add_subjects(project, df)
    upload_subjects_data(project, df, options.basedir, options.data_type, int(options.n_threads))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-i', '--info',
                        dest='info_file',
                        action='store',
                        default='info.csv')
    parser.add_argument('-d', '--dir',
                        dest='basedir',
                        action='store',
                        default='./')
    parser.add_argument('-u', '--user',
                        dest='user',
                        action='store',
                        default=None)
    parser.add_argument('-p', '--password',
                        dest='password',
                        action='store',
                        default=None)
    parser.add_argument('-j', '--project',
                        dest='project',
                        action='store',
                        default=None)
    parser.add_argument('-t', '--type',
                        dest='data_type',
                        action='store',
                        default='mri')
    parser.add_argument('-n', '--threads',
                        dest='n_threads',
                        action='store',
                        default='5')


    options = parser.parse_args()
    main(options)
