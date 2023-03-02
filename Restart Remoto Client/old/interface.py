import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PySide6.QtGui import Qt, QIcon, QFont, QColor
from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel, QListWidget, QListWidgetItem

global App, Index
App = ''
Index = ''

#Usado para listar quais máquinas estão sendo verificadas e as aplicações de cada uma delas
url_of_all_machines = ['http://10.74.154.233:5000/']
#url_of_all_machines = ['http://10.74.154.233:5000/','http://172.22.160.49:5000/']

list_nicks_machines = list()
list_programs = list()

class AppDemo(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowIcon(QIcon(r'Images/icon.ico'))
		self.setGeometry(100, 100, 350, 100)
		self.setWindowTitle("Restart Remoto")
		self.main_vLayout = QVBoxLayout()

		self.hLayout_1 = QHBoxLayout()
		self.main_vLayout.addLayout(self.hLayout_1)

		self.vLayout_1 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_1)
		
		self.vLayout_2 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_2)

		self.vLayout_3 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_3)

		self.setLayout(self.main_vLayout)
		self.get_machines_names(url_of_all_machines)
		
		self.combo_machine_name = QComboBox()
		self.hLayout_1.addWidget(self.combo_machine_name)
		
		'''self.combo_app = QComboBox()
		self.hLayout_1.addWidget(self.combo_app)
'''
		self.list_status_apps = QListWidget()
		self.vLayout_1.addWidget(self.list_status_apps)
		self.list_status_apps.setFont(QFont('Arial', 11))
		
		self.list_status_apps.setSpacing(5)
		self.list_status_apps.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status_apps.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status_apps.setMinimumHeight((self.list_status_apps.sizeHint().height()/2))

		for i in range(len(list_nicks_machines)):
			list_programs.clear()
			list_programs.append('Escolha o Programa')
			
			if i != 0:
				self.get_app_list(url_of_all_machines)
			
			self.combo_machine_name.addItem(list_nicks_machines[i], list_programs)


		self.combo_machine_name.currentIndexChanged.connect(self.updateAppCombo)
		self.combo_machine_name.activated.connect(self.on_change_machine)
		#self.combo_app.activated.connect(self.on_change_app)

		self.updateAppCombo(self.combo_machine_name.currentIndex())
		
		self.button_1 = QPushButton('Fechar o Programa')
		self.vLayout_2.addWidget(self.button_1)
		self.button_1.clicked.connect(self.killApp)

		self.button_2 = QPushButton('Abrir o Programa')
		self.vLayout_2.addWidget(self.button_2)
		self.button_2.clicked.connect(self.openApp)

		self.label = QLabel(self)
		self.vLayout_3.addWidget(self.label)
		self.label.setAlignment(Qt.AlignBottom)

		self.timer = QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.check_state_recurring)
		self.timer.start()
		
	def get_machines_names(self, URL_of_all):
		list_nicks_machines.clear()
		list_nicks_machines.append('Escolha a Máquina')
		try:
			for i in range(len(URL_of_all)):
				self.response = requests.get(URL_of_all[i] + '/check')
				self.soup = BeautifulSoup(self.response.text, 'html.parser')
				self.machine_name = self.soup.find(id = 'machine_name')
			
				list_nicks_machines.append(self.machine_name.text)
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(self.log_text)

	def get_app_list(self, machine_url):
		try:
			for url in machine_url:
				self.response = requests.get(url + '/check')
				self.soup = BeautifulSoup(self.response.text, 'html.parser')
				self.apps_names = self.soup.find_all(id = 'app_name')
				for app_name in self.apps_names:
					list_programs.append(app_name.text)
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_app_list'
			self.log_doc(self.log_text)

	def check_app_state(self):
		global Index, App
		
		try:
			self.response = requests.get(url_of_all_machines[Index-1] +'/check')
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			self.apps_names = self.soup.find_all(id = 'app_name')
			self.apps_status = self.soup.find_all(id = 'status')
		
			for app_name, app_status in zip(self.apps_names, self.apps_status):
				if app_name.text == App:
					return app_name.text, app_status.text

		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: check_app_state'
			self.log_doc(self.log_text)

	def call_url(self, command, application):
		global Index
		try:
			self.response = requests.get(url_of_all_machines[Index-1] + '/' + command + '/' + application)
			self.log_text = url_of_all_machines[Index-1] + ' ' + command + ' ' + application + ' status code: ' + str(self.response.status_code)

			self.log_uso(self.log_text)
			
			self.now = (datetime.now()).strftime("%H:%M:%S")
			self.label.setText(self.now + ' ' + command + '  ' + application + ' status<' + str(self.response.status_code)+'>')

		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: call_url'
			self.log_doc(self.log_text)
	
	def log_doc(self, log_text):
		self.now = datetime.now()
		self.now_format = self.now.strftime("%d-%m-%y %H:%M:%S")
		
		with open(os.path.relpath("Interface/Log/LogErros.txt"), 'a+') as f:
			f.writelines(self.now_format + "  " + log_text + "\n")

	def log_uso(self, log_text):
		self.now = datetime.now()
		self.now_format = self.now.strftime("%d-%m-%y %H:%M:%S")
		
		with open(os.path.relpath("Interface/Log/LogUso.txt"), 'a+') as f:
			f.writelines(self.now_format + "  " + log_text + "\n")

	@Slot()
	def updateAppCombo(self, index):
		global Index
		try:
			Index = int(self.combo_machine_name.currentIndex())
		
			self.combo_app.clear()
			apps_list = self.combo_machine_name.itemData(Index)
			if apps_list:
				self.combo_app.addItems(apps_list)
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: updateAppCombo'
			self.log_doc(self.log_text)
	
	@Slot()
	def on_change_app(self):
		global App
		try:
			App = self.combo_app.currentText()
		
			if (App == '') or App == ('Escolha o Programa'):
				return
			else:
				self.label.setText('Trabalhando no app: ' + App)
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: on_change_app'
			self.log_doc(self.log_text)

	@Slot()
	def on_change_machine(self):
		global Index
		try:
			Index = self.combo_machine_name.currentIndex()
			if Index != 0:
				self.label.setText('Trabalhando na máquina: ' + list_nicks_machines[Index] + '   URL: ' + url_of_all_machines[Index-1])			
				
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: on_change_machine'
			self.log_doc(self.log_text)


	@Slot()
	def check_state_recurring(self):
		global Index
		try:
			self.list_status_apps.clear()
			if Index == 0:
				self.now = (datetime.now()).strftime("%H:%M:%S")
				self.label.setText(self.now + ' Escolha uma máquina e programa')
				return
			
			self.response = requests.get(url_of_all_machines[Index-1] +'/check')
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			self.apps_names = self.soup.find_all(id = 'app_name')
			self.apps_status = self.soup.find_all(id = 'status')

			for app_name, app_status in zip(self.apps_names, self.apps_status):
				if app_status.text == 'Fechado':
					self.list_item = QListWidgetItem(app_name.text + '   status: ' + app_status.text)
					self.list_item.setBackground(QColor('#FF0000'))
				else:
					self.list_item = QListWidgetItem(app_name.text + '   status: ' + app_status.text)
					self.list_item.setBackground(QColor('#7fc97f'))
				
				self.list_status_apps.addItem(self.list_item)
				
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: check_state'
			self.log_doc(self.log_text)

	@Slot()
	def openApp(self):
		global App, Index
		try:
			self.apps, self.apps_status = self.check_app_state()
		
			if Index == 0:
				self.label.setText('Escolha um programa para abrir')

			elif (App == self.apps) and (self.apps_status == 'Fechado'):
				self.label.setText('Abrindo o app: ' + App)
				self.call_url('open', App)
				return
			elif (App == self.apps) and (self.apps_status == 'Aberto'):
				self.label.setText('O programa já está aberto!')
				return
		
			self.label.setText('Programa não encontrado!')
		
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(self.log_text)

	@Slot()
	def killApp(self):
		global App, Index
		try:
			
			self.apps, self.apps_status = self.check_app_state()

			if Index == 0:
				self.label.setText('Escolha um programa para fechar')
				

			if (App == self.apps) and (self.apps_status == 'Aberto'):
				self.label.setText('Fechando o app: ' + App)
				self.call_url('close', App)
				return
		
			if (App == self.apps) and (self.apps_status == 'Fechado'):
				self.label.setText('Programa já está fechado!')
				return

			self.label.setText('Programa não encontrado!')
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(self.log_text)

#Inicialização da aplicação
if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = AppDemo()
    demo.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Fechando Janela...')
            
