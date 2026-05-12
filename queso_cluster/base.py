from .atoms import base as baseAtom
#from .atoms import aux as auxAtom
from .runners import base as baseRun
from .addon.logg import loggTimer
import numpy as np
#import dask.array as da
#import numba as nb

from numba_progress import ProgressBar


@loggTimer
def mainIntrinsic(config, prepSquare, lineIndx, intrinsicSkip=False):
	intrinsicLine = np.zeros(prepSquare.shape[0])
	if not intrinsicSkip:
		intrinsicConfig = config.clusterConfig['intrinsic']
		for i in range(len(intrinsicConfig)):
			key =  intrinsicConfig[i]['label']
			indxs = config.lines[lineIndx][key]
			if type(indxs) == list:
				iframe = prepSquare[:, indxs[0]:indxs[1]].mean(axis=-1)#.astype(np.float64).compute()
			else:
				iframe = prepSquare[:, indxs]#.astype(np.float64).compute()
			if 'layerConfig' in list(intrinsicConfig[i].keys()):
				if 'bins' in list(intrinsicConfig[i]['layerConfig'].keys()):
					bins = intrinsicConfig[i]['layerConfig']['bins']
					intrinsicLine_tmp 	= baseRun.runIntrinsic(len(np.diff(bins)), iframe, edgeOverride=np.array(bins).astype(float))

				if 'nbins' in list(intrinsicConfig[i]['layerConfig'].keys()):
					nbins = intrinsicConfig[i]['layerConfig']['nbins']
					intrinsicLine_tmp 	= baseRun.runIntrinsic(nbins, iframe)

			else:
				intrinsicLine_tmp 	= baseRun.runIntrinsic(1, iframe)
			intrinsicLine += intrinsicLine_tmp * 10**i
		s0_Lst = np.unique(intrinsicLine)
		for i in range(len(s0_Lst)):
			indx = np.where(intrinsicLine == s0_Lst[i])[0]
			intrinsicLine[indx.astype(int)] = i+1
	else:
		intrinsicLine += 1
	#print(np.unique(intrinsicLine))
	return(intrinsicLine)


