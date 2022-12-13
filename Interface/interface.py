import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PySide6.QtGui import Qt, QIcon
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel)

global App, Index
App = ''
Index = ''

#Usado para listar quais máquinas estão sendo verificadas e as aplicações de cada uma delas
url_of_all_machines = ['http://127.0.0.1:5000/']
list_nicks_machines = list()
list_programs = list()

class AppDemo(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowIcon(QIcon(r'Interface/Images/icon.ico'))
		self.setGeometry(100, 100, 500, 100)
		self.setWindowTitle("Restart Remoto")
		self.main_vLayout = QVBoxLayout()

		self.hLayout_1 = QHBoxLayout()
		self.main_vLayout.addLayout(self.hLayout_1)

		self.vLayout_1 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_1)

		self.vLayout_2 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_2)

		self.setLayout(self.main_vLayout)
		self.get_machines_names(url_of_all_machines)
		
		self.combo_machine_name = QComboBox()
		self.hLayout_1.addWidget(self.combo_machine_name)
		
		self.combo_app = QComboBox()
		self.hLayout_1.addWidget(self.combo_app)

		for i in range(len(list_nicks_machines)):
			list_programs.clear()
			list_programs.append('Choose the Application')
			
			if i != 0:
				self.get_app_list(url_of_all_machines)
			
			self.combo_machine_name.addItem(list_nicks_machines[i], list_programs)

		self.combo_machine_name.currentIndexChanged.connect(self.updateAppCombo)
		self.combo_machine_name.activated.connect(self.on_change_machine)
		self.combo_app.activated.connect(self.on_change_app)

		self.updateAppCombo(self.combo_machine_name.currentIndex())
		

		self.button_1 = QPushButton('Check Application Status')
		self.vLayout_1.addWidget(self.button_1)
		self.button_1.clicked.connect(self.check_state)
		

		self.button_2 = QPushButton('Close Application')
		self.vLayout_1.addWidget(self.button_2)
		self.button_2.clicked.connect(self.killApp)

		self.button_3 = QPushButton('Open Application')
		self.vLayout_1.addWidget(self.button_3)
		self.button_3.clicked.connect(self.openApp)

		self.label = QLabel(self)
		self.vLayout_2.addWidget(self.label)
		self.label.setAlignment(Qt.AlignBottom)
		
	def get_machines_names(self, URL_of_all):
		list_nicks_machines.clear()
		list_nicks_machines.append('Choose the Machine')
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
			apps_list = self.combo_machine_name.itemData(index)
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
		
			if (App == '') or App == ('Choose the Application'):
				return
			else:
				self.label.setText('Working on app: ' + App)
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: on_change_app'
			self.log_doc(self.log_text)

	@Slot()
	def on_change_machine(self):
		global Index
		try:
			Index = self.combo_machine_name.currentIndex()
			if Index != 0:
				self.label.setText('Working on machine: ' + list_nicks_machines[Index] + '   URL: ' + url_of_all_machines[Index-1])

		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: on_change_machine'
			self.log_doc(self.log_text)
	
	@Slot()
	def check_state(self):
		global Index
		try:
			if Index == 0:
				self.now = (datetime.now()).strftime("%H:%M:%S")
				self.label.setText(self.now + ' Impossible to check! Choose something!')
				return
		
			self.response = requests.get(url_of_all_machines[Index-1] +'/check')
			self.soup = BeautifulSoup(self.response.text, 'html.parser')
			self.apps_names = self.soup.find_all(id = 'app_name')
			self.apps_status = self.soup.find_all(id = 'status')

			for app_name, app_status in zip(self.apps_names, self.apps_status):
				if app_name.text == App:
					self.now = (datetime.now()).strftime("%H:%M:%S")
					self.label.setText(self.now + ' ' + app_name.text + '   status: ' + app_status.text)
				
			
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: check_state'
			self.log_doc(self.log_text)

	@Slot()
	def openApp(self):
		global App, Index
		try:
			self.apps, self.apps_status = self.check_app_state()
		
			if Index == 0:
				self.label.setText('Choose an Application to open')

			elif (App == self.apps) and (self.apps_status == 'Fechado'):
				self.label.setText('Opening aplication: ' + App)
				self.call_url('open', App)
				return
			elif (App == self.apps) and (self.apps_status == 'Aberto'):
				self.label.setText('Application is already open')
				return
		
			self.label.setText('Application not found!')
		
		except Exception as e:
			self.log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(self.log_text)

	@Slot()
	def killApp(self):
		global App, Index
		try:
			self.apps, self.apps_status = self.check_app_state()

			if Index == 0:
				self.label.setText('Choose an Application to close')

			if (App == self.apps) and (self.apps_status == 'Aberto'):
				self.label.setText('Closing aplication: ' + App)
				self.call_url('close', App)
				return
		
			if (App == self.apps) and (self.apps_status == 'Fechado'):
				self.label.setText('Application is already closed')
				return

			self.label.setText('Application not found!')
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
        print('Closing Window...')
            
