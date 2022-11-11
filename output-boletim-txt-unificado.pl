#! /usr/bin/perl -w

open(FH,"modelo-urna.csv") or die;
# UE2013;ac;01007;0009;0001
while (not eof FH) {
    chomp($a = <FH>);
    @b = split(/;/,$a,2);
    $b[1] =~ s/\;/_/g;
    $model{$b[1]} = $b[0];
}
close FH;

$i = 1;
open(FH,"txt-files.txt") or die;
while (not eof FH) {
    chomp($a = <FH>);
    $b = $a;
    $b =~ s:^.*/::;
    $b =~ s/.txt$//;
    $model{$b} = "UNKNOWN" unless defined $model{$b};
    print "=> FILENAME $i $b $model{$b} <=\n";
    open(BU,"$a") or die;
    while (not eof BU) {
	$a = <BU>;
	print $a;
    }
    close BU;
    print "\n";
    $i++;
    if (($i % 1000) == 0) {
	print STDERR "progress: $i\n";
    }
}
close FH;
