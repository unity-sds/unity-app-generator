#!/bin/bash


# Prints usage message
#
usage() {
  echo "Usage: $0 [ PATH ] [ -b BRANCH ] [ -m MESSAGE ] [ -t TOKEN_NAME:TOKEN ]" 1>&2 
}

# This function is for error exit.
#
exit_abnormal() {
  usage
  exit 1
}


#=============== Get some optional input parameters ===============

# Default values for non-positional input arguments.
#
branch="main"
message="initial revision"
tauthentication=""

ipos=0
while [ $# -gt 0 ]; do
    unset OPTIND
    unset OPTARG
    while getopts hb:m:t: opt; do
       if [[ ${OPTARG} =~ ^-.*$ ]]; then
            echo "ERROR:  Option argument cannot start with '-'"
            exit_abnormal
        fi
        case "$opt" in
            h) usage; exit 0;;
            b) branch=${OPTARG};;
            m) message=${OPTARG};;
            t) tauthentication=${OPTARG};;
            *) echo "ERROR:  Unknown option."; exit_abnormal;;
        esac
    done
    shift $((OPTIND-1))
    (( ipos=ipos+1 ))
    case $((ipos)) in
        1) path="$1";;
        *) [ ! -z "$1" ] && echo "ERROR:  Incorrect number of positional arguments!" && exit_abnormal;;
    esac
    shift
done

# Default values for positional input arguments.
#
if [ -z $path ]; then
    path='.'
fi

echo "branch  '$branch'"
echo "message '$message'"
echo "token   '$tauthentication'"
echo "path    '$path'"


#=============== Check if "$path" is a valid URL ===============

# Boolean: true if $path is a valid URL that can be found, false otherwise.
#
path_valid_url=$(! wget --spider "$path" > /dev/null 2>&1; echo $?)

# Check whether or not the path is a valid URL
#
if (( $path_valid_url )); then
    echo "INFO:  Verified URL '$path'"
fi


#=============== Check if $path is a Git repo URL ===============
# If it is a Git repo URL,
#   1) clone it
#   2) set $path to be the locally cloned subdirectory name
# It may not be an error if $path is not a Git repo URL that can be
# found.  It could be a path pointing at a location in the local
# file system.

# Boolean: true if $path is a valid git repo, false otherwise.
# This flag will be true if $path is either
#   - a URL for a remote git repository
#   - or a path to a local git repository
#
path_valid_git=$(! git ls-remote "$path" > /dev/null 2>&1; echo $?)

# Here we assume that $path is a URL pointing at a public repository
# and no authentication is necessary.  Just $path_valid_git being
# true is not enough here.  $path_valid_git would be true if $path
# were a path to a git repository in the local filesystem.  Just
# $path_valid_url being true is not enough either.  For example,
# $path_valid_url would be true if $path were "https://www.apple.com",
# which is not a git project URL.  Therefore, both flags must be true
# for us to conclude that $path is the URL of a remote git repository.
#
# If in the working directory there is a file or subdirectory named
# $reponame, cloning will fail (see the 'if' block).  We may want to
# handle this in a different way.
#
just_cloned=false
if (( $path_valid_git && $path_valid_url )); then
    echo "INFO:  Verified a git repository '$path'"
    basename=$(basename $path)
    reponame=${basename%.*}
    #extension=${basename##*.}
    echo "INFO:  Repository name is '$reponame'."
    git clone $path
    if [ $? -ne 0 ]; then
        echo "ERROR:  Command 'git clone $path' failed!"
        exit $?
    fi
    just_cloned=true
    git -C $reponame remote set-url --push origin DISABLED
    path=$reponame
else
    echo "INFO:  Could not be verified as a remote git repository '$path'"
fi


#=============== Check if $path is a local filesystem subdirectory ===============
# At this point, path must be an existing local subdirectory.

# If not a valid directory, just exit.  If not exited, the process
# steps into $path.
#
if [ ! -d $path ]; then
    echo "ERROR:  '$path' must be an existing directory!"
    exit_abnormal
fi

cd $path


