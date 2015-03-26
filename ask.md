# USAGE: #
```
 ask "input string"
 if ask "input string"
```
# DESCRIPTION: #
> ASK is an internal ADORE function.
> It is used in ADORE scripts and commands to get user input.
> The string " [y/n]" is appended to the end of the input string.
> The user can use lowercase or uppercase Y or N characters as an answer.
> For multiple character long answers, second and later characters are ignored.
> If the user input does not start with a Y or N character the question is asked again until a valid answer is given.
# INPUT: #
> input string: Yes or no question asked to the user.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> Returns 0 for yes and 1 for no, compatible with conditionals for if statements etc.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/scr/fun/functions
```
# EXAMPLE: # ask "Shall I continue?" && echo yes || echo no
 if ask "Shall I delete the old ${saveFileName}?"
```