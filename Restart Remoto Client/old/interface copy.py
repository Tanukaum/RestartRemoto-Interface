import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PySide6.QtGui import Qt, QIcon, QFont, QColor
from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QAbstractItemView, QApplication, QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel, QListWidget, QListWidgetItem

global Index
Index = ''

#Usado para listar quais máquinas estão sendo verificadas e as aplicações de cada uma delas
#url_of_all_machines = ['http://172.22.160.50:5000/']
url_of_all_machines = ['http://10.74.154.233:5000/','http://172.22.160.49:5000/']

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

		self.hLayout_2 = QHBoxLayout()
		self.vLayout_1.addLayout(self.hLayout_2)
		
		self.vLayout_2 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_2)

		self.vLayout_3 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_3)

		self.setLayout(self.main_vLayout)
		self.get_machines_names(url_of_all_machines)
		
		self.combo_machine_name = QComboBox()
		self.hLayout_1.addWidget(self.combo_machine_name)
		
		for machine in list_nicks_machines:
			self.combo_machine_name.addItem(machine)
		

		self.list_apps = QListWidget()
		self.hLayout_2.addWidget(self.list_apps)

		self.list_status = QListWidget()
		self.hLayout_2.addWidget(self.list_status)

		self.list_apps.setFont(QFont('Arial', 11))
		
		self.list_apps.setSpacing(5)
		self.list_apps.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_apps.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_apps.setMinimumHeight((self.list_apps.sizeHint().height()/2))

		self.list_status.setFont(QFont('Arial', 11))
		
		self.list_status.setSpacing(5)
		self.list_status.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status.setMinimumHeight((self.list_status.sizeHint().height()/2))

		self.list_apps.setSelectionMode(QAbstractItemView.MultiSelection)
		
		self.combo_machine_name.activated.connect(self.on_change_machine)


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

	def save_item_click(self):
		items = self.list_apps.selectedItems()
		list_items = []
		for i in range(len(items)):
			list_items.append(str(self.list_apps.selectedItems()[i].text()))

		return list_items
	
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
			list_programs.clear()
			self.response = requests.get(machine_url + '/check')
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			self.apps_names = self.soup.find_all(id = 'app_name')
			for app_name in self.apps_names:
				list_programs.append(app_name.text)
		
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_app_list'
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

	def check_request(self):
		self.response = requests.get(url_of_all_machines[Index-1] +'/check')
		self.soup = BeautifulSoup(self.response.text, 'html.parser')
		self.apps_names = self.soup.find_all(id = 'app_name')
		self.apps_status = self.soup.find_all(id = 'status')

		return self.apps_names, self.apps_status

	@Slot()
	def on_change_machine(self):
		global Index
		try:
			Index = self.combo_machine_name.currentIndex()
			if Index != 0:
				self.label.setText('Trabalhando na máquina: ' + list_nicks_machines[Index] + '   URL: ' + url_of_all_machines[Index-1])
				self.get_app_list(url_of_all_machines[Index-1])		

			self.apps_names, self.apps_status = self.check_request()
			for app_name, app_status in zip(self.apps_names, self.apps_status):
				if app_status.text == 'Fechado':
					self.list_item = QListWidgetItem(app_name.text)
					self.list_item.setBackground(QColor('#FF0000'))
				else:
					self.list_item = QListWidgetItem(app_name.text)
					self.list_item.setBackground(QColor('#7fc97f'))
				
				self.list_apps.addItem(self.list_item)


		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: on_change_machine'
			self.log_doc(self.log_text)


	@Slot()
	def check_state_recurring(self):
		global Index
		try:
			if Index == 0:
				self.now = (datetime.now()).strftime("%H:%M:%S")
				self.label.setText(self.now + ' Escolha uma máquina e programa')
				return
			
			self.apps_names, self.apps_status = self.check_request()

			for app_name, app_status in zip(self.apps_names, self.apps_status):
				if app_status.text == 'Fechado':
					self.list_item = QListWidgetItem('status: ' + app_status.text)
					self.list_item.setBackground(QColor('#FF0000'))
				else:
					self.list_item = QListWidgetItem('status: ' + app_status.text)
					self.list_item.setBackground(QColor('#7fc97f'))
				
				self.list_status.addItem(self.list_item)
				
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: check_state'
			self.log_doc(self.log_text)

	@Slot()
	def openApp(self):
		global Index
		try:
			self.itens_clicados = self.save_item_click()
			self.apps_names, self,apps_status = self.check_request()

			for item in self.itens_clicados:
				print('item: ' + item)
				for app_name, app_status in zip(self.apps_names, self,apps_status):
					print('app_name: ' + app_name)
					if Index == 0:
						self.label.setText('Escolha um programa para abrir')

					elif (app_status == 'Fechado') and (app_name == item):
						self.call_url('open', item)
						
					elif (app_status == 'Aberto') and (app_name == item):
						self.label.setText('O programa já está aberto!')
						
					else:
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
            
