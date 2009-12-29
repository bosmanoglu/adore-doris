package functions;

###################################
###	   functions.pm	        ###
###################################

###################################
### This perl module includes	###
### general functions commonly	###
### used by Adore.		### 
###				### 
###	ADORE			###
### Automated DORis Environment ###
### 				###
### Batuhan Osmanoglu		###
###		CSTARS 2007	###
###################################

###################################
###		To-Do		###
###	-Get Orbit List Problem	###
###################################

require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw();
@EXPORT_OK = qw(ReadSettingsFile PrintAdore);

use warnings; use strict; use Data::Dumper;
use File::Path;

sub ReadSettingsFile;
sub ModifyFiles;
#sub Clear;
sub PrintAdore;

sub PrintAdore{
print "AdoreAdoreAdore\n";
}

sub ReadSettingsFile(){
	$ProjectFile = @_;
	open(FH_settings, $ProjectFile) or die ("Could not open project file!");	### FH_settings=FileHandle_settings
	@Settings_=<FH_settings>;
	if ($debug) {print "DEBUG: Project Settings are:\n @Settings_\n";}

	foreach $setting_ (@Settings_)
	{
		chomp($setting_);
		$setting_ =~ s/^c\s.*//i ; ### Remove comment lines starting with c or C
		$setting_ =~ s/ccc.*//i; ### Remove comments following a setting. Starts with ccc or CCC
		$setting_ =~ s/^\s*$//  ; ### Remove White Space (Blank Lines)
		$setting_ =~ s/\/$//;	 ### Remove trailing slash (For Folder Names)
		if ($debug) {print "Read Setting: $setting_\n"};
		if (! $setting_) {next;}	### Skip Comment Lines	
		($parameter_, $value_)=split(/\s/,$setting_);	#read each parameter and value from file
		if ($debug) {print $parameter_ . " = " . $value_ ."\n";} 
		$Settings{$parameter_} = $value_;
		if ($debug) {print "Hash ". $Settings{$parameter_} . "\n"};
	}
	close(FH_settings);
	return %Settings;
}
1;



