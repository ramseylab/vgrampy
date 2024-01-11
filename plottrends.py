import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import os
import vg2signal
import sys
from mpl_toolkits.mplot3d import Axes3D

def get_data(folder, trend, stat):
	os.chdir(folder)
	#dict(key:conc, [[trendval],[stat]])
	gdict = dict()
	for fn in os.listdir(): #for each 'stats' excel file in folder
		if fn[:5] == "stats":
			#param to trend
			paramval = float(fn[:-5].split('_')[trend+2])
			df = pd.read_excel(fn)
			for i in range(len(df[stat])): #for each concentration
				conc = df['conc'][i] #get concentration
				statval = df[stat][i] #get stat value (CV or T-Statistic)
				if conc in gdict.keys():
					prevtrends = gdict[conc][0]
					prevstat = gdict[conc][1]
					prevtrends.append(paramval)
					prevstat.append(statval)
					gdict[conc][0] = prevtrends
					gdict[conc][1] = prevstat
				else:
					gdict[conc] = [[paramval],[statval]]
	return gdict

def plot_trend(pltn,folder,trend,stat,zeros):
	gdict = get_data(folder,trend,stat)
	xlabels = ["smoothing_bw","stiffness","vcenter","vwidth1","vwidth2"]
	titlename = folder[folder.rfind("/")+1:]
	colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
	shapes = ['o','s','v','X']
	cnt = 0
	#ax1 = pltn.subplots()
	ax1 = pltn
	for key in gdict:
		if ((key=="0.0 \u03BCM") and (zeros==True)) or (key!="0.0 \u03BCM"):
			if stat == 'T-Statistic':
				ax1.scatter(gdict[key][0],gdict[key][1],label=key,color=colors[cnt],facecolors='none',marker=shapes[cnt])
			else:
				ax1.scatter(gdict[key][0],gdict[key][1],label=key,color=colors[cnt],marker=shapes[cnt])
		cnt +=1

	#ax1.xscale('log')
	if stat == "CV":
		ax1.set_ylim(0,0.90)
		ax1.set_ylabel("CV", weight='bold', fontsize=15)
	else:
		ax1.set_ylim(-1,20)
		ax1.set_ylabel("t-statistic", weight='bold', fontsize=15)
	if trend == 2:
		ax1.set_xscale('log')
		ax1.set_xlabel('Stiffness', weight='bold', fontsize=15)
	elif trend == 4:
		ax1.set_xlabel('Window Width', weight='bold', fontsize=15)
	elif trend == 1:
		ax1.set_xlabel('Smoothing', weight='bold', fontsize=15)

	#ax1.set_title(titlename)
	#ax1.legend(bbox_to_anchor=(0, 2), loc='upper right',prop={'size': 7})
	#ax1.legend(bbox_to_anchor=(0.3, 0.65),prop={'size': 13}) #tstat 0.7,0.65=top R,
	ax1.legend(bbox_to_anchor=(0.3,0.65), prop={'size': 13})
	#plt.show()

def plot_double_trend(pltn,folder,trend,zeros):
	xlabels = ["smoothing_bw","stiffness","vcenter","vwidth1","vwidth2"]
	titlename = folder[folder.rfind("/")+1:]
	dictcv = get_data(folder,trend,'CV')
	dictTT = get_data(folder,trend,'T-Statistic')
	ax1 = pltn.subplots()
	#plt.figure(figsize=(10,10))
	colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
	shapes = ['o','s','v','h','X']
	cnt = 0
	for key in dictcv:
		if (key=="0.0 \u03BCM" and zeros) or key!="0.0 \u03BCM":
			ax1.scatter(dictcv[key][0],dictcv[key][1],label=key+' CV',marker=shapes[cnt],facecolors='none',edgecolors=colors[cnt])
		cnt+=1
	ax1.tick_params(axis='y')
	ax1.set_xlabel(xlabels[trend-1])
	ax1.set_ylabel('CV')
	ax1.set_ylim(0,0.80)
	ax2=ax1.twinx()
	cnt=0
	for key in dictTT:
		if key!="0.0 \u03BCM":
			ax2.scatter(dictTT[key][0],dictTT[key][1],label=key+' T-Statistic',marker=shapes[cnt],color=colors[cnt])
		cnt+=1
	ax2.tick_params(axis='y')
	ax2.set_ylabel('T-Statistic')
	ax2.set_ylim(0,9)
	if trend == 2:
		ax1.set_xscale('log')
	ax1.legend(bbox_to_anchor=(0, 1.14), loc='upper left',prop={'size': 7})
	ax2.legend(bbox_to_anchor=(1, 1.14), loc='upper right',prop={'size': 7})
	pltn.suptitle(titlename)
	#plt.show()

