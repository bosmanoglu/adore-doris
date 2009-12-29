#!/usr/bin/perl -w
###################################
###	   findmaster.pl	###
###################################

###################################
### This perl script selects    ###
### a master scene based on 	###
### baseline information	### 
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

use warnings; use strict; use Data::Dumper;
use File::Path;

sub Usage;
sub ReadProjectSettings;
sub BaselineAnalysis;

###################################
###	Read input arguments    ###
###################################
use Getopt::Long;
@ARGV >= 1 or &Usage;
my $ProjectFile; my @Settings_; my $debug; my $clear;
my $setting_; my $parameter_; my $value_;
my %Settings =();								### Initialize Hash

GetOptions('ps=s' => \$ProjectFile, 'debug' =>\$debug); 
if ($debug) {print "DEBUG: Project Settings are in: $ProjectFile\n";}

&ReadProjectSettings();                                                                                 ### Will put settings in %Settings Hash

chdir $Settings{"DataFolder"} or die "Non-existing data folder: " . $Settings{"DataFolder"}. "\n";
my $slclist_ = `/bin/ls -F | grep "/"`;
my @SLCFolder= split /\n/, $slclist_;  
foreach my $folder_ (@SLCFolder)
{
	folder_ =~ s/\/$//;            #REMOVE TRAILING SLASH
      #chdir $folder_ or die "Can not change directory: $folder_!\n";
      if ($debug) {print "DEBUG: At $folder_\n"};
      my $line_ = substr($externalcommand_, $index_+1);                               ### Don't change the original buffer.
      $line_ =~ s/SLCFolder/$folder_/g;       ### Replace SLCFolder
      while ( ($parameter_, $value_) = each(%Settings) ) {
          	line_ =~ s/$parameter_/$value_/g;      ### Replace Setting Values...
      }
      if ($debug) {print "Preparing to run command: " . $line_ . "\n";}
}
chdir $Settings{"ProjectFolder"} or die "Non-existing data folder: " . $Settings{"ProjectFolder"}. "\n";

###################################
###	Check input files	###
###################################
### Generate Doris Run Template
my $commandline_;
	### Remove existing template
$commandline_ = "rm -f " . $Settings{"ProjectFolder"} ."/temp/baseline_run.drs";
if ($debug) {print "$commandline_\n";}
system($commandline_) == 0 or die ("Could not execute $commandline_ : $?");
	### Combine environment settings with Run settings
$commandline_ = "cat " . $Settings{"AdoreFolder"} . "/settings/environment.drs > " . $Settings{"ProjectFolder"} ."/temp/baseline_run.drs";
if ($debug) {print "$commandline_\n";}
system($commandline_) == 0 or die ("Could not execute $commandline_ : $?");
$commandline_ = "cat " . $Settings{"AdoreFolder"} . "/settings/readdata.drs >> " . $Settings{"ProjectFolder"} ."/temp/baseline_run.drs";
if ($debug) {print "$commandline_\n";}
system($commandline_) == 0 or die ("Could not execute $commandline_ : $?");

### Get list of SLC Folders
chdir $Settings{"DataFolder"} or die "Non-existing data folder: " . $Settings{"DataFolder"}. "\n";
my $slclist_ = `/bin/ls -F | grep "/"`;
my @SLCFolder= split /\n/, $slclist_;
undef($slclist_);
if ($debug) {print "DEBUG: Listed Data Folders are: @SLCFolder\n";}

### Generate Process folder if necessary...
mkpath($Settings{"ProjectFolder"} . "/process/crops");
mkpath($Settings{"ProjectFolder"} . "/process/i12s");

### Define Master SLC Orbit
if ($Settings{"MasterFolder"} eq "AUTO") 
{
	$Settings{"MasterFolder"} = $SLCFolder[1];
	$Settings{"MasterFolder"} = &BaselineAnalysis(%Settings);
	$commandline_ = $Settings{"ScriptsFolder"} . "/analyze_baseline.pl -ps " . $ProjectFile . "-clear";
	if ($debug) {print "$commandline_\n";}
	system($commandline_) == 0 or die ("Could not execute $commandline_ : $?");
	&BaselineAnalysis(%Settings);
	
}
else
{
	&BaselineAnalysis(%Settings);
}
exit 0;


###################################
###     Subroutines             ###
###################################

