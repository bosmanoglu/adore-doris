function [StructName]=dorisResult2Struct(resfile)
%
% Usage: 
%   [StructName]=dorisResult2Struct(resfile)
%
% Description:
%   This function reads the Doris Result File (resfile) into a struct
%   similar to igram. It does not read the data file (since there are many
%   in resfile).
%
% resfile: Can be a single file (string) or an array of strings. Can also
% be a cell array of strings.
% StructName: is an array of structs. If resfile only includes one filename
% the array is 1X1. 
%
%
% Example:
%

% Get resfiles
if ~iscellstr(resfile)
    resfileCell=cellstr(resfile);
else
    resfileCell=resfile;
end %if
clear resfile;

for k=1:size(resfileCell,1);
    tmpStruct=ReadProcessList(resfileCell{k});
    StructName(k)=tmpStruct;
end % for

end%end Function

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%    ReadProcessList
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function tmpStruct=ReadProcessList(resfile)
% get filenameForResFile
[pathstr, resfilename, ext]=fileparts(resfile);
tmpStruct.resfile=resfilename;
tmpStruct.inputfile=resfile;
if exist(resfile,'file')==0
   fprintf('exiting --- file %s does not exist',resfile);
   return
end

processFlag=0;  %Initialize Process Flag.

[resLines]=textread(resfile,'%s','delimiter','\n');
for k=1:length(resLines)
    lineBuffer=resLines{k};
    
    if strfind(lineBuffer, 'Start_process_control') > 0 %Process Flag must be before this line.
        processFlag=1;
        continue;
    elseif strfind(lineBuffer, 'End_process_control') > 0
        break;
    elseif processFlag==1;
        tmpStruct=ReadProcess(resLines, k, tmpStruct);
    else
        continue;
    end 
end

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%    ReadResField
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [fieldname, outfield]=ReadResField(lineBuffer)
    % Remove trailing comment if exists... "// comment"
    location_of_comment=(min(strfind(lineBuffer, '//')));
    if (location_of_comment > 0) lineBuffer=lineBuffer(1:location_of_comment-1); end
        
    location_of_column=max(strfind( lineBuffer, ':' ));
    fieldname=lineBuffer(1:location_of_column-1);
    if sum(isletter(lineBuffer(location_of_column+1:end))) == 0
        location_of_comma=max(strfind(lineBuffer(location_of_column+1:end), ','));
        if location_of_comma
            location_of_comma = location_of_comma + location_of_column;
            outfield=zeros(2,1);
            outfield(1,1) = str2double(lineBuffer(location_of_column+1:location_of_comma));
            outfield(2,1) = str2double(lineBuffer(location_of_comma +1:end));
        else
            outfield = str2double(lineBuffer(location_of_column+1:end));
        end
    else
        outfield=strtrim(lineBuffer(location_of_column+1:end));
    end
