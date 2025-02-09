# WebAurion Note Scraper

Ce script Python est un scraper simple pour vérifier les nouvelles notes sur WebAurion. Il est conçu pour fonctionner sur les systèmes Unix.

## Utilisation

1. **Téléchargement** : Téléchargez le script sur votre machine.
2. **Configuration** : Ouvrez le script et remplacez les `$$$$` par vos identifiants WebAurion.
3. **Exécution** : Lancez le script avec Python 3.

   ```bash
   python3 scraper.py
   

## Fonctionnalités

- **Version Basique** : Le script vérifie si une nouvelle note est disponible et l'affiche dans le terminal.
- **Version Sonore** : En cas de nouvelle note, un son est émis et le site WebAurion s'ouvre automatiquement dans votre navigateur par défaut.

## Pré-requis

- Python 3 installé sur votre système.
- Les bibliothèques Python suivantes doivent être installées :
  ```bash
  pip install selenium webdriver-manager beautifulsoup4
  ```
- ChromeDriver doit être installé et configuré. Le script utilise `webdriver_manager` pour gérer cela automatiquement.

## Imports nécessaires

Le script utilise les bibliothèques suivantes :

```python
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import re
```

## Remarque

Assurez-vous que vos identifiants sont corrects et que vous avez accès à WebAurion avant de lancer le script. De plus, Chrome doit être installé sur votre système pour que Selenium puisse fonctionner correctement.
