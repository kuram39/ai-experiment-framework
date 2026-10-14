# AI Experiment Framework

**Praktický způsob, jak mohou člověk a AI společně systematicky pracovat na datovém experimentu.**

Framework pomáhá udržet experiment srozumitelný i po skončení konverzace s AI. Odděluje výzkumnou otázku a aktuální závěr od důkazů jednotlivých běhů, dává souborům jasnou roli a nabízí jednoduché nástroje pro založení a kontrolu experimentu.

Nejde o datovou platformu ani službu pro sledování experimentů. Je to lehký pracovní postup založený na Markdownu, JSONu, běžných souborech a volitelných skriptech.

## Co repozitář obsahuje

- [`skills/create-experiment/`](skills/create-experiment/SKILL.md): skill pro AI agenta, který zakládá nebo rozvíjí trvalý experiment.
- [`create_experiment.py`](skills/create-experiment/scripts/create_experiment.py): vytvoří datovanou základní strukturu a nepřepíše existující experiment.
- [`validate_experiment.py`](skills/create-experiment/scripts/validate_experiment.py): kontroluje dohodnuté strukturální konvence a vybrané odkazy na artefakty.
- [`examples/2026-10-14_customer-analysis/`](examples/2026-10-14_customer-analysis/README.md): ukázka analýzy odchodu zákazníků nad syntetickými daty. Obsahuje dvě zaznamenaná spuštění a předání, na které může navázat další agent.
- [`docs/architecture.md`](docs/architecture.md) a [`docs/agent-workflow.md`](docs/agent-workflow.md): popis modelu experimentu a spolupráce člověka s agentem.

## Rychlý začátek

Požadavky: Python 3.10 nebo novější. Generátor i validátor používají pouze standardní knihovnu Pythonu.

Založení experimentu ve složce existujícího projektu:

```bash
python3 skills/create-experiment/scripts/create_experiment.py \
  --root /cesta/k/projektu \
  --title "Ověření pravidla kvality dat" \
  --question "Sníží nové pravidlo počet neplatných záznamů, aniž by odmítalo platné?" \
  --hypothesis "Pravidlo sníží počet neplatných záznamů alespoň o 10 % a chybně odmítne méně než 2 % platných." \
  --in-scope "Porovnat nové pravidlo se současným základem na dodaném snapshotu." \
  --out-of-scope "Tento experiment nepovoluje změny v produkci."
```

Generátor vytvoří datovanou složku s `README.md`, `OUTCOME.md` a `.gitignore`. Neprohlíží ani nepřesouvá vaše data, experiment nespouští a nic nikam nepublikuje. Další složky a soubory přidávejte až ve chvíli, kdy je práce skutečně potřebuje.

Skill nainstalujte zkopírováním `skills/create-experiment/` do adresáře skillů vašeho agenta. V Codexu lze použít projektovou cestu `.agents/skills/create-experiment/` nebo uživatelskou `~/.codex/skills/create-experiment/`. Jiné nástroje mohou mít vlastní umístění; ověřte si jejich aktuální dokumentaci.

## Vyzkoušejte ukázku

Ukázka obsahuje reprodukovatelný syntetický CSV soubor, skript, který jej vytvořil, analytický kód, dva záznamy běhů a aktuální stav experimentu. Postup pro opakování je v [README ukázky](examples/2026-10-14_customer-analysis/README.md). První hypotéza nesplnila předem uvedený práh. Druhá analýza našla popisnou souvislost v syntetických datech. Ani jeden výsledek nedokazuje příčinnou souvislost a žádný nevypovídá o skutečných zákaznících.

## Základní princip

Experiment má dva propojené pohledy:

1. **Aktuální stav:** jakou otázku řešíme, co nyní nejlépe podporují důkazy, které artefakty jsou platné a jaký je další krok.
2. **Evidence jednotlivých běhů:** co každý pokus udělal, co zjistil, o jaké vstupy se opíral a zda jeho výsledek zůstává platný.

Aktuální stav se mění s tím, jak přibývá poznání. Identita běhu a původní záznam výsledku zůstávají zachované. Ověřený kandidát může nahradit současný artefakt na jeho stabilní cestě; změna i nahrazený důkaz se zaznamenají.

## Soukromí a sdílení

Ukázka používá pouze vygenerovaná syntetická data. Do veřejného repozitáře nevkládejte soukromé záznamy zákazníků, přístupové údaje ani důvěrné informace. Skutečná data uchovávejte na vhodném místě s odpovídajícím řízením přístupu a veřejně sdílejte jen to, co můžete a potřebujete sdílet k vysvětlení metody.

## Zdroje a návaznost

Tento systém jsem rozvíjel a ověřoval při vlastní experimentální práci s daty a složkami. Jeho vývoj zachycuje také historie tohoto repozitáře. Z osobní šablony `experiments/0000-00-00_experiment-template` vychází samostatný skill, generátor, validátor a veřejná ukázka. Jádrem je struktura, která roste spolu s experimentem, oddělené `README.md` a `OUTCOME.md`, aktuální stav a další krok, evidence běhů, provenience vstupů a předání práce dalšímu člověku či agentovi. Veřejná verze tento pracovní postup zpřístupňuje jako adaptovatelný princip.

Při tvorbě přístupu jsem se inspiroval také těmito veřejnými projekty věnovanými organizaci datové a výzkumné práce:

