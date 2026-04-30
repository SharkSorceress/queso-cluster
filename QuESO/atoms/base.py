def normZ(dataSquare):
	print("TBD")
	return(dataSquare)

def normMaximum(dataSquare):
	norm_func = lambda x: x/(x.max(axis=1))[:,None]
	normCube = da.blockwise(norm_func, 'ij', dataCube, 'ij', dtype=np.float32)
	return(normSquare)

def normContinuum(dataSquare, continuumIndx):
	norm_func = lambda x: x/(x[:, int(continuum)])[:,None]
	normCube = da.blockwise(norm_func, 'ij', dataSquare, 'ij', dtype=np.float32)
	return(normSquare)
	
def concatSpectra(dataSquareLst):
	return(dask.array.concatenate(dataSquareLst))	


@nb.njit(cache=True)
def minimize(data, decisions, size):
	data_label      = np.zeros(data.shape[0], dtype=np.int32)
	D_x             = np.zeros(data.shape[0], dtype=data.dtype)
	sq_dist         = np.zeros(size, dtype=data.dtype)
	for ii in range(data.shape[0]):
		for kk in range(size):
			sq_dist[kk] 	= similarityMetric(data[ii,:], decisions[kk, :])
		data_label[ii]  = sq_dist.argmin()
		D_x[ii]         = sq_dist[nb.u4(data_label[ii])]
	return(data_label, D_x)

@nb.njit(cache=True)
def maximize(data, decisions, size):
	data_label      = np.zeros(data.shape[0])
	D_x             = np.zeros(data.shape[0])
	sq_dist         = np.zeros(size)
	for ii in range(data.shape[0]):
		for kk in range(size):
			# diff            = data[ii,:] - decisions[kk, :]
			# sq_dist[kk]     = np.sqrt(diff.dot(diff))
			sq_dist[kk] 	= similarityMetric(data[ii,:], decisions[kk, :])
		data_label[ii]  = sq_dist.argmax()
		D_x[ii]         = sq_dist[nb.u4(data_label[ii])]
	return(data_label, D_x)

@nb.njit()
def similarityMetric(x, y, type='dist', ref=0):
	if type  == 'dist':
		delta = (x - y).astype(x.dtype)
		metric = np.sqrt(delta.dot(delta))
	elif type == 'cosine':
		ref = 1.0 - 0.5 * np.exp(-11*np.arange(-int(len(x)/2), int(len(x)/2), step=1)**2)
		x -= ref
		y -= ref
		similarityCoeff = (x).dot(y) / (np.sqrt(x.dot(x)) * np.sqrt(y.dot(y)))	
		metric = 1 - similarityCoeff
	return(metric)

@nb.njit(cache=True)
def curvature(y):
	grady = np_gradient(y)
	signedCurvature = np_gradient(grady)/(np.power(np.sqrt(1 + grady.dot(grady)), 3))
	return(np.sqrt(np.power(signedCurvature, 2)))
#	return(np.abs(np.gradient(np.gradient(y)))/(np.sqrt(1 + np.gradient(y)**2)**3))


@nb.njit()
def startMax(data, k, decisions):
	killer = np.ones(decisions.shape[1], dtype=decisions.dtype)
	while True:
		dc_left = np.flatnonzero(1-_calc.np_all_axis1(decisions))
		if len(dc_left) == 0:
			return(decisions)
		_, D_x = _calc.minimize(data, decisions, k-len(dc_left))        
	
		if (killer - data[nb.u4(D_x.argmax()), :]).sum() == 0:
			return(decisions)
		
		decisions[dc_left[0], :]    = data[nb.u4(D_x.argmax()), :]
		killer = data[nb.u4(D_x.argmax()), :]

@nb.njit(cache=True)
def startPlusPlus(data, k, decisions):
	killer = np.ones(decisions.shape[1], dtype=decisions.dtype)
	while True:
		dc_left = np.flatnonzero(1-_calc.np_all_axis1(decisions))
		if len(dc_left) == 0:
			return(decisions)
		_, D_x = _calc.minimize(data, decisions, k-len(dc_left))     
		probs = D_x/D_x.sum()
		r = np.random.rand()
		for j, p in enumerate(probs.cumsum()):
			if r < p:
				i = j
				break
		if (killer - data[nb.u4(i), :]).sum() == 0:
			return(decisions)

		decisions[dc_left[0], :]    = data[nb.u4(i), :]
		killer = data[nb.u4(i), :]


