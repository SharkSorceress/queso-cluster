import QuESO.atoms.base as baseAtom

def prep(dataSquare, norm='continuum', maskSquare=None, quSquare=None):
	match norm:
		case 'continuum':
			prepSquare = baseAtom.normContinuum(dataSquare)
		case 'maximum':
			prepSquare = baseAtom.normMaximum(dataSquare)
		case 'Z':
			prepSquare = baseAtom.normZ(dataSquare)

	if not (maskSquare is None):
		prepSquare *= maskSquare.rebin(1, -1).broadcast_to(dataSquare.shape)

	if not (quSquare is None):
		#> TODO: Implement quSquare normalization
		prepSquare -= quSquare

	return(prepSquare)



def main(config, frame, spectralParams, quiescentFrame=np.array(0), optimalGroups=None, intrinsicPass=True, altLabels=None):
	_, ii, jj = spectralParams
	
	lineIndx = 0

	intrinsic_frame = frame
	filter_indx 	= np.where(np.logical_not(np.isnan(frame.sum(axis=-1))))[0]
 
	if quiescentFrame.sum() != 0:
		intrinsic_frame = frame - quiescentFrame
		filter_indx = filter_indx[np.where(intrinsic_frame[filter_indx, ii:jj+1].sum(axis=-1) != 0)[0]]
		util.logg("msg", val="residuals calculated")

	# intrinsic_frame = frame
	# filter_indx 	= np.where(np.logical_not(np.isnan(frame.sum(axis=-1))))[0]

	# if quiescentFrame.sum() != 0:
	# 	intrinsic_frame = frame - quiescentFrame
	# 	filter_indx = filter_indx[np.where(intrinsic_frame[filter_indx, ii:jj].sum(axis=-1) != 0)[0]]
	# 	util.logg("msg", val="residuals calculated")

	# s0_no_nan = np.ones(len(filter_indx))
	# if intrinsicPass:
	# 	s0_no_nan_tmp = np.zeros(len(filter_indx))

	# 	intrinsicConfig = config.clusterConfig['intrinsic']
	# 	for i in range(len(intrinsicConfig)):
	# 		key =  intrinsicConfig[i]['label']
	# 		indxs = config.lines[lineIndx][key]
	# 		if type(indxs) == list:
	# 			iframe = intrinsic_frame[filter_indx, indxs[0]:indxs[1]].sum(axis=-1)
	# 		else:
	# 			iframe = intrinsic_frame[filter_indx, indxs]

	# 		print(intrinsicConfig[i])
	# 		if 'layerConfig' in list(intrinsicConfig[i].keys()):
	# 			if 'bins' in list(intrinsicConfig[i]['layerConfig'].keys()):
	# 				bins = intrinsicConfig[i]['layerConfig']['bins']
	# 				s0_0_no_nan 	= _runIntrinsic(len(np.diff(bins)), iframe, edgeOverride=np.array(bins).astype(float))

	# 			if 'nbins' in list(intrinsicConfig[i]['layerConfig'].keys()):
	# 				nbins = intrinsicConfig[i]['layerConfig']['nbins']
	# 				s0_0_no_nan 	= _runIntrinsic(nbins, iframe)

	# 		else:
	# 			s0_0_no_nan 	= _runIntrinsic(1, iframe)

	# 		s0_no_nan_tmp += s0_0_no_nan*(10**(i))

	# 	s0_Lst = np.unique(s0_no_nan_tmp)
	# 	for i in range(len(s0_Lst)):
	# 		# print([i, s0_Lst[i]])
	# 		indx = np.where(s0_no_nan_tmp == s0_Lst[i])[0]
	# 		s0_no_nan[indx.astype(int)] = i+1
	
	# print(np.unique(s0_no_nan))
	if type(altLabels) != type(None):		
		s0_no_nan = altLabels[filter_indx]
	else:
		s0_no_nan = _mainIntrinsic(config, frame, intrinsicPass, filter_indx, lineIndx)

	if quiescentFrame.sum() == 0:
		continuum_indx = config.lines[lineIndx]['continuum']
		no_nan_frame = frame[filter_indx, :]
		norm_func = lambda x: x/(x[:, continuum_indx])[:,None]
		frameNorm = da.blockwise(norm_func, 'ij', no_nan_frame, 'ij', dtype=np.float32)
		frame_norm = frameNorm[:, ii:jj+1].compute()
	else:
		intrinsic_frame = frame/(np.nanmax(frame[:, :], axis=-1))[:, None] - quiescentFrame/(np.nanmax(quiescentFrame[:, :], axis=-1))[:, None]
		frame_norm = intrinsic_frame[filter_indx, ii:jj+1]

	loopOpt = True
	while loopOpt:
		s0s1_labels, sscore = _mainOptimization(config, frame_norm, s0_no_nan, optimalGroups=optimalGroups)
		if np.array(s0s1_labels != 0).all():
			loopOpt = False

	labels = np.zeros(frame.shape[0]) + np.nan

	labels[filter_indx] = s0s1_labels.astype(np.uint)
	return(labels, sscore)