sub BaselineAnalysis()
{	
	### Read Parameters/Settings
	my %Settings = @_;
	
	### Modify Template
	open(FH_baseline, $Settings{"ProjectFolder"} . "/temp/baseline_run.drs") or die ("Could not open baseline_run.drs template file!");
	my @baseline_; my $line_;	
	@baseline_ = <FH_baseline>;
	my $folder_;
	
	
	open(FH_batchfile, ">". $Settings{"ProjectFolder"} . "/temp/run_batch.sh") or die ("Could not open run_batch.sh template file!");
	print FH_batchfile "\#!/bin/bash \n";	### INITIALIZE BATCH FILE
	foreach $folder_ (@SLCFolder)
	{
		$folder_ =~ s/\/$//;		#REMOVE TRAILING SLASH
		#chdir $folder_ or die "Can not change directory: $folder_!\n";
		if ($debug) {print "DEBUG: In $folder_\n"}; 
		seek FH_baseline, 0,0;
		mkdir($Settings{"ProjectFolder"} . "/process/crops/" . $folder_);
		open(FH_baselineSLC, ">" . $Settings{"ProjectFolder"} . "/process/crops/" . $folder_ ."/readdata.input") or die ("Could not create readdata.input file in process directory!");
		foreach $line_ (@baseline_)	
		{
			my $_line_ = $line_;			### Don't change the original buffer.
			if ($_line_ =~ /^\s*c/) {next;}
			$_line_ =~ s/SLCFolder/$folder_/gi;	### Replace SLCFolder
			while ( my ($parameter_, $value_) = each(%Settings) ) {
	     	   		$_line_ =~ s/$parameter_/$value_/gi;	### Replace Setting Values...
	    		}
			print FH_baselineSLC $_line_;
			if ($debug) {print $_line_;}
		}
		close(FH_baselineSLC);
		### Add doris run to batch file. 
		print FH_batchfile $Settings{"AdoreFolder"} . "/doris/doris " . $Settings{"ProjectFolder"} . "/process/crops/" . $folder_ ."/readdata.input \n";
	}
	close(FH_batchfile);
	close(FH_baseline);
}

sub Usage {
  print STDERR "\nUSAGE: <main.pl> -ps project.settings [-debug] [-clear] \n\n";
  print STDERR "Project Folder has to include the Delft Processing Folder Structure. \n";  
  exit 1;
}

###
### ReadProjectSettings
###
sub ReadProjectSettings {
        my $setting_; my $parameter_; my $value_;
        my @Settings_;

        open(FH_settings, $ProjectFile) or die ("Could not open project file!");        ### FH_settings=FileHandle_settings
        @Settings_=<FH_settings>;
        if ($debug) {print "DEBUG: Project Settings are:\n @Settings_\n";}

        foreach $setting_ (@Settings_)
        {
                chomp($setting_);
                $setting_ =~ s/^c\s.*//i ; ### Remove comment lines starting with c or C
                $setting_ =~ s/\s*ccc.*//i; ### Remove comments following a setting. Starts with ccc or CCC
                $setting_ =~ s/^\s//  ; ### Remove White Space (Blank Lines)
                $setting_ =~ s/\/$//;    ### Remove trailing slash (For Folder Names)
                if (! $setting_) {next;}        ###If nothing left go to next
                if ($debug) {print "Read Setting: $setting_\n"};
                if (! $setting_) {next;}        ### Skip Comment Lines  
                ($parameter_, $value_)=split(/=/,$setting_);    #read each parameter and value from file
                if ((! $value_) && ($parameter_)){next;}                ###If no value, skip setting
                if ($debug) {print $parameter_ . " = " . $value_ ."\n";} 
                $Settings{$parameter_} = $value_;
                if ($debug) {print "Placed in Hash as " .$parameter_ . " -> " . $Settings{$parameter_} . "\n";}
        }
        close(FH_settings);
        undef($parameter_); undef($value_);undef($setting_);undef(@Settings_);
        
        $Settings{"DataFolder"} = $Settings{"ProjectFolder"} . "/data";
        $Settings{"ScriptsFolder"} = $Settings{"AdoreFolder"} . "/scripts";
        if ($debug) {print "DEBUG: Project Folder is:". $Settings{"ProjectFolder"} . "\n";}
}