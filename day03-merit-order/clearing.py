"""
Toy electricity market clearing engine.
Single hour, single zone, no transmission constraints.
"""
from dataclasses import dataclass


@dataclass
class Block:
    """One step of an offer curve: a generator's willingness to supply
    `mw` MW if the cleared price is at least `price` $/MWh."""
    gen: str
    mw: float
    price: float


def clear_market(blocks, demand_mw):
    """
    Uniform-price merit-order auction.

    Returns:
        clearing_price : $/MWh paid to every cleared MW
        dispatch       : dict {generator: total MW awarded}
        log            : list of (gen, used_mw, offered_mw, price)
    """
    # 1. Sort the stack cheapest first
    stack = sorted(blocks, key=lambda b: b.price)

    remaining = demand_mw
    dispatch = {}
    log = []
    clearing_price = None

    # 2. Walk up the stack, dispatching until demand is met
    for b in stack:
        if remaining <= 0:
            log.append((b.gen, 0.0, b.mw, b.price))
            continue
        used = min(b.mw, remaining)
        dispatch[b.gen] = dispatch.get(b.gen, 0.0) + used
        log.append((b.gen, used, b.mw, b.price))
        remaining -= used
        # the last block we touched sets the price
        clearing_price = b.price

    if remaining > 1e-6:
        raise ValueError(f"Insufficient supply: {remaining:.1f} MW unmet")

    return clearing_price, dispatch, log


def producer_surplus(log, clearing_price):
    """Sum of (clearing_price - block_price) * used_mw across cleared blocks."""
    return sum(used * (clearing_price - price) for _, used, _, price in log)


if __name__ == "__main__":
    stack = [
        Block("A", 1500, 5),
        Block("B", 1000, 25),
        Block("B", 500, 35),
        Block("C", 700, 40),
        Block("C", 400, 55),
        Block("C", 300, 80),
        Block("D", 300, 95),
        Block("D", 200, 140),
        Block("E", 200, 250),
        Block("E", 100, 500),
    ]
# Note:For truly massive datasets, libraries like pandas or numpy (which use contiguous memory arrays rather than arrays of object references) are often preferred over standard Python objects.
    price, dispatch, log = clear_market(stack, demand_mw=4200)

    print(f"Clearing price: ${price}/MWh")
    print(f"Total producer surplus: ${producer_surplus(log, price):,.0f}")
    print("\nDispatch by generator:")
    for gen, mw in sorted(dispatch.items()):
        print(f"  {gen}: {mw:>6.1f} MW")
    print("\nBlock-by-block clearing log:")
    print(f"  {'Gen':<4}{'Used':>10}{'Offered':>12}{'Price':>10}{'Status':>14}")
    for gen, used, offered, p in log:
        if used == 0:
            status = "idle"
        elif used < offered:
            status = "marginal"
        else:
            status = "full"
        print(f"  {gen:<4}{used:>10.1f}{offered:>12.1f}{p:>10.2f}   {status}")