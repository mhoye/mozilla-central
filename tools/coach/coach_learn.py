#!/usr/bin/env python

import sys, os, shutil, subprocess, pickle, signal, re

def main():

  file_list = dict()
  
  file_list = { 
          'temp_file'               : "/tools/coach/.coaching_data",  # leading slash matters
          'final_file'              :  "/tools/coach/coaching_data"  # in both these strings.
          }

  try:  
    setup()             # Get us into the top of the source tree
    learn(file_list)    # Once  
    finish(file_list)
    exit(0);
  except Exception as e:
    print( "\nSorry, something has thrown an error I don't understand. This shouldn't happen," +
           "\nperhaps obviously. The error is below. I don't know what to do here, so I'm out." +
           "\n\n" + str(e) );
    exit(-100);


def get_commit_hashes():

# Mach-coach will through any additional command-line options to git rev-list unless
# it doesn't get any, in which case the default behavior is "--all". 
#
# If you're playing this game at home, "origin/master --max-count=<n>" might be a better
# option for some well-chosen value of <n> - if you're going to do "--all" here on a project 
# as venerable as Mozilla, you'd better have some free time on your hands.

  git_rev_list_opts = "git rev-list " 

  if len(sys.argv) < 2:
    git_rev_list_opts += ( " --all " )
  else:
    for arg in sys.argv[1:]:
      git_rev_list_opts += " " + arg

  try: 
    all_commit_hashes = subprocess.check_output( git_rev_list_opts.split(),
                                                 shell=False, 
                                                 universal_newlines=True)
  except subprocess.CalledProcessError as e:
    print ( "\nAre you sure we're in a Git repository here? I can't get any commit hashes.")
    exit ( e.returncode )
  
  return all_commit_hashes.strip().split()

def get_files_from_hash( commit_hash ):

  list_files_per_commit = "git show --pretty=format: --name-only " + commit_hash
  
  try:
    all_files_per_commit = subprocess.check_output( list_files_per_commit.split(), 
                                                    shell=False, 
                                                    universal_newlines=True)
  except subprocess.CalledProcessError as e:
    print ( "\nI couldn't get a list of modified files for this commit: " 
            + commit_hash 
            + "\n\nI don't know what to do here, sorry. I'm out.")
    exit ( e.returncode )

  return all_files_per_commit.strip().split('\n')  

def learn(f_lst):

  all_hashes = list()
  all_files = list()
  
  correlation = dict()
  
  output_file = "./" + f_lst["temp_file"]

  try: 
    output_stream = open(output_file, 'w')
  except IOError as e:
    print ("\nOutput file " + output_file + " already exists, and I can't overwrite it." + \
           "\nThis shouldn't happen; you'll have to delete it and re-run gitlearn." )
    exit ( -1 )


  all_hashes = get_commit_hashes()

  for a_hash in all_hashes:
    files = get_files_from_hash(a_hash)  
    for f in files:
      if f not in all_files:
          all_files.append(f) 
          print("Noting file: " + f)
          
      for g in files:
        if (f != g) :
          if (f,g) not in correlation:
            correlation[(f,g)] = 0
            correlation[(g,f)] = 0
            print("Correlation: " + g)

          correlation[(g,f)] += 1
          correlation[(f,g)] += 1
  
  pickle.dump(all_files, output_stream)
  pickle.dump(correlation,output_stream)
  output_stream.close()

  return()

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

def finish(f_list):
  
  # clean up and exit

  output_file = "./" + f_list["temp_file"] 
  destination_file = "./" + f_list["final_file"]

  try:
    shutil.move(output_file, destination_file)
  except subprocess.CalledProcessError as e:
    print ( "\nIt looks like we can't overwrite the existing coaching_data file" + \
            "\nThis shouldn't happen; you'll have to delete it manually, then either copy" + \
            "\n .git/.coaching_data to .git/coaching_data or re-run gitlearn.")
    exit ( e.returncode )

  return()

def signal_handler(signal, frame):
  print ( "\nProcess interrupted. Goodbye.\n")
  sys.exit(0)
  
signal.signal(signal.SIGINT, signal_handler)

main()
exit(0)

