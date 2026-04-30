from lib.util.imports import *

def epoch_main(config):
	import lib.approach.epoch as ep
	import lib.paper as paper01
	import lib.util.calc as _calc 


#	catalogLst = ['', 
	#catalogLst = ['cut3_10stdev', '5stdev', 'cut3_5stdev', 'cut3_3stdev', '10stdev_25jul22']
	#catalogLst = ['bas-cosine']# 'cut3_bas', 'cut3_5stdev']

	# if True:
	# 	eventObj = eventInput("./eventRunners.yml", 0, 2)
	# 	srcUse_QS = eventObj.event.runners.config['src']
	# 	eventObj.event.srcLst 	= eventObj.event.srcLst[eventObj.event.srcLabelLst.index(srcUse_QS)]

	# 	catalogQS = eventObj.event.runners.label + '-' + eventObj.event.runners.config['aia']
	# 	__cataQSLog__ = util.logg('start', catalogQS)
	# 	epochDev = ep.EpochDriven(eventObj.event, catalogQS)
	# 	noMask_labels, _ = epochDev.clustering(epochDev.dataCube)#
	# 	util.logg("stop", _log=__cataQSLog__)


	srcUse = config.runners.config['src']
	aiaUse = config.runners.config['aia']

	srcConfig 	= config.srcLst[config.srcLabelLst.index(srcUse)]
	config.srcLst = srcConfig

	c = config.runners.label + '-' + aiaUse
	__cataLog__ = util.logg('start', c)
	epochDev = ep.EpochDriven(config, c)
	if not config.runners.overwrite:
		__loadLog__ = util.logg("start", 'Reading from file...')
		try:
			dataFile = Dataset(epochDev.figDir + '/epochCCS_{}_sorted.nc'.format(c), 'r', format="NETCDF4")	
		except FileNotFoundError:
			dataFile = Dataset(epochDev.figDir + '/epochCCS_{}.nc'.format(c), 'r', format="NETCDF4")	


		labels = dataFile.variables['labelMap'][...].data.astype(float)
		noMask_labels = dataFile.variables['noMask_labels'][...].data.astype(float)
		util.logg('stop', _log=__loadLog__)

	else:
		frame = epochDev.prep()
		#noMask_labels, sscore = epochDev.clustering(epochDev.dataCube)#
		noMask_labels, labels, scores  = epochDev.clustering(frame.reshape(epochDev.dataCube.shape))
		labels = epochDev._sortFile(labels)
		epochDev._writeMask(labels, noMask_labels)



#		epochProd = ep.EpochProducts(epochDev)
		# epochProd.catalogDelayKey(labels, noMask_labels)
		# epochProd.catalogKey(labels, sscores, noMask_labels)

		# from multiprocessing import Process, Pool
		# import threading

		# epochProd.catalogTemplate(labels, sscores, noMask_labels, 'spectral')
		# epochProd.catalogTemplate(labels, sscores, noMask_labels, 'timeDelay')



	try:
		keepI0 = config.runners.config['keepI0']
	except AttributeError:
		keepI0 = None

	p01 = paper01.paper01_products(epochDev, labels.astype(float), keepI0=keepI0, noMask_labels=noMask_labels.astype(float))
		
	p01.run()
	util.logg("stop", _log=__cataLog__)

def evo_main(config):
	import lib.approach.evo as ev
	import lib.paper as paper01


	srcUse = config.runners.config['primary']['src']
	srcConfigPrimary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	srcUse = config.runners.config['support']['src']
	srcConfigSecondary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	config.srcLst = [srcConfigPrimary, srcConfigSecondary]
#	catalogName = 'alt'

	evoDev = ev.EvolutionDriven(config, config.runners.alignmentDir, config.runners.label)

	if not config.runners.overwrite:
		frameLst, _, timeLst = evoDev.clustering()
		try:
			dataFile = Dataset(evoDev.figDir + '/evoCCS_{}_sorted.nc'.format(config.runners.label), 'r', format="NETCDF4")	
		except FileNotFoundError:
			dataFile = Dataset(evoDev.figDir + '/evoCCS_{}.nc'.format(config.runners.label), 'r', format="NETCDF4")	

		#dataFile = Dataset('./configs/enhancedMask_final_SPD.nc', 'r', format="NETCDF4")	
		labelEntry = np.zeros((5, 125*89))
		for t in range(5):
			print(dataFile.variables['labels_full'][t, ...].data.shape)
			labelEntry[t, :] = dataFile.variables['labels_full'][t, ...].data.astype(float).reshape(125*89)

		labelLst = [labelEntry]
	else:
		frameLst, labelLst, timeLst = evoDev.clustering()

	import lib.dev.evo as paper02
	p02 = paper02.paper02_products(evoDev, labelLst, frameLst)
	p02.run()


