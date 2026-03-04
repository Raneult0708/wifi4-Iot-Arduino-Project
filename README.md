#  Système IoT WiFi 4 — Arduino Uno + Flask Dashboard

> Projet de groupe — 2ème année Systèmes Embarqués & IoT  
> Réseaux Sans Fil & Protocoles de Communication IoT — 2024-2025

---

##  Description

Système IoT complet basé sur la norme **IEEE 802.11n (WiFi 4)**.  
Un Arduino Uno collecte des données capteurs (température, humidité, luminosité) et les transmet via USB Serial à un PC jouant le rôle de **gateway IoT**. Le PC expose un dashboard web accessible depuis n'importe quel appareil connecté au même réseau WiFi.

---

##  Architecture Générale

```
┌─────────────────────┐     USB Serial      ┌──────────────────────────┐    WiFi 802.11n    ┌─────────────────┐
│    ARDUINO UNO      │ ──────────────────► │   PC / LAPTOP            │ ─────────────────► │ Smartphone / PC │
│                     │     9600 bauds      │   Gateway IoT            │                    │ Client WiFi     │
│  ● DHT11 → D2       │                     │                          │                    │                 │
│  ● LDR   → A0       │                     │  ● Python (pyserial)     │                    │ Dashboard       │
│                     │                     │  ● Serveur Flask :5000   │                    │ http://IP:5000  │
│                     │                     │  ● Clé USB WiFi 802.11n  │                    │                 │
└─────────────────────┘                     └──────────────────────────┘                    └─────────────────┘
        PAN filaire (USB)                              LAN sans fil (WiFi 4)
```

> **Pourquoi cette architecture ?**  
> L'Arduino Uno (ATmega328P) ne dispose pas de contrôleur USB Host — il fonctionne uniquement en mode USB Device (esclave). Il ne peut pas piloter une clé WiFi USB directement. Le PC fait le pont entre le monde filaire (Serial USB) et le réseau WiFi 802.11n.

---

##  Note sur l'interface réseau utilisée

> **Contexte de développement :** La clé USB WiFi 802.11n est le composant cible du projet, mais elle n'est pas toujours disponible pendant la phase de développement.  
>
> **Bonne nouvelle : ça n'a aucun impact sur le code.**  
> Le serveur Flask est lancé avec `host='0.0.0.0'`, ce qui signifie qu'il écoute sur **toutes les interfaces réseau disponibles** — carte WiFi intégrée, Ethernet, clé USB WiFi — sans distinction.  
>
> | Phase | Interface utilisée | Comportement |
> |---|---|---|
> | Développement / test | Carte réseau intégrée du PC | Identique — Flask expose le dashboard sur l'IP de cette carte |
> | Déploiement final | Clé USB WiFi 802.11n branchée | Identique — Flask expose le dashboard sur l'IP de la clé |
>
> La seule chose qui change entre les deux : l'**adresse IP** communiquée aux clients pour accéder au dashboard (`http://<IP_DU_PC>:5000`). Le code Python, le sketch Arduino et le dashboard HTML restent **strictement identiques**.

---

##  Schéma de Câblage

### DHT11 → Arduino Uno

```
         Arduino Uno
            ┌──────┐
    5V ────►│ 5V   │
            │      │        ┌──────────┐
    D2 ◄────│ D2   │◄───────┤ DATA     │  DHT11
            │      │        │          │
   GND ────►│ GND  │        │ VCC ────►│ 5V
            └──────┘        │ GND ────►│ GND
                            └──────────┘
```

### LDR → Arduino Uno (diviseur de tension)

```
        5V
         │
        LDR    ← photorésistance (en haut, R_haute variable)
         │
         ├──────────────► A0  (lecture ADC 10 bits : 0–1023)
         │
        10kΩ   ← résistance fixe (en bas, R_basse)
         │
        GND
```

> **Comportement et explication :**  
> Le LDR est en position haute dans le diviseur.  
> Formule : `V_A0 = 5V × 10kΩ / (R_LDR + 10kΩ)`  
>
> | Situation | R_LDR | V_A0 | Valeur ADC |
> |---|---|---|---|
> | Lumière forte | ~1kΩ | ~4.5V | **élevée (~920)** |
> | Obscurité | ~500kΩ | ~0.09V | **basse (~20)** |
>
> **Pourquoi ?** Plus le LDR est résistant (obscurité), plus il absorbe de tension avant A0 — il en reste peu sur A0.  
> La résistance physique du LDR augmente dans l'obscurité, mais la tension lue (et donc l'ADC) diminue.  
> C'est la loi d'Ohm appliquée au diviseur : **résistance LDR haute ≠ valeur ADC haute**.

### Récapitulatif des connexions

```
DHT11 VCC  ──► Arduino 5V
DHT11 DATA ──► Arduino D2  
DHT11 GND  ──► Arduino GND

5V ──► A0 + LDR ──► 10kΩ ──► GND

Arduino USB-B ──► Port USB-A du PC  (données + alimentation)
Clé USB WiFi  ──► Port USB-A libre du PC
```

---

##  Technologie WiFi 4 — IEEE 802.11n

