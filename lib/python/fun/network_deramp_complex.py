"""This method calculates individual ramps from the interferograms, 
solves a least squares inversion over the network,
and applies the results to each interferograms.         
"""        
import deramp
import basic
import glob
from subprocess import call
#get iobj list
process=setobj._ipy_.p
i12sFolder=setobj.adore.i12sfolder.strip('"')
ifiles=glob.glob(i12sFolder+'/*/*_*.res')
i12s=[]    #interferogram objects list
i12sd=[]   #interferogram dict list
master=[]  #master names list
slave=[]   #slave names list
for f in ifiles:
  d=adore.res2dict(f) #dictionary
  i12sd.append(d)
  i12s.append(adore.dict2obj(d))
  master.append(os.path.splitext(os.path.basename(f))[0].split('_')[0])
  slave.append(os.path.splitext(os.path.basename(f))[0].split('_')[1])

#estimate individual ramps
## here for each interferogram we estimate azimuth and range ramps.
print "Calculating individual ramps..."
ramps=squeeze(dstack([ deramp.estrampcpx(adore.getProduct(x,process)) for x in i12sd ]))
dS=adore.getProduct(i12sd[0],process).shape
#least sq. inversion
print "Calculating network solution..."
## get required info
allDates=master + slave #merge master and slave lists
allDates=sort(list(set(allDates)));
I=len(allDates); #Number of images (dates)
N=len(ifiles)    #Number of interferograms
## the individual ramps are solved in a network fashion such that:
## A x = b where
## Design matrix
## A= SBAS design matrix [1 0 0 0... 0 -1 0 ...] 
## x= ramp estimated for each date
## b= ramp estimated for each inteferogram
tk=0
A=zeros([N+1,I]);        
for k in xrange(N):
    A[k,:]=(allDates==master[k])*-1+(allDates==slave[k])*1;     
    if basic.progresstime(tk):
      basic.progress(k,N,);tk=basic.time.time()
A[-1,0]=1
pinvA=linalg.pinv(A)
x0=dot(pinvA, list(ramps[0,:])+[0]) #merge zero to the end of list
x1=dot(pinvA, list(ramps[1,:])+[0]) #merge zero to the end of list
            
#deramp
print "Deramping interferograms..."
## Calculate Ax
r0=dot(A,x0)
r1=dot(A,x1)        
## Remove Ax from each interferogram
X,Y=meshgrid(r_[0:dS[1]], r_[0:dS[0]])
tk=0
for k in xrange(N):
  surface=pi*( r0[k]*Y + r1[k]*X )
  p=adore.getProduct(i12sd[k],process)  #product
  dp=p*exp(-1.j*surface)                 #deramped product
  adore.writedata(i12sd[k][process]['Data_output_file']+'deramp', dp, 'cr4')
  call(['modifyRes.sh',ifiles[k], process, 'Data_output_file', i12sd[k][process]['Data_output_file']+'deramp']) 
  if basic.progresstime(tk):
    basic.progress(k,N,);tk=basic.time.time()
  