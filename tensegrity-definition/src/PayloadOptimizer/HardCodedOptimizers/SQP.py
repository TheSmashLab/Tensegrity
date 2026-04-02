import numpy as np
from scipy.optimize import approx_fprime
from qpsolvers import solve_qp
import LinearSearch
fFun = None

def SPQ(f, g, h, numLamdas, numSigmas, x0, tauOpt, tauFeas):
    lambdas = np.zeros(numLamdas)
    sigmas = np.zeros(numSigmas)
    alphaInit = 1
    matrixLength = numLamdas + numSigmas + len(x0)

    f0 = f(x0)
    g0 = g(x0)
    h0 = h(x0)

    delF = approx_fprime(x0,f)
    Jg = approx_fprime(x0,g)
    Jh = approx_fprime(x0,h)

    lagrandDelk = delF + Jg.T@sigmas + Jh.T@lambdas
    lagrandDelkp1 = lagrandDelk
    k = 0
    reset = False
    xk = x0
    xkp1 = 0
    hessian = np.eye(matrixLength)

    while np.linalg.norm(lagrandDelkp1) > tauOpt or np.linalg.norm(h0) > tauFeas:
        if k == 0 or reset:
            hessian = np.eye(matrixLength)
        else:
            sk = xkp1 - xk
            yk = lagrandDelkp1 - lagrandDelk
            if sk.T@yk >= .2*sk.T@hessian@sk:
                thetaK = 1
            else:
                thetaK = 0.8*sk.T@hessian@sk/(sk.T@hessian@sk - sk.T@yk)

            rk = thetaK *yk + (1-thetaK)*hessian@sk
            hessian = hessian -(hessian@sk@sk.T@hessian)/(sk.T@hessian@sk)+ rk@rk.T/rk.T@sk

        sol = solve_qp(hessian, xk,Jg, sigmas, Jh, lambdas, solver = "quadprog")
        px = sol['x'][:len(x0)]
        lambdas = lambdas + sol['x'][len(x0):len(x0) + len(lambdas)]
        sigmas = sigmas + sol['x'][len(x0) + len(lambdas):]
        alpha = LinearSearch.LinearSearch().bracket(f, fprime, sol['x'], alphaInit, xkp1)
        xk = xkp1
        xkp1 = xkp1 + alpha*px
        #Ws = Wks
        f0 = f(x0)
        g0 = g(x0)
        h0 = h(x0)

        delF = approx_fprime(x0, f)
        Jg = approx_fprime(x0, g)
        Jh = approx_fprime(x0, h)

        lagrandDelk = delF + Jg.T @ sigmas + Jh.T @ lambdas
        lagrandDelkp1 = lagrandDelk
        k = k + 1


def workingSet(Wk, sigmas, p, constraints, currentX):
    if np.linalg.norm(p) < .00001:
        if np.min(sigmas) >= 0:
            pass
        else:
            i = np.min(sigmas)
            Wk = np.delete(Wk, i, 0)
    else:
        alpha = 1
        beta = []
        for i in range(len(constraints)):
            if constraints[i] == Wk:
                pass
            else:
                if constraints[i].T.dot(p) > 0:
                    alphab = -(constraints[i].T.dot(currentX))/(constraints[i].T.dot(p))
                    if alphab < alpha:
                        alpha = alphab
                        beta = i
        Wk = np.append(Wk, constraints[beta])
    return Wk



def fprime(x0):
    return approx_fprime(x0,fFun)






