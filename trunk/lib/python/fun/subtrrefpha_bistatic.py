cint=adore.getProduct(ires, 'interfero');
x=linspace(-2,2,cint.shape[0])
y=linspace(-2,2,cint.shape[1])
Y,X=meshgrid(y,x);
refpha=adore.polyval(X,Y, ires['comp_refphase']['Estimated_coefficients_flatearth']);
srp=cint*exp(-1j*refpha/2);
adore.writedata(ires['subtr_refphase']['Data_output_file'], srp, 'cr4');
