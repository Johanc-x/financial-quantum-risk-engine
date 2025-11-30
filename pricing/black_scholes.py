import math
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma):
    """
    Precio de una opción call europea usando Black-Scholes.
    S: spot
    K: strike
    T: tiempo a vencimiento (años)
    r: tipo libre de riesgo
    sigma: volatilidad anual
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    call = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return call

def black_scholes_put(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    put = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put