end    

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%    ReadProcess
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function [tmpStruct]=ReadProcess(reslines, k, tmpStruct)
lineBuffer=reslines{k};
[processName, processValue]=ReadResField(lineBuffer);
if processValue==1    %If processed
    if strfind(processName, 'readfiles')> 0
        readFields={'Scene_centre_latitude', 'Scene_centre_longitude',...
             'Radar_wavelength', 'First_pixel_azimuth_time', 'Pulse_Repetition_Frequency',...
             'Total_azimuth_band_width','Xtrack_f_DC_constant', 'Xtrack_f_DC_linear',...
             'Xtrack_f_DC_quadratic', 'Range_time_to_first_pixel', 'Range_sampling_rate',...
             'Total_range_band_width','Datafile','Number_of_lines_originalNumber_of_lines_original',...
             'Number_of_pixels_original'};
    elseif strfind(processName, 'precise_orbits')> 0
        readFields={'NUMBER_OF_DATAPOINTS'};
        tmpStruct.(str2fieldname(processName)).stateVectors=...
             readDorisResultFile(tmpStruct.inputfile, 'stateVectors',processName);
    elseif strfind(processName, 'crop')> 0
        readFields={'Data_output_file','Data_output_format','First_line'...
            'Last_line','First_pixel','Last_pixel'};
    elseif strfind(processName, 'resample')> 0
        readFields={'Shifted azimuth spectrum','Data_output_file','Data_output_format','First_line'...
            'Last_line','First_pixel','Last_pixel', 'Interpolation kernel'};
    elseif strfind(processName, 'filt_azi')> 0
        readFields={'Input_file','Data_output_file','Data_output_format',...
            'First_line','Last_line','First_pixel','Last_pixel'};
    elseif strfind(processName, 'coarse_orbits')> 0
        readFields={'Btemp', 'Bperp','Bpar', 'Bh', 'Bv', 'B', 'alpha', 'theta', 'inc_angle', 'orbitconv',...
            'Height_amb', 'Coarse_orbits_translation_lines', 'Coarse_orbits_translation_pixels'};
        %writeFields=readFields;
    elseif strfind(processName, 'coarse_correl') > 0
        readFields={'Coarse_correlation_translation_lines', 'Coarse_correlation_translation_pixels'};
        %writeFields=readFields;
    elseif strfind(processName, 'fine_coreg') >0
        readFields={'Initial offsets', 'Window_size_L_for_correlation', 'Window_size_P_for_correlation', ...
            'Max. offset that can be estimated', 'Peak search ovs window', 'Oversampling factor', ...
            'Number_of_correlation_windows'};
        %writeFields={'Initial offsets', 'Window_size_L_for_correlation', 'Window_size_P_for_correlation', 'Max offset that can be estimated', 'Peak search ovs window', 'Oversampling factor', 'Number_of_correlation_windows'};
    elseif strfind(processName, 'comp_coregpm') >0        
        readFields={'Degree_cpm'};
        %writeFields={'Degree_cpm'};
    elseif strfind(processName, 'interfero') > 0
        readFields={'Master Result File', 'Slave Result File', 'Earth Radius', 'Near Range', ...
            'Satellite Altitude', 'Data_output_file', 'Data_output_format', ...
            'Flatearth correction subtracted', 'First_line','Last_line','First_pixel', 'Last_pixel',...
            'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', 'Number of lines', ...
            'Number of pixels'};
        %writeFields=readFields;
    elseif strfind(processName, 'coherence') >0
        readFields={'Data_output_file','Data_output_format','First_line','Last_line','First_pixel', ...
            'Last_pixel', 'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', ...
            'Number of lines', 'Number of pixels'};
        %writeFields=readFields;
    elseif strfind(processName, 'comp_refphase') >0
        readFields={'Degree_flat','Degree_h2ph'};
        %writeFields=readFields;
    elseif strfind(processName, 'subtr_refphase') > 0
        readFields={'Data_output_file','Data_output_format','First_line','Last_line','First_pixel', ...
            'Last_pixel', 'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction',...
            'Number of lines', 'Number of pixels'};
        %writeFields=readFields;
    elseif strfind(processName, 'comp_refdem') > 0
        readFields={'Method', 'flat earth', 'DEM source file', 'Min. of input DEM','Max. of input DEM',...
            'Data_output_file','Data_output_format','First_line','Last_line','First_pixel', 'Last_pixel',...
            'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', 'Number of lines', ...
            'Number of pixels'};
        %writeFields={'Method', 'flat earth', 'DEM source file', 'Min of input DEM','Max of input DEM','Data_output_file','Data_output_format','First_line','Last_line','First_pixel', 'Last_pixel', 'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', 'Number of lines', 'Number of pixels'};
    elseif strfind(processName, 'subtr_refdem') > 0
        readFields={'Method', 'Additional_azimuth_shift', 'Additional_range_shift', 'Data_output_file', ...
            'Data_output_format', 'First_line','Last_line','First_pixel', 'Last_pixel', ...
            'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction',...
            'Number of lines', 'Number of pixels'};
    elseif strfind(processName, 'filtphase') > 0
        readFields={'Input_file','Data_output_file','Data_output_format','First_line','Last_line',...
            'First_pixel', 'Last_pixel', 'Multilookfactor_azimuth_direction', ...
            'Multilookfactor_range_direction', 'Number of lines', 'Number of pixels'};
        %writeFields={'Input_file','Data_output_file','Data_output_format','First_line','Last_line','First_pixel', 'Last_pixel', 'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', 'Number of lines', 'Number of pixels'};
    elseif strfind(processName, 'unwrap') > 0
        readFields={};
    elseif strfind(processName, 'slant2h') >0 
        readFields={'Method', 'Data_output_file','Data_output_format','First_line','Last_line',...
            'First_pixel', 'Last_pixel', 'Multilookfactor_azimuth_direction', ...
            'Multilookfactor_range_direction', 'Ellipsoid'};
        %writeFields={'Method', 'Data_output_file','Data_output_format','First_line','Last_line','First_pixel', 'Last_pixel', 'Multilookfactor_azimuth_direction', 'Multilookfactor_range_direction', 'Ellipsoid'};
    elseif strfind(processName, 'geocoding') > 0
        readFields={};
    elseif strfind(processName, 'dinsar') > 0
        readFields={};
    else
        disp(['Unknown process: ' processName]); 
        return;
    end
    
    %find the location of process record on the file.
    resultCell=strfind(reslines, ['_Start_' processName]);
    resultMat=cellfun('isempty', resultCell);
    startIndex=find(resultMat==0);
    
    resultCell=strfind(reslines, ['End_' processName]);
    resultMat=cellfun('isempty', resultCell);
    endIndex=find(resultMat==0);
    
    %Now Read lines between startIndex and endIndex and add to the structure   
    for k=1:length(readFields)
        resultCell=strfind(reslines(startIndex:endIndex), readFields{k});
        resultMat=cellfun('isempty', resultCell);        
        fieldIndex=find(resultMat==0);
        validProcessName=regexprep(processName, '[\s\]\[]*','_');
        validProcessName=regexprep(validProcessName, '_$', '');
        validField=regexprep(readFields{k}, '[*\s\]\[.]*','_'); %Translate all whitespace and brackets to underscore
        validField=regexprep(validField, '_$', ''); %Remove Last underscore
        if ~isempty(fieldIndex)
            fieldBuffer=reslines{startIndex+fieldIndex-1};
            [Field, Value]=ReadResField(fieldBuffer);                    
            tmpStruct.(validProcessName).(validField)=Value;
        else
            tmpStruct.(validProcessName).(validField)=[];
        end
    end
end

end