### Positionnement dans la famille WiFi

| Génération | Norme | Fréquence | Débit Max | Année |
|---|---|---|---|---|
| WiFi 1 | 802.11b | 2.4 GHz | 11 Mbps | 1999 |
| WiFi 2 | 802.11a | 5 GHz | 54 Mbps | 1999 |
| WiFi 3 | 802.11g | 2.4 GHz | 54 Mbps | 2003 |
| **WiFi 4** | **802.11n** | **2.4 / 5 GHz** | **600 Mbps** | **2009** |
| WiFi 5 | 802.11ac | 5 GHz | 3.5 Gbps | 2013 |
| WiFi 6 | 802.11ax | 2.4 / 5 / 6 GHz | 9.6 Gbps | 2019 |

### Innovations clés du 802.11n

| Mécanisme | Description |
|---|---|
| **MIMO** | Plusieurs antennes en émission/réception — multiplexage spatial des données |
| **Channel Bonding** | Fusion de deux canaux 20 MHz → canal 40 MHz — doublement du débit |
| **A-MPDU** | Agrégation jusqu'à 64 trames en une seule transmission — réduction de l'overhead |
| **MCS adaptatif** | 32 schémas de modulation (BPSK → 64-QAM) choisis selon la qualité du signal |
| **OFDM** | 52 sous-porteuses — robustesse aux interférences et aux trajets multiples |

### Mécanismes actifs dans ce projet

| Mécanisme | Rôle dans le système |
|---|---|
| OFDM | Modulation de toutes les transmissions WiFi de la clé USB |
| MCS adaptatif | Sélection automatique du schéma selon RSSI/SNR |
| WPA2-AES-CCMP | Chiffrement de toutes les requêtes HTTP |
| CSMA/CA | Gestion des accès au canal — évitement de collisions |
| A-MPDU | Agrégation des paquets HTTP du dashboard (refresh toutes les 3s) |
| Beacon frames | Maintien de la connexion (émises par le routeur toutes les 100 ms) |

### Paramètres de la clé USB WiFi 802.11n

```
Interface physique  :  USB 2.0
Norme WiFi          :  IEEE 802.11n + rétrocompatibilité 802.11b/g
Fréquence           :  2.4 GHz (mono-bande)
Débit max           :  150 Mbps (1T1R, canal 20 MHz)
Chipsets courants   :  Realtek RTL8188EUS / Ralink RT5370 / Atheros AR9271
Modes               :  Station (STA), Access Point (AP), Monitor
Sécurité            :  WPA2-PSK (AES-CCMP)
Consommation        :  0.3 – 0.5 W (bus USB)
```

---

##  Structure du Projet

```
wifi4-Iot-Arduino-Project/
├── gateaway_iot.py          # Script Python — gateway Serial + serveur Flask
├── templates/
│   └── dashboard.html       # Dashboard web (HTML + JavaScript)
├── static/
│   └── style.css            # Styles (dark theme)
├── arduino/
│   └── dht11_ldr.ino        # Sketch Arduino à téléverser
└── README.md
```

---

##  Installation et Lancement

### 1. Prérequis Python

```bash
pip install pyserial flask
```

### 2. Bibliothèques Arduino

Dans l'Arduino IDE → **Outils → Gérer les bibliothèques** :
- `DHT sensor library` par Adafruit
- `Adafruit Unified Sensor`

### 3. Téléverser le sketch

```
Arduino IDE → Fichier → Ouvrir → arduino/dht11_ldr.ino
Outils → Carte → Arduino Uno
Outils → Port → /dev/ttyACM0 (Linux) ou COM3 (Windows)
Cliquer : Téléverser
```

Vérifier dans le **Moniteur Série à 9600 bauds** :
```json
{"temp":32,"hum":69,"lum":233}
{"temp":32,"hum":69,"lum":51}
```

### 4. Adapter le port série

Dans `gateaway_iot.py` :
```python
PORT_SERIE = '/dev/ttyACM0'   # Linux
PORT_SERIE = 'COM3'           # Windows — vérifier dans le Gestionnaire de périphériques
```

### 5. Lancer le serveur

```bash
# Fermer d'abord le Moniteur Série Arduino IDE (libère le port)
python3 gateaway_iot.py
```

Sortie attendue :
```
[OK] Port série ouvert : /dev/ttyACM0
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.100.28:5000
[DATA] {'temp': 32, 'hum': 69, 'lum': 233, 'ts': '23:46:28'}
```

### 6. Accéder au dashboard

```
Depuis le PC          :  http://localhost:5000
Depuis un autre appareil (même réseau WiFi) :  http://<IP_DU_PC>:5000
```

Trouver l'IP du PC :
```bash
# Linux
ip a show wlan0 | grep 'inet '

# Windows
ipconfig | findstr IPv4
```

### 7. Migration vers la clé USB WiFi 802.11n