@loggTimer
def mainOptimization(prepSquare, labelLine, kLst=None, stageMax=2):
	if not (kLst is None):
		if type(kLst[0]) == dict:
			k_lst  	= [x['layerGroups'] for x in kLst]
			k_pre 	= [np.arange(len(k_lst[0])).astype(int).tolist()] + [[int(np.sum(k_lst[a][:b])) for b in range(len(k_lst[a]))] for a in range(len(k_lst)-1)]
		else:
			k_lst = kLst

	else:
		validationFuncLst = [baseAtom.calcInertiaScore, baseAtom.calcSilhouetteScore]
		criteriaFuncLst = [baseAtom.criteriaInertiaScore, baseAtom.criteriaSilhouetteScore]
	print(k_lst)
	pwrSeq = (10**(stageMax - np.arange(stageMax+1))).astype(np.uint16)
	labelLine *= pwrSeq[0]

	stageCounter = 1
	scoreLst = []
	with ProgressBar(total=stageMax, ascii=False, leave=True, 
				desc='mainOptimization',
				bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as pS:
		while stageCounter <= stageMax:
			labelLst = np.unique(labelLine[~np.isnan(labelLine)])
			with ProgressBar(total=labelLst.size, ascii=False, leave=True, 
						desc='mainOptimization (Stage {})'.format(stageCounter),
						bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as p:
				for l in range(labelLst.size):
					indx = np.where(labelLine == labelLst[l])[0]
					lstr = str(labelLst[l])
					#print((lstr, len(indx)))
					if not (kLst is None):
						if type(kLst[0]) == dict:
							kindx = [int(lstr[a])-1 for a in range(len(lstr)) if int(lstr[a]) > 0]
							k1 = 0
							k0 = int(np.sum(kindx[0]))
							if stageCounter > 1:
								k0 = int(np.sum(kindx[:stageCounter-1]))
								k1 = kindx[stageCounter-1]
				
							kk = k_pre[stageCounter-1][k0] + k1
							k = k_lst[stageCounter - 1][kk]
						else:
							k = k_lst[l]

					else:
						k = baseRun.runOptimalKSearch(prepSquare[indx, :], validationFuncLst, criteriaFuncLst)
					nxtLabelLineUnsorted, scoreLine = baseRun.runOptimization(k, prepSquare[indx, :], 1e-6)
					nxtLabelLineSorted, sortIndx 	= baseRun.runLabelSort(prepSquare[indx, :], nxtLabelLineUnsorted) 

					scoreLst.append(scoreLine[sortIndx])
					labelLine[indx] += nxtLabelLineSorted*pwrSeq[stageCounter]

					p.update(1)
			pS.update(1)
			stageCounter += 1
	return(labelLine.astype(int), scoreLst)
	


# def _mainOptimization(config, dataCube, labels, optimalGroups=None):

# 	k_lst = [int(len(np.unique(labels)))]
# 	if type(optimalGroups) == type(None):
# 		k_lst  += [x['layerGroups'] for x in config.clusterConfig['optimized']]
# 	else:
# 		k_lst += [optimalGroups]

# 	pwrSeq = (10**(len(k_lst) - np.arange(len(k_lst)) - 1)).astype(np.uint16)

# 	labels *= pwrSeq[0]

# 	for k in range(len(k_lst)-1):
# 		converge = float(config.clusterConfig['optimized'][k]['layerConfig']['converge'])
# 		ss_thresh = np.array(config.clusterConfig['optimized'][k]['layerConfig']['ss_thresh'])
# 		labelLst = np.unique(labels)
# 		if type(k_lst[k+1]) == list:
# 			optimalGroups = np.array(k_lst[k+1])
# 		else:
# 			optimalGroups = k_lst[k+1] * np.ones(len(labelLst))

# 		Narr= auxAtom.pick_jth_label(labels, 0)
# 		Marr= auxAtom.pick_jth_label(labels, 1)

# 		if k > 0:
# 			orderIndx = []
# 			a = k_lst[k]
# 			NLst = np.unique(Narr)
# 			for n in range(len(np.unique(Narr))):
# 				Nindx = np.where(Narr == np.unique(Narr)[n])[0]
# 				Mlst = np.unique(Marr[Nindx])
# 				x = np.array(a[0:NLst[n]]).sum()
# 				for m in range(len(Mlst)):
# 					orderIndx.append(x - Mlst[-m])
# 		else:
# 			orderIndx =  auxAtom.pick_jth_label(np.unique(labels), 0) - 1

# 		optimalGroups1 = optimalGroups[orderIndx]
# 		label_lst = np.unique(labels)

# 		import copy
		
# 		ss_final = []
# 		lab_final = []
# 		bins = np.unique(auxAtom.pick_jth_label(label_lst, 0))
# 		label_index_counter = 0
# 		searchBool = False
# 		for q in range(len(bins[~np.isnan(bins)])):
# 			sup_indx = np.where(auxAtom.pick_jth_label(labels, 0) == bins[q])[0]
# 			sup_labelLst = np.unique(labels[sup_indx])
# 			nxt_labels = np.zeros(labels.shape)	
# 			loop_counter = 0
# 			ss_score_minimum = [[] for s in range(9)]
# 			while True:
# 				label_loop = copy.deepcopy(labels)	
# 				with ProgressBar(total=int(len(sup_indx)), ascii=False, leave=False, 
# 								desc='Hi-K Layer {} ({}, {})'.format(str(k+1), loop_counter, bins[q]),
# 								bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as p:
					

# 					label_index_counter_tmp = copy.deepcopy(label_index_counter)
# 					#print(label_index_counter_tmp)
# 					k_lst_loop = []
# 					for l in range(len(sup_labelLst)):
# 						sub_index    = np.where(label_loop.astype(np.uint16) == nb.u2(sup_labelLst[l]))[0]
# 						sub_data = dataCube[sub_index.astype(np.uint32),:] #.compute()  
# 						# print(optimalGroups1)
# 						# print(optimalGroups1[label_index_counter])
# 						# print(label_index_counter)
# 						if optimalGroups1[label_index_counter_tmp] == 0:
# 							__elbowLog__ = util.logg("start", "optimalKSearch")
# 							k_entry = int(_runOptimalKSearch(label_loop[sub_index], sub_data, converge))
# 							util.logg("stop", _log=__elbowLog__)
# 						else:
# 							k_entry = int(optimalGroups1[label_index_counter_tmp])					

# 						k_lst_loop.append(k_entry)
# 						if len(sub_index) > k_entry:
# 							nxt_labels[sub_index] = baseRun._runOptimization(k_entry, sub_data, converge)
# 						else:
# 							print("\nStalled\n")
						
# 						label_index_counter_tmp += 1
						
# 						p.update(len(sub_index))

# 				label_loop += (nxt_labels*pwrSeq[k+1]).astype(np.uint16)

# 				if len(np.unique(label_loop[sup_indx])) == 1:# or len(np.array(ss_scoreLst[~np.isnan(ss_scoreLst)])) == 0:
# 					labels = label_loop
# 					ss_final.append([np.nan])
# 					lab_final.append(np.unique(label_loop[sup_indx]))
# 					break			
# 				# print(ss_score_minimum)			
				
# 				ss_score, ch_score, lab_order = _recordValidation(label_loop[sup_indx], dataCube[sup_indx, :])
# #				print(ss_score)
# #				print(lab_order)
# #				
# 				#lindx_tmp = 0#copy.deepcopy(label_index_counter)
# 				ss_score_bool = True
# 				label_index_counter_tmp_tmp = copy.deepcopy(label_index_counter)
# 				# print((label_index_counter_tmp_tmp, label_index_counter))

# 				#lab_orderLst = np.unique(_calc.pick_jth_label(lab_order[0], k))
# 				# print(ss_thresh)
# 				# print(lab_orderLst)
# 				killer = int(str(lab_order[0][0])[k])
# 				for l in range(len(lab_order[0])):
# 					if killer != int(str(lab_order[0][l])[k]):
# 						label_index_counter_tmp_tmp += 1
# 						#ss_score_bool = True
					

# 					#lindx = np.where(_calc.pick_jth_label(lab_order[0], k+1) == lab_orderLst[l])[0]
# 					ss_scoreLst = ss_score[0][l]#[lindx_tmp:lindx_tmp+k_lst_loop[l]]

# 					ss_score_minimum[int(str(lab_order[0][l])[k])-1].append(ss_scoreLst)
# 					ss_score_bool *= (ss_scoreLst >= float(ss_thresh[label_index_counter_tmp_tmp]))

# 					# ss_score_bool *= np.nanmax(np.unique(np.array(ss_score_minimum))) >= 
# 					killer = int(str(lab_order[0][l])[k])
				
# 				if float(ss_thresh[label_index_counter]) >= 0:
# 					if ss_score_bool:#(np.array(ss_scoreLst[~np.isnan(ss_scoreLst)]) >= float(ss_thresh[label_index_counter])).all():# or k == 0:
# 						labels = label_loop
# 						print("loop broken: {}".format(loop_counter))
# 						ss_final.append([s[n] for s in ss_score_minimum for n in range(len(s)) if len(s) > 0])
# 						lab_final.append(lab_order[0])
# 						break
# 				else:
# 					if loop_counter == 300:
# 						label_index_counter_tmp = 0#copy.deepcopy(label_index_counter)
# 						for l in range(len(ss_score_minimum)):
# 							# print(ss_score_minimum[l])
# 							# print((lab_order[0], label_index_counter_tmp))
# 							if len(ss_score_minimum[l]) == 0:
# 								continue
# 							# print(np.unique(ss_score_minimum[l]))
# 							#util.logg('msg', val='{},{} Max: {} | Min: {}'.format(lab_order[0][label_index_counter_tmp], label_index_counter_tmp, np.nanmax(np.array(ss_score_minimum[l])), np.nanmin(np.array(ss_score_minimum[l]))))

# 							#fig = plt.figure(layout='constrained', figsize=(3,3))
# 							#ax = fig.add_subplot(111)

# 							# _, edges = _calc.numba_histogram(ss_score_minimum[l], 20, 
# 							# 							lim=np.array([0, 1]))
					

# 							#ax.hist(ss_score_minimum[l], bins=np.arange(0, 1, step=0.05), range=[0, 1], rwidth=1, histtype='step', log=True, fill=False, color='black')

# 							#ax.set_title(lab_order[0][label_index_counter_tmp])
# 							#fig.savefig("./fig/sscore_{}".format(lab_order[0][label_index_counter_tmp]))


# 							# print(np.unique(np.array(ss_score_minimum[l])))
# 							print(len(ss_score_minimum[l]))
# 							label_index_counter_tmp += 1

# 						searchBool = True
# 						break
				
# 				if loop_counter == 1000:
# 					#util.logg('error', '{} Iteration exceeded {}. Killing...'.format(bins[q], loop_counter))
# 					return(0, 0)
# 					# _mainOptimization(config, dataCube, labels, optimalGroups=optimalGroups)
# 						# sys.exit()
# 				loop_counter += 1
# 			label_index_counter += len(sup_labelLst)
# 	if searchBool:
# 		#util.logg('error', 'Search mode was active. Killing....')
# 		sys.exit()
# 	label_final = [l[n] for l in lab_final for n in range(len(l))]
# 	score_final = [s[n] for s in ss_final for n in range(len(s))]
	
# 	print(label_final)
# 	print(score_final)
# 	return(labels, [label_final,  score_final])