def threeD_plot(folder,param1,param2,trend,zeros):
	p1data = get_data(folder,param1,trend)
	p2data = get_data(folder,param2,trend)
	#fig = plt.figure()
	#ax = fig.add_subplot(projection='3d')
	xlabels = ["smoothing_bw","stiffness","vcenter","vwidth1","vwidth2"]
	titlename = folder[folder.rfind("/")+1:]
	colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
	shapes = ['o','s','v','h','X']
	cnt = 0
	for key in p1data:
		#if ((key=="0.0\u03BCM") and (zeros==True)) or (key!="0.0\u03BCM"):
		if key == "15.0\u03BCM":
			fig = plt.figure()
			ax = plt.axes(projection='3d')
			x = p1data[key][0]
			y = p1data[key][1]
			x, y = np.meshgrid(x,y)
			#print(p2data[key][1])
			z = np.array(p2data[key][:1])
			#z = (np.sin(x **2) + np.cos(y **2) )

			ax.set_zlabel(xlabels[param2-1])
			ax.set_ylabel(trend)
			ax.set_xlabel(xlabels[param1-1])
			ax.set_title(titlename)
			ax.plot_surface(x,y,z,cmap=plt.cm.coolwarm,label=key)
			#ax.legend()
			plt.show()
		cnt +=1
	#ax.set_zlabel(trend)
	#ax.set_ylabel(xlabels[param2-1])
	#ax.set_xlabel(xlabels[param1-1])
	#ax.set_title(titlename)
	#plt.legend(bbox_to_anchor=(0, 1.15), loc='upper left',prop={'size': 7})
	#plt.show()

def plotraw(folders):
	colors = ['tab:orange', 'tab:blue', 'tab:green', 'tab:red', 'tab:purple']
	cnt = 0
	for folder in folders:
		os.chdir(folder)
		for fn in os.listdir():  # for each 'stats' excel file in folder
			if fn[-3:] == "txt":
				underlines = fn.split("_")
				cbzamt = underlines[-2][-2:]
				print(cbzamt)
				if cbzamt == "15":
					print("in")
					vgdf = vg2signal.read_raw_vg_as_df(str(fn))
					plt.plot(vgdf["V"], vgdf["I"], color = colors[cnt])
		cnt += 1
	plt.title("Raw Voltammogram")
	plt.xlabel("Potential (V)")
	plt.ylabel("Current (\u03BCM)")
	plt.show()

					

if __name__ == '__main__':
	#foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_19_SOD4',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S4',  
	#]
	#'C:/Users/patri/Box/Fu Lab/Noel/CBZdata/vg2signalwork/0/0',
	#'C:/Users/patri/Box/Fu Lab/Noel/CBZdata/vg2signalwork/0/0p025',
	foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/manuscript2/nolog/LC3/2023_12_12_LowConc3',
                ]
	#foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_17_SAL2/N','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_17_SAL2/SAL']
	#foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inSnoN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inS']
    #foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S1','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_06_29_KNonWorking1/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S1','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_07_14_KNonWorking2/S3']
	tall = 0
	wide = 0
	param1 = 2 #1=smoothing_bw,2=stiffness,3=vcenter,4=vwidth1,5=vwidth2
	param2 = 5
	stat = 'CV' #'CV' or 'T-Statistic' or both
	zeros = True
	#xlabels = ["smoothing_bw","stiffness","vcenter","vwidth1","vwidth2"]
	groupraw = False
	if groupraw:
		plotraw(foldersS)
		sys.exit()

	
	threeD=False
	if not threeD:
		talltotal = -(-len(foldersS)//3)
		widetotal = 3
		if talltotal < 2:
			talltotal=2
		fig, axs = plt.subplots()
		#fig = plt.figure(figsize=(15,10))
		#axs = fig.subfigures(talltotal,widetotal)
		
	#fig.supxlabel(xlabels[param-1])
	#fig.supylabel(stat)

	for folder in foldersS:
		#print(tall,",",wide)
		if stat != 'both':
			if threeD:
				threeD_plot(folder, param1, param2, stat, zeros)
			else:
				#plot_trend(axs[tall,wide],folder, param1, stat, zeros)
				plot_trend(axs,folder, param1, stat, zeros)
				#plt.show()
		else:
			plot_double_trend(axs[tall,wide],folder,param1, zeros)
		if wide ==2:
			tall+=1
			wide=0
		elif wide==1:
			wide=2
		else:
			wide=1
	if wide != 0:
		if wide == 1:
			print("")
			#fig.delaxes(axs[tall,1])
		#fig.delaxes(axs[tall,2])
	plt.show()
	#foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_31/2023_04_19_SOD4','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_31/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_31/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_31/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_31/2023_04_03_SOD2/S4']
	#foldersS =#['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_19_SOD4',
                #'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_04_03_SOD2/S4',  
	#foldersS = ['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)onN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p2)pN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inSnoN','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/08_01/2023_05_11_KRedoSDSpN/SDS(0p4)inS',
    