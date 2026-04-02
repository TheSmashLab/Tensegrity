import numpy as np

#initializes the linear search class
class LinearSearch:
    def __init__(self):
        self.u1 = 1e-4
        self.u2 = .2
        self.sigma = 2
        self.iterations = 0
        self.gradientMags = []

    #does the bracket function as defined in the text book/
    def bracket(self, f, fder, p, alpha, loc0):
        #initializes variables.
        phi0 = f(loc0)
        phi0dot = p.dot(self.partials(loc0, fder))
        alpha1 = 0
        alpha2 = alpha
        first = True

        while True:
            #finds the locations that the alpha multipliers correspond to.
            loc2 = loc0 + alpha2 * p
            loc1 = loc0 + alpha1 * p
            phi1 = f(loc1)
            phi2 = f(loc2)
            phi1Dot = p.dot(self.partials(loc1, fder))

            if phi2 > phi0 + self.u1 * alpha2 * phi0dot or (not first and phi2 > phi1):  #checks if the new location at alpha2 is higher than the initial locaiton.  If so, function increased and
                # pinpointing can begin.
                alphaStar = self.pinPoint(alpha1, alpha2, phi0,  phi1Dot, f, fder, p, loc0)
                return alphaStar
            phi2Dot = p.dot(self.partials(loc2, fder))
            if np.abs(phi2Dot) <= -self.u2 * phi0dot: #check to see if the new slope is within the slope limit.  If so, can use that point.
                return alpha2
            elif phi2Dot >= 0: # checks to see if on a positive slope.  If so, the function is rising and can pinpoint.
                alphastar = self.pinPoint(alpha2, alpha1, phi0,  phi1Dot, f, fder, p, loc0)
                return alphastar
            else:#otherwise the bracketed region is increased and it does the above checks again.
                alpha1 = alpha2
                alpha2 = alpha2 * self.sigma
            first = False


    def interpolation(self, alpha1, alpha2, phi1, phi2, phi1Dot):  # does a parabolic interpolation of the new minimum point.
        num = 2 * alpha1 * (phi2 - phi1) + phi1Dot * (alpha1**2 - alpha2**2)
        denom = 2 * (phi2 - phi1 + phi1Dot * (alpha1 - alpha2))
        return num / denom


    def partials(self, location, fder): # returns the derivative values of the function at a specific loction, or what the gradient is at that location.
        return fder(location)


    def pinPoint(self, alphaLow, alphaHigh, phi0, phi0Dot, f, fder, p, loc0):  # once the minimizing bounds are found, pinpoints the bottom using a quadratic estimation.
        while True:
            #intial values that need to be updated depending on alphas.
            loc1 = loc0 + p * alphaLow
            loc2 = loc0 + p * alphaHigh
            phi1 = f(loc1)
            phi2 = f(loc2)
            phi1Dot =  p.dot(self.partials(loc1, fder))
            alpha_p = self.interpolation(alphaLow, alphaHigh, phi1, phi2, phi1Dot)
            loc_p = loc0 + p * alpha_p
            phi_p = f(loc_p)
            if phi_p > phi0 + self.u1 * alpha_p * phi0Dot or phi_p > phi1: #checks if phi_p is still higher than phi_0, if so, moves the alphaHigh to the new locaiton.
                alphaHigh = alpha_p
            else:
                phiDot_p = p.dot(self.partials(loc_p, fder))  # slope along the p line.
                if abs(phiDot_p) <= -self.u2 * phi0Dot: #checks to see if the found slope is within the realm of reason.
                    return alpha_p
                elif (phiDot_p * (alphaHigh - alphaLow)) >= 0: #essentially ensures that the slopes at alphaHigh and alphaLow are equivilant.
                    alphaHigh = alphaLow
                alphaLow = alpha_p
