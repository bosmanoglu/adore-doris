function [output]=readDorisDataFile(varargin)
% Usage:
%   [output]=readDorisDataFile(inputfilename, inputformat, datawidth, datalength, [FirstRow, LastRow, FirstCol, LastCol])
%   [output]=readDorisDataFile(dorisStruct, [FirstRow, LastRow, FirstCol, LastCol]);
%
% Description:
%   This function reads individual Doris data output files. The parameters
%   are:
%   InputFileName:  Data file to read
%   InputFormat:    Input format of the data file (i.e. 'complex_real4')
%   DataWidth:      Width of the data file (i.e. 4000, read from .res
%   file:Number of pixels)
%   DataLength:     Length of the data file (i.e. 9000, read from .res
%   file:Number of lines)
%   Optional Parameters: 
%       window: [FirstCol, LastCol, FirstRow, LastRow]
%   output: Output Data in matrix format. 
%
% Also See:
% freadWindow, doris2igram
% 
% Author:
% Batuhan Osmanoglu, RSMAS, 2008.
% Modified - June 2008: Added Window capability.

%%% Get input parameters
window=[];FLIP=0;
if nargin==1 || nargin==2
    ts=varargin{1}; %temporary structure.
    inputfilename=ts.Data_output_file;
    inputformat=ts.Data_output_format;
    if isfield(ts, 'Number_of_lines')
        datalength=ts.Number_of_lines;
        datawidth=ts.Number_of_pixels;
    else
        if isfield(ts,'Multilookfactor_azimuth_direction')
            datalength=floor((ts.Last_line-ts.First_line+1)./ts.Multilookfactor_azimuth_direction);                    
        else
            datalength=(ts.Last_line-ts.First_line+1);
        end
        if isfield(ts,'Multilookfactor_range_direction')
            datawidth=floor((ts.Last_pixel-ts.First_pixel+1)./ts.Multilookfactor_range_direction);
        else
            datawidth=ts.Last_pixel-ts.First_pixel+1;
        end
    end
    if nargin==2
        window=cell2mat(varargin(2));
    end
elseif nargin==4 || nargin==5
    inputfilename=cell2mat(varargin(1));
    inputformat=cell2mat(varargin(2));
    datawidth=cell2mat(varargin(3));
    datalength=cell2mat(varargin(4));    
    if nargin==5
        if strcmpi(varargin{5}, 'flip')
            FLIP=1;
        else
            FLIP=0;
            window=cell2mat(varargin(5));
        end
    else
        FLIP=0;
    end
else
    error('Wrong number of input parameters. Please type: "help ReadDorisDataFile"');
end

%%% Check if file exist
if ~exist(inputfilename, 'file')
    error(['File does not exist. Reading File: ' inputfilename]);
end
%%% Read File

fid_input = fopen(inputfilename);

%switch over real cases
switch inputformat
    case 'int16'
        output = freadWindow(fid_input, [datawidth,datalength], 'int16', window);
    case 'int32'
        output = freadWindow(fid_input, [datawidth,datalength], 'int32', window);
    case 'uint'
        output = freadWindow(fid_input, [datawidth,datalength], 'uint32', window);
    case 'real4'
        output = freadWindow(fid_input, [datawidth,datalength], 'single', window);
    case 'real8'
        output = freadWindow(fid_input, [datawidth,datalength], 'double', window);
end

if isempty(who('output'))   %If above switch case was not active.
    if ~isempty(window)     %Modify Window for complex data
        window=[2*window(1)-1 2*window(2) window(3) window(4)];
    end
    datasize=[datawidth*2,datalength];
    if FLIP==1; datasize=fliplr(datasize);end
    switch inputformat      %Switch over complex formats..
        case 'complex_short'
            p = freadWindow(fid_input, datasize, 'int16', window);
            output = complex(p(1:2:end,:),p(2:2:end,:));
        case 'compli32'
            p = freadWindow(fid_input, datasize, 'int32', window);
            output = complex(p(1:2:end,:),p(2:2:end,:));
        case 'complex_real4'
            p = freadWindow(fid_input, datasize, 'single', window);
            output = complex(p(1:2:end,:),p(2:2:end,:));
        case 'complex_real8'
            p = freadWindow(fid_input, datasize, 'double', window);
            output = complex(p(1:2:end,:),p(2:2:end,:));
        case 'hgt'
            p = freadWindow(fid_input, datasize, 'uint32', window);
            %Amp=p(1:width,:);  %Amplitude
            %output = p(width+1:2*width,:); %Unwrapped Phase
            % MODIFIED FOR WINDOWING output = complex(p(1:datawidth,:), p(datawidth+1:2*datawidth,:));
            windowWidth=window(2)-window(1);
            output=complex(p(1:windowWidth,:), p(windowWidth+1:end,:));
    end
end
fclose(fid_input);
end
