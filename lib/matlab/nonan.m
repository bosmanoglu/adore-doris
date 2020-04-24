function [rvar]=nonan(varargin)
% Usage:
%   [output]=nonan(input, ['rows'])
% Description:
%   Returns input variable free of NaN's. 
% If you specify the 'rows' option and provide a matrix as input, output
% does not have any rows with NaN values in any column.
%
% Author:
% Batuhan Osmanoglu
% RSMAS, June 2008

%Read Input variables
dorows=0;   %Initialize dorows
if nargin==2
    dorows=1;
elseif (nargin > 2) && (nargin < 1)
    error('Wrong number of input arguments!');
end
% var=cell2mat(varargin(1));
var=varargin{1};

if dorows==0
%     rvar=var(find(isnan(var) ~= 1));
    rvar=var(isnan(var) ~= 1);
else
%     [r,c]=find(isnan(var) == 1);
%     clear c;
%     r=unique(r);
%     rows=1:1:size(var,1);
%     rows=setdiff(rows,r);
%     rvar=var(rows,:);
    rvar=var(any(~isnan(var.')),:);
end