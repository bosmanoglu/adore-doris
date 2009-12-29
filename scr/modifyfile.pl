#!/usr/bin/perl -w
###################################
###     modifyfile.pl           ###
###################################

###################################
### This perl script modifies   ###
### given file using a parameter###
### file.			###
###                             ### 
###     ADORE                   ###
### Automated DORis Environment ###
###                             ###
### Usage: modifyfile.pl inputfile parameterfile###
###                             ###
### Batuhan Osmanoglu           ###
###             CSTARS 2007     ###
###################################

use warnings; use strict; use Data::Dumper;
use File::Path;

sub Usage;
sub ModifyTemplate;
sub ReadProjectSettings;

###################################
###     Read input arguments    ###
###################################
use Getopt::Long;
@ARGV >= 1 or Usage();
my $InputFile; my $ParameterFile; my $debug;
GetOptions('i=s' => \$InputFile,'p=s' => \$ParameterFile, 'debug' =>\$debug);

if (! $InputFile) {&Usage();}
if (! $ParameterFile) {&Usage();}

%Settings=&ReadProjectSettings($ParameterFile);
&ModifyTemplate($InputFile



###
### ReadProjectSettings
###
sub ReadProjectSettings {
	# Requires:
	#	- Project Settings Input Name
	#
	my $ProjectFile;
	my $setting_; my $parameter_; my $value_;
	my @Settings_;

	$ProjectFile = shift;
	
	open(FH_settings, $ProjectFile) or die ("Could not open project file!");	### FH_settings=FileHandle_settings
	@Settings_=<FH_settings>;
	
	if ($debug) {print "DEBUG: Project Settings are:\n @Settings_\n";}

	foreach $setting_ (@Settings_)
	{
		chomp($setting_);
		$setting_ =~ s/^c\s.*//i ; ### Remove comment lines starting with c or C
		$setting_ =~ s/\s*ccc.*//i; ### Remove comments following a setting. Starts with ccc or CCC
		$setting_ =~ s/^\s//  ; ### Remove White Space (Blank Lines)
		$setting_ =~ s/\/$//;	 ### Remove trailing slash (For Folder Names)
		if (! $setting_) {next;}	###If nothing left go to next
		if ($debug) {print "Read Setting: $setting_\n"};
		if (! $setting_) {next;}	### Skip Comment Lines	
		($parameter_, $value_)=split(/=/,$setting_);	#read each parameter and value from file
		if ((! $value_) && ($parameter_)){next;}		###If no value, skip setting
		if ($debug) {print $parameter_ . " = " . $value_ ."\n";} 
		$Settings{$parameter_} = $value_;
		if ($debug) {print "Placed in Hash as " .$parameter_ . " -> " . $Settings{$parameter_} . "\n";}
	}
	close(FH_settings);
	undef($parameter_); undef($value_);undef($setting_);undef(@Settings_);
	
	$Settings{"DataFolder"} = $Settings{"ProjectFolder"} . "/data";
	$Settings{"ScriptsFolder"} = $Settings{"AdoreFolder"} . "/scripts";
	if ($debug) {print "DEBUG: Project Folder is:". $Settings{"ProjectFolder"} . "\n";}
	### If no master orbit specified pick the first one as master for initial processing.
	if (! $Settings{"MasterFolder"}) {
		chdir $Settings{"DataFolder"} or die "Non-existing data folder: " . $Settings{"DataFolder"}. "\n";
		my $slclist_ = `/bin/ls -F | grep "/"`;
		my @SLCFolder= split /\n/, $slclist_;
		$Settings{"MasterFolder"} = $SLCFolder[0];
		$Settings{"MasterFolder"} =~ s/\/$//;
	}
	return %Settings;
}

###
### ModifyTemplate
###
sub ModifyTemplate {
	### Requires 
	### 	-inputfile (the template to be modified, templatefile),
	###	 	-outputfolder (crops/ifgs)  
	###		-outputfile (for each frame)
	###		-batchfile (to add command to list)
	my $templatefile_ = shift;
	my $outputfolder_ = shift; 	
	my $outputfile_ = shift;
	my $batchfile_ = shift;
	
	
	### Get list of SLC Folders
	chdir $Settings{"DataFolder"} or die "Non-existing data folder: " . $Settings{"DataFolder"}. "\n";
	my $slclist_ = `/bin/ls -F | grep "/"`;
	my @SLCFolder= split /\n/, $slclist_;

	if ($debug) {print "DEBUG: Listed Data Folders are: @SLCFolder\n";}

	### Modify Template
	open(FH_templatefile, $templatefile_) or die ("Could not open $templatefile_ template file!");
	my @templatefilelines_; my $line_;	
	@templatefilelines_ = <FH_templatefile>;
	my $folder_; my $parameter_; my $value_;

	### Generate Process folder if necessary...
	mkpath($Settings{"ProjectFolder"} . "/process/crops");
	mkpath($Settings{"ProjectFolder"} . "/process/i12s");

	if ( -e $batchfile_ ) {
		open(FH_batchfile, ">>". $batchfile_) or die ("Could not open run_batch.sh template file!");
	}
	else {
		open(FH_batchfile, ">". $batchfile_) or die ("Could not open run_batch.sh template file!");
		print FH_batchfile "\#!/bin/bash \n";		### INITIALIZE BATCH FILE
		&RunCommandLine('chmod a+x ' . $batchfile_);
	}
	foreach $folder_ (@SLCFolder)
	{
		$folder_ =~ s/\/$//;					#REMOVE TRAILING SLASH
		#chdir $folder_ or die "Can not change directory: $folder_!\n";
		if ($debug) {print "DEBUG: In $folder_\n"}; 
		seek FH_templatefile, 0,0;
		mkdir($Settings{"ProjectFolder"} . $outputfolder_ . $folder_);
		open(FH_templateSLC, ">" . $Settings{"ProjectFolder"} . $outputfolder_ . $folder_ ."/". $outputfile_ ) or die ("Could not create readdata.input file in process directory!");
		foreach $line_ (@templatefilelines_)
		{
			my $_line_ = $line_;				### Don't change the original buffer.
			$_line_ =~ s/SLCFolder/$folder_/g;	### Replace SLCFolder
			if ($_line_ =~ /^\s*c/) {next;}
			while ( ($parameter_, $value_) = each(%Settings) ) {
	     	   		$_line_ =~ s/$parameter_/$value_/g;	### Replace Setting Values...
	    		}
			print FH_templateSLC $_line_;
			if ($debug) {print $_line_;}
			
		}
		close(FH_templateSLC);
		### Add doris run to batch file. 
		print FH_batchfile $Settings{"AdoreFolder"} . "/doris/doris " . $Settings{"ProjectFolder"} . "/process/crops/" . $folder_ . "/" . $outputfile_ . "\n";
	}
	close(FH_batchfile);	
	close(FH_templatefile);
	undef($slclist_);undef(@templatefilelines_); undef($line_); undef(@SLCFolder);undef($parameter_); undef($value_);
	undef($templatefile_);undef($outputfolder_);undef($outputfile_);undef($batchfile_);
}
