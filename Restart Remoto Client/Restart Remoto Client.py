import os
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from PySide6.QtGui import Qt, QIcon, QFont, QColor
from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel, QListWidget, QListWidgetItem, QAbstractItemView

global Index_nick, Index_url
Index_nick = Index_url = ''

#Usado para listar quais máquinas estão sendo verificadas e as aplicações de cada uma delas
url_of_all_machines = ['http://localhost:5000/']

list_programs = list()

class AppDemo(QWidget):
	def __init__(self):
		super().__init__()
		self.setGeometry(100, 100, 350, 100)
		self.setWindowTitle("Restart Remoto")
		
		self.UiComponents()
		self.get_machine_nicks()

	def UiComponents(self):
		self.main_vLayout = QVBoxLayout()

		self.hLayout_1 = QHBoxLayout()
		self.main_vLayout.addLayout(self.hLayout_1)

		self.vLayout_1 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_1)
		
		self.vLayout_2 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_2)

		self.vLayout_3 = QVBoxLayout()
		self.main_vLayout.addLayout(self.vLayout_3)

		self.combo_machine_name = QComboBox()
		self.combo_machine_name.addItem('Escolha um Engine')
		self.hLayout_1.addWidget(self.combo_machine_name)
		
		self.list_status_apps = QListWidget()
		self.vLayout_1.addWidget(self.list_status_apps)
		self.list_status_apps.setFont(QFont('Arial', 11))
		self.list_status_apps.setSelectionMode(QAbstractItemView.MultiSelection)
		self.list_status_apps.setSpacing(5)
		self.list_status_apps.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status_apps.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.list_status_apps.setMinimumHeight((self.list_status_apps.sizeHint().height()/2))

		self.combo_machine_name.currentIndexChanged.connect(self.machine_name_changed)
		
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
		

		self.setLayout(self.main_vLayout)

	def request_info(self, url):
		try:
			response = requests.get(url +'check')
			soup = BeautifulSoup(response.text, 'html.parser')
			apps_names = soup.find_all(id = 'app_name')
			apps_status = soup.find_all(id = 'status')
			machine_name = soup.find(id = 'machine_name')
			
			return apps_names, apps_status, machine_name.text
		except Exception as e:
			now = (datetime.now()).strftime("%H:%M:%S")
			self.log_doc(now + ' ' + str(e) + ' ' + str(e.args) + ' function: request_info')
	
	@Slot()
	def machine_name_changed(self):
		global Index_url
		
		Index_url = self.combo_machine_name.currentIndex()-1
		apps_name, apps_status, nick = self.request_info(url_of_all_machines[Index_url])
		self.label.setText('Trabalhando na máquina: ' + nick + '   URL: ' + url_of_all_machines[Index_url])
		
		self.list_status_apps.clear()
		self.color_status_correction()
		
		if self.timer.isActive() and Index_url == -1:
			self.timer.stop()
		else:
			self.timer.start()
		
	def get_all_list_itens(self):
		itens = []
		for i in range(self.list_status_apps.count()):
			itens.append(self.list_status_apps.item(i))

		return itens
		
	def get_machine_nicks(self):
		try:
			for url in url_of_all_machines:
				app_name, app_status, nick = self.request_info(url)
				self.combo_machine_name.addItem(nick)
		except Exception as e:
			self.label.setText('Problema ao carregar um ou mais Engines')
			
			now = (datetime.now()).strftime("%H:%M:%S")
			self.log_doc(now + ' ' + str(e) + ' ' + str(e.args) + ' function: get_machine_nicks')
			
	def save_selection(self):
		items = self.list_status_apps.selectedItems()
		text = []
		index = []
		for i in range(len(items)):
			text.append(str(self.list_status_apps.selectedItems()[i].text()))
			index.append(str(self.list_status_apps.selectedIndexes()[i].row()))
		return text, index

	def color_status_correction(self):
		global Index_url
		apps_name, apps_status, nick = self.request_info(url_of_all_machines[Index_url])
		self.list_status_apps.clear()
		for app_name, app_status in zip(apps_name, apps_status):
			if app_status.text == 'Fechado':
				list_item = QListWidgetItem(app_name.text + ' : ' + app_status.text)
				list_item.setBackground(QColor('#FF0000'))
			else:
				list_item = QListWidgetItem(app_name.text + ' : ' + app_status.text)
				list_item.setBackground(QColor('#7fc97f'))
				
			self.list_status_apps.addItem(list_item)

	def check_state_recurring(self):
		global Index_url
		if Index_url == '':
			if self.label.text() != 'Problema ao carregar um ou mais Engines':
				self.label.setText('Escolha um Engine')
			return
		
		name_app, status_app, nick = self.request_info(url_of_all_machines[Index_url])
		list_itens = self.get_all_list_itens()

		for i in range(len(name_app)):
			if (name_app[i].text + ' : ' + status_app[i].text) != list_itens[i].text():
				self.color_status_correction()
		
	def call_url(self, command, application):
		global Index_url
		try:
			response = requests.get(url_of_all_machines[Index_url] + '/' + command + '/' + application)
			log_text = url_of_all_machines[Index_url] + ' ' + command + ' ' + application + ' status code: ' + str(response.status_code)

			self.log_uso(log_text)
			self.label.setText(log_text)
			
			now = (datetime.now()).strftime("%H:%M:%S")
			self.label.setText(now + ' ' + command + '  ' + application + ' status<' + str(response.status_code)+'>')

		except Exception as e:
			now = (datetime.now()).strftime("%H:%M:%S")
			self.log_doc(now + ' ' + str(e) + ' ' + str(e.args) + ' function: call_url')

	def filter_clicked_itens(self, item):
		item = item.split(' : ')
		return item

	@Slot()
	def openApp(self):
		global Index_url
		try:
			itens_clicados, itens_index = self.save_selection()
			name_app, status_app, nick = self.request_info(url_of_all_machines[Index_url])
			
			if len(itens_clicados) == 0:
				self.label.setText('Escolha um programa para abrir')
				return

			for item in itens_clicados:
				item = self.filter_clicked_itens(item)
				for app_name, app_status in zip(name_app, status_app):
					if (app_status.text == item[1] == 'Fechado') and (app_name.text == item[0]):
						self.call_url('open', item[0])
						break
						
					elif (app_status == 'Aberto') and (app_name.text == item):
						self.label.setText('O programa já está aberto!')
						break
					else:
						pass
			
				#self.label.setText('Programa não encontrado!')
			
			

		except Exception as e:
			log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(log_text)

	@Slot()
	def killApp(self):
		global Index_url
		try:
			itens_clicados, itens_index = self.save_selection()
			name_app, status_app, nick = self.request_info(url_of_all_machines[Index_url])
			
			if len(itens_clicados) == 0:
				self.label.setText('Escolha um programa para abrir')
				return

			for item in itens_clicados:
				item = self.filter_clicked_itens(item)
				for app_name, app_status in zip(name_app, status_app):
					if (app_status.text == item[1] == 'Aberto') and (app_name.text == item[0]):
						self.call_url('close', item[0])
						break
						
					elif (app_status == 'Fechado') and (app_name.text == item):
						self.label.setText('O programa já está fechado!')
						break
					else:
						pass
		
		except Exception as e:
			log_text = str(e) + '  ' + str(e.args) + '  function: get_machines_names'
			self.log_doc(log_text)


	
	def log_doc(self, log_text):
		now = datetime.now()
		now_format = now.strftime("%d-%m-%y %H:%M:%S")
		
		with open(os.path.relpath("Restart Remoto Client/Log/LogErros.txt"), 'a+') as f:
			f.writelines(now_format + "  " + log_text + "\n")

	def log_uso(self, log_text):
		now = datetime.now()
		now_format = now.strftime("%d-%m-%y %H:%M:%S")
		
		with open(os.path.relpath("Restart Remoto Client/Log/LogUso.txt"), 'a+') as f:
			f.writelines(now_format + "  " + log_text + "\n")

#Inicialização da aplicação
if __name__ == '__main__':
    app = QApplication(sys.argv)

    demo = AppDemo()
    demo.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Fechando Janela...')
            