- [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science) popisuje flexibilní strukturu datového projektu, včetně oddělení surových, průběžných a zpracovaných dat.
- [Velexi Research Project Cookiecutter](https://github.com/velexi-research/VLXI-Cookiecutter-Research) se zaměřuje na výzkumné projekty s průzkumem, experimenty, analýzou a reportováním.
- [Reproducible Workflow Template](https://github.com/emgthomas/reproducible-workflow-template) ukazuje další přístup k reprodukovatelnému uspořádání výzkumné práce.

Framework tyto myšlenky přizpůsobuje vlastnímu pracovnímu postupu a přidává důraz na spolupráci s AI agentem: průběžný stav je čitelný ze souborů, pokusy mají vlastní záznamy a nový agent může navázat bez historie původní konverzace.

## Jazyk a licence

README je nejprve česky a následuje úplný anglický překlad. Skill zachovává konvenci zdrojového pracovního postupu: nově založené lokální dokumenty experimentu jsou v češtině. Přizpůsobte si ji podle jazyka svého týmu.

Repozitář používá licenci MIT; úplné znění je v souboru [LICENSE](LICENSE). Před dalším šířením si ověřte, že máte právo sdílet všechny materiály, které do projektu přidáte.

---

# AI Experiment Framework — English

**A practical way for people and AI to work systematically on data experiments.**

The framework keeps an experiment understandable after an AI conversation ends. It separates the research question and current conclusion from the evidence recorded by individual runs, gives files clear roles, and provides small tools for creating and checking an experiment.

This is not a data platform or an experiment-tracking service. It is a lightweight working method built from Markdown, JSON, ordinary files, and optional scripts.

## What is included

- [`skills/create-experiment/`](skills/create-experiment/SKILL.md): an agent skill for creating or continuing a durable experiment.
- [`create_experiment.py`](skills/create-experiment/scripts/create_experiment.py): creates a dated scaffold without overwriting an existing experiment.
- [`validate_experiment.py`](skills/create-experiment/scripts/validate_experiment.py): checks agreed structural conventions and selected artifact references.
- [`examples/2026-10-14_customer-analysis/`](examples/2026-10-14_customer-analysis/README.md): a customer-churn analysis example using synthetic data. It includes two recorded runs and a handoff another agent can continue.
- [`docs/architecture.md`](docs/architecture.md) and [`docs/agent-workflow.md`](docs/agent-workflow.md): explain the experiment model and the human-agent workflow.

## Quick start

Requirements: Python 3.10 or newer. The generator and validator use only the Python standard library.

Create an experiment in an existing project directory:

```bash
python3 skills/create-experiment/scripts/create_experiment.py \
  --root /path/to/your/project \
  --title "Evaluate a data-quality rule" \
  --question "Does the new rule reduce invalid records without rejecting valid ones?" \
  --hypothesis "The rule lowers invalid records by at least 10% while false rejection stays below 2%." \
  --in-scope "Compare the new rule with the current baseline on the supplied snapshot." \
  --out-of-scope "This experiment does not authorize production changes."
```

The generator creates a dated directory with `README.md`, `OUTCOME.md`, and `.gitignore`. It does not inspect or move your data, run the experiment, or publish anything. Add directories and files only when the work actually needs them.

Install the skill by copying `skills/create-experiment/` into the skills directory supported by your agent. For Codex, use the project location `.agents/skills/create-experiment/` or the user location `~/.codex/skills/create-experiment/`. Other tools may use a different location; check their current documentation.

## Try the worked example

The example includes a reproducible synthetic CSV file, the script that generated it, analysis code, two run receipts, and the current experiment state. Follow the [example README](examples/2026-10-14_customer-analysis/README.md) to reproduce it. The first hypothesis did not meet its predeclared threshold. The second analysis found a descriptive association in synthetic data. Neither result establishes causation or says anything about real customers.

## Core idea

An experiment has two connected views:

1. **Current state:** the question being investigated, the answer best supported by evidence so far, the artifacts that are current, and the next step.
2. **Run evidence:** what each attempt did, what it found, which inputs it relied on, and whether its result remains valid.

The current state changes as knowledge improves. Run identity and the original result receipt remain preserved. A verified candidate may replace a current artifact at its stable path; the transition and superseded evidence are recorded.

## Privacy and sharing

The example uses generated synthetic data only. Do not put private customer records, credentials, or confidential information in a public repository. Keep real data in an appropriate access-controlled location and share publicly only what you are allowed to share and what is needed to explain the method.

## Sources and lineage

I developed and tested this system through my own experimental work with data and folders. The history of this repository also records its development. My personal `experiments/0000-00-00_experiment-template` led to the standalone skill, generator, validator, and public example. The core is a structure that grows with the experiment, separate `README.md` and `OUTCOME.md` documents, current state and next action, run evidence, input provenance, and handoff to another person or agent. The public version makes this working method available as an adaptable principle.

I also drew inspiration from these public projects for organizing data and research work:

- [Cookiecutter Data Science](https://github.com/drivendataorg/cookiecutter-data-science) describes a flexible data-project structure, including separation of raw, intermediate, and processed data.
- [Velexi Research Project Cookiecutter](https://github.com/velexi-research/VLXI-Cookiecutter-Research) focuses on research projects with exploration, experimentation, analysis, and reporting.
- [Reproducible Workflow Template](https://github.com/emgthomas/reproducible-workflow-template) presents another approach to organizing reproducible research work.

The framework adapts these ideas to my own workflow and adds an emphasis on working with an AI agent: the current state is readable from files, attempts have their own records, and a new agent can continue without access to the original conversation history.

## Language and license

The README is written first in Czech, followed by its complete English translation. The skill preserves a convention from the source workflow: newly created local experiment documents are in Czech. Adapt that convention to your team's language.

This repository is licensed under the MIT License; see [LICENSE](LICENSE). Before redistributing, make sure you have the right to share all materials you add to the project.
