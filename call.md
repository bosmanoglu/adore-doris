# USAGE: #
```
 call "(out1 out2 ... outK)=functionName in1 in2 ... inK ;"
```
# DESCRIPTION: #
> CALL is an internal ADORE function to return multiple variables from a BASH
> function.
> BASH functions can only return an integer number, and multiple variables can
> only be assigned if variable names are known beforehand. CALL function creates
> the specified output variables in the environment for the given function in
> functionName. The function can have multiple input and output parameters.
> Names of output parameters should be declared in a special variable which
> starts with the functionName and has the 