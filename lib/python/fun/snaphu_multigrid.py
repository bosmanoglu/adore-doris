import snaphu

print("__Input parameters__")
print("Filename:   %s" % setobj._ipy_.f)
print("Conf file:  %s" % setobj._ipy_.c)
print("File width: %d" % int(setobj._ipy_.w))
sn=snaphu.Snaphu()
sn.read_config(setobj._ipy_.c)
sn.infile=setobj._ipy_.f
sn.width=int(setobj._ipy_.w)
#Assuming cr4. This needs to be checked. 
sn.lines=int(os.path.getsize(sn.infile)/sn.width/8)
sn.unwrap_multigrid()
