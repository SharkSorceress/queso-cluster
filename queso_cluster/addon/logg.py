#> file:  ./QuESO/addon/logg
#> lang:  python
#> synopsis: 
#> author:   <>
import logging
import timeit 
import functools

logger = logging.getLogger("queso_cluster")
logger.addHandler(logging.NullHandler())

def loggTimer(func):
#> detail: 
#> param type func:
#> return (type): 
#> test-method:
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		__log__ = logg("start", val="{}".format(func.__name__))
		value = func(*args, **kwargs)
		logg("stop", _log=__log__)
		return(value)
	return(wrapper)


def logg(tag, val=None, _time=None, _log=None):
#> detail: 
#> param type tag:
#> param type [None] val:
#> param type [None] _time:
#> param type [None] _log:
#> return (type): 
#> test-method:
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
				logger.info(ptag)
				return(None, timeit.default_timer())
		case 'start': 
			log_str = ptag + '\t\t' + val.upper()
			logger.info(log_str)
			return(val.upper(), timeit.default_timer())
		case 'stop': 
			log_str = ptag + '[' + duration_string(dur) + ']\t' + val.upper()
		case 'msg': 
			log_str = ptag + '\t\t' + val.upper()
		case 'warn':
			logger.warning(val.upper())
			return None
		case 'error':
			logger.error(val.upper())
			return None
	logger.info(log_str)

def duration_string(dur):
#> detail: 
#> param type dur:
#> return (type): 
#> test-method:
	return("{:02d}h {:02d}m {:02d}s".format(int(dur/3600), int(int(dur/60) % 60), int(dur % 60))) 
