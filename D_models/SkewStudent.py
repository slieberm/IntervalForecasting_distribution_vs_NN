#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Skewed Student Distribution
===========================

Introduction
------------

The distribution was proposed in [1]_.

The probability density function is given by

.. math::

    f\left(x|\eta,\lambda\right)=\begin{cases}
    bc\left(1+\frac{1}{\eta-2}\left(\frac{a+bx}{1-\lambda}\right)^{2}\right)
        ^{-\left(\eta+1\right)/2}, & x<-a/b,\\
    bc\left(1+\frac{1}{\eta-2}\left(\frac{a+bx}{1+\lambda}\right)^{2}\right)
        ^{-\left(\eta+1\right)/2}, & x\geq-a/b,
    \end{cases}

where :math:`2<\eta<\infty`, and :math:`-1<\lambda<1`.
The constants :math:`a`, :math:`b`, and :math:`c` are given by

.. math::

    a=4\lambda c\frac{\eta-2}{\eta-1},\quad b^{2}=1+3\lambda^{2}-a^{2},
        \quad c=\frac{\Gamma\left(\frac{\eta+1}{2}\right)}
        {\sqrt{\pi\left(\eta-2\right)}\Gamma\left(\frac{\eta}{2}\right)}.

A random variable with this density has mean zero and unit variance.
The distribution becomes Student t distribution when :math:`\lambda=0`.

References
----------

.. [1] Hansen, B. E. (1994). Autoregressive conditional density estimation.
    *International Economic Review*, 35(3), 705–730.
    <http://www.ssc.wisc.edu/~bhansen/papers/ier_94.pdf>

Examples
--------
>>> skewt = SkewStudent(eta=3, lam=-.5)
>>> arg = [-.5, 0, .5]

>>> print(skewt.pdf(arg))
[ 0.29791106  0.53007599  0.72613873]

>>> print(skewt.cdf(arg))
[ 0.21056021  0.38664586  0.66350259]

>>> print(skewt.ppf([.1, .5, .9]))
[-0.9786634   0.19359403  0.79257129]

>>> print(skewt.rvs(size=(2, 3)))
[[ 0.02398666 -0.61867166 -1.25345387]
 [-0.68277535 -0.30256514 -0.04516005]] #random

