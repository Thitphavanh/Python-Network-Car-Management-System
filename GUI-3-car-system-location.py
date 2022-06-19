from tkinter import *
from tkinter import ttk, messagebox
import socket
from datetime import datetime
import csv
import threading



#  ----------------Threading Server----------------
plate_dict = {}
# plate_dict = {'ກຄ8888':['14564644','14564544','14564744']}

serverip_location = '192.168.0.54'
port_location = 8899
buffsize_location = 4096

# -------------IP Adress-------------
serverip = '192.168.0.54'
port = 8888
buffsize = 4096

def writeToCsv(data):
	# data = ['Tesla','black','AF1234','1001','2022-05-07 16:01:20']
	with open('2-car-system-in.csv', 'a', newline='', encoding='utf-8') as file:
		file_writer = csv.writer(file)
		file_writer.writerow(data)
	print('csv saved')


#  ----------------Split----------------
def splitRow(datalist, columns=7):
	result = []
	buflist = []
	for i, t in enumerate(datalist, start=1):
		if i % columns == 0:
			buflist.append(t)
			# print(buflist)
			result.append(buflist)
			buflist = []
		else:
			buflist.append(t)
	return result

def locationServer():
	while True:
		server = socket.socket()
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((serverip_location, port_location))
		server.listen(1)
		print('waiting client...')

		client, addr = server.accept()
		print('connected from : ', addr)

		data = client.recv(buffsize_location).decode('utf-8')
		print('Data from client : ', data)

		# data from 4 : data = 'check|ກຄ8888'
		source = data.split('|')[0]  # ມາຈາກໂປຣແກຣມຝັ່ງໃດ in / location / check
		plate = data.split('|')[1]  # 'ກຄ8888'

		if source == 'check':
			# ['in', 'Tesla', 'red', 'AA8888', '1001', '2022-05-08, 11:41:42', '41c83a9c']
			check = plate_dict[plate]
			text = 'location|'
			for c in check:
				text += c + '|'

			client.send(text.encode('utf-8'))
			client.close()
		else:
			client.close()


GUI = Tk()
GUI.title('[3] Location')
GUI.geometry('300x400')
FONT = (20)

label = Label(GUI,text='PLATE',font=FONT)
label.pack()

v_plate = StringVar()
entry1 = ttk.Entry(GUI, textvariable=v_plate,font=FONT)
entry1.pack()

label = Label(GUI,text='ZONE',font=FONT)
label.pack()

v_zone = StringVar()
entry2 = ttk.Entry(GUI, textvariable=v_zone,font=FONT)
entry2.pack()


def saveData():
	plate = v_plate.get()
	getzone = v_zone.get()

	# get data server
	text = 'location|allcar'
	server = socket.socket()
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.connect((serverip, port))
	server.send(text.encode('utf-8'))
	data_server = server.recv(buffsize).decode('utf-8')
	print('Data from server : ', data_server)
	# [1:-1] remove prefix and subfix
	datalist = data_server.split('|')[1:-1]
	for row in splitRow(datalist, 7):
		print(row)
		# ['in', 'Tesla', 'red', 'AA8888', '1001', '2022-05-08, 11:41:42', '41c83a9c']
		if row[4] not in plate_dict:
			plate_dict[row[4]] = row  # ບັນທຶກຂໍ້ມູນຂອງລົດເກັບໄວ້ເປັນ dict
	server.close()

	if len(plate_dict[plate]) == 7:
		# ຍັງບໍ່ເຄີຍໃສ່ ຂໍ້ມູນທັງມົດຈະມີ 7 ລາຍການ
		plate_dict[plate].append(getzone)
	else:
		# ຖ້າເຄີຍພິມໄປແລ້ວ ຕ້ອງການປ່ຽນໃຫ້ໃຊ້ແບບນີ້
		plate_dict[plate][7] = getzone

button1 = ttk.Button(GUI,text='SAVE',command=saveData)
button1.pack(ipadx=20,ipady=5,pady=50)


#  ----------------Run Thread----------------
task = threading.Thread(target=locationServer)
task.start()


GUI.mainloop()
