% This function creates filters using matlab.
% createKernel(windowHandle, size, filename)
% 
% windowHandle: any window handle that the window function accepts. 
% (ex. @hamming, @gausswin etc.)
% n: window size. (ex. 8)
% filename: name of the output file.
%
% See Also:
%  window
%
% Example:
%   createKernel(@hamming, 8, 'filter_hamming_2D_8_8')
%
% References:
% Doris Users Manual v4.02 p.94
%
% M file by Batuhan Osmanoglu, Mar 2010.
function createKernel(windowHandle, n, filename)

f=window(windowHandle, n);
f=f*f.';
fid=fopen(filename, 'w');
fprintf(fid, '%i %i 1.0\n', n,n);
for ii=1:n
    fprintf(fid, '%4.2f ', f(ii,:));
    fprintf(fid, '\n');
end
