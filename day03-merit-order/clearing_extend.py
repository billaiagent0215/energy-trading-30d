"""
Toy electricity market clearing engine.
Single hour, single zone, no transmission constraints.
Add demand bids for 3 (A,B,C) village
"""
from dataclasses import dataclass


@dataclass
class Block:
    """One step of an offer curve: a generator's willingness to supply
    `mw` MW if the cleared price is at least `price` $/MWh."""
    gen: str
    mw: float
    price: float

@dataclass
class Demand_bid:
    """The demand bid block"""
    customer: str
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
    supply_stack = sorted(blocks, key=lambda b: b.price)
    demand_stack = sorted(demand_mw, key=lambda a: a.price)

    dispatched = {}
    fulfilled = {}
    clearing_price = None
    
    # 2.Compare supply and demand
    for d in demand_stack: # $50 500MW
        for s in supply_stack: # $5 1500MW
            if d.price > s.price: # When Demand.price > Supply.price Match!

                #  Check current residual capacity
                # avaliable_supply = s.mw - dispatched.get(s.gen, 0.0)
                # avaliable_demand = d.mw - fulfilled.get(d.customer, 0.0)

                if s.mw <= 0 or d.mw <= 0:
                    continue
                elif d.mw <= s.mw: # Check avaliability
                    fulfilled[d.customer] = fulfilled.get(d.customer, 0.0) + d.mw
                    dispatched[s.gen] = dispatched.get(s.gen, 0.0) + d.mw
                    s.mw -= d.mw
                    d.mw = 0
                    clearing_price = s.price
                else:
                    fulfilled[d.customer] = fulfilled.get(d.customer, 0.0) + s.mw
                    dispatched[s.gen] = dispatched.get(s.gen, 0.0) + s.mw
                    d.mw -= s.mw
                    s.mw = 0
            else: # If Demand.price < Supply.price Demand not fulfilled!
                break


    return clearing_price, dispatched, fulfilled

# Producer surplus
def producer_surplus(log, clearing_price):
    """Sum of (clearing_price - block_price) * used_mw across cleared blocks."""
    return sum(used * (clearing_price - price) for _, used, _, price in log)

# Demand surplus

if __name__ == "__main__":
    supply_stack = [
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

    demand_stack = [
        Demand_bid("a", 500, 5),
        Demand_bid("a", 500, 10),
        Demand_bid("b", 500, 500),
        Demand_bid("b", 500, 150),
        Demand_bid("c", 500, 350),
        Demand_bid("c", 500, 50),
    ]

    price, dispatched, fulfilled = clear_market(supply_stack, demand_stack)
    print(f"${price}\n {dispatched}\n {fulfilled}")
