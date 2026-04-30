from lib.util.imports import *
#import lib.util.calc as _calc 


import atoms.base as atom
@nb.njit()
def runStart(k, data, start='max'):
	N                          = data.shape[0]
	starting_centroid          = np.zeros((k, data.shape[1]), data.dtype)
	starting_centroid[0, :]    = data[nb.u4(N * np.random.random()), :]
	match start:
		case '++':
			initial_condition  = atom.startPlusPlus(data, k, starting_centroid)
		case 'max':
			initial_condition  = atom.startMax(data, k, starting_centroid)
	return(initial_condition)



def _runOptimalKSearch(labels, dataCube, converge):
	labelLst = np.unique(labels)
	# optimalGroups = np.zeros(len(labelLst))
	for z in range(len(labelLst)):
		print(labelLst[z])
		zindx = np.where(labels == labelLst[z])[0]
		optimalGroupLst = _findOptimalK(dataCube, converge, zindx, _calcCHindex, _calcSilhouetteScore)	
#		print(_calcFeatureDensity(dataCube, converge, zindx, _calcCHindex))
		print(optimalGroupLst)
		vals, counts = np.unique(optimalGroupLst, return_counts=True)
		optimalGroups = int(vals[int(np.argmax(counts))])

		util.logg("msg", val='elbow test yields {} groups'.format(optimalGroups))
		if optimalGroups >= dataCube.shape[0]:
			util.logg("warn", val='Optimal number of groups is greater than the number of data points')
			optimalGroups = dataCube.shape[0]
	return(optimalGroups)

def _recordValidation(labels, dataCube):
	i0_labelArr = np.array([str(x)[0] for x in labels])
	i0_labelLst = np.unique(i0_labelArr)
	#inner_sscore = [[] for a in range(len(i0_labelLst))]
	# outer_sscore = [[] for a in range(len(i0_labelLst))]
	ss_score = []
	ch_score = []
	label_order = []

	with open("./quantified.txt", 'w') as file:
		for i in range(len(i0_labelLst)):

			i0_indx = np.where(i0_labelArr == i0_labelLst[i])[0]
#			o1_labelArr = np.array([str(x)[1] for x in labels[i0_indx]])
#			o1_labelLst = np.unique(o1_labelArr)

			ss_score.append(_calcSilhouetteScore(dataCube[i0_indx, :], labels[i0_indx]))
			ch_score.append(_calcCHindex(dataCube[i0_indx, :], labels[i0_indx]))
			label_order.append(np.unique(labels[i0_indx]))
			#print([outer_sscore[i], inner_sscore[i]])
			# for j in range(len(outer_sscore[i])):
#			file.write("{}X\t{}\t{}\t{}\n".format(i0_labelLst[i], ss_score[i], (ss_score[i] > 0.7).all(), ch_score[i]))

			# for j in range(len(o1_labelLst)):
			# 	o1_indx = i0_indx[np.where(o1_labelArr == o1_labelLst[j])[0]]	
			# 	# __silhouetteLog__ = util.logg("start", "Silhouette Score [i0 = {}]".format(i0_labelLst[i]))
			# 	inner_sscore[i].append(_calcSilhouetteScore(dataCube[o1_indx, :], labels[o1_indx]))
			# 	print(inner_sscore[i])
			# 	for k in range(len(inner_sscore[i][j])):
			# 		file.write("{}{}{}\t{:.3f}\n".format(i0_labelLst[i], o1_labelLst[j], k+1, inner_sscore[i][j][k]))
			# util.logg("stop", _log=__silhouetteLog__)
			file.write("---\n")

	return(ss_score, ch_score, label_order)

# @nb.njit()
def _runIntrinsic(nbins, data, edgeOverride=None):
	init_label  = np.ones(data.shape[0], dtype=np.uint16)
	if type(edgeOverride) == type(None):
		_, edgets = _calc.numba_histogram(data, nbins, 
									np.array([data.min(), data.max()]))
	else:
		edges = edgeOverride

	for q in range(nbins):
		qindex = np.where(edges[q+1] > data) and np.where(edges[q] <= data)
		for r in qindex[0].astype(np.uint32):
			init_label[r] = nb.u8(q+1)
	return(init_label)


@nb.njit(nogil=True)
def _runOptimization(k, sub_data, converge):
	ic                      = pre.runStart(k, sub_data)
	_, data_label           = _calcOptimization(k, sub_data, ic, converge)
	return(data_label+1)
	

@nb.njit()
def _findOptimalK(data, converge, zindx, func1, func2):
	optimalGroupLst = np.zeros(30)
	a = 0
	counter = 0
	while a < optimalGroupLst.shape[0]:
		# print((a, counter))
		scores1 = np.zeros(6)
		scores2 = np.zeros(6)

		groupEntry_tmp = 0
		for i in range(scores1.shape[0]):
			labels = _runOptimization(i+1, data[zindx, :], converge)#, label[zindx])
			scores1_tmp = func1(data[zindx, :], labels)
			scores2_tmp = func2(data[zindx, :], labels)
			scores1[i] = scores1_tmp#np.nanmean(scores_tmp)
			scores2[i] = np.nanmedian(scores2_tmp)


			f = 1
			if (i > 1 or i < scores1.shape[0]-1) and (scores1[i] > scores1[i-1]*f) and (scores1[i] > scores1[i + 1]*f):
				if (scores2[i] > scores2[i-1]*f) and (scores2[i] > scores2[i+1]*f):
					optimalGroupLst[a] = i+1
					a += 1
					break
				
		if optimalGroupLst[a] == 0:
			counter += 1
			if counter == 30:
				optimalGroupLst[a] = int(np.min(np.where(scores1 == np.nanmax(scores1))[0]) + 1)
				a += 1
				counter = 0
		
	return(optimalGroupLst)

