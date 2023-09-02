"""
JAOUANNE Lilian & GARCON Bastian PEI2   04-2023
Soft Application Thermocouple WiFI

Le script python est un client qui se connecte au serveur TCP généré par un ESP8266.
Il recoit les donnees de tension de la soudure chaude et la temperature de la soudure froide par le serveur.
Apres traitement des donnees, des valeurs de durees et les valeurs de temperatures de la SC deduites sont stockees dans un fichier csv (Excel).
"""

import ClientTCP_fct #On importe le scripte contenant certaines fonctions
from tkinter import filedialog
import tkinter as tk
import subprocess
import socket
import time
import csv
import os

#initialisation des variables globales
nom_fichier=""
headers = ["Temps (ms)", "Température (°C)"]

"""Classe Application qui hérite de la classe Frame de Tkinter
Cette classe contient une méthode __init__ qui est appelée lors 
de la création d'un nouvel objet de la classe Application. Dans cette méthode, 
nous appelons également la méthode create_widgets, qui crée les boutons"""
class Application(tk.Frame):
    #ATTRIBUTS
    # Variable de classe pour stocker une référence aux fenetres de la barre de menu
    about_window = None
    begin_window = None
    sf_window = None
    variable_label = None
    
    #CONSTRUCTEURS
    def __init__(self, master=None, title="", dimX="", dimY=""):
        super().__init__(master)
        self.master = master
        self.i = 0  #valeur soudure froide temperature pour calibrage
        self.master.title(title)
        self.master.geometry(dimX+"x"+dimY)
        # Définition de la taille minimale de la fenêtre
        self.master.minsize(dimX,dimY)
        self.pack()
        self.create_widgets()
        

    #METHODES
    def create_widgets(self):
        # Calcul de la largeur et hauteur de la fenêtre
        self_width = self.winfo_reqwidth()
        self_height = self.winfo_height()
        
        # Création de la barre de menu
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        
        # Créer l'onglet "Fichier" avec son sous-onglet
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Enregistrer", command=self.save)
        file_menu.add_command(label="Ouvrir", command=self.open)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        #Creer l onglet "Réglages"
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="Soudure Froide", command=self.sf)
        menubar.add_cascade(label="Réglages", menu=config_menu)
        
        # Créer l'onglet "Aide" avec ses sous-onglets
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="A propos", command=self.about)
        help_menu.add_command(label="Utilisation", command=self.begin)
        menubar.add_cascade(label="Aide", menu=help_menu)

        # Ajout d'un widget étiquette
        label_titre1 = tk.Label(self, text="Thermocouple avec acquisition WiFi", font=("Arial", 18, "bold"), pady=20)
        label_titre1.pack()
        
        # Créer un widget Label pour afficher le nom du fichier choisi
        self.filename_label = tk.Label(self, text="Sélectionner un fichier .csv depuis l'onglet Fichier/Enregistrer", font=("Arial", 9))
        self.filename_label.pack()
        
        # Création du conteneur de widgets rond annimation acquisition
        containerAcquisition = tk.Frame(self)
        self.canvas = tk.Canvas(containerAcquisition, width=20, height=20, highlightthickness=1)
        self.canvas.pack(side="left")
        self.circle = self.canvas.create_oval(1, 1, 20, 20, fill="#FF7700")
        self.label_acquisition = tk.Label(containerAcquisition, text="Arrêté", font=("Arial", 12, "bold"))
        self.label_acquisition.pack(side="left")
        containerAcquisition.pack(pady=50)
        
        # Création du conteneur de widgets bouttons start et stop
        containerStartStop = tk.Frame(self)
        # Ajout d'une zone de texte et d'un bouton Valider
        bouton_start = tk.Button(containerStartStop, text="Démarrer", height=2, width=10, bg="Green", command=self.start)
        bouton_start.grid(row=0, column=0)
        texte_espace = tk.Label(containerStartStop, text="  ")
        texte_espace.grid(row=0, column=1)
        bouton_stop = tk.Button(containerStartStop, text="Arrêter", height=2, width=10, bg="Red", command=self.stop)
        bouton_stop.grid(row=0, column=2)
        # Placement du conteneur au centre de la fenêtre
        containerStartStop.pack()
        
        # Créer un label permettant l affichage de messages d informations
        self.text_message = tk.Label(self.master, text="", font=("Arial", 12), fg="red")
        self.text_message.place(relx=0.5, rely=0.8, anchor="center")
        
        # Créer un cadre en bas à gauche de la fenêtre
        bottom_left_frame = tk.Frame(self.master)
        bottom_left_frame.pack(side="left", padx=10, pady=10, anchor="sw")
        # Ajouter deux étiquettes dans le cadre bottom_left_frame
        label1 = tk.Label(bottom_left_frame, text="Thermocouple WiFi   ", anchor="sw", font=("Arial", 9))
        label1.pack(side="left")
        label2 = tk.Label(bottom_left_frame, text="Version 1.0", anchor="sw", font=("Arial", 9, "underline"))
        label2.pack(side="left", padx=(0,0)) # Ajouter un padding horizontal à gauche de la deuxième étiquette
        
        # Créer un cadre en bas à droite de la fenêtre
        bottom_right_frame = tk.Frame(self.master)
        bottom_right_frame.pack(side="right", padx=10, pady=10, anchor="se")
        # Créer un bouton "Quitter" qui ferme la fenêtre
        quit_btn = tk.Button(bottom_right_frame, text="Quitter", anchor="se", fg="red", font=("Arial", 9), command=self.master.destroy)
        quit_btn.pack(side="right")

    def connect(self):
        global client_socket
        HOST = '192.168.4.1'#adresse IP par defaut de l'ESP8266
        PORT = 12345 #port d'ecoute defini de l'ESP8266
        try:
            # Créer un objet socket TCP
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((HOST, PORT))
            print('Connecté au serveur')
            local_ip, local_port = client_socket.getsockname()
            print("Informations de connexion {}:{}".format(local_ip,local_port))
            self.text_message.config(text="")
            return 1
        except:
            print('Connection échouée')
            self.text_message.config(text="Vérifier votre connexion au réseau de l'ESP8266\nSSID : Thermocouple   MDP : ENSIBS2023")
            return 0
    
    def disconnect(self):
        global client_socket
        client_socket.close()
        print('Déconnecté du serveur')

    def open(self):
        # Affichage de la fenêtre de dialogue pour sélectionner le fichier CSV
        file_path = filedialog.askopenfilename(filetypes=[('Fichiers CSV', '*.csv')])
        # Si un fichier a été sélectionné, ouvrir le fichier dans Excel
        if file_path:
            subprocess.run(['start', '', file_path], shell=True)
    
    def sf(self):
        if not self.sf_window:
            # Création de la fenêtre de la variable
            self.sf_window = tk.Toplevel(self.master)
            self.sf_window.title("Réglage soudure froide")
            self.sf_window.geometry("300x150")
            self.sf_window.minsize(300,150)
            
            # Ajout d'un label pour la variable
            labelhead1 = tk.Label(self.sf_window, text="Calibrage de la soudure froidre", font=("Arial", 12, "bold"), fg = "blue")
            labelhead1.pack(side="top", pady=10)
            self.sf_label = tk.Label(self.sf_window, text="Régler manuellement le potentiomètre\n\nSF = " + str(self.i) + " °C")
            self.sf_label.pack()
            
            # Essaye de se connecter au serveur ESP8266
            etat_connection = self.connect()
            if(etat_connection==1):
                # Lancement de la fonction d'incrémentation toutes les 100ms
                self.master.after(100, self.actualiser_sf)
            else:
                self.sf_window.destroy()
                self.sf_window = None
        
        def on_close():
            self.sf_window.destroy()
            self.sf_window = None
            if (etat_connection==1):
                self.disconnect()

        # Configurer la fonction de fermeture de la fenêtre
        self.sf_window.protocol("WM_DELETE_WINDOW", on_close)

    def actualiser_sf(self):#recuperer valeur temperature SF (soudure froide) par wifi
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            nul=0
        #Si on recoie une valeur sur plus de 13 caracteres -> on aura recu plusieurs / trop de valeurs
        elif (len(data) <= 13):
            try:
                TensionThermo,TemperatureSF = data.strip().split(',')
                TemperatureSF = float(TemperatureSF)
                self.i = TemperatureSF
            except:
                print("erreur")
        self.update()
        if self.sf_label:
            # Mise à jour du label affichant la variable
            self.sf_label.config(text="Calibrage de la soudure froidre\nRégler manuellement le potentiomètre\n\nSF = " + str(self.i) + " °C")
        # Relance de la fonction d'incrémentation toutes les 100ms
        self.master.after(100, self.actualiser_sf)
    
    
    def begin(self):
        # Si une fenêtre "Utilisation" est déjà ouverte, ne rien faire
        if self.begin_window is not None:
            return

        # Créer une nouvelle fenêtre pour afficher les informations "Utilisation"
        self.begin_window = tk.Toplevel(self)
        self.begin_window.title("Utilisation")
        self.begin_window.geometry("700x250")
        self.begin_window.minsize(700,250)
        
        # Ajouter un widget Text pour afficher le texte et y attacher une barre de défilement
        labelhead1 = tk.Label(self.begin_window, text="Commencer avec Thermocouple_WiFi IDE", font=("Arial", 12, "bold"), fg = "blue")
        labelhead1.pack(side="top", pady=10)
        
        # Créer un lien cliquable pour ouvrir le fichier PDF
        lien = tk.Label(self.begin_window, text="Ouvrir le manuel d'utilisation", fg="blue", cursor="hand2", underline=True)
        lien.pack()
        # Associer la fonction ouvrir_pdf() au clic sur le lien
        lien.bind("<Button-1>", lambda e: os.startfile("AppThermocouple\Manuel_Utilisation.pdf"))
        
        text = "  -Se connecter au réseau WiFi : \"thermocouple\" mot de passe : \"ensibs\"\n\n   -Calibrer la température ambiante dans la barre de menu dans Réglage/Soudure Froide\n\n   -Créer ou sélectionner un fichier .cvs depuis la barre de menu dans Fichier/Enregistrer\n\n   -Presser le bouton \"Start\" pour commencer l'enregistrement des données reçues dans le fichier sélectionné\n\n   -Arrêter la réception en pressant le bouton \"Stop\"\n\n   -Consulter les données reçues en sélectionnant le fichier depuis la barre de menu dans Fichier/Ouvrir"
        text_widget = tk.Text(self.begin_window, wrap="word")
        text_widget.insert("1.0", text)
        text_widget.pack(side="left", fill="both", expand=True)
        
        #ajoute une barre verticale pour scroller le texte
        scrollbar = tk.Scrollbar(self.begin_window, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Définir une fonction pour supprimer la référence à la fenêtre "Utilisation" lorsque la fenêtre est fermée
        def on_close():
            self.begin_window.destroy()
            self.begin_window = None

        # Configurer la fonction de fermeture de la fenêtre
        self.begin_window.protocol("WM_DELETE_WINDOW", on_close)
        
    
    def about(self):
        # Si une fenêtre "A propos" est déjà ouverte, ne rien faire
        if self.about_window is not None:
            return

        # Créer une nouvelle fenêtre pour afficher les informations "A propos"
        self.about_window = tk.Toplevel(self)
        self.about_window.title("A propos")
        self.about_window.geometry("200x150")
        self.about_window.minsize(200,150)
        self.about_window.maxsize(200,150)
        
        # Ajouter un widget Text pour afficher le texte et y attacher une barre de défilement
        labelhead1 = tk.Label(self.about_window, text="Thermocouple_WiFi IDE", font=("Arial", 12, "bold"), fg = "blue")
        labelhead1.pack(side="top", pady=10)
        text = "Version: 1.0.1\nDate: 2023-05\n\nCopyright © 2023 ENSIBS"
        text_widget = tk.Text(self.about_window, wrap="word")
        text_widget.insert("1.0", text)
        text_widget.pack(side="left", fill="both", expand=True)

        # Définir une fonction pour supprimer la référence à la fenêtre "A propos" lorsque la fenêtre est fermée
        def on_close():
            self.about_window.destroy()
            self.about_window = None

        # Configurer la fonction de fermeture de la fenêtre
        self.about_window.protocol("WM_DELETE_WINDOW", on_close)

    def save(self):
        global nom_fichier
        # Ouvrir une boîte de dialogue pour sélectionner un emplacement et un nom de fichier
        filename = filedialog.asksaveasfilename(defaultextension='.csv')

        # Vérifier si l'utilisateur a sélectionné un emplacement et un nom de fichier
        if filename:
            print("Fichier courant : ", filename)
            # Mettre à jour le texte du widget Label avec le nom du fichier choisi
            self.filename_label.config(text="Répertoire courant : \n" + filename, font=("Arial", 9))
            nom_fichier = filename
            # Ouvrir le fichier en mode écriture avec le module csv
            fichier = open(filename, "a", newline="")# a -> ajouter et ne pas ecrire par dessus des donnees existantes
            writer = csv.writer(fichier, delimiter=";")#ecrire sur les colonnes
            fichier.close()
            self.text_message.config(text="")
           
    def start(self):
        global nom_fichier
        # Essaye de se connecter au serveur ESP8266
        etat_connection = self.connect()
        if(etat_connection==1):
            start_time = time.time()
            if (nom_fichier!=""):#Si un fichier a ete selectionne via l'onglet enregistrer
                # Ouvrir le fichier en mode écriture avec le module csv
                fichier = open(nom_fichier, "a", newline="")
                writer = csv.writer(fichier, delimiter=";")#ecrire sur les colonnes
                writer.writerow(headers) #Ecrit le nom des colonnes
                # Récupérer les données envoyées par le serveur
                self.canvas.itemconfigure(self.circle, fill="gray")
                self.label_acquisition.config(text="Acquisition en cours")
                k=10
                self.running = True
                while self.running:
                    #actualisation couleur led annimation touus les 10 cycles
                    if(k==0):
                        k=10
                        color = self.canvas.itemcget(self.circle, "fill")
                        if color == "green":
                            self.canvas.itemconfigure(self.circle, fill="gray")
                        else:
                            self.canvas.itemconfigure(self.circle, fill="green")
                        
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    #Si on recoie une valeur sur plus de 13 caracteres -> on aura recu plusieurs / trop de valeurs
                    if(len(data) <= 13):
                        try:
                            TensionThermo,TemperatureSF = data.strip().split(',')
                            TensionThermo = float(TensionThermo)#conversion des string en float
                            TemperatureSF = float(TemperatureSF)
                            current_time = time.time() - start_time
                            millisecondes = int(current_time * 1000)
                            TensionCapteur = ClientTCP_fct.ConvertTemp_Tension(TemperatureSF)
                            TemperatureSC = round(ClientTCP_fct.ConvertTension_Temp(TensionThermo + TensionCapteur), 2)#arrondir a deux decimales
                            print(f'TensionSC : {TensionThermo} mV, Temperature: {TemperatureSC} °C, Temps: {millisecondes}')
                            millisecondes = str(millisecondes)#conversion en string
                            TemperatureSC = str(TemperatureSC)
                            TemperatureSC = format(TemperatureSC).replace('.', ',')#remplacer les points par des vigules pour excel
                            writer.writerow([millisecondes, TemperatureSC])#methode pour ecrire une ligne dans un fichier csv
                        except:
                            print("erreur")
                    self.update() # Verifie que le bouton stop n'est pas appuyé
                    k-=1
                    
                # Fermer la connexion et fermeture du fichier csv
                self.label_acquisition.config(text="Arrêté")
                self.canvas.itemconfigure(self.circle, fill="#FF7700")
                fichier.close()
                self.disconnect()
                
            else:
                self.text_message.config(text="Veuiller charger un fichier pour l'enregistrement des données")
                self.disconnect()
        

    def stop(self):
        self.disconnect()
        self.running = False
        self.text_message.config(text="") #Aucun message d alterte a afficher
    
    
"""Creation d une instance de la classe Application et appelons la méthode 
mainloop de l'objet pour démarrer l'application Tkinter"""
root = tk.Tk()
app = Application(master=root, title="Thermocouple WiFi", dimX="700", dimY="400")
app.mainloop()