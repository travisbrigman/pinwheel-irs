## Instructions and _errata_ on pinwheelIRS script

__Python Version:__ 3.8.1

#### To Run The script (assuming you have python 3.8.1 or newer installed):
1. From a terminal ```cd``` in the directory
2. Create a virtual environment (either ```pipenv shell``` or ```virtualenv venv```)
3. If you used virtualenv, activate with ```. venv/bin/activate```
4. Run the command ```pip install .```
5. The command to run the script is ```pinwheelIRS```

#### Command Line Arguments:
```-info``` This is a string that can have multiple comma delimited form names,
> __For example:__ "Form 11-C" or "Form W-2,Form 1095-C,Form 11-C"

```-download``` This is a single string value of a form name.
> e.g. "Form W-2"

Both of the above arguments must have the format letters, numbers, dashes or underscores.
No other characters are accepted.

```-years``` The mininum and maximum years as integers for downloading forms.
> example format: 2018 2020

```-help``` help in the terminal about the script.

##### Example form info query:
```$ pinwheelIRS -info "Form W-2,Form 11-C"```

##### Example form download query:
```$ pinwheelIRS -download "Form W-2" -years 2000 2005```

#### Things to note:

* The a string of multiple forms in the form info argument should formatted with no spaces after the commas.
* The script should strip the spaces it should be case-insensitive.

* The Form name (aside from case) needs to be exact. So "Form W2" or "FormW-2" will not work.
* The ```download``` argument only accepts one form name. Passing a list in the same form as what the ```info``` argument accepts won't work.
* Once a download starts, a subdirectory called "pdfs" will be created and downloads will be placed there.
* The JSON from the ```info``` argument is printed to the console. If a user selects, a irs.json file will be created in the same directory as the script.


#### Thoughts on the challenge:

I thought this was a good challenge that aligned with the required skill level that is outlined in the job description. I think that the requirements were specific enough in the right places and left vague enough for a developer to create something unique. Overall great job, it was a lot of fun and thanks for the opportunity.
