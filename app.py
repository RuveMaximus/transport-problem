import litestar
from litestar.config.cors import CORSConfig
from dataclasses import dataclass
import transportation_problem as tp
import numpy as np


@dataclass
class TPProblem:
    costs: list[list[int]]
    demand: list[int]
    supply: list[int]
    method: str


@litestar.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Server works'}


@litestar.post('/solve/')
async def solve(data: TPProblem) -> list[list[int]]:
    problem = tp.TransportProblem(
        np.array(data.supply),
        np.array(data.demand),
        np.array(data.costs)
    )
    solution: list[list[int]] = problem.solve(method=data.method)
    return solution


app = litestar.Litestar(
    route_handlers=[root, solve],
    cors_config=CORSConfig(
        allow_origins=['*']
    )
)
