"""
script to generate morse wavelets
"""

import numpy as np
from morsefuncs import morsefreq, morseafun
from scipy.special import gammaln, gamma

def morse_wave(N, ga, be, fs, K=1, nmlz='bandpass', fam='primary'):
    """
    parameters
    ----------
        N: integer
            length of each wavelet
        ga: a matrix or a scalar
            gamma
        be: matrix of the same size as gamma or a scalar
            beta
        fs: a scalar or a 1-D array
            the radian frequencies at which the Fourier transform of the wavelets reach their maximum amplitudes
        K: natural number
            number different of orthogonal wavelets
        nmlz: string, either 'bandpass' or 'energy'
            normalization scheme
            - 'bandpass': "meaning tha the FFT of the wavelet has a peak value of 2 for all frequencies FS"
            - 'energy': "the time-domain wavelet energy SUM(ABS(PSI).^2,1) is then always unity"
        fam: string, either 'primary' or 'edge'
            types of wavelets"
            - 'primary': the first or standard generalized morse wavelet
            - 'edge':  the second morse wavelet. "The edge wavelet is formed by taking the first frequency-domain derivative of the primary wavelet"
    return
    -------
        psi: numpy matrix of size (N, len(fs), K)
            morse wavelet in time domain, specified by beta and gamma 
        psif: numpy matrix of size (N, len(fs), K)
            morse wavelet in frequency domain
    ___________________________________________________________________
    source
    ------
        JLAB (C) 2004--2016 J.M. Lilly and F. Rekibi
        https://github.com/jonathanlilly/jLab/blob/master/jWavelet/morsewave.m
    """

    if nmlz!='bandpass' and nmlz!='energy':
        print('Input not recognized. Please check the normalization method')
        return

    if fam!='primary' and fam!='edge':
        print('Input not recognized. Please check the wavelet family')
        return
    elif fam=='edge':
        print('The edge wavelet has not been implemented yet.')
        return

    # make sure the parameters are numpy arrays
    fs = np.array(fs)
    ga = np.array(ga)
    be = np.array(be)
    

    print(N)
    print(np.size(fs))
    print(K)
    psi=np.zeros((N,np.size(fs),K))
    psif=np.zeros((N,np.size(fs),K))

    if np.size(fs)==1:

        psif[:,:,:], psi[:,:,:] = morsewave1(N,K,ga,be,np.abs(fs),nmlz,fam)
    else:
        for n in range(len(fs)):

            psif[:,n,:], psi[:,n,:] = morsewave1(N,K,ga,be,np.abs(fs[n]),nmlz,fam)
            if fs[n] < 0:
                if len(psi)==0:
                    psi[:,n,:] = np.conj(psi[:,n,:])
                psif[1:,n,:] = np.flip(psif[1:,n,:],0)

    return psi, psif


def morsewave1(N, K, ga, be, fs, nmlz, fam):

    fo = morsefreq(ga,be,1)
    print(fo)
    fact = np.divide(fs,fo)
    tt = np.linspace(0,1-np.divide(1,N),N)
    om = 2*np.pi*np.divide(tt, fact)


    if nmlz=='energy':
        if np.all(be==0):
            psizero = np.exp(np.power(-om,ga))
        else:
            psizero=np.exp(np.multiply(be,np.log(om))-np.power(om,ga))
    elif nmlz=='bandpass':
        if np.all(be==0):
            psizero = np.exp(np.power(-om,ga))
        else:
            # Alternate calculation to cancel things that blow up
            psizero=2*np.exp(np.multiply(-be,np.log(fo)) + np.power(fo,ga) + np.multiply(be,np.log(om)) - np.power(om,ga))

    psizero[0] /= 2 # due to unit step function

    psizero[psizero==np.nan] = 0

    if fam=='primary':
        X = morsewave_first_family(fact,N,K,ga,be,om,psizero,nmlz)
    elif fam=='edge':
        print('The edge wavelet has not been implemented yet.')
        return

    X[X==np.inf] = 0
    X[X==np.nan] = 0


    ommat = np.tile(om, (K,1,np.size(fs))).T


    Xr = np.multiply(X, np.exp(1j*np.multiply(ommat,(N+1))/2*fact)) # ensures wavelets are centered 
    
    x = np.fft.ifft(Xr,axis=0)

    return X, x


def morsewave_first_family(fact,N,K,ga,be,om,psizero,nmlz):
    r = np.divide((2*be+1),ga)
    c = r-1
    L = np.zeros(np.size(om))
    index = np.arange(round(N/2))
    psif = np.zeros((len(psizero),1,K))

    for k in range(K):
        if nmlz=='energy':
            A = morseafun(k+1,ga,be,nmlz)
            coeff = np.sqrt(np.divide(1,fact))*A
        elif nmlz=='bandpass':
            if be!=0:
                coeff = np.sqrt(np.exp(gammaln(r)+gammaln(k+1)-gammaln(k+r)))
            else:
                coeff = 1

        L[index]=laguerre(2*np.power(om[index],ga),k,c)
        
        psif[:,:,k] = np.reshape(np.multiply(np.multiply(coeff, psizero), L), (N, np.size(ga)))
    
    print('psif',psif.shape)

    return psif

def laguerre(x, k, c):
    """
    LAGUERRE Generalized Laguerre polynomials
    """
    x = np.array(x)

    y = np.zeros((np.size(x)))
    for m in range(k+1):
        fact = np.exp(gammaln(k+c+1)-gammaln(c+m+1)-gammaln(k-m+1))
        y += np.divide(np.multiply(np.multiply(np.power(-1,m), fact), np.power(x,m)), gamma(m+1))

    return y

#print("Plotting Morse Wavelets in Time Domain and Frequency Domain")
#fs_list = [1,5,10]
#psi, psif =  morse_wave(100, 2, 5, fs_list, K=1, nmlz='bandpass', fam='primary')
#plt.figure()
#plt.title('Time Domain Morse Wavelets')
#for i in range(len(fs_list)):
#    plt.plot(psi[:,i,0], label = 'Real Part for FS={}'.format(fs_list[i]))
#    plt.plot(psi[:,i,1], label = 'Imaginary Part for FS={}'.format(fs_list[i]))
#plt.legend()
#
#plt.figure()
#plt.title('Frequency Domain Morse Wavelets')
#for i in range(len(fs_list)):
#    plt.plot(psif[:,i,0], label = 'FS={}'.format(fs_list[i])) 
#plt.legend()

print('Morse Wavelet Test...')
N = 256 * 4
be = 5
ga = 2
K = 3
fs = 2 * pi/8/4

x,X = morse_wave(N,ga,be,fs,K,'bandpass')
f = np.linspace(0,1,N)/N
t = np.arange(0,len(X)) - len(X)/2

plt.subplot(3,2,1)
plt.plot(t,x[:,0,0])
# mess around with xlim and ylim
plt.ylim((-np.max(abs(x))*1.05, maxmax(abs(x))*1.05))
plt.xlim((-60, 60))

plt.subplot(3,2,2)
plt.plot(t,x[:,0,1])
plt.subplot(3,2,3)
plt.plot(t,x[:,0,2])

plt.subplot(3,2,4)
plt.plot(f,abs(X[:,0,0]))
plt.subplot(3,2,5)
plt.plot(f,abs(X[:,0,1]))
plt.subplot(3,2,6)
plt.plot(f,abs(X[:,0,2]))


