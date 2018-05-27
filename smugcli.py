#!/usr/bin/python
# Command line tool for SmugMug. Uses SmugMug API V2.

import smugmug as smugmug_lib
import smugmug_fs
import smugmug_shell

import argparse
import collections
import inspect
import json
import persistent_dict
import os
import sys


CONFIG_FILE = os.path.expanduser('~/.smugcli')


def run(args, requests_sent=None):
  try:
    config = persistent_dict.PersistentDict(CONFIG_FILE)
  except persistent_dict.InvalidFileError:
    print ('Config file (%s) is invalid. '
           'Please fix or delete the file.' % CONFIG_FILE)
    return

  smugmug = smugmug_lib.SmugMug(config, requests_sent)
  fs = smugmug_fs.SmugMugFS(smugmug)

  main_parser = argparse.ArgumentParser(description='SmugMug commandline interface.')
  subparsers = main_parser.add_subparsers(title='sub commands')

  # ---------------
  login_parser = subparsers.add_parser(
    'login', help='Login onto the SmugMug service')
  login_parser.set_defaults(func=lambda a: fs.smugmug.login((a.key, a.secret)))
  login_parser.add_argument('--key',
                            type=lambda s: unicode(s, 'utf8'),
                            required=True,
                            help='SmugMug API key')
  login_parser.add_argument('--secret',
                            type=lambda s: unicode(s, 'utf8'),
                            required=True,
                            help='SmugMug API secret')
  # ---------------
  logout_parser = subparsers.add_parser(
    'logout', help='Logout of the SmugMug service')
  logout_parser.set_defaults(func=lambda a: fs.smugmug.logout())

  # ---------------
  get_parser = subparsers.add_parser(
    'get', help='Do a GET request to SmugMug using the API V2 URL.')
  get_parser.set_defaults(func=lambda a: fs.get(a.url))
  get_parser.add_argument('url',
                          type=lambda s: unicode(s, 'utf8'),
                          help=('A SmugMug V2 API URL to get the JSON response '
                                'from. Useful combined with `smugcli.py ls -l '
                                '...` which will list URI you may want to '
                                'fetch.'))
  # ---------------
  ls_parser = subparsers.add_parser(
    'ls', help='List the content of a folder or album.')
  ls_parser.set_defaults(func=lambda a: fs.ls(a.user, a.path, a.l))
  ls_parser.add_argument('path',
                         type=lambda s: unicode(s, 'utf8'),
                         nargs='?',
                         default=os.sep,
                         help='Path to list.')
  ls_parser.add_argument('-l',
                         help=('Show the full JSON description of the node '
                               'listed. Useful with `smugcli.py get ...`, '
                               'which can be used to fetch the URIs listed in '
                               'the JSON description.'),
                         action='store_true')
  ls_parser.add_argument('-u', '--user',
                         type=lambda s: unicode(s, 'utf8'),
                         default='',
                         help=('User whose SmugMug account is to be accessed. '
                               'Uses the logged-in user by default.'))
  # ---------------
  for cmd, node_type in (('mkdir', 'Folder'), ('mkalbum', 'Album')):
    mkdir_parser = subparsers.add_parser(
      cmd, help='Create a %s.' % node_type.lower())
    mkdir_parser.set_defaults(
      func=lambda a, t=node_type: fs.make_node(a.user, a.path, a.p, t,
                                               a.privacy.title()))
    mkdir_parser.add_argument('path',
                              type=lambda s: unicode(s, 'utf8'),
                              nargs='+',
                              help='%ss to create.' % node_type)
    mkdir_parser.add_argument('-p',
                              action='store_true',
                              help='Create parents if they are missing.')
    mkdir_parser.add_argument('--privacy',
                              type=lambda s: unicode(s, 'utf8'),
                              default='public',
                              choices=['public', 'private', 'unlisted'],
                              help='Access control for the created folders.')
    mkdir_parser.add_argument('-u', '--user',
                              type=lambda s: unicode(s, 'utf8'),
                              default='',
                              help=('User whose SmugMug account is to be '
                                    'accessed. Uses the logged-in user by '
                                    'default.'))
  # ---------------
  rmdir_parser = subparsers.add_parser(
    'rmdir', help='Remove a folder(s) if they are empty.')
  rmdir_parser.set_defaults(func=lambda a: fs.rmdir(a.user, a.parents, a.dirs))
  rmdir_parser.add_argument('-p', '--parents',
                            action='store_true',
                            help=('Remove parent directory as well if they are '
                                  'empty'))
  rmdir_parser.add_argument('-u', '--user',
                            type=lambda s: unicode(s, 'utf8'),
                            default='',
                            help=('User whose SmugMug account is to be accessed. '
                                  'Uses the logged-in user by default.'))
  rmdir_parser.add_argument('dirs',
                            type=lambda s: unicode(s, 'utf8'),
                            nargs='+', help='Directories to create.')
  # ---------------
  rm_parser = subparsers.add_parser(
    'rm', help='Remove files from SmugMug.')
  rm_parser.set_defaults(
    func=lambda a: fs.rm(a.user, a.force, a.recursive, a.paths))
  rm_parser.add_argument('-u', '--user',
                         type=lambda s: unicode(s, 'utf8'),
                         default='',
                         help=('User whose SmugMug account is to be accessed. '
                               'Uses the logged-in user by default.'))
  rm_parser.add_argument('-f', '--force',
                         action='store_true',
                         help=('Do not prompt before deleting files.'))
  rm_parser.add_argument('-r', '--recursive',
                         action='store_true',
                         help=('Recursively delete all of folder\'s content.'))
  rm_parser.add_argument('paths',
                         type=lambda s: unicode(s, 'utf8'),
                         nargs='+', help='Path to remove.')
  # ---------------
  upload_parser = subparsers.add_parser(
    'upload', help='Upload files to SmugMug.')
  upload_parser.set_defaults(func=lambda a: fs.upload(a.user, a.src, a.album))
  upload_parser.add_argument('src',
                             type=lambda s: unicode(s, 'utf8'),
                             nargs='+', help='Files to upload.')
  upload_parser.add_argument('album',
                             type=lambda s: unicode(s, 'utf8'),
                             help='Path to the album.')
  upload_parser.add_argument('-u', '--user',
                             type=lambda s: unicode(s, 'utf8'),
                             default='',
                             help=('User whose SmugMug account is to be '
                                   'accessed. Uses the logged-in user by '
                                   'default.'))
  # ---------------
  sync_parser = subparsers.add_parser(
    'sync', help='Synchronize all local albums with SmugMug.')
  sync_parser.set_defaults(func=lambda a: fs.sync(a.user, a.source, a.target))
  sync_parser.add_argument('source',
                           type=lambda s: unicode(s, 'utf8'),
                           nargs='*',
                           default=u'*',
                           help=('Folder to sync. Defaults to the local '
                                 'folder. Uploads the current folder by '
                                 'default.'))
  sync_parser.add_argument('-t', '--target',
                           type=lambda s: unicode(s, 'utf8'),
                           default=os.sep,
                           help=('The destination folder in which to upload '
                                 'data. Uploads to the root folder by '
                                 'default.'))
  sync_parser.add_argument('-u', '--user',
                           type=lambda s: unicode(s, 'utf8'),
                           default='',
                           help=('User whose SmugMug account is to be '
                                 'accessed. Uses the logged-in user by '
                                 'default.'))
  # ---------------
  ignore_parser = subparsers.add_parser(
    'ignore', help='Mark paths to be ignored during sync.')
  ignore_parser.set_defaults(
    func=lambda a: fs.ignore_or_include(a.paths, True))
  ignore_parser.add_argument('paths',
                             type=lambda s: unicode(s, 'utf8'),
                             nargs='+',
                             help=('List of paths to ignore during sync.'))
  # ---------------
  include_parser = subparsers.add_parser(
    'include',
    help='Mark paths to be included during sync.',
    description=('Mark paths to be included during sync. Everything is '
                 'included by default, this commands is used to negate the '
                 'effect of the "ignore" command.'))
  include_parser.set_defaults(
    func=lambda a: fs.ignore_or_include(a.paths, False))
  include_parser.add_argument('paths',
                              type=lambda s: unicode(s, 'utf8'),
                              nargs='+',
                              help=('List of paths to include during sync.'))
  # ---------------
  smugmug_shell.SmugMugShell.set_parser(main_parser)
  shell_parser = subparsers.add_parser(
    'shell', help=('Start smugcli in interactive shell mode.'))
  shell_parser.set_defaults(
    func=lambda a: smugmug_shell.SmugMugShell(fs).cmdloop())
  # ---------------

  parsed = main_parser.parse_args(args)

  try:
    parsed.func(parsed)
  except smugmug_fs.Error as e:
    print e
  except smugmug_lib.NotLoggedInError:
    return


if __name__ == '__main__':
  run(sys.argv[1:])
