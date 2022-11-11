#! /usr/bin/perl -w

# soma todos os eleitores aptos por municipio e adiciona
# essa coluna no CSV
#
# fornecer como input o arquivo gerado pelo output-CSV-presidente-por-municipio-1.pl

$fname = $ARGV[0];
die unless -e $fname;

open(FH,"<",$fname) or die;
while (not eof FH) {
    chomp($a = <FH>);
    @b = split(/,/,$a);
    die unless $#b == 12;
    if ($b[0] ne "Estado") {
	$k = "$b[0]:$b[1]";
	$cnt{$k} = 0 unless defined $cnt{$k};
	$cnt{$k} += $b[7];
    }
}
close FH;
open(FH,"<",$fname) or die;
while (not eof FH) {
    chomp($a = <FH>);
    @b = split(/,/,$a);
    die unless $#b == 12;
    if ($a =~ m/^Estado/) {
	print "$a,VotantesMunicipio\n";
    } else {
	$k = "$b[0]:$b[1]";
	die unless defined $cnt{$k};
	print "$a,$cnt{$k}\n";
    }
}
close FH;
