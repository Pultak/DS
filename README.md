## 1. SAMOSTATNÁ PRÁCE

### Zadání:
Implementujte distribuovanou aplikaci pro volbu 1 uzlu jako mastera z N identických uzlů. Ve druhé fázi master uzel
řídí “obarvení“ 1/3 uzlů jako „zelený“ a zbylých 2/3 jako „červený“. Master uzel je vždy obarvený jako „zelený“,
počet „zelených“ uzlů se zaokrouhluje směrem nahoru.

### Základní podmínky:
- Zdrojový kód včetně dokumentace bude uložen v repozitáři https: //github.com/ nebo https://gitlab.kiv.zcu.cz/
- Dokumentace v souboru README.md v kořenovém adresáři. Musí obsahovat:
- Popis způsobu řešení/algoritmy jednotlivých problémů (volba mastera, barvení uzlů)
- Pokud není zajištěno automatické sestavení aplikace před jejím spuštěním, popis sestavení
- Popis spuštění a ověření funkčnosti aplikace
- Minimální počet uzlů systému je 3 a je možné jej změnou hodnoty parametru změnit.
- Každý uzel vypisuje do logu (standardní výstup) zřetelně každou změnu svého stavu, včetně stavu v jakém
začal (např. “init”, “master”, “green”, “red”)
- Po ukončení volby mastera a obarvení uzlů, vypíše master do logu přehled uzlů a jejich obarvení.

### Technické podmínky:
- Využití nástrojů Vagrant a Docker pro vytvoření a spuštění infrastruktury.
- Sestavení aplikace musí být možné v prostředí Unix/Linux

# Popis implementace

Během celého chodu aplikace je periodicky zasílán broadcast ping, který značí, že je node v síti aktivní (ve třídě master_selector.py konstanta PING_PERIOD). V jiném prostředí by takovýto způsob nemusel stačit (zejména pro systém přes několik privátních sítí), ale pro naše účely se mi tento způsob jevil jako dostatečný. Každý node si tedy díky těmto pingum udržuje list se všemi aktivními nody (dochází ke kontrole podle posledního přijatého pingu). Pokud se uzel neozve do stanoveného času, dojde k jeho vyřazení (ve třídě master_selector.py konstanta MAX_OUTAGE_TIME). 


1. Volba mastera

Každý uzel vypisuje do logu (standardní výstup) zřetelně každou změnu svého stavu pod logovací třídou INFO. V případě, že chcete podrobnější popis je potřeba v souboru main.py na 14. řádce přepsat level na DEBUG. 

Pokud v siti neni zadny master (nepřišel žádný ping od žádného po nejakou dobu) zvolíme se jako master. V případě, že se poté objeví v síti dva uzly, ktere se nazyvaji masterem, tak preda veleni tomu ktery ma nizsi časový klíč. O změně svého vůdce se jednotlivé uzly dozví pomocí pingu (obsahuje totiž o něm i ty nejdůležitější informace). 

V případě, že dojde k výpadku master uzlu dojde po čase (MAX_OUTAGE_TIME) k novému volení uzlu, tak jak je popsáno dříve v této sekci.


2. Obarvení uzlů

Master uzel je vždy obarvený jako „zelený“, počet „zelených“ uzlů se zaokrouhluje směrem nahoru. Po stanoveni mastera se jednotlivé uzly dotazují přes HTTP API na svojí přiřazenou barvu. Master si interně vede mapu všech již přiřazených barev a podle poměru zelených a červených stanoví tázajícímu novou barvu. 

V případě, že dojde k výpadku obarveného uzlu, podívá se master na aktuální stav poměru barev a podle situace zvolí nejbližší červený/zelený uzel a přebarví ho na druhou barvu.


## Možné nedostatky aplikace


## Popis aplikace


## Sestavení a spuštění


## Testování aplikace