Quand la clé est disponible :
```bash
# 1. Brancher la clé USB WiFi sur un port libre du PC
# 2. Vérifier qu'elle est reconnue
lsusb                         # Linux — chercher Realtek / Ralink / Atheros
# Gestionnaire de périphériques → Adaptateurs réseau  (Windows)

# 3. Relever la nouvelle IP attribuée à la clé
ip a                          # Linux
ipconfig                      # Windows

# 4. Relancer le serveur (aucune modification du code)
python3 gateaway_iot.py

# 5. Communiquer la nouvelle IP aux clients
# http://<nouvelle_IP>:5000
```

> Le code ne change pas — seule l'IP communiquée aux clients est différente.

---

##  Captures d'Écran

### Dashboard principal
```
┌─────────────────────────────────────────────────────────┐
│         📡 Dashboard IoT - WiFi 4 (802.11n)             │
├──────────────────┬──────────────────┬───────────────────┤
│  🌡️ Température  │  💧 Humidité     │  ☀️ Luminosité    │
│                  │                  │                   │
│      32°C        │      69 %        │  Obscurité (712)  │
│                  │                  │                   │
├──────────────────┴──────────────────┴───────────────────┤
│  Dernière mise à jour : 23:46:28                        │
├──────────┬────────────┬──────────────┬──────────────────┤
│  Heure   │  Temp (°C) │  Humidité(%) │  Luminosité      │
├──────────┼────────────┼──────────────┼──────────────────┤
│ 23:46:28 │     32     │      69      │      712         │
│ 23:46:26 │     32     │      69      │      233         │
│ 23:46:24 │     32     │      69      │       51         │
└──────────┴────────────┴──────────────┴──────────────────┘
```

>  Remplacer ce bloc par de vraies captures d'écran du dashboard.  
> Ajouter dans le repo un dossier `screenshots/` avec `dashboard.png`, `terminal.png`, `montage.jpg`.

---

##  Flux de Données Complet

```
[DHT11 + LDR]
     │  lecture toutes les 2 secondes
     ▼
[Arduino Uno — ATmega328P]
     │  formatage JSON  →  {"temp":32,"hum":69,"lum":233}
     │  Serial.println() à 9600 bauds
     ▼
[Câble USB — protocole CDC/UART]
     │
     ▼
[PC — Thread Python pyserial]
     │  readline() → decode UTF-8 → json.loads()
     │  horodatage → stockage deque(maxlen=50)
     ▼
[PC — Serveur Flask 0.0.0.0:5000]
     │  GET /      →  dashboard.html
     │  GET /data  →  JSON {actuel, historique}
     ▼
[Clé USB WiFi 802.11n — IEEE 802.11n PHY/MAC]
     │  OFDM + WPA2-AES + CSMA/CA
     ▼
[Client WiFi — Navigateur]
     │  fetch('/data') toutes les 3 secondes
     ▼
[Affichage dashboard temps réel]
```

---

##  Tests de Validation

| # | Test | Commande / Action | Résultat attendu |
|---|---|---|---|
| 1 | Capteur Arduino | Moniteur Série 9600 bauds | JSON toutes les 2s |
| 2 | Liaison Serial Python | `python3 gateaway_iot.py` | `[DATA] {'temp':...}` dans terminal |
| 3 | Connectivité WiFi | `ping <IP_DU_PC>` | Réponse sans perte |
| 4 | Dashboard local | `http://localhost:5000` | Dashboard affiché avec données |
| 5 | Dashboard distant | `http://IP:5000` depuis smartphone | Dashboard identique |
| 6 | API JSON | `curl http://IP:5000/data` | JSON `{actuel, historique}` |
| 7 | Analyse réseau | Wireshark → filtre `http.request.uri contains "/data"` | Trames HTTP visibles |
| 8 | Portée WiFi | S'éloigner avec smartphone | Dashboard fonctionnel jusqu'à ~20–50m |

---

##  Plan d'Adressage Réseau

| Équipement | Interface | Adresse IP | Rôle |
|---|---|---|---|
| Routeur WiFi Labo | WiFi 802.11n | 192.168.1.1 | Point d'accès + DHCP |
| PC Gateway IoT | wlan0 (clé USB) | 192.168.1.105 (DHCP) | Serveur Flask IoT |
| Arduino Uno | USB Serial | — (pas d'IP) | Nœud capteur |
| Smartphone 1 | WiFi 802.11n | 192.168.1.111 (DHCP) | Client dashboard |
| Smartphone 2 | WiFi 802.11n | 192.168.1.112 (DHCP) | Client dashboard |

---

##  Références

- IEEE Std 802.11n-2009 — Wireless LAN MAC and PHY Specifications
- [Arduino Uno Documentation](https://docs.arduino.cc/hardware/uno-rev3)
- [Flask Documentation](https://flask.palletsprojects.com)
- [PySerial Documentation](https://pythonhosted.org/pyserial)
- [DHT11/DHT22 Datasheet — Aosong Electronics](https://www.aosong.com)
- [Wireshark User Guide](https://wireshark.org)
- Tanenbaum, A. & Wetherall, D. — *Computer Networks*, 5th ed. — Pearson

---

##  Auteurs

Projet réalisé dans le cadre du cours **Réseaux Sans Fil & Protocoles de Communication IoT**  
2ème année Systèmes Embarqués & IoT — Année académique 2025-2026