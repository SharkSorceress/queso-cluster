
from astropy.io import fits

class iris:
	def __init__(self, dataPath):
		self.dataPath = dataPath

	def load(self):
		#> detail: 
		#> param type self:
		#> return (type): 
		#> test-method:
			dataset = fits.open(self.dataPath, memmap=True, do_not_scale_image_data=True)