#=============== Not a Git repo? Then convert into a Git repo ===============
# If the working directory (folder) is inside a git repository, which
# was not recently cloned, then perhaps the caller wanted to pull
# updates from the original remote and push it into MCP.  The code 
# block here follows this assumption, but it only pulls updates from
# remote 'origin' if available.  However, if the current subdirectory
# (folder) is not inside a git repository, then convert it (and its
# contents) into a git repository.  The caller must eliminate all
# unwanted files, links, subdirectories ... before calling this script.

# Boolean: true if at the top level of a local git repo, false otherwise.
#
git_repo_top_level=$(! [[ "`git rev-parse --git-dir 2> /dev/null`" == ".git" ]]; echo $?)

# Boolean: true if somewhere inside a git repo, false otherwise.
#
git_repo_somewhere=$(! git rev-parse --git-dir > /dev/null 2>&1; echo $?)

if (( $git_repo_somewhere )); then
    echo "INFO:  Already in a git repository: $PWD"
    if [[ "$just_cloned" = false ]]; then
        # If this git repository was already cloned before calling this
        # script, then simply pull updates only from remote 'origin'
        # to be pushed into MCP later.
        
        original_remote_name="origin"
        result="`git remote | grep $original_remote_name 2> /dev/null`"
        if [ -z "$result" ]; then
            echo "WARN:  There is no remote named '$original_remote_name' for updates."
        else
            # The following disabling may not be necessary.
            git remote set-url --push $original_remote_name DISABLED
            echo "INFO:  Pulling updates from remote '$original_remote_name' for MCP push later."
            git pull $original_remote_name
            if [ $? -ne 0 ]; then
                echo "ERROR:  Command 'git pull $original_remote_name' failed!"
                exit $?
            fi
        fi
    fi
else
    echo "INFO:  Converting to a local git repository: $PWD"

    # Initializing as a git repository.  This should be done
    # only if the current location is not a git repository.
    #   git branch -m <name>     just renames the current branch
    #
    git init
    git branch -m "$branch"
    git add *
    git commit -m "$message"
fi


#=============== Working directory must be a local Git repository ===============
# At this point, the working directory must be a git repository;
# otherwise, something is wrong.

# The following flag must be false at this point.
#
not_a_git_repo=$( git rev-parse --git-dir > /dev/null 2>&1; echo $? )
if (( $not_a_git_repo )); then
    echo "ERROR:  The working directory must be inside a git repository."
    exit_abnormal
fi


#=============== Determine current branch name ===============

branch="`git branch --show-current 2> /dev/null`"
if [ $? -ne 0 ]; then
    echo "ERROR:  Could not obtain current branch name."
    exit $?
elif [ -z "$branch" ]; then
    echo "ERROR:  Current branch name is null."
    exit 1
else
    echo "INFO:  Curent branch name is '$branch'."
fi


#=============== Add MCP remote link if it does not exist. ===============

# Remote name for MCP GitLab Ultimate
#
name="mcp"

result="`git remote | grep $name 2> /dev/null`"
if [ -z "$result" ]; then
    echo "INFO:  Remote '$name' does not exist.  Creating remote '$name' link."

    # Creating an MCP URL for the new project.

    if [ "$tauthentication" = "" ]; then
        gitlaburl="https://gitlab.mcp.nasa.gov/unity/"
    else
        gitlaburl="https://$tauthentication@gitlab.mcp.nasa.gov/unity/"
    fi

    # The current subdirectory name (last token of PWD) is
    # chosen as the project name.
    #
    project=${PWD##*/}

    # And finally the project URL:
    #
    mcp_projecturl=$gitlaburl$project.git
    echo "INFO:  MCP URL for cloning is '$mcp_projecturl'"

    # Create the remote link.
    #
    git remote add "$name" "$mcp_projecturl"

    # Ideally, I would like to disable mcp fetch, I don't know how
    # to do it.  The following command only works for --push.
    #
    #git remote set-url --fetch "$name" DISABLE

else
    echo "INFO:  Remote '$name' already exists."
fi


#=============== Finally, push into MCP GitLab ===============

# Do not add "-u" option for "git push ..." command.
#
echo "INFO:  Executing the command"
echo "   git push $name $branch"
git push "$name" "$branch"


exit 0
