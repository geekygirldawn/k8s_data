"""
 This is a hack to read an Elekto voters.yaml file and
 find GH logins where the case in the yaml file doesn't 
 match what the GH API returns. The API doesn't treat them
 case sensitive, but Elekto did. Since devstats (the source
 of the yaml file) forces gh logins to lower case, but Elekto
 wasn't anyone with upper case letters in their GH login was
 ineligible to vote. They are in the process of fixing this in 
 Elekto.
"""

def read_args():
    """Reads the yaml filename where the voters can be found and prompts for a 
       GitHub API Personal Access Token.
    
    Parameters
    ----------
    None

    Returns
    -------
    file_name : str
        This should be an Elekto yaml file stored locally with the path to that file
    """
    import sys

    # read filename from command line or prompt if no 
    # arguments were given.
    try:
        file_name = str(sys.argv[1])

    except:
        print("Please enter the filename for voters.yaml.")
        file_name = input("Enter a file name: ")

    api_token = input("Enter your GitHub Personal Access Token: ")

    return file_name, api_token

from github import Github
import yaml
import sys

file_name, api_token = read_args()

try:
    g = Github(api_token)
except:
    print("Cannot read gh_key file or does not contain a valid GitHub API token?")
    sys.exit()

# Loads the yaml file and creates a list of voters
try:
    
    #voters_file = urllib.request.urlopen(file_name)
    #voters = yaml.safe_load(file_name)
    with open(file_name, 'r') as file:
        voters = yaml.safe_load(file)
        voter_list = voters['eligible_voters']

except:
    print("Cannot load or process the yaml file. Did you use the raw link?")
    sys.exit()

for user in voter_list:
    login_case = g.get_user(user).login
    if login_case != user:
        print(login_case, user)
