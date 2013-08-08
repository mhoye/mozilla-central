#!/usr/bin/env python

def setup():

  # get us into the top of the tree to start this party right.

  get_git_toplevel_dir = "git rev-parse --show-toplevel"

  # Figure out where we are, do some looking around before we do a ton of work.

  starting_directory = os.getcwd()

  # git rev-parse --show-toplevel doesn't work if we're in a .git objdir, so... 

  if ".git" in starting_directory:
    safe_dir = re.sub( "\.git/*", "", starting_directory) 
    os.chdir(safe_dir) 

  # It's conceivable that this fails if somebody puts all their git repositories
  # under .git/something but if you've done that, you've got other problems.

  git_toplevel_dir = "" 

  try:
    git_toplevel_dir = subprocess.check_output( get_git_toplevel_dir.split(), shell=False, universal_newlines=False)
  except subprocess.CalledProcessError as e:
    print ( "\nAre you sure we're in a Git repository here? I can't find the top-level directory,"
          + "\nand Mock Learn only works in Git.")
    exit ( e.returncode )

  # this next bit should never happen, if that while loop just above works like it should...

  if len(git_toplevel_dir) == 0:
    print ("\nI can't find the top of your source tree with \"git rev-parse --show-toplevel\", so I can't continue.\n" )
    # This can happen if you're running gitlearn from under the .git object directory, but the while loop above
    # should have taken care of that, so I don't know what's going on here. Bailing out.
    exit (-1)

  os.chdir( git_toplevel_dir[:-1] )

  return()
