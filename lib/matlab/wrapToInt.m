function A=wrapToInt(A,I)
A=mod(A+I,2*I)-I;
end