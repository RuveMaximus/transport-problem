from typing import Dict, Optional, Tuple

from enum import Enum
import numpy as np


class StartPlanMethods(Enum):
    MIN_ELEMENT = 1
    NW_CORNER = 2


class TransportProblem:
    """
    Класс для представления транспортной задачи

    :param supply: объемы поставщиков;
    :param demand: объемы потребителей;
    :param costs:  матрица затрат на транспортировку;
    :param r: штраф за излишки/дефицит;
    """

    def __init__(
        self,
        supply: np.array,
        demand: np.array,
        costs: np.array,
        r: Optional[Dict[str, np.array]] = None,
    ) -> None:
        from .plan import (
            StartPlan,
        )

        self.supply = supply
        self.demand = demand
        self.costs = costs
        self.r = r

        if r is None:
            self.r = {
                'a': np.full(self.m, 0),
                'b': np.full(self.n, 0)
            }

        self.has_dummy_row = False
        self.has_dummy_column = False

        self.start_plan = StartPlan(self)

    @property
    def m(self) -> int:
        """Количество поставщиков (строк матрицы c)."""
        return len(self.supply)

    @property
    def n(self) -> int:
        """Количество потребителей (столбцов матрицы c)."""
        return len(self.demand)

    def get_supply_demand_difference(self) -> int:
        """Получить разницу между спросом и предложением."""
        return sum(self.supply) - sum(self.demand)

    def add_dummy_supplier(self, volume: int) -> None:
        """Добавить фиктивного поставщика."""
        e = np.ones(self.n) * self.r['b']
        self.costs = np.row_stack((self.costs, e))
        self.supply = np.append(self.supply, volume)

        if np.all(e == 0):
            self.has_dummy_row = True

    def add_dummy_customer(self, volume: int) -> None:
        """Добавить фиктивного потребителя."""
        e = np.ones(self.m) * self.r['a']
        self.costs = np.column_stack((self.costs, e))
        self.demand = np.append(self.demand, volume)

        if np.all(e == 0):
            self.has_dummy_column = True

    def calculate_cost(self, x: np.ndarray) -> float:
        """Подсчет стоимости (целевой функции)."""
        return np.sum(self.costs * np.nan_to_num(x))

    def calculate_potentials(self, x: np.ndarray) -> Dict[str, np.ndarray]:
        """Вычисление потенциалов."""
        res = {'a': [np.inf for _ in range(self.m)], 'b': [np.inf for _ in range(self.n)]}
        res['a'][0] = 0.0

        while np.inf in res['a'] or np.inf in res['b']:
            for i in range(self.m):
                for j in range(self.n):
                    if x[i][j] != 0:
                        if res['a'][i] != np.inf:
                            res['b'][j] = self.costs[i][j] - res['a'][i]
                        elif res['b'][j] != np.inf:
                            res['a'][i] = self.costs[i][j] - res['b'][j]

        return res

    def is_plan_optimal(self, x: np.ndarray, p: Dict[str, np.ndarray]) -> bool:
        """Проверка плана на оптимальность."""
        for i, j in zip(*np.nonzero(x == 0)):
            if p['a'][i] + p['b'][j] > self.costs[i][j]:
                return False

        return True

    def get_best_free_cell(self, x: np.ndarray, p: Dict[str, np.ndarray]) -> Tuple[int, int]:
        free_cells = tuple(zip(*np.nonzero(x == 0)))
        return free_cells[np.argmax([p['a'][i] + p['b'][j] - self.costs[i][j] for i, j in free_cells])]

    def __str__(self) -> str:
        return f'Матрица затрат:\n{self.costs}\nЗапасы: {self.supply}\nПотребности: {self.demand}'
        # return f'a: {self.supply}\nb: {self.demand}\n\nc:\n{self.costs}\n\nr[a]: {self.r["a"]}\nr[b]: {self.r["b"]}'

    def solve(self, method='min-element'):
        from .plan import (
            find_cycle_path,
            is_degenerate_plan,
            make_start_plan_non_degenerate,
            recalculate_plan
        )
        print(f'--- ДАНО ---\n{self}\n')

        diff = self.get_supply_demand_difference()
        print(f'Разница между предложением и спросом: {diff}')
        print(f'Условие равновесия: {diff == 0}')

        if diff < 0:
            self.add_dummy_supplier(-diff)
            print(f'Добавлен фиктивный поставщик с объемом: {-diff}')
            print(f'Итог: {self}')
        elif diff > 0:
            self.add_dummy_customer(diff)
            print(f'Добавлен фиктивный потребитель с объемом: {diff}')
            print(f'Итог: {self}')

        if method == 'nw-corner':
            x = self.start_plan.find(method=StartPlanMethods.NW_CORNER)
            print(f'Начальный опорный план, найденный методом северо-западного угла\n{x.copy()}')
        elif method == 'min-element':
            x = self.start_plan.find(method=StartPlanMethods.MIN_ELEMENT)
            print(f'Начальный опорный план, полученный методом минимального элемента:\n {x.copy()}')

        check_res = is_degenerate_plan(x)
        print(f'Вырожденный план: {check_res}')
        if check_res:
            make_start_plan_non_degenerate(x)
            print(f'Делаем начальный опорный план невырожденным:\nε - очень малое положительное число\n{x}')
                  # (x.copy(), self.supply, self.demand))

        i = 1
        while True:
            print(f'--- STEP {i} ---')
            cost = self.calculate_cost(x)
            print(f'Целевая функция: {cost}')

            p = self.calculate_potentials(x)
            print(f'Потенциалы: {p}')
            print(x.copy())

            check_res = self.is_plan_optimal(x, p)
            print(f'Оптимальный план: {check_res}')
            if check_res:
                print(f'--- ОТВЕТ ---\n{x.copy()}\nЦелевая функция: {cost}')
                # print('Ответ: ', (x.copy(), self.supply, self.demand), f'Целевая функция: {cost}')
                break

            cycle_path = find_cycle_path(x, self.get_best_free_cell(x, p))
            # print(f'Цикл пересчета: {cycle_path}')
            # print((x.copy(), cycle_path, self.supply, self.demand))

            o = recalculate_plan(x, cycle_path)
            print(f'Величина пересчета: {o}\nПлан после пересчета:\n {x}')
            i += 1
        return x.tolist()
