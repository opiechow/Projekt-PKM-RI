import numpy as np

class kalmenFilter():
    Q = 1e-5 # process variance
    sz = (2,2)
    xhat=np.zeros(sz)      # a posteri estimate of x
    P=np.ones(sz)         # a posteri error estimate
    xhatminus=np.zeros(sz) # a priori estimate of x
    Pminus=np.zeros(sz)    # a priori error estimate
    K=np.zeros(sz)         # gain or blending factor

    R = [0.1**7, 0.1] # estimate of measurement variance, change to see effect

    # intial guesses
    # xhat[0] = 0.0
    # P[0] = 1.0

    def measure(self, modelVal, measuredVal, source, scale):
        for k in range(2):
            if source == "czujnik":
                a = 0
            else:
                a = 1
            # time update
            # self.xhatminus[k, a] = self.xhat[k, a]
            self.Pminus[k, a] = self.P[k, a]+self.Q

            # measurement update
            self.K[k, a] = self.Pminus[k, a]/( self.Pminus[k, a]+self.R[a] )
            self.xhat[k, a] = modelVal[a]/scale+self.K[k, a]*(measuredVal[k]-modelVal[k]/scale)
            self.P[k, a] = (1-self.K[k, a])*self.Pminus[k, a]

        return self.xhat
