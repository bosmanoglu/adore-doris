# USAGE: #
```
      waitjob hostname.jobid
	waitjob (hostname.jobid1 hostname.jobid2 ...)
```
# DESCRIPTION: #
> WAITJOB is an internal ADORE command.
> It loops over the given jobs and returns upon their completion.
> This script is compatible with the Torque-PBS system.
# INPUT: #
> hostname.jobid: hostname of the system running the job and the job number
> > separated by a dot. This is printed on the screen after each quejob command.
> > Alternatively a list of jobs can be given. In this case this command
> > will return only after all jobs are finished.
# OUTPUT #
> > Displays the number of minutes passed on the screen. No files are generated.
# FILES and REFERENCES: #  ${ADORESCR}/fun/waitjob
```