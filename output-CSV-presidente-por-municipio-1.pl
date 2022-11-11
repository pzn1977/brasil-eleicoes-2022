#! /usr/bin/perl -w

# Gera um CSV partindo do TXT com todos os boletins de urna concatenados
# que foi gerado pelo output-boletim-txt-unificado.pl

print "Estado,Municipio,Zona,Secao,Local,Voto13,Voto22,Aptos,Nominais,Nulos,Brancos,Apurados,Modelo\n";

$pre = 0;
while (not eof STDIN) {
    chomp($a = <STDIN>);
    # die "FILENAME5\n" if ($a =~ m/^=> FILENAME 5/);
    if ($a =~ m/^=> FILENAME/) {
	$bol = '';
	@b = split(/ /,$a);
	die unless $#b == 5;
	$fn = $b[3];
	$est = $b[3]; $est =~ s/_.*//;
	$mod = $b[4];
	$pre = 0;
    }
    $bol .= "# $a\n";
    if ($a =~ m/^Município +[0-9]+$/) {
	die if defined $mun;
	$mun = $a; $mun =~ s/[^0-9]//g; $mun = int($mun);
    }
    if ($a =~ m/^Zona Eleitoral +[0-9]+$/) {
	die if defined $zon;
	$zon = $a; $zon =~ s/[^0-9]//g; $zon = int($zon);
    }
    if ($a =~ m/^Local de Votação +[0-9]+$/) {
	die if defined $loc;
	$loc = $a; $loc =~ s/[^0-9]//g; $loc = int($loc);
    }
    if ($a =~ m/^Junta Apuradora +[0-9]+$/) {
	die if defined $loc;
	$loc = 0; # sem local de votacao, foi junta apuradora
	#$loc = $a; $loc =~ s/[^0-9]//g; $loc = "JA".int($loc);
    }
    if ($a =~ m/^Seção Eleitoral +[0-9]+$/) {
	die if defined $sec;
	$sec = $a; $sec =~ s/[^0-9]//g; $sec = int($sec);
    }
    if ($pre) {
	if ($a =~ m/^Código Verificador/) {
	    processa_boletim();
	    $pre = 0;
	    undef $fn;
	    undef $mod;
	    undef $mun;
	    undef $zon;
	    undef $loc;
	    undef $sec;
	    undef $v13;
	    undef $v22;
	    undef $vapt;
	    undef $vnom;
	    undef $vbra;
	    undef $vnul;
	    undef $vapu;
	}
	if ($a =~ m/^ *LULA +13 +[0-9]{4}$/) {
	    die if defined $v13;
	    $v13 = int(substr($a,-4));
	}
	if ($a =~ m/^ *JAIR BOLSONARO +22 +[0-9]{4}$/) {
	    die if defined $v22;
	    $v22 = int(substr($a,-4));
	}
	if ($a =~ m/^Eleitores Aptos +[0-9]{4}$/) {
	    die if defined $vapt;
	    $vapt = int(substr($a,-4));
	}
	if ($a =~ m/^Total de votos Nominais +[0-9]{4}$/) {
	    die if defined $vnom;
	    $vnom = int(substr($a,-4));
	}
	if ($a =~ m/^Brancos +[0-9]{4}$/) {
	    die if defined $vbra;
	    $vbra = int(substr($a,-4));
	}
	if ($a =~ m/^Nulos +[0-9]{4}$/) {
	    die if defined $vnul;
	    $vnul = int(substr($a,-4));
	}
	if ($a =~ m/^Total Apurado +[0-9]{4}$/) {
	    die if defined $vapu;
	    $vapu = int(substr($a,-4));
	}
    }
    $pre = 1 if ($a =~ m/^-+PRESIDENTE-+/);
}

sub processa_boletim {
    die unless defined $fn;
    die unless defined $mod;
    die unless defined $mun;
    die unless defined $zon;
    die unless defined $loc;
    die unless defined $sec;
    die unless defined $vapt;
    die unless defined $vnom;
    die unless defined $vbra;
    die unless defined $vnul;
    die unless defined $vapu;
    die unless $fn eq sprintf("%s_%05d_%04d_%04d",$est,$mun,$zon,$sec);
    $v13 = 0 unless defined $v13;
    $v22 = 0 unless defined $v22;
    die unless ($v13 + $v22) == $vnom;
    die unless ($vnom + $vbra + $vnul) == $vapu;
    $mun = sprintf("%05d",$mun);
    $zon = sprintf("%04d",$zon);
    $sec = sprintf("%04d",$sec);
    print "$est,$mun,$zon,$sec,$loc,$v13,$v22,$vapt,$vnom,$vnul,$vbra,$vapu,$mod\n";
}

# => FILENAME 1 ac_01007_0009_0001 UE2013 <=
#            Boletim de Urna

#          Eleições Gerais 2022
#                2º Turno
#              (30/10/2022)

# Município                        01007
#                 BUJARI

# Zona Eleitoral                    0009
# Local de Votação                  1104
# Seção Eleitoral                   0001

# Eleitores aptos                   0335
# Comparecimento                    0261
# Eleitores faltosos                0074
# Habilitados por ano nascimento    0019

# Código identificação UE       01663883
# Data de abertura da UE      30/10/2022
# Horário de abertura           06:00:01
# Data de fechamento da UE    30/10/2022
# Horário de fechamento         15:00:53

#       RESUMO DA CORRESPONDÊNCIA
#       566.041

# Código Verificador: 7.956.892.948

# ======================================

# --------------PRESIDENTE--------------
# Nome do candidato       Num cand Votos

#   LULA                        13  0075
#   JAIR BOLSONARO              22  0175

# --------------------------------------
# Eleitores Aptos                   0335
# Total de votos Nominais           0250
# Brancos                           0005
# Nulos                             0006
# Total Apurado                     0261

# Código Verificador: 1.588.465.787


# ======================================

