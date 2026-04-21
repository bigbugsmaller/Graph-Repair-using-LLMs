"""
Global reproducibility seeding.

Call ``init_seed()`` once at the top of every entry-point (main.py,
runner.py, graph_generator.py, scripts/*) **before** any random calls.

When ``config.RANDOM_SEED`` is set the following are seeded:
  - ``random`` (stdlib)
  - ``Faker`` (if importable)

Within a seeded run every call to ``random.randint``, ``random.choice``,
etc. still returns a *different* value on each invocation, but the
*sequence* is identical across runs — which is exactly what
reproducibility requires.
"""

from __future__ import annotations

import logging
import random

import config

_SEEDED = False


def init_seed(seed: int | None = None) -> int | None:
    """Seed all sources of Python-side randomness.

    Parameters
    ----------
    seed : int | None
        Explicit seed value.  Falls back to ``config.RANDOM_SEED``.
        If both are ``None`` the function is a no-op.

    Returns
    -------
    int | None
        The seed that was applied, or ``None`` if skipped.
    """
    global _SEEDED
    if _SEEDED:
        return seed

    seed = seed if seed is not None else config.RANDOM_SEED
    if seed is None:
        logging.info("RANDOM_SEED not set — running non-deterministically.")
        return None

    # stdlib random
    random.seed(seed)

    # Faker (optional dependency — only graph_generator.py uses it)
    try:
        from faker import Faker
        Faker.seed(seed)
    except ImportError:
        pass

    _SEEDED = True
    logging.info("Global seed set to %d.", seed)
    return seed
