function newarr=rescale(arr, lim, varargin)
%rescale(array, limits, trim=False, arrlim=None)
%    scale the values of the array to new limits ([min, max])
%    Trim:
%      With this option set to a number, the limits are stretced between [mean-TRIM*stdev:mean+TRIM*stdev]
p=inputParser;
p.addParamValue('trim', 0, @isnumeric);
p.addParamValue('arrlim', 0, @isnumeric);
p.parse(varargin{:});

if p.Results.arrlim ~=0
    minarr=arrlim(1);
    maxarr=arrlim(2);
end
if p.Results.trim > 0
    m=mean(arr(:));
    s=std(arr(:));
    minarr=m-p.Results.trim*s;
    maxarr=m+p.Results.trim*s;
elseif ( (p.Results.trim==0) && (p.Results.arrlim==0) )
    minarr=min(arr(:));
    maxarr=max(arr(:));
end

newarr = (arr-minarr) / (maxarr-minarr)*(lim(2)-lim(1))+lim(1);
newarr(newarr<lim(1))=lim(1);
newarr(newarr>lim(2))=lim(2);
end


    