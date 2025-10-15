# gr.ai.ce x Klub Ada - Izdelaj svojega AI agenta

Materiali za delavnico "Izdelaj svojega AI agenta", ki jo organizirata Klub Ada in gr.ai.ce.

## Priprava na delavnico

### Ollama - Dostop do LLM

Za izdelavo agenta potrebujemo dostop do velikega jezikovnega modela (LLM), ki vrača odgovore v naravnem jeziku. Uporabile bomo Ollama - orodje, ki omogoča lokalen dostop do različnih LLM modelov. 

Na delavnici bomo delale z modelom llama3.1. Če se bo tvojemu računalniku zatikalo, pa rajši izberi llama3.2.

#### Inštalacija

MacOS

1. Odpri spletno stran: https://ollama.com/download/mac
2. Izberi "Download for macOS" in prenesi datoteko
3. Odpri prenešeno datoteko in sledi navodilom za namestitev
4. Zaženi aplikacijo Ollama

Windows

1. Odpri spletno stran: https://ollama.com/download/windows
2. Izberi "Download for Windows" in prenesi datoteko
3. Odpri prenešeno datoteko in sledi navodilom za namestitev

Linux

1. V terminalu poženi

    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

#### Prenos modela

1. Odpri Terminal / Command Prompt / Powershell
2. Zaženi ukaz:

    ```bash
    ollama pull llama3.1
    ```
   
   ⏱️ Opomba: Prvi zagon lahko traja nekaj minut, ker se model prenaša.

3. Preveri inštalacijo:

    ```bash
    ollama list
    ```

### Python

Agenta bomo programirale v jeziku *Python*.

### Inštalacija

MacOS, Windows

1. Obišči: https://www.python.org/downloads/
2. Klikni na rumen gumb "Download Python 3.14.0"
3. Odpri prenešeno `.pkg` datoteko
4. Sledi navodilom namestitvenega čarovnika
5. Preveri inštalacijo:
    ```bash
    python3 --version
    ```

Linux

```bash
sudo apt update
sudo apt upgrade
sudo apt install python3
sudo apt install python3-pip python3-dev python3-venv build-essential
```

### Priprava projekta

1. Prenesi projekt
    ```bash
    git clone git@github.com:klub-ada/izdelaj-svojega-ai-agenta.git
    ```
2. Ustvari virtualno okolje
    ```bash
    python3 -m venv venv
    ```
3. Aktiviraj virtualno okolje

    MacOS, Linux

    ```bash
    source venv/bin/activate
    ```

    Windows - Powershell: 

    ```bash
    .\venv\Scripts\activate.psl
    ```

    Windows - Command Prompt
    ```bash
    .\venv\Scripts\activate.bat
    ```

4. Namesti potrebne knjižnice
    ```bash
    pip install -r requirements.txt
    ```