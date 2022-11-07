#!/usr/bin/perl -w

# este programa recebe o nome dos arquivos de log no STDIN e
# processa os mesmos verificando o modelo da urna

# como usar:
#   find data/ -type f -name '*.logjez.pickle' | ./detecta-modelo-urna.pl

# nota sobre o diretorio temporario:
# um diretorio que roda sobre ramdisk resulta em performance muito
# melhor (ex: por exemplo dentro de /run ao inves de /tmp)
# portanto, como root, crie um diretorio e coloque as permissoes corretas
# e indique o diretorio na variavel $tmpdir abaixo caso queira melhorar a
# performance, ou entao use o padrao /tmp

$tmpdir="/tmp";      # $tmpdir="/run/eleicoes";

# este programa utiliza o python pickle-dump.py para extrair informacoes
# no formato pickle, entao certifique-se que o ambiente 'venv' se
# encontra inicializado

# este programa utiliza o utilitario "7z" para extrair arquivos de log
# que se encontram comprimidos com formato 7-zip nas urnas, certifique-se
# que ele encontra-se instalado

use File::Path qw(make_path remove_tree);

$| = 1;

die unless -d $tmpdir;
$tmpdir .= "/detecta-modelo-urna-$$";
die if -d $tmpdir;
make_path($tmpdir);

$zip = "$tmpdir/x.7z";
unlink $zip;
remove_tree "$tmpdir/exp";

$valid_model{"UE2009"} = 1;
$valid_model{"UE2010"} = 1;
$valid_model{"UE2011"} = 1;
$valid_model{"UE2013"} = 1;
$valid_model{"UE2015"} = 1;
$valid_model{"UE2020"} = 1;

$ok_cnt = 0;

while (not eof STDIN) {
    chomp($f=<STDIN>);
    die unless -e $f;
    $fn = $f;
    $fn =~ s/.*data\///;
    $fn =~ s/[.]pickle$//;
    $fnm = $f;
    $fnm =~ s/[.]log.*//;
    $fnm .= ".modelo";
    if (! -e $fnm) {
        make_path "$tmpdir/exp";
        print "run: $fn\n";
        `python pickle-dump.py --binary $f > $zip`;
        die unless $? == 0;
        die unless $zip;
        $ok = 0;
        $t7 = `7z t $zip`;
        if ($t7 =~ m/Files: [0-9]/) {
            if ($t7 =~ m/Files: 1[^0-9]/) {
                $ok++;
            }
        } else {
            $ok++;
        }
        $ok++ if ($t7 =~ m/Everything is Ok/);
        $unzip = ''; $unzip = `cd $tmpdir/exp && 7z e $zip`;
	
        die unless -e "$tmpdir/exp/logd.dat";
	
        undef $model;
        open(LH,"$tmpdir/exp/logd.dat") or die "no logd.dat file";
	$lhtxt = '';
	$lhsize = 0; $lhsize = -s "$tmpdir/exp/logd.dat";
	$modelmismatch=0;
        while (not eof LH) {
            chomp($ll = <LH>);
	    $lhtxt .= $ll."\n";
            if ($ll =~ m/Modelo de Urna: UE[0-9]+/) {
                $model_tmp = $ll;
                $model_tmp =~ s/.*Modelo de Urna: //;
                $model_tmp =~ s/[\t ].*//;
                $model = $model_tmp unless defined $model;
		$modelmismatch=1 if $model ne $model_tmp;
            }
        }
	undef $model if $modelmismatch==1;
	close LH;
        unlink $zip;
        remove_tree "$tmpdir/exp";
        if (defined $model) {
            die unless defined $valid_model{$model};
            open(MD, ">", $fnm) or die;
	    my $x = $fnm;
	    $x =~ s:data/::;
	    $x =~ s:.modelo::;
	    $x =~ s:[/_]: :g;
            print "OUT: $model $x\n";
            print MD "$model $x\n";
            close MD;
        } else {
	    # print "**FILENAME**\n$f\n**7ZIP**\n$unzip\n**LOG $lhsize**\n$lhtxt\n";
	    if ($modelmismatch) {
	      print "\n*** MODEL MISMATCH $f **\n";
	    } else {
	      print "\n*** NO MODEL DETECTED $f **\n";
	    }
	}

	if (($ok_cnt % 100) == 0) {
	    print "runtime_progress: ".time()." $ok_cnt\n";
	}
	$ok_cnt++;

    }

    die if -e "extract-modelo-urna.stop";
}

remove_tree "$tmpdir";
print "END\n";
