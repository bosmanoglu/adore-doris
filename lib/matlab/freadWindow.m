function [output]=freadWindow(varargin)
%
% USAGE:
%   A=freadWindow(fid, sizeA, precision, skip, machineformat, Window)
%
% Description:
%   This function tries to expand capabilities of matlabs "fread" function
%   by adding optional Windowing. For Windowing row and column numbering
%   starts from 1.
%
%   fid: file pointer
%
%   sizeA: fread's size ([fileCols,fileRows]) is in column order. And since
%     freadWindow is based on that number of Columns are specified first.
%     (default [fileSize, 1])
%
%   precision: byte-format of the data, int8, int16, uint16 etc. 
%     (default 'uint8=>double')
%
%   skip: skip given number of bytes after each read. (default 0)
%
%   machineformat: little or big endian file. (default is 'native').
%
%   Window: given as [firstCol, lastCol, firstRow, lastRow]. (default [],
%     all data).
%
% See Also:
%   fread
%
% Author:
% Batuhan Osmanoglu, June 2008, RSMAS, Miami
%

p=inputParser;
p.addRequired('fid', @isnumeric);
p.addOptional('count', [], @isnumeric);
p.addOptional('precision', 'uint8', @ischar);
p.addOptional('skip', [], @isnumeric);
p.addOptional('machineformat', 'native', @ischar);
p.addOptional('window', [], @isnumeric);
p.parse(varargin{:});

fid=p.Results.fid;
count=p.Results.count;
if isempty(count)
    fseek(fid,0,'eof');
    filewidth=ftell(fid);   %FileCols
    filelength=1;           %FileRows
    count=[filewidth, filelength];
end
precision=p.Results.precision;
skip=p.Results.skip;
if isempty(skip)
    skip=zeros(size(count));
else
    %check if count and skip is the same size
    if ~isequal(size(count), size(skip))
        error('SizeA and skip should be the same size');
    end
end
machineformat=p.Results.machineformat;
Window=p.Results.window;

%[fid, count, precision, skip, machineformat, Window]=handle_input(varargin{:});

if isempty(Window) && ~all(skip) %if window is empty and skip is zeros.
    % We do not skip using the standard fread because if the file size is
    % not divisible by the skip+1 we have to read the file line by line.
    % Otherwise we have offset errors.
    % Ex.
    % FileSize=125x125 (real4).
    % requested skip 1 sample (4 bytes)
    % Output should be 62x62 but each line has 62*(skipInBytes+1)+1=125
    % element. Therefore we read the last px of the first line when we need
    % to read the first element of the second line. 
    output=fread(fid, count, precision, machineformat);
else
    if numel(count)~=2
        error('Please specify [filelength, filewidth] in second parameter.');
    end
    eval(['sample=' precision '(1);']);
    sizeInSamples=getByteSize(sample);
    skipInSamples=(skip./sizeInSamples); %aka. number of samples to skip.

    if isempty(Window) && any(skip)     
        outputSize=fliplr(fix(count./(skipInBytes+1)));        
    elseif ~isempty(Window) && ~any(skip) %skip is all zeros == ~any(skip)
        outputSize=[Window(4)-Window(3)+1, Window(2)-Window(1)+1];%LastRow-FirstRow+1, LastCol-FirstCol+1
    else %both window and skip defined.
        outputSize=[round((Window(4)-Window(3)+1)/(skipInSamples(2)+1)), ...
                    round((Window(2)-Window(1)+1)/(skipInSamples(1)+1))];
    end    
    output=zeros(outputSize);
    if isempty(Window)
        Window=[1 count(1) 1 count(2)];
    end   
    rowOffset=Window(3)-1;  %firstRow-1 in samples
    colOffset=Window(1)-1;  %firstCol-1 in samples
    
    for r=Window(3):skipInSamples(2)+1:Window(4) %firstRow:lastRow
        %offst=((r-1)*fileCols+colOffset)*sizeInBytes;
        offset=((r-1)*count(1)+colOffset)*sizeInSamples;%Replaced rowOffset with (r-1) since this needs to be calculated every time.        
        fseek(fid, offset, 'bof');
        %Read that row. 
%         if skipInSamples(2)==0
%             output(r-rowOffset,:)=fread(fid, outputSize(2), precision, skip(1), machineformat);   
%         else
%             output((r-rowOffset)/(skipInSamples(2)),:)=fread(fid, outputSize(2), precision, skip(1), machineformat);        
%         end
        rowNumber=(r-rowOffset)- (r-rowOffset-1)*skipInSamples(2)/(skipInSamples(2)+1);
        output(rowNumber,:)=fread(fid, outputSize(2), precision, skip(1), machineformat);   
    end
    output=output.'; %Make output Column Order just like fread!.
