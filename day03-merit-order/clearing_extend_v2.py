"""
Toy market clearing engine — supply offers + demand bids.
Single hour, single zone, uniform-price double auction.
"""
from dataclasses import dataclass


@dataclass
class Block:
    """Supply offer: gen will produce up to `mw` MW if cleared price >= `price`."""
    gen: str
    mw: float
    price: float


@dataclass
class DemandBid:
    """Demand bid: customer will buy up to `mw` MW if cleared price <= `price`."""
    customer: str
    mw: float
    price: float


def clear_market(supply, demand):
    """
    Two-sided uniform-price merit-order clearing.

    Returns:
        clearing_price : marginal supply price ($/MWh)
        dispatched     : {gen: total MW awarded}
        fulfilled      : {customer: total MW served}
        cleared_qty    : total MW transacted
    """
    # Sort copies so we don't mutate caller's lists or objects
    sup = sorted(supply,  key=lambda b: b.price)              # cheap → expensive
    dem = sorted(demand,  key=lambda d: -d.price)             # high WTP → low

    s_idx = d_idx = 0
    s_remaining = sup[0].mw if sup else 0.0
    d_remaining = dem[0].mw if dem else 0.0

    dispatched, fulfilled = {}, {}
    cleared_qty = 0.0
    clearing_price = None

    while s_idx < len(sup) and d_idx < len(dem):
        s_block, d_bid = sup[s_idx], dem[d_idx]
        if d_bid.price < s_block.price:
            break  # no more profitable trades

        traded = min(s_remaining, d_remaining)
        dispatched[s_block.gen]  = dispatched.get(s_block.gen, 0.0) + traded
        fulfilled[d_bid.customer] = fulfilled.get(d_bid.customer, 0.0) + traded
        cleared_qty += traded
        clearing_price = s_block.price

        s_remaining -= traded
        d_remaining -= traded
        if s_remaining == 0 and s_idx + 1 < len(sup):
            s_idx += 1
            s_remaining = sup[s_idx].mw
        elif s_remaining == 0:
            s_idx += 1  # exhaust loop
        if d_remaining == 0 and d_idx + 1 < len(dem):
            d_idx += 1
            d_remaining = dem[d_idx].mw
        elif d_remaining == 0:
            d_idx += 1

    return clearing_price, dispatched, fulfilled, cleared_qty


if __name__ == "__main__":
    supply = [
        Block("A", 1500, 5),
        Block("B", 1000, 25),  Block("B", 500, 35),
        Block("C", 700, 40),   Block("C", 400, 55),  Block("C", 300, 80),
        Block("D", 300, 95),   Block("D", 200, 140),
        Block("E", 200, 250),  Block("E", 100, 500),
    ]
    demand = [
        DemandBid("a", 500, 5),    DemandBid("a", 500, 10),
        DemandBid("b", 500, 500),  DemandBid("b", 500, 150),
        DemandBid("c", 500, 350),  DemandBid("c", 500, 50),
    ]

    price, dispatched, fulfilled, qty = clear_market(supply, demand)

    print(f"Clearing price : ${price}/MWh")
    print(f"Cleared qty    : {qty:,.0f} MW")
    print("\nDispatched:")
    for gen, mw in sorted(dispatched.items()):
        print(f"  {gen}: {mw:>6.1f} MW")
    print("\nFulfilled:")
    for cust, mw in sorted(fulfilled.items()):
        print(f"  {cust}: {mw:>6.1f} MW")