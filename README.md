# linkedin-organization-scraper
Scrapes all profiles from any linkedin organization

### Step 1 : Download The Repository and place it in a folder
### Step 2 : [Download The Lastest Stable Release Of Chrome](https://www.google.com/chrome/)
### Step 3 : [Download The Lastest Stable Release Of Chrome Driver and place it in the repository folder](https://sites.google.com/a/chromium.org/chromedriver/)
### Step 4 : [Download and Install the Lastest Stable Release of Python 3, make sure it's added to PATH](https://www.python.org/downloads/)
### Step 5 : Install the requirements
once you install Python, open a commandline and go to the repository's folder. Execute the following command:
`pip install -r requirements.txt`

## Now You're all set, time to run the script

### Open a commandline in the repository folder
To execute the script. You must use 3 arguments. Here's the usage
- `python script.py csv link mode`
- `csv` is the file you want to export the data to. Example : `outfile.csv`
- `link` is the search filter that you'll apply. Example : `https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223139%22%2C%2251686%22%5D`
- `mode` is writing mode for the file. If you want to start a new csv file. use `w`, if you want to append. use `a`. You would use `a` if you quit the script in the middle of the process, and want to continue without starting over.

- So and example to run the script would be:
- `python script.py outfile.csv https://www.linkedin.com/search/results/people/?facetCurrentCompany=%5B%223139%22%2C%2251686%22%5D w`