end

end
function [fid, count, precision, skip, machineformat, Window]=handle_input(varargin)

if nargin<1 || nargin>6
    error('Wrong number of input parameters!');
elseif nargin==1    
    fid=cell2mat(varargin(1));   
    fseek(fid,0,'eof');
    filewidth=ftell(fid);   %FileCols
    filelength=1;           %FileRows
    count=[filewidth, filelength];
    precision='uint8';
    skip=0;
    machineformat='native';
    Window=[];
elseif nargin==2    
    fid=cell2mat(varargin(1));   
    count=cell2mat(varargin(2));
    if ischar(count)    %actually precision is given.
        precision=count;
        fseek(fid,0,'eof');
        filewidth=ftell(fid);   %FileCols
        filelength=1;           %FileRows
        count=[filewidth, filelength];
    else
        precision='uint8';
    end
    skip=0;
    machineformat='native';    
    Window=[];
elseif nargin==3
    fid=cell2mat(varargin(1));
    count=cell2mat(varargin(2));
    if ischar(count)    %size is skipped, precision and skip is given.
        precision=count;
        fseek(fid,0,'eof');
        filewidth=ftell(fid);   %FileCols
        filelength=1;           %FileRows
        count=[filewidth, filelength];
        if ischar(cell2mat(varargin(3)))
            machineformat=cell2mat(varargin(3));
            skip=0;
        else
            skip=cell2mat(varargin(3));
            machineformat='native';    
        end
    else
        precision=cell2mat(varargin(3));        
        skip=0;
        machineformat='native';    
    end
    Window=[];    
elseif nargin==4
    fid=cell2mat(varargin(1));
    count=cell2mat(varargin(2));
    if ischar(count)    %size is skipped, precision and skip is given.
        precision=count;
        fseek(fid,0,'eof');
        filewidth=ftell(fid);   %FileCols
        filelength=1;           %FileRows
        count=[filewidth, filelength];
        if ischar(cell2mat(varargin(3)))
            machineformat=cell2mat(varargin(3));
            skip=0;
        else
            skip=cell2mat(varargin(3));
            if ischar(cell2mat(varargin(4)))
                machineformat=cell2mat(varargin(4));
                Window=[];
            else
                machineformat='native';
                Window=cell2mat(varargin(4));
            end
        end
    else        
        precision=cell2mat(varargin(3));
        if ischar(cell2mat(varargin(4)))
            skip=0;
            machineformat=cell2mat(varargin(4));
            Window=[];
        else
            machineformat='native';
            if numel(cell2mat(varargin(4)))==1
                skip=cell2mat(varargin(4));
                Window=[];
            else
                skip=0;
                Window=cell2mat(varargin(4));
            end
        end
    end
elseif nargin==5
    
    fid=cell2mat(varargin(1));
    count=cell2mat(varargin(2));
    if ischar(count)    %size is skipped, precision and skip is given.
        precision=count;
        fseek(fid,0,'eof');
        filewidth=ftell(fid);   %FileCols
        filelength=1;           %FileRows
        count=[filewidth, filelength];
        if ischar(cell2mat(varargin(3)))
            machineformat=cell2mat(varargin(3));
            skip=0;
        else
            skip=cell2mat(varargin(3));
            if ischar(cell2mat(varargin(4)))
                machineformat=cell2mat(varargin(4));
                Window=cell2mat(varargin(5));
            else
                error('Wrong number/order of input parameters.'); %4th may be Window, then what is 5th???
            end
        end
    else        
        precision=cell2mat(varargin(3));
        if ischar(cell2mat(varargin(4)))
            skip=0;
            machineformat=cell2mat(varargin(4));
            Window=cell2mat(varargin(5));
        else
            skip=cell2mat(varargin(4));
            if ischar(cell2mat(varargin(5)))
                machineformat=cell2mat(varargin(5));
            else
                machineformat='native';
                Window=cell2mat(varargin(5));
            end
        end
    end
elseif nargin==6
    fid         =cell2mat(varargin(1));
    count       =cell2mat(varargin(2));
    precision   =cell2mat(varargin(3));
    skip        =cell2mat(varargin(4));
    machineformat=cell2mat(varargin(5));
    Window      =cell2mat(varargin(6));
end

end