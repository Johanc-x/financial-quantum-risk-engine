import math

def binomial_option_price(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    N: int = 100,
    option_type: str = "call"
) -> float:
    """
    Precio de una opción europea usando el modelo binomial CRR.

    Parámetros
    ----------
    S0 : float
        Precio spot inicial del subyacente.
    K : float
        Precio de ejercicio (strike).
    T : float
        Tiempo a vencimiento en años (por ejemplo, 0.5 = 6 meses).
    r : float
        Tipo libre de riesgo (en términos anuales, continuo).
    sigma : float
        Volatilidad anual del subyacente.
    N : int
        Número de pasos del árbol binomial.
    option_type : str
        "call" o "put".

    Retorna
    -------
    float
        Precio teórico de la opción europea (call o put).
    """

    if option_type not in ("call", "put"):
        raise ValueError("option_type debe ser 'call' o 'put'")

    # Tamaño de paso temporal
    dt = T / N

    # Parámetros del modelo CRR
    u = math.exp(sigma * math.sqrt(dt))   # factor de subida
    d = 1 / u                             # factor de caída
    disc = math.exp(-r * dt)              # factor de descuento por paso

    # Probabilidad riesgo-neutral
    p = (math.exp(r * dt) - d) / (u - d)

    if not (0 < p < 1):
        raise ValueError("Los parámetros producen una probabilidad inválida (p fuera de (0,1)).")

    # 1. Valores del subyacente en el último nivel del árbol
    prices = [S0 * (u ** j) * (d ** (N - j)) for j in range(N + 1)]

    # 2. Payoff en el vencimiento
    if option_type == "call":
        option_values = [max(S - K, 0.0) for S in prices]
    else:  # put
        option_values = [max(K - S, 0.0) for S in prices]

    # 3. Retroceso en el árbol (backward induction)
    for step in range(N - 1, -1, -1):
        option_values = [
            disc * (p * option_values[j + 1] + (1 - p) * option_values[j])
            for j in range(step + 1)
        ]

    # El primer nodo es el precio hoy
    return option_values[0]


if __name__ == "__main__":
    # Pequeño ejemplo de prueba local
    S0 = 100     # spot
    K = 105      # strike
    T = 1.0      # 1 año
    r = 0.02     # 2% tipo libre de riesgo
    sigma = 0.25 # 25% volatilidad
    N = 200      # pasos del árbol

    call_price = binomial_option_price(S0, K, T, r, sigma, N, option_type="call")
    put_price = binomial_option_price(S0, K, T, r, sigma, N, option_type="put")

    print(f"Binomial call price: {call_price:.4f}")
    print(f"Binomial put  price: {put_price:.4f}")