@nb.njit(cache=True)
def _calcMoment(waveAxis, ii, jj, lineCore, dataCube, order, ref, counter=0):    
	momentN = np.zeros((order+1, dataCube.shape[0]))
	while counter <= order:
		factor = np.power((waveAxis[ii:jj] - waveAxis[lineCore]), counter)
		for i in range(dataCube.shape[0]):
			momentN[counter, i] = ((dataCube[i, ii:jj] - ref[ii:jj])*factor).sum()
		if counter > 0:
			momentN[counter, :] /= momentN[0, :]
		counter += 1
	
	return(momentN)

@nb.njit()
def _calcFeatureDensity(data, converge, zindx, func1):
	featureDensityArr = np.zeros(50)
	for a in range(featureDensityArr.shape[0]):
		scores1 = np.zeros(len(zindx))
		for i in range(int(scores1.shape[0]/100)):
			print((a, i, i*100/(len(zindx)/100)))
			labels = _runOptimization(i+1, data[zindx, :], converge)
			scores1_tmp = func1(data[zindx, :], labels)
			scores1[i] = scores1_tmp
		featureDensityArr[a] = np.min(np.where(scores1 == np.nanmax(scores1))[0]) + 1
	featureDensity = np.median(featureDensityArr)/len(zindx)
	return(featureDensity)


@nb.njit()
def _calcOptimization(k, data, decision, threshold):
	while True:
		data_label, _ = _calc.minimize(data, decision, k)
		new_centroid = np.zeros((k, data.shape[1]), dtype=data.dtype)
		converge = 0
		for kk in range(k):
			sub_data = data[np.where(data_label == kk)[0], :]
			new_centroid[kk,:]  = sub_data.sum(axis=0)/sub_data.shape[0]
			# new_centroid[kk,:]  = np.median(sub_data, axis=0)

			diff_centroid   = new_centroid[kk,:] - decision[kk,:]
			converge        = np.max(np.asarray([converge, 
												np.sqrt(diff_centroid.dot(diff_centroid))]))
		decision = new_centroid
		if (converge <= threshold) or np.isnan(converge):
			return(decision, data_label)    


@nb.njit()
def _calcElbowEntry(data, labels):

	labelLst = np.unique(labels)
	localDistance = np.zeros(len(labelLst))
	for j in range(len(labelLst)):
		indx = np.where(labels == labelLst[j])[0]
		centroid = data[indx, :].sum(axis=0)/len(indx)
		d2 = 0.0
		for k in range(len(indx)):
			d = data[indx[k], :] - centroid
			d2 += np.sqrt(d.dot(d))
		#print(d2/len(indx))
		localDistance[j] = d2/len(indx)

	# def _calcScore(scores):
	# 	return(np.argmax(np_gradient(np_gradient(_calcCurvature(scores)))) + 1)

	return(localDistance)#, _calcScore)

@nb.njit()
def _calcVarianceScore(data):

	avg_var = np.std(data, axis=0).sum()/data.shape[1]
	centroid = data.sum(axis=0)/data.shape[0]


@nb.njit()
def _calcSilhouetteScore(data, labels):
	
	labelLst = np.unique(labels)
	intraDistance = np.zeros(len(labelLst))
	interDistance = np.zeros(len(labelLst))
	if len(labelLst) > 1:
		for j in range(len(labelLst)):
			intraIndx = np.where(labels == labelLst[j])[0]
			interIndx = np.where(labels != labelLst[j])[0]

			centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
			intra_d2 = 0.0
			for k in range(len(intraIndx)):
				d = data[intraIndx[k], :] - centroid
				intra_d2 += np.sqrt(d.dot(d))		
			
			inter_d2 = 0.0
			for k in range(len(interIndx)):
				d = data[interIndx[k], :] - centroid
				inter_d2 += np.sqrt(d.dot(d))

			intraDistance[j] = intra_d2/len(intraIndx)
			interDistance[j] = inter_d2/len(interIndx)

	# def _calcScore(scores):
	# 	return(np.argmax(scores) + 1)

	# denomArr 	= np.array([intraDistance, interDistance])
	# maxIndx = np.argmax(np.array([intraDistance.max(), interDistance.max()]))

#	return((interDistance - intraDistance)/np.maximum(intraDistance, interDistance))

	return(1 - intraDistance/interDistance)


@nb.njit()
def _calcSingleSilhouetteScore(data, labels, lab):
	
	labelLst = np.unique(labels)
	if len(labelLst) > 1:
		# for j in range(len(labelLst)):
		intraIndx = np.where(labels == lab)[0]
		interIndx = np.where(labels != lab)[0]

		centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		intra_d2 = 0.0
		for k in range(len(intraIndx)):
			d = data[intraIndx[k], :] - centroid
			intra_d2 += np.sqrt(d.dot(d))		
		
		inter_d2 = 0.0
		for k in range(len(interIndx)):
			d = data[interIndx[k], :] - centroid
			inter_d2 += np.sqrt(d.dot(d))

		intraDistance = intra_d2/len(intraIndx)
		interDistance = inter_d2/len(interIndx)

	# def _calcScore(scores):
	# 	return(np.argmax(scores) + 1)

	# denomArr 	= np.array([intraDistance, interDistance])
	# maxIndx = np.argmax(np.array([intraDistance.max(), interDistance.max()]))

