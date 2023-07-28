import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import os

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
				statval = df[stat][i] #get stat value (CV or t-Test)
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
	xlabels = ["smoothing_bw","smoothness_param","vcenter","vwidth1","vwidth2"]
	titlename = folder[folder.rfind("/")+1:]
	colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
	shapes = ['o','s','v','h','X']
	cnt = 0
	for key in gdict:
		if ((key=="0.0\u03BCM") and (zeros==True)) or (key!="0.0\u03BCM"):
			pltn.scatter(gdict[key][0],gdict[key][1],label=key,color=colors[cnt],marker=shapes[cnt])
		cnt +=1
	pltn.set_ylabel(stat)
	pltn.set_xlabel(xlabels[trend-1])
	pltn.set_title(titlename)
	pltn.legend(bbox_to_anchor=(0, 1.15), loc='upper left',prop={'size': 7})
	#plt.show()

def plot_double_trend(pltn,folder,trend,zeros):
	xlabels = ["smoothing_bw","smoothness_param","vcenter","vwidth1","vwidth2"]
	titlename = folder[folder.rfind("/")+1:]
	dictcv = get_data(folder,trend,'CV')
	dictTT = get_data(folder,trend,'T-Test')
	ax1 = pltn.subplots()
	#plt.figure(figsize=(10,10))
	colors = ['tab:orange', 'tab:green', 'tab:blue', 'tab:red', 'tab:purple']
	cnt = 0
	for key in dictcv:
		if (key=="0.0\u03BCM" and zeros) or key!="0.0\u03BCM":
			ax1.scatter(dictcv[key][0],dictcv[key][1],label=key+' CV',marker='o',facecolors='none',edgecolors=colors[cnt])
		cnt+=1
	ax1.tick_params(axis='y')
	ax1.set_xlabel(xlabels[trend-1])
	ax1.set_ylabel('CV')
	ax2=ax1.twinx()
	cnt=0
	for key in dictTT:
		if (key=="0.0\u03BCM" and zeros) or key!="0.0\u03BCM":
			ax2.scatter(dictTT[key][0],dictTT[key][1],label=key+' T-Test',marker='o',color=colors[cnt])
		cnt+=1
	ax2.tick_params(axis='y')
	ax2.set_ylabel('T-Test')
	ax1.legend(bbox_to_anchor=(0, 1.14), loc='upper left',prop={'size': 7})
	ax2.legend(bbox_to_anchor=(1, 1.14), loc='upper right',prop={'size': 7})
	pltn.suptitle(titlename)
	#plt.show()
					

if __name__ == '__main__':
	foldersS =['C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_19_SOD4','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S1', 'C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S2','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S3','C:/Users/lefevrno/Box/Fu Lab/Noel/CBZdata/vg2signalwork/07_28/2023_04_03_SOD2/S4']
	tall = 0
	wide = 0
	param = 4 #1=smoothing_bw,2=smoothness_param,3=vcenter,4=vwidth1,5=vwidth2
	stat = 'both' #'CV' or 'TT' or both
	zeros = False
	#xlabels = ["smoothing_bw","smoothness_param","vcenter","vwidth1","vwidth2"]
	talltotal = -(-len(foldersS)//3)
	widetotal = 3
	fig = plt.figure(figsize=(15,10))
	axs = fig.subfigures(talltotal,widetotal)
	#fig.supxlabel(xlabels[param-1])
	#fig.supylabel(stat)

	for folder in foldersS:
		#print(tall,",",wide)
		if stat != 'both':
			plot_trend(axs[tall,wide],folder, param, stat, zeros)
		else:
			plot_double_trend(axs[tall,wide],folder,param, zeros)
		if wide ==2:
			tall+=1
			wide=0
		elif wide==1:
			wide=2
		else:
			wide=1
	if wide != 0:
		if wide == 1:
			fig.delaxes(axs[tall,1])
		#fig.delaxes(axs[tall,2])
	plt.show()