def _mainIntrinsic(config, intrinsic_frame, intrinsicPass, filter_indx, lineIndx):

	s0_no_nan = np.ones(len(filter_indx))
	if intrinsicPass:
		s0_no_nan_tmp = np.zeros(len(filter_indx))

		intrinsicConfig = config.clusterConfig['intrinsic']
		for i in range(len(intrinsicConfig)):
			key =  intrinsicConfig[i]['label']
			indxs = config.lines[lineIndx][key]
			if type(indxs) == list:
				iframe = intrinsic_frame[filter_indx, indxs[0]:indxs[1]].sum(axis=-1)
			else:
				iframe = intrinsic_frame[filter_indx, indxs]

			if 'layerConfig' in list(intrinsicConfig[i].keys()):
				if 'bins' in list(intrinsicConfig[i]['layerConfig'].keys()):
					bins = intrinsicConfig[i]['layerConfig']['bins']
					s0_0_no_nan 	= _runIntrinsic(len(np.diff(bins)), iframe, edgeOverride=np.array(bins).astype(float))

				if 'nbins' in list(intrinsicConfig[i]['layerConfig'].keys()):
					nbins = intrinsicConfig[i]['layerConfig']['nbins']
					s0_0_no_nan 	= _runIntrinsic(nbins, iframe)

			else:
				s0_0_no_nan 	= _runIntrinsic(1, iframe)

			s0_no_nan_tmp += s0_0_no_nan*(10**(i))

		s0_Lst = np.unique(s0_no_nan_tmp)
		for i in range(len(s0_Lst)):
			# print([i, s0_Lst[i]])
			indx = np.where(s0_no_nan_tmp == s0_Lst[i])[0]
			s0_no_nan[indx.astype(int)] = i+1
	return(s0_no_nan)

