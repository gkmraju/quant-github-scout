from __future__ import annotations

from top_quant_gits.models import CategoryQuery


DEFAULT_CATEGORIES: list[CategoryQuery] = [
    CategoryQuery(
        slug="quant",
        title="Quant Research",
        search_terms=[
            "\"quantitative trading\"",
            "\"factor investing\"",
            "\"quant research\"",
        ],
        keywords=[
            "quant",
            "quantitative",
            "factor",
            "alpha",
            "portfolio",
            "research",
        ],
    ),
    CategoryQuery(
        slug="algo-trading",
        title="Algo Trading",
        search_terms=[
            "\"algorithmic trading\"",
            "\"trading bot\"",
            "\"systematic trading\"",
        ],
        keywords=[
            "algo",
            "algorithmic",
            "trading",
            "execution",
            "broker",
            "strategy",
        ],
    ),
    CategoryQuery(
        slug="crypto-trading",
        title="Crypto Trading",
        search_terms=[
            "\"crypto trading\"",
            "\"defi trading\"",
            "\"crypto arbitrage\"",
        ],
        keywords=[
            "crypto",
            "bitcoin",
            "ethereum",
            "defi",
            "arbitrage",
            "exchange",
        ],
    ),
    CategoryQuery(
        slug="indian-options",
        title="Indian Options",
        search_terms=[
            "\"nifty options\"",
            "\"banknifty options\"",
            "\"nse option chain\"",
            "\"zerodha options\"",
        ],
        keywords=[
            "nifty",
            "banknifty",
            "nse",
            "fno",
            "options",
            "zerodha",
            "upstox",
            "dhan",
        ],
    ),
    CategoryQuery(
        slug="backtesting",
        title="Backtesting",
        search_terms=[
            "\"backtesting engine\"",
            "\"strategy backtest\"",
            "\"event driven backtest\"",
        ],
        keywords=[
            "backtest",
            "backtesting",
            "simulation",
            "engine",
            "performance",
            "metrics",
        ],
    ),
]
