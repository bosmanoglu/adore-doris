ADORESCR=getenv('ADORESCR');
[ADOREFOLDER,~,~]=fileparts(ADORESCR)
addpath(genpath(strcat(ADOREFOLDER,filesep, 'lib', filesep, 'matlab')));
tmpFolder=getenv('tmpFolder');

settings=ini2struct(strcat(tmpFolder,filesep, 'settings.set'));

try
  mres=dorisResult2Struct(settings.general.m_resfile); %strcat(settings.adore.outputFolder, filesep, settings.adore.master, '.res'));
catch
  mres=struct();
end
try
  sres=dorisResult2Struct(settings.general.s_resfile); %strcat(settings.adore.outputFolder, filesep, settings.adore.slave, '.res'));
catch
  sres=struct();
end
try
  ires=dorisResult2Struct(settings.general.i_resfile); %strcat(settings.adore.outputFolder, filesep, settings.adore.master,'_', settings.adore.slave, '.res'));
catch
  ires=struct();
end
clear tmpFolder
    
