# USAGE: #
```
 testFunction input1 input2 input3
```
# DESCRIPTION: #
> TESTFUNCTION is an internal ADORE function to test the usage of CALL
function.
> input2 and input1 are swapped. Output1 equals input2, output2 equals input1
and output3 equals input3.
# INPUT: #
> Three input variables are required.
> ## OPTIONAL: ##
> > There are no optional input parameters for this command.
# OUTPUT #

> Three variables are output.
# FILES and REFERENCES: #
```
 ${ADOREFOLDER}/fun/functions
```
# EXAMPLE: #
```
 call "(a b c)=testFunction ${variable1} ready breakfast ;"
```
# KNOWN BUGS: #
> None.