def DKIST_02_main(configs):
	import lib.approach.evo as ev
	import lib.paper as paper02
	import lib.util.calc as _calc 


	scaling = 'low'

	dirMod = {'hi': {'catalog': 'hiRes', 'alignment': '_noRebin'},
		   	  'low': {'catalog': 'lowRes', 'alignment': '_x5bin'}}

	dirMod[scaling]['catalog'] = 'FISS'#'_peakCluster_wSecondary_alt'#_wTertiary'


	catalogName 	=  dirMod[scaling]['catalog'] 
	alignmentDir 	= 'aligned' + dirMod[scaling]['alignment'] 	

	evoDev = ev.EvolutionDriven(configs, alignmentDir, catalogName)

	if False:
		frameLst, _, timeLst = evoDev.clustering()

		dataFile = Dataset('./enhancedMask_final_' + dirMod[scaling]['catalog'] + '.nc', 'r', format="NETCDF4")	
		labelEntry = np.zeros((5, evoDev.spaceInfo['rasterSize']*evoDev.spaceInfo['alongSlitSize']))
		for t in range(5):
			print(dataFile.variables['labels_full'][t, ...].data.shape)
			labelEntry[t, :] = evoDev.flatten(dataFile.variables['labels_full'][t, ...].data.astype(float))

		labelLst = [labelEntry]
	else:
		frameLst, labelLst, timeLst = evoDev.clustering()

	#---
	peakIntrinsicLabels = _calc.pick_jth_label(labelLst[0][evoDev.dynamicIndx,...].astype(int), 0).astype(float)
	evoDev.intrinsicOptimizationMap(labelLst, frameLst, peakIntrinsicLabels, mod='_before')
	# evoDev._labelFilter(labelLst, base=peakIntrinsicLabels)
	evoDev.catalogSeqKey(frameLst, labelLst, timeLst, mod='_before')

def download_new(did):
	res = Fido.search(a.dkist.Dataset(did))[0][0]
	if hasattr(globalVars, 'globus_dir') and res['Downloadable']:
		util.logg("start", "{} will be downloaded".format(did))
		dataset_date = res['Start Time'].to_value('iso', subfmt='date')
		dirid   = ''.join(dataset_date.split('-'))

		try:
			os.system(globalVars.globus_dir + 'globusconnectpersonal -start &')
			files = Fido.fetch(res, path=globalVars.home_dir + dirid + "/raw/dkist/{dataset_id}/")
			ds = dkist.load_dataset(files)
			ds[...].files.download(path=globalVars.home_dir + dirid + "/raw/dkist/{dataset_id}/")
			os.system(globalVars.globus_dir + 'globusconnectpersonal -stop &')
			yml_entry = [{"run": {"date": dataset_date, 
								"override": True,
								"kmeans": 'blind',
								"data": {"visp_id": [did]}}}]
			with open("./run_kmeans.yml", mode="a") as configFile:
				yaml.safe_dump(yml_entry, configFile, default_flow_style=False, sort_keys=False)
		except:
			util.logg('error', "An error occured during the download")
	else:
		util.logg("warn", "This dataset cannot be downloaded at this time") 
		with open('./download_queue.txt', 'a+', encoding="utf-8") as f:
			f.write('{}\t{}\t{}\t{}'.format(res['Instrument'], did, 
											res['Embargo End Date'], 
											np.floor(np.average(res['Wavelength']))))
		util.logg('msg', 'This dataset id and date is stored at ./download_queue.txt')  

