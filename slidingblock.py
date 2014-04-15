# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from sys import argv
from collections import OrderedDict


def slide(blocks, i, j):
    """滑动一个积木块"""
    if i > j:
        i, j = j, i
    if i < j:
        blocks = "".join([
            blocks[:i],
            blocks[j],
            blocks[i+1:j],
            blocks[i],
            blocks[j+1:],
        ])
    return blocks


def generate_route(blocks, status):
    """生成滑动方案

    :param blocks: 目标积木块序列
    :param status: 状态集
    :return: 从最初的序列开始的 (积木块序列, 要滑动到空格处的积木块的位置) 列表
    """
    route = [(blocks, "-",)]
    while 'slided' in status[blocks]:
        slided = status[blocks]['slided']
        i = blocks.index("E")
        blocks = slide(blocks, slided, i)
        route.insert(0, (blocks, i))
    return route


def heuristic_const(target_blocks, status, i, j):
    """返回固定值的启发函数"""
    return 0


def heuristic_right_w_count(target_blocks, status, i, j):
    """计算每个 B 块右侧 W 块数目的启发函数

    来自 http://www.ics.uci.edu/~dechter/courses/ics-271/fall-08/homeworks/old/hw2-sol.pdf
    """
    right_w_count = len(target_blocks) // 2
    heuristic = 0
    for block in target_blocks:
        if block == "B":
            heuristic += max(0, right_w_count)
        if block == "W":
            right_w_count -= 1
    return heuristic


def heuristic_awful(target_blocks, status, i, j):
    """奇怪的启发函数，慢而且非最佳

    来自 Neeta Deshpande 的书 Artificial Intelligence 中的第 2-36 页
    """
    l = len(target_blocks) // 2
    g = status['depth']
    x = max(0, abs(i-j)-1)
    y = target_blocks[:l].count("B") + target_blocks[l:].count("W")
    h = x + y
    f = g + h
    return f


def heuristic_pos_to_end(target_blocks, status, i, j):
    """计算到结尾距离的启发函数，快但是非最佳

    来自 http://uk.docsity.com/en-docs/Logic_Programming_and_Artifical_Intelligence__Solution_Sheets_-_Computer_Science_-_Prof_Dimitar_Kazakov_8
    """
    length = len(target_blocks)
    heuristic = 0
    for index, block in enumerate(target_blocks):
        if block == "B":
            heuristic += length - 1 - index
        elif block == "W":
            heuristic += index
    return heuristic


def heuristic_pos_to_mid(target_blocks, status, i, j):
    """计算到中间距离的的启发函数，不确定是否最佳

    """
    center = len(target_blocks) // 2
    heuristic = 0
    for index, block in enumerate(target_blocks[:center]):
        if block == "B":
            heuristic += max(center-index-1, 1)
    for index, block in enumerate(target_blocks[center+1:]):
        if block == "W":
            heuristic += max(index-center-1, 1)
    return heuristic


def solve(blocks, heuristic_func):
    """求解滑动方案"""
    history = OrderedDict({
        blocks: {
            'closed': False,
            #'slided': "-",
            'cost': 0,
            #'hcost': 0,
            'depth': 1,
        }
    })

    attempt_count = 0
    while blocks.lstrip("WE").rstrip("BE") != "":
        attempt_count += 1

        status = history[blocks]
        status['closed'] = True

        i = blocks.index("E")
        for j in range(max(0, i-3), min(len(blocks), i+4)):
            target_blocks = slide(blocks, i, j)
            cost = status['cost'] + max(1, abs(i-j)-1)
            target_status = history.get(target_blocks)
            if not target_status or (not target_status['closed'] and cost < target_status['cost']):
                history[target_blocks] = {
                    'closed': False,
                    'slided': i,  # 标记那个块是最近被滑动过的
                    'cost': cost,
                    'hcost': cost + heuristic_func(target_blocks, status, i, j),
                    'depth': status['depth'] + 1,
                }

        blocks = filter(lambda b: not history[b]['closed'], reversed(history))
        blocks = min(blocks, key=lambda b: history[b]['hcost'])

    route = generate_route(blocks, history)

    logging.debug("启发函数 %s", heuristic_func.__name__)
    logging.debug("总耗散值 %s", history[blocks]['cost'])
    logging.debug("搜索次数 %s", attempt_count)
    logging.debug("总状态数 %s", len(history))
    logging.debug("滑动方案")
    for step in route:
        logging.debug("\t %s %s", *step)

    return route


def test():
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    for heuristic_func in [
            heuristic_const,
            heuristic_right_w_count,
            heuristic_awful,
            heuristic_pos_to_end,
            heuristic_pos_to_mid,
    ]:
        solve("BBBWWWE", heuristic_func)
        logging.debug("")


def main():
    blocks = "BBBWWWE"
    if len(argv) > 1:
        if argv[1].isdecimal():
            n = int(argv[1])
            blocks = "B"*n + "W"*n + "E"
        else:
            blocks = argv[1]

    route = solve(blocks, heuristic_right_w_count)
    print(" ".join(map(lambda s: str(s[1]), route[:-1])))


if __name__ == "__main__":
    main()
    #test()