#	return((interDistance - intraDistance)/np.maximum(intraDistance, interDistance))

	return(1 - intraDistance/interDistance)

@nb.njit()
def _calcCHindex(data, labels):
	N = data.shape[0]
	K = len(np.unique(labels))

	labelLst = np.unique(labels)
	if len(labelLst) == 1:
		return(np.nan)
	
	wgss = np.zeros(len(labelLst)) #+ np.nan
	bgss = np.zeros(len(labelLst))# np.nan
	for k in range(len(labelLst)):
		intraIndx = np.where(labels == labelLst[k])[0]
		interIndx = np.where(labels != labelLst[k])[0]

		intra_centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		intra_d2 = 0.0
		for i in range(len(intraIndx)):
			d = data[intraIndx[i], :] - intra_centroid
			intra_d2 += d.dot(d)

		inter_centroid = (data[interIndx, :].sum(axis=0) + data[intraIndx, :].sum(axis=0))/(len(intraIndx) + len(interIndx))
		# print(inter_centroid)
		d = inter_centroid - intra_centroid
		bgss[k] = nb.float32(len(intraIndx) * d.dot(d))
		wgss[k] = nb.float32(intra_d2)#/len(intraIndx)

	return((bgss.sum()/wgss.sum()) * (N - K)/(K - 1))


def labelGluer(labels):
	time_label_concat = np.char.asarray(np.zeros(labels[0].shape[1], dtype=int))
	for i in range(len(labels)):
		for l in range(labels[i].shape[0]):
			time_label_concat = np.char.add(time_label_concat, np.char.asarray(labels[i][l, ...].astype(int)))	

	return(time_label_concat)

def labelReorder(labels):
	time_label = []
	for i in range(len(labels)):
		time_label_wave = labelGluer([labels[i]])
		time_label_lst 	= np.unique(time_label_wave)
		time_label_bool = [element.decode("utf-8").find("-") < 0 for element in time_label_lst]

		for j in range(len(time_label_lst)):
			if time_label_bool[j]:
				newLabel = int('9' * int(np.ceil(np.log10(len(time_label_lst))) + 1)) - j
				while newLabel in np.unique(time_label_lst):
					if not (newLabel % 10):
						newLabel -= 1
				time_label_wave[np.where(time_label_wave == time_label_lst[j])[0]] = newLabel
			else:
				time_label_wave[np.where(time_label_wave == time_label_lst[j])[0]] = -1
		time_label.append(time_label_wave)

	time_label_concat = np.char.asarray(np.zeros(labels[0].shape[1], dtype=int))
	for i in range(len(labels)):
		time_label_concat = np.char.add(time_label_concat, np.char.asarray(time_label[i]))	

	return(time_label_concat)

@nb.njit()
def _calcQuiescentFrame(spectralData, spectralParams, contIndxs, progress=None):
	lineCore, ii, jj = spectralParams
	quiescentFrame 	= np.zeros(spectralData.shape[1:])
	for x in range(spectralData.shape[1]):
		for y in range(spectralData.shape[2]):
			quiescentScanNum = np.zeros(spectralData.shape[0])
			for t in range(spectralData.shape[0]):
				quiescentScanNum[t] = spectralData[t, x, y, lineCore]/np.nanmax(spectralData[t, x, y, :])#).sum(axis=-1)
			qindx = np.argsort(quiescentScanNum)[len(quiescentScanNum)//4]#np.where(quiescentScanNum == np.median(quiescentScanNum))#
			quiescentFrame[x, y, :] = spectralData[qindx, x, y, :]
			if progress != None:
				progress.update(1)
	return(quiescentFrame.reshape(spectralData.shape[1]*spectralData.shape[2], spectralData.shape[-1]))

@nb.njit()
def _calcDynamicFrame(spectralData, dynamicScanNum, progress=None, delta=0):
	dynamicFrame 	= np.zeros(spectralData.shape[1:]) + np.nan
	for x in range(spectralData.shape[1]):
		for y in range(spectralData.shape[2]):
			T = nb.uint(dynamicScanNum[x, y] + delta)
			if (T < spectralData.shape[0]) and (T >= 0):
				dynamicFrame[x, y, :] = spectralData[T, x, y, :]
				if progress != None:
					progress.update(1)
	return(dynamicFrame)