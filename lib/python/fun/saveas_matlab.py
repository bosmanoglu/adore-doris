import scipy
import scipy.io
p=setobj._ipy_.process;
process=A.pn2rs[p];
matlabDict=A.ires[process].copy()
try:
  dorisFile=adore.getProduct(A.ires, process);
  matlabDict[p]=dorisFile;
except:
  print('No output files exist for step: %s', process);

scipy.io.savemat(p, matlabDict,  appendmat=True); 

