from typing import List, Tuple


def compute_avg_beta(
        data: List[Tuple[float, List[float], List[float]]]
) -> List[Tuple[float, float]]:
    results: List[Tuple[float, float]] = []
    for u_ce, ic_list, ib_list in data:
        betas = [
            ic / ib
            for ic, ib in zip(ic_list, ib_list)
            if ib > 0
        ]
        if betas:
            avg = sum(betas) / len(betas)
            results.append((u_ce, avg))
    return results