def _mainOptimization(config, dataCube, labels, optimalGroups=None):

	k_lst = [int(len(np.unique(labels)))]
	if type(optimalGroups) == type(None):
		k_lst  += [x['layerGroups'] for x in config.clusterConfig['optimized']]
	else:
		k_lst += [optimalGroups]

	pwrSeq = (10**(len(k_lst) - np.arange(len(k_lst)) - 1)).astype(np.uint16)

	labels *= pwrSeq[0]

	for k in range(len(k_lst)-1):
		converge = float(config.clusterConfig['optimized'][k]['layerConfig']['converge'])
		ss_thresh = np.array(config.clusterConfig['optimized'][k]['layerConfig']['ss_thresh'])
		labelLst = np.unique(labels)
		if type(k_lst[k+1]) == list:
			optimalGroups = np.array(k_lst[k+1])
		else:
			optimalGroups = k_lst[k+1] * np.ones(len(labelLst))

		Narr= _calc.pick_jth_label(labels, 0)
		Marr= _calc.pick_jth_label(labels, 1)

		if k > 0:
			orderIndx = []
			a = k_lst[k]
			NLst = np.unique(Narr)
			for n in range(len(np.unique(Narr))):
				Nindx = np.where(Narr == np.unique(Narr)[n])[0]
				Mlst = np.unique(Marr[Nindx])
				x = np.array(a[0:NLst[n]]).sum()
				for m in range(len(Mlst)):
					orderIndx.append(x - Mlst[-m])
		else:
			orderIndx =  _calc.pick_jth_label(np.unique(labels), 0) - 1

		optimalGroups1 = optimalGroups[orderIndx]
		label_lst = np.unique(labels)

		import copy
		
		ss_final = []
		lab_final = []
		bins = np.unique(_calc.pick_jth_label(label_lst, 0))
		label_index_counter = 0
		searchBool = False
		for q in range(len(bins[~np.isnan(bins)])):
			sup_indx = np.where(_calc.pick_jth_label(labels, 0) == bins[q])[0]
			sup_labelLst = np.unique(labels[sup_indx])
			nxt_labels = np.zeros(labels.shape)	
			loop_counter = 0
			ss_score_minimum = [[] for s in range(9)]
			while True:
				label_loop = copy.deepcopy(labels)	
				with ProgressBar(total=int(len(sup_indx)), ascii=False, leave=False, 
								desc='Hi-K Layer {} ({}, {})'.format(str(k+1), loop_counter, bins[q]),
								bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as p:
					

					label_index_counter_tmp = copy.deepcopy(label_index_counter)
					#print(label_index_counter_tmp)
					k_lst_loop = []
					for l in range(len(sup_labelLst)):
						sub_index    = np.where(label_loop.astype(np.uint16) == nb.u2(sup_labelLst[l]))[0]
						sub_data = dataCube[sub_index.astype(np.uint32),:] #.compute()  
						# print(optimalGroups1)
						# print(optimalGroups1[label_index_counter])
						# print(label_index_counter)
						if optimalGroups1[label_index_counter_tmp] == 0:
							__elbowLog__ = util.logg("start", "optimalKSearch")
							k_entry = int(_runOptimalKSearch(label_loop[sub_index], sub_data, converge))
							util.logg("stop", _log=__elbowLog__)
						else:
							k_entry = int(optimalGroups1[label_index_counter_tmp])					

						k_lst_loop.append(k_entry)
						if len(sub_index) > k_entry:
							nxt_labels[sub_index] = _runOptimization(k_entry, sub_data, converge)
						else:
							print("\nStalled\n")
						
						label_index_counter_tmp += 1
						
						p.update(len(sub_index))

				label_loop += (nxt_labels*pwrSeq[k+1]).astype(np.uint16)

				if len(np.unique(label_loop[sup_indx])) == 1:# or len(np.array(ss_scoreLst[~np.isnan(ss_scoreLst)])) == 0:
					labels = label_loop
					ss_final.append([np.nan])
					lab_final.append(np.unique(label_loop[sup_indx]))
					break			
				# print(ss_score_minimum)			
				
				ss_score, ch_score, lab_order = _recordValidation(label_loop[sup_indx], dataCube[sup_indx, :])
#				print(ss_score)
#				print(lab_order)
#				
				#lindx_tmp = 0#copy.deepcopy(label_index_counter)
				ss_score_bool = True
				label_index_counter_tmp_tmp = copy.deepcopy(label_index_counter)
				# print((label_index_counter_tmp_tmp, label_index_counter))

				#lab_orderLst = np.unique(_calc.pick_jth_label(lab_order[0], k))
				# print(ss_thresh)
				# print(lab_orderLst)
				killer = int(str(lab_order[0][0])[k])
				for l in range(len(lab_order[0])):
					if killer != int(str(lab_order[0][l])[k]):
						label_index_counter_tmp_tmp += 1
						#ss_score_bool = True
					

					#lindx = np.where(_calc.pick_jth_label(lab_order[0], k+1) == lab_orderLst[l])[0]
					ss_scoreLst = ss_score[0][l]#[lindx_tmp:lindx_tmp+k_lst_loop[l]]

					ss_score_minimum[int(str(lab_order[0][l])[k])-1].append(ss_scoreLst)
					ss_score_bool *= (ss_scoreLst >= float(ss_thresh[label_index_counter_tmp_tmp]))

					# ss_score_bool *= np.nanmax(np.unique(np.array(ss_score_minimum))) >= 
					killer = int(str(lab_order[0][l])[k])
				
				if float(ss_thresh[label_index_counter]) >= 0:
					if ss_score_bool:#(np.array(ss_scoreLst[~np.isnan(ss_scoreLst)]) >= float(ss_thresh[label_index_counter])).all():# or k == 0:
						labels = label_loop
						print("loop broken: {}".format(loop_counter))
						ss_final.append([s[n] for s in ss_score_minimum for n in range(len(s)) if len(s) > 0])
						lab_final.append(lab_order[0])
						break
				else:
					if loop_counter == 300:
						label_index_counter_tmp = 0#copy.deepcopy(label_index_counter)
						for l in range(len(ss_score_minimum)):
							# print(ss_score_minimum[l])
							# print((lab_order[0], label_index_counter_tmp))
							if len(ss_score_minimum[l]) == 0:
								continue
							# print(np.unique(ss_score_minimum[l]))
							util.logg('msg', val='{},{} Max: {} | Min: {}'.format(lab_order[0][label_index_counter_tmp], label_index_counter_tmp, np.nanmax(np.array(ss_score_minimum[l])), np.nanmin(np.array(ss_score_minimum[l]))))

							fig = plt.figure(layout='constrained', figsize=(3,3))
							ax = fig.add_subplot(111)

							# _, edges = _calc.numba_histogram(ss_score_minimum[l], 20, 
							# 							lim=np.array([0, 1]))
					

							ax.hist(ss_score_minimum[l], bins=np.arange(0, 1, step=0.05), range=[0, 1], rwidth=1, histtype='step', log=True, fill=False, color='black')

							ax.set_title(lab_order[0][label_index_counter_tmp])
							fig.savefig("./fig/sscore_{}".format(lab_order[0][label_index_counter_tmp]))


							# print(np.unique(np.array(ss_score_minimum[l])))
							print(len(ss_score_minimum[l]))
							label_index_counter_tmp += 1

						searchBool = True
						break
				
				if loop_counter == 1000:
					util.logg('error', '{} Iteration exceeded {}. Killing...'.format(bins[q], loop_counter))
					return(0, 0)
					# _mainOptimization(config, dataCube, labels, optimalGroups=optimalGroups)
						# sys.exit()
				loop_counter += 1
			label_index_counter += len(sup_labelLst)
	if searchBool:
		util.logg('error', 'Search mode was active. Killing....')
		sys.exit()
	label_final = [l[n] for l in lab_final for n in range(len(l))]
	score_final = [s[n] for s in ss_final for n in range(len(s))]
	
	print(label_final)
	print(score_final)
	return(labels, [label_final,  score_final])