if __name__ == '__main__':
	__alohaLog__ = util.logg("start", val="ALOHA")

	if False:
		dev.AIAmask()
		exit()
	
		dev.showViSPonEUV()
		import cv2
		image_folder 	= './fig/euvMovie'
		video_name 		= './fig/euvCutout'

		for form in [".avi"]:
			images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
			frame = cv2.imread(os.path.join(image_folder, images[0]))
			height, width, layers = frame.shape

			video = cv2.VideoWriter(video_name + form, 0, 10, (width, height))

			for image in images:
				video.write(cv2.imread(os.path.join(image_folder, image)))

			cv2.destroyAllWindows()
			video.release()
		exit() 


	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--event')
	parser.add_argument('-r', '--run')
	args = parser.parse_args()
	print([args.event, args.run])

	from lib.util.datClass import eventInput
	eventObj = eventInput("./eventRunners.yml", int(args.event), int(args.run))

	match eventObj.event.runners.approach:
		case "epoch":
			epoch_main(eventObj.event)
		case 'evo':
			evo_main(eventObj.event)


#	sys.exit()

	# # cat.add_catalog_www('AKEMR', runnerLst[0])
	# if len(sys.argv) > 1:
	# 	match str(sys.argv[1]):
	# 		# case 'seq':
	# 		# 	util.logg("msg", "Sequential Mode Selected")
	# 		# 	a = np.arange(len(runnerLst))
	# 		# 	if len(sys.argv) > 2:
	# 		# 		a = sys.argv[2][1:len(sys.argv[2])-1].split(',') 
	# 		# 	for i in a:
	# 		# 		analysis_main(runnerLst[int(i)])
	# 		case 'DKIST_02':
	# 			util.logg("msg", "DKIST_02 Mode Selected")
	# 			# a = np.arange(len(runnerLst))
	# 			# if len(sys.argv) > 2:
	# 			# 	a = sys.argv[2][1:len(sys.argv[2])-1].split(',') 
	# 			a = [2, 3] #, 4, 5]
	# 			runnerCollection = []
	# 			for i in a:
	# 				runnerCollection.append(runnerLst[int(i)])
	# 			DKIST_02_main(runnerCollection)
	# 		case 'DKIST_01':
	# 			a = 0
	# 			DKIST_01_main(runnerLst[a])
	# 		# case 'par':
	# 		# 	util.logg('msg', 'Parallel Mode Selected')
	# 		# 	pool = Pool(sys.argv[2])
	# 		# 	pool.map(analysis_main, runnerLst[1:3])
	# 		# 	pool.close()
	# 		# 	pool.join()
	# 		# case 'cat':
	# 		# 	visp_id = dataKey[int(sys.argv[2])]
	# 		# 	dirid = ''.join(runnerLst[int(sys.argv[2])].date.split('-'))
	# 		# 	if not os.path.isfile(globalVars.home_dir + dirid + '/catalog_' + visp_id + '.pkl' ):
	# 		# 		util.logg("warn", "catalog pkl file not found")
	# 		# 		cat.catalog_store(runnerLst[int(sys.argv[2])])
	# 		# 		util.logg("warn", "catalog pkl file stored")
	# 		# 	cat.catalog_access(runnerLst[int(sys.argv[2])], complex(sys.argv[3]))
	# 		case 'queue':
	# 			#download_queue = ['ADPNE', 'AKOJM']
	# 			download_queue = [i.strip() for i in sys.argv[2].split(',')]
	# 			print(download_queue)
	# 			if len(download_queue) > 0:
	# 				for q in range(len(download_queue)):
	# 					if download_queue[q] not in dataKey:
	# 						download_new(download_queue[q])
	# 		# case num if sys.argv[1].isdigit:
	# 		# 	util.logg('msg', 'Individal Mode Selected')
	# 		# 	analysis_main(runnerLst[int(num)])
	# 		case _:
	# 			util.logg("error", "Not a valid mode")
	# else:
	# 	util.logg('msg', 'Mode not selected')

		
	# 	correction_queue = ['AKEJR']
	# 	if len(correction_queue) > 0:
	# 		for q in range(len(correction_queue)):
	# 			visp_id = str(correction_queue[q])  
	# 			runnerDate = runnerLst[dataKey.index(visp_id)].date
	# 			dirid   = ''.join(runnerDate.split('-'))
	# 			vispData = vispDataset(globalVars.home_dir + "/" + 
	# 							dirid + "/raw/dkist/" + visp_id + "/")
	# 			saxis.derive_spectral_axis(vispData)

	util.logg("aloha", _log=__alohaLog__)
	

