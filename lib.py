__author__    = 'TAKASE Kazuyuki'
__copyright__ = 'TAKASE Kazuyuki'
__license__   = 'The MIT License'


from typing import Literal, Generator
from collections import Counter
from itertools import chain, combinations
from functools import reduce


Theme = Literal[
    # "思考力" に関わる資質
    '分析思考',
    '原点思考',
    '未来志向',
    '着想',
    '収集心',
    '内省',
    '学習欲',
    '戦略性',

    # "人間関係力" に関わる資質
    '適応性',
    '運命思考',
    '成長促進',
    '共感性',
    '調和性',
    '包含',
    '個別化',
    'ポジティブ',
    '親密性',

    # "影響力" に関わる資質
    '活発性',
    '指令性',
    'コミュニケーション',
    '競争性',
    '最上志向',
    '自己確信',
    '自我',
    '社交性',

    # "実行力" に関わる資質
    '達成欲',
    'アレンジ',
    '信念',
    '公平性',
    '慎重さ',
    '規律性',
    '目標志向',
    '責任感',
    '回復志向',
]


ThemesTable = dict[str, list[Theme]]


def histogram(table: ThemesTable, rate: int = 5) -> tuple[dict[Theme, int], dict[Theme, int]]:
    """
    Calculate the histogram of themes in the given table.

    Args:
        table (ThemesTable): The table containing themes of a team.
        rate (int, optional): The number of themes to consider from the start and end of each item. Defaults to 5.

    Returns:
        tuple[dict[Theme, int], dict[Theme, int]]: A tuple containing two dictionaries representing the histograms:
            - The first dictionary represents the histogram of strengths.
            - The second dictionary represents the histogram of weaknesses.
    """

    empty = { theme: 0 for theme in Theme.__args__ } # type: ignore

    s_hist = Counter(chain.from_iterable(map(lambda xs: xs[:rate], table.values())))
    w_hist = Counter(chain.from_iterable(map(lambda xs: xs[-rate:], table.values())))

    return ( { **empty, **s_hist }, { **empty, **w_hist } )


def _jaccard(Xi: set, Xj: set) -> float:
    return len(Xi & Xj) / len(Xi | Xj)


def _distance(Xi: list[Theme], Xj: list[Theme], rate: int) -> float:
    s_jaccard = _jaccard(set(Xi[:rate]), set(Xj[:rate]))
    w_jaccard = _jaccard(set(Xi[-rate:]), set(Xj[-rate:]))

    return 1 - (s_jaccard + w_jaccard) / 2


def distance_gen(table: ThemesTable, rate: int = 5) -> Generator[tuple[str, str, float], None, None]:
    """
    Generates a sequence of tuples representing the distance between pairs of team-members.

    Args:
        table (ThemesTable): The table containing themes of a team.
        rate (int, optional): The number of themes to consider from the start and end of each item. Defaults to 5.

    Yields:
        tuple[str, str, float]: A tuple containing the names of the two team-members and their distance.
    """

    for (name_i, Xi), (name_j, Xj) in combinations(table.items(), 2):
        yield ( name_i, name_j, _distance(Xi, Xj, rate) )


def _skipped_union(name_i: str, table: ThemesTable, rate: int) -> set[Theme]:
    skipped = ( set(Xj[:rate]) for name_j, Xj in table.items() if name_j != name_i )

    return reduce(lambda x, y: x | y, skipped)


def specific_gen(table: ThemesTable, rate: int = 5) -> Generator[tuple[str, set[Theme]], None, None]:
    """
    Generate a sequence of tuples representing the specific themes of a team-member.

    Args:
        table (ThemesTable): The table containing themes of a team.
        rate (int, optional): The number of themes to consider from the start of each item. Defaults to 5.

    Yields:
        tuple[str, set[Theme]]: A tuple containing the name and a set of his/her specific themes.
    """

    for name_i, Xi in table.items():
        yield ( name_i, set(Xi[:rate]) - _skipped_union(name_i, table, rate) )


if __name__ == '__main__':
    from sys import stdin
    from json import load


    def pretty_histogram(hist: dict[Theme, int]) -> None:
        for theme, count in hist.items():
            print(f'{theme}: {count}')

        print('')


    def pretty_distance_gen(gen: Generator[tuple[str, str, float], None, None]) -> None:
        for name_i, name_j, distance in gen:
            print(f'{name_i} <-> {name_j}: {distance:.2f}')

        print('')


    def pretty_specific_gen(gen: Generator[tuple[str, set[Theme]], None, None]) -> None:
        for name, specific in gen:
            print(f'{name}: {specific}')

        print('')


    table = load(stdin)
    strengths, weaknesses = histogram(table)

    print('=== Strengths Histogram ===')
    pretty_histogram(strengths)

    print('=== Weaknesses Histogram ===')
    pretty_histogram(weaknesses)

    print('=== Distances ===')
    pretty_distance_gen(distance_gen(table))

    print('=== Specific Themes ===')
    pretty_specific_gen(specific_gen(table))