"""

from __future__ import print_function, division

import numpy as np
import matplotlib.pylab as plt
import seaborn as sns

from scipy.special import gamma
from scipy.stats import t, uniform

__all__ = ['SkewStudent']

__author__ = "Stanislav Khrapov"
__email__ = "khrapovs@gmail.com"


class SkewStudent(object):

    """Skewed Student distribution class.

    Attributes
    ----------
    eta : float
        Degrees of freedom. :math:`2 < \eta < \infty`
    lam : float
        Skewness. :math:`-1 < \lambda < 1`

    Methods
    -------
    pdf
        Probability density function (PDF)
    cdf
        Cumulative density function (CDF)
    ppf
        Inverse cumulative density function (ICDF)
    rvs
        Random variates with mean zero and unit variance

    """

    def __init__(self, eta=10., lam=-.1):
        """Initialize the class.

        Parameters
        ----------
        eta : float
            Degrees of freedom. :math:`2 < \eta < \infty`
        lam : float
            Skewness. :math:`-1 < \lambda < 1`

        """
        self.eta = eta
        self.lam = lam

    def __const_a(self):
        """Compute a constant.

        Returns
        -------
        a : float

        """
        return 4*self.lam*self.__const_c()*(self.eta-2)/(self.eta-1)

    def __const_b(self):
        """Compute b constant.

        Returns
        -------
        b : float

        """
        return (1 + 3*self.lam**2 - self.__const_a()**2)**.5

    def __const_c(self):
        """Compute c constant.

        Returns
        -------
        c : float

        """
        return gamma((self.eta+1)/2) \
            / ((np.pi*(self.eta-2))**.5*gamma(self.eta/2))

    def pdf(self, arg):
        """Probability density function (PDF).

        Parameters
        ----------
        arg : array
            Grid of point to evaluate PDF at

        Returns
        -------
        array
            PDF values. Same shape as the input.

        """
        c = self.__const_c()
        a = self.__const_a()
        b = self.__const_b()

        return b*c*(1 + 1/(self.eta-2) * ((b*arg+a)/(1+np.sign(arg+a/b)*self.lam))**2)**(-(self.eta+1)/2)

    def loglikelihood(self, param, arg):
        """Probability density function (PDF).

        Parameters
        ----------
        param: (eta, lambda)
        arg : array
            Grid of point to evaluate PDF at

        Returns
        -------
        array
            PDF values. Same shape as the input.

        """
        self.eta, self.lam = param

        # return -np.log(self.pdf(arg)).sum()
        return np.log(self.pdf(arg))

    def cdf(self, arg):
        """Cumulative density function (CDF).

        Parameters
        ----------
        arg : array
            Grid of point to evaluate CDF at

        Returns
        -------
        array
            CDF values. Same shape as the input.

        """
        a = self.__const_a()
        b = self.__const_b()

        y = (b*arg+a)/(1+np.sign(arg+a/b)*self.lam) * (1-2/self.eta)**(-.5)
        cond = arg < -a/b

        return cond * (1-self.lam) * t.cdf(y, self.eta) \
            + ~cond * (-self.lam + (1+self.lam) * t.cdf(y, self.eta))

    def ppf(self, arg):
        """Inverse cumulative density function (ICDF).

        Parameters
        ----------
        arg : array
            Grid of point to evaluate ICDF at. Must belong to (0, 1)

        Returns
        -------
        array
            ICDF values. Same shape as the input.

        """
        arg = np.atleast_1d(arg)

        a = self.__const_a()
        b = self.__const_b()

        cond = arg < (1-self.lam)/2

        ppf1 = t.ppf(arg / (1-self.lam), self.eta)
        # ppf2 = t.ppf(.5 + (arg - (1-self.lam)/2) / (1+self.lam), self.eta)
        ppf2 = t.ppf((arg+self.lam) / (1+self.lam), self.eta)
        # ppf = -999.99*np.ones_like(arg)
        ppf = np.nan_to_num(ppf1) * cond \
            + np.nan_to_num(ppf2) * np.logical_not(cond)
        ppf = (ppf * (1+np.sign(arg-(1-self.lam)/2)*self.lam) * (1-2/self.eta)**.5 - a)/b

        if ppf.shape == (1, ):
            return float(ppf)
        else:
            return ppf

    def rvs(self, size=1):
        """Random variates with mean zero and unit variance.

        Parameters
        ----------
        size : int or tuple
            Size of output array

        Returns
        -------
        array
            Array of random variates

        """
        return self.ppf(uniform.rvs(size=size))

    def plot_pdf(self, arg=np.linspace(-2, 2, 100)):
        """Plot probability density function.

        Parameters
        ----------
        arg : array
            Grid of point to evaluate PDF at

        """
        scale = (self.eta/(self.eta-2))**.5
        plt.plot(arg, t.pdf(arg, self.eta, scale=1/scale),
                 label='t distribution')
        plt.plot(arg, self.pdf(arg), label='skew-t distribution')
        plt.legend()
        plt.show()

    def plot_cdf(self, arg=np.linspace(-2, 2, 100)):
        """Plot cumulative density function.

        Parameters
        ----------
        arg : array
            Grid of point to evaluate CDF at

        """
        scale = (self.eta/(self.eta-2))**.5
        plt.plot(arg, t.cdf(arg, self.eta, scale=1/scale),
                 label='t distribution')
        plt.plot(arg, self.cdf(arg), label='skew-t distribution')
        plt.legend()
        plt.show()

    def plot_ppf(self, arg=np.linspace(.01, .99, 100)):
        """Plot inverse cumulative density function.

        Parameters
        ----------
        arg : array
            Grid of point to evaluate ICDF at

        """
        scale = (self.eta/(self.eta-2))**.5
        plt.plot(arg, t.ppf(arg, self.eta, scale=1/scale),
                 label='t distribution')
        plt.plot(arg, self.ppf(arg), label='skew-t distribution')
        plt.legend()
        plt.show()

    def plot_rvspdf(self, arg=np.linspace(-2, 2, 100), size=1000):
        """Plot kernel density estimate of a random sample.

        Parameters
        ----------
        arg : array
            Grid of point to evaluate ICDF at. Must belong to (0, 1)
        size : int or tuple
            Size of rvs to plot

        """
        rvs = self.rvs(size=size)
        xrange = [arg.min(), arg.max()]
        sns.kdeplot(rvs, clip=xrange, label='kernel')
        plt.plot(arg, self.pdf(arg), label='true pdf')
        plt.xlim(xrange)
        plt.legend()
        plt.show()


if __name__ == '__main__':

    sns.set_context('paper')
    skewt = SkewStudent(eta=3, lam=-.5)
    skewt.plot_pdf()
    skewt.plot_cdf()
    skewt.plot_ppf()
    skewt.plot_rvspdf()
