######################################################################
#                                                                    #
# VSF-Routing                                                        #
#                                                                    #
# Dieser kleine Parser uebersetzt eine mit OpenSeaMap.org oder       #
# OpenCPN erstellte KML-Wegpunktdatei in das VSF oder VS:NG Format.  #
# Den Inhalt der erstellten Textdatei komplett in die                #
# VSF Situationsdatei kopieren.                                      #
#                                                                    #
# Version:0.7.1          Datum:09.08.2021        Autor: Stefan Rothe #
#                                                                    #
# Release History:                                                   #
#                                                                    #
# Version 0.1: Initial Release, quick and dirty                      #
# Version 0.2: TKInter-Module included, Open und Save Dialoge        #
# Version 0.3: Textfeld eingebaut                                    #
# Version 0.4: OOP Architektur implementiert                         #
# Version 0.5: Menubar eingebaut                                     #
# Version 0.6: Methode "konvertieren" neu; OpenCPN Support           #
# Version 0.7.1: Aufraeumen und kommentieren. Referenz fuer GitHub   #
#                                                                    #
######################################################################

import sys
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from xml.dom import minidom



class VSFRoute():
	# Environment einrichten
	def __init__(self, master):
		
		##################---GUI---###################################
	
		# Globalvariable initialisieren
		self.waypoints = ''
		self.wplist = ''
		self.KMLfile = ''

		# Fonts fuer Widgets deklarieren
		self.Helv10Bold = 'Helvetica 10 bold'
		
		# Anwendungsfenster einrichten
		master.title('VSF-Waypoint Konverter')
		master.geometry("640x480")
		
		# Menueleiste
		menubar = Menu(master)
		filemenu = Menu(menubar, tearoff = 0)
		filemenu.add_command(label = 'Open KML file ...', command = self.konvertieren)
		filemenu.add_command(label = 'Save Waypoints ...', command = self.speichern)
		filemenu.add_separator()
		filemenu.add_command(label = "Quit", accelerator="Ctrl+Q", command = quit)
		menubar.add_cascade(label = 'File', menu = filemenu)
		editmenu = Menu(menubar, tearoff=0)
		editmenu.add_command(label="Cut", accelerator="Ctrl+X", \
            command=lambda: self.editor.event_generate('<<Cut>>'))
		editmenu.add_command(label="Copy", accelerator="Ctrl+C", \
            command=lambda: self.editor.event_generate('<<Copy>>'))
		editmenu.add_command(label="Paste", accelerator="Ctrl+V", \
            command=lambda: self.editor.event_generate('<<Paste>>'))
		menubar.add_cascade(label="Edit", menu=editmenu)
		convertmenu = Menu(menubar, tearoff = 0)
		convertmenu.add_command(label = 'Convert to VS:NG', command = self.toVSNG)
		convertmenu.add_command(label = 'Convert to VSF', command = self.toVSF)
		menubar.add_cascade(label = 'Convert', menu = convertmenu)
		master.config(menu=menubar)
		filemenu.bind_all("<Control-q>", quit)
		
		# Textedit Bereich mit Scrollbar
		topframe=Frame(master, height=100, width=200)
		topframe.pack(fill=NONE)
		self.editor=Text(topframe,height=24, width=80, padx=10, pady=5)
		self.scrollbar=Scrollbar(topframe)
		self.scrollbar.pack(side=RIGHT, fill=Y)
		self.editor.pack(side=LEFT, fill=Y)
		self.scrollbar.config(command=self.editor.yview)
		self.editor.config(yscrollcommand=self.scrollbar.set)

		# Steuerbereich
		bottomframe=Frame(master, pady=10, padx=10)
		bottomframe.pack(side=BOTTOM)
		openButton = Button(bottomframe, padx = 10, pady=5, font=self.Helv10Bold, text="Convert to VS:NG", command=self.toVSNG)
		openButton.pack(side=LEFT)
		openButton = Button(bottomframe, padx = 10, pady=5, font=self.Helv10Bold, text="Convert to VSF", command=self.toVSF)
		openButton.pack(side=LEFT)
		space=Label(bottomframe, padx = 80, pady=5, text='')
		space.pack(side=LEFT)
		exitButton = Button(bottomframe, padx = 10, pady=5, font=self.Helv10Bold, text="Exit", command=self.clickExitButton)
		exitButton.pack(side=RIGHT)
		saveButton = Button(bottomframe, padx = 10, pady=5, font=self.Helv10Bold, text="Save Waypoints...", command=self.speichern)
		saveButton.pack(side=RIGHT)
		
		
		
		##################---ENDE GUI---##############################

	# Funktionen definieren        

	def konvertieren(self):
		# KML Datei mit Koordinaten in Dezimalgrad einlesen
		alert="" # Warnung initialisieren
		f=fd.askopenfile(title='KML Datei oeffnen',filetypes=[('KML Files', '*.kml')])
		app.KMLfile = f.name
		if f:
			kml=minidom.parse(f) #kml-Datei in DOM parsen
			root=kml.documentElement #Root-Element finden
			#Die Liste der Wegpunktkoordinaten befindet sich im Tag "LineString"
			waypoints=root.getElementsByTagName("LineString")[0].firstChild.nextSibling.firstChild.data
			
			# Datenquelle ermitteln und spezifische Umformungen vornehmen
			if root.firstChild.nextSibling.firstChild.nextSibling.firstChild.data.find("OpenSeaMap") != -1:
				# OpenSeaMap Export
				# Umformatierung fuer VSF
				waypoints=waypoints.replace('\n','') #OpenSeaMap-spezifisch: Umbruch vor erstem Wegpunkt entfernen
				waypoints=waypoints.replace(' ',',0.00000,')
				waypoints.strip()
			elif root.firstChild.nextSibling.firstChild.nextSibling.firstChild.data.find("OpenCPN") != -1:
				# OpenCPN Export
				# Umformatierung fuer VSF
				waypoints=waypoints.replace(',0.',',0.00000,') #OpenCPN-spezifisch: Z-Wert ohne Nachkommastellen anpassen
				waypoints.strip()				
			else:
				# Warnung: Datenquelle nicht unterstuetzt
				mb.showinfo("Error", "Unsupported KML Source")
				alert=('\nKML source not supported!\n\nValid KML sources are OpenSeaMap and OpenCPN')
			
			# Anzeige der Wegpunktliste im Editor
			self.editor.delete('1.0', END)
			if alert: #Warnmeldung anzeigen
				self.editor.insert(END, alert)
			else:	  
				#Wegpunktstring in Liste zerlegen
				app.wplist = list(waypoints.split(','))
				del app.wplist[-1:]	#Loescht das letzte Listenelement (leer, wegen Komma am Ende des Strings)
				app.toVSNG()
				 
				    
	def toVSNG(self):
		#Fuer VS:NG formatieren
		app.editor.delete('1.0', END)
		app.editor.insert(END,'\n//Waypoints List for VS:NG Situation File\n//KML-File: '+app.KMLfile+'\n\n') # Header Zeile (Kommentar)
		#Listenelemente zu VS:NG Wegpunktliste formatieren
		for i in range(0,len(app.wplist),3):
			app.editor.insert(END,('%.6f\t%.6f\t%.6f\t[vehicle_waypoint]\n' % (float(app.wplist[i]), float(app.wplist[i+1]), float(app.wplist[i+2]))))
			
	def toVSF(self):
		#Fuer VSF formatieren
		app.editor.delete('1.0', END)
		app.editor.insert(END,'\n//Waypoints List for VSF Situation File\n//KML-File: '+app.KMLfile+'\n\n') # Header Zeile (Kommentar)
		app.editor.insert(END, (str(len(app.wplist)//3)+'\t[waypoints_num]\n\n')) #Anzahl Wegpunkte, wird im VSF benoetigt
		#Listenelemente zu VSF Wegpunktliste formatieren  
		for i in range(0,len(app.wplist),3):
			app.editor.insert(END,('%.6f\t[waypoint_x]\n%.6f\t[waypoint_y]\n%.7f\t[waypoint_z]\n\n' % (float(app.wplist[i]), float(app.wplist[i+1]), float(app.wplist[i+2]))))				     
		
	def speichern(self):
		# Editor auslesen
		vsfWP=self.editor.get('1.0',END)
		vsfWP.strip()
		# Dateioperationen
		if (len(vsfWP)>0):
			out=fd.asksaveasfile(title='Wegpunkte speichern',mode='w', defaultextension=".txt",)
			out.write(vsfWP)
			out.close()
			self.editor.delete('1.0', END)
			
	def clickExitButton(self):
		quit()

# Und los geht's...Laufzeitumgebung

root = Tk() #Tk-Objekt definieren
app = VSFRoute(root) #Laufzeitumgebung
root.mainloop() # Instanz einrichten

