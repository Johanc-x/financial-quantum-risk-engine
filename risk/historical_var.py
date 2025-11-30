import numpy as np

def historical_var(returns, confidence=0.95):
    """
    Calcula un VaR histórico sencillo.
    returns: array-like de rendimientos diarios
    confidence: nivel de confianza (0.95 -> 95%)
    """
    returns = np.sort(returns)
    index = int((1 - confidence) * len(returns))
    return abs(returns[index])
