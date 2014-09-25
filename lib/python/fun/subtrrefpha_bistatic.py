import insar
cint=adore.getProduct(ires, 'interfero');
srp_multilook=[0,0];
srp_multilook[0]=int(setobj.subtrrefpha.srp_multilook.strip('"').split(" ")[0]);
srp_multilook[1]=int(setobj.subtrrefpha.srp_multilook.strip('"').split(" ")[1]);
if srp_multilook!=[1,1]:
  cint=insar.multilook(cint, srp_multilook);
x=linspace(-2,2,cint.shape[0]);
y=linspace(-2,2,cint.shape[1]);
Y,X=meshgrid(y,x);
refpha=adore.polyval(X,Y, ires['comp_refphase']['Estimated_coefficients_flatearth']);
srp=cint*exp(-1j*refpha/2);
adore.writedata(ires['subtr_refphase']['Data_output_file'], srp, 'cr4');

