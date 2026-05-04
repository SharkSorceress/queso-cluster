import logging
import timeit 

logFormatter = logging.Formatter("!> [%(asctime)s]%(message)s")
loggers = logging.getLogger(__name__)
loggers.setLevel(logging.INFO)

#fileHandler = logging.FileHandler("./.log", mode='w')
#fileHandler.setFormatter(logFormatter)
#loggers.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
loggers.addHandler(consoleHandler)
def loggTimer(func):
	def wrapper(*args, **kwargs):
		__log__ = logg("start", val="{}".format(func.__name__))
		value = func(*args, **kwargs)
		logg("stop", _log=__log__)
		return(value)
	return(wrapper)

def logg(tag, val=None, _time=None, _log=None):
	ptag = '[' + tag.upper() + '\t]'
	if _log is not None:
		val, _time = _log
	if _time is not None:
		dur = timeit.default_timer() - _time
	match tag:
		case 'aloha': 
			if _log is not None:
				log_str = ptag + '[' + duration_string(dur) + ']'
			else:
				#print(ptag + 'DURATION\tMESSAGES\tRUNNERS')
				loggers.info(ptag)
				return(None, timeit.default_timer())
		case 'start': 
			log_str = ptag + '\t\t' + val.upper()
			loggers.info(log_str)
			return(val.upper(), timeit.default_timer())
		case 'stop': 
			log_str = ptag + '[' + duration_string(dur) + ']\t' + val.upper()
		case 'msg': 
			log_str = ptag + '\t\t' + val.upper()
		case 'warn':
			loggers.warning(val.upper())
			return None
		case 'error':
			loggers.error(val.upper())
			return None
	loggers.info(log_str)

def duration_string(dur):
	return("{:02d}h {:02d}m {:02d}s".format(int(dur/3600), int(int(dur/60) % 60), int(dur % 60))) 
