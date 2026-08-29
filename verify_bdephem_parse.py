"""
与 C++ 版 bdephem_txt_loader.h 同逻辑的 Python 验证脚本：
  - 读取 col1 跳过
  - 解析 col2~col16 → 对应 15 个字段
  - 列顺序与 C++ 实现完全一致
用于在没有 Qt 环境的沙箱中快速验证解析逻辑。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class BDEphemDataStruct:
    usWeek: int          # quint16
    usZ_Week: int        # quint16
    dSecond: float       # double
    iPRN: int            # qint32  (字符串 -> 整数，保留 C 前缀时把字母去掉，按 int() 行为)
    uiHealth: int        # quint32
    uiAODE: int          # quint32
    uiAODC: int          # quint32
    fToe: float          # float
    dRootA: float        # double
    dEcc: float          # double
    dOmega: float        # double
    dDeltaN: float       # double
    dM0: float           # double
    dOmega0: float       # double
    BD2OrBD3flag: int    # quint8


def _parse_prn(s: str) -> int:
    """PRN 列可能形如 C01 / C30 等，按 Qt 的 toInt 行为：
    toInt 在遇到非数字前缀时会解析失败并返回 0。
    这里做同样处理：若转 int 失败则尝试去掉前面字母再转。
    """
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        m = re.search(r'(\d+)', s)
        return int(m.group(1)) if m else 0


def load_from_txt(path: str, skip_header: int = 0) -> List[BDEphemDataStruct]:
    result: List[BDEphemDataStruct] = []
    with open(path, 'r', encoding='utf-8') as f:
        for idx, raw in enumerate(f, start=1):
            line = raw.rstrip('\r\n')
            if idx <= skip_header:
                continue
            trimmed = line.strip()
            if not trimmed or trimmed.startswith('#'):
                continue
            # 逗号 → 空格，再分割
            cols = line.replace(',', ' ').split()
            if len(cols) < 16:
                print(f"[WARN] 第{idx}行列数不足16(实际{len(cols)})，跳过: {line}")
                continue
            try:
                # cols[0] col1=跳过
                eph = BDEphemDataStruct(
                    usWeek       = int(cols[1]),   # col2
                    usZ_Week     = int(cols[2]),   # col3
                    dSecond      = float(cols[3]), # col4
                    iPRN         = _parse_prn(cols[4]),  # col5
                    uiHealth     = int(cols[5]),   # col6
                    uiAODE       = int(cols[6]),   # col7
                    uiAODC       = int(cols[7]),   # col8
                    fToe         = float(cols[8]), # col9
                    dRootA       = float(cols[9]), # col10
                    dEcc         = float(cols[10]),# col11
                    dOmega       = float(cols[11]),# col12
                    dDeltaN      = float(cols[12]),# col13
                    dM0          = float(cols[13]),# col14
                    dOmega0      = float(cols[14]),# col15
                    BD2OrBD3flag = int(cols[15]),  # col16
                )
            except (ValueError, IndexError) as e:
                print(f"[WARN] 第{idx}行字段解析失败，跳过: {e}; 行={line}")
                continue
            result.append(eph)
    return result


if __name__ == '__main__':
    import sys
    fp = sys.argv[1] if len(sys.argv) > 1 else '/workspace/bd_ephem_test.txt'
    rows = load_from_txt(fp)
    print(f"解析成功 {len(rows)} 条\n")
    for i, r in enumerate(rows, 1):
        print(f"--- 第{i}条 ---")
        print(f"  usWeek       = {r.usWeek}")
        print(f"  usZ_Week     = {r.usZ_Week}")
        print(f"  dSecond      = {r.dSecond}")
        print(f"  iPRN         = {r.iPRN}")
        print(f"  uiHealth     = {r.uiHealth}")
        print(f"  uiAODE       = {r.uiAODE}")
        print(f"  uiAODC       = {r.uiAODC}")
        print(f"  fToe         = {r.fToe}")
        print(f"  dRootA       = {r.dRootA}")
        print(f"  dEcc         = {r.dEcc}")
        print(f"  dOmega       = {r.dOmega}")
        print(f"  dDeltaN      = {r.dDeltaN}")
        print(f"  dM0          = {r.dM0}")
        print(f"  dOmega0      = {r.dOmega0}")
        print(f"  BD2OrBD3flag = {r.BD2OrBD3flag}  ({'BD2' if r.BD2OrBD3flag == 1 else 'BD3' if r.BD2OrBD3flag == 2 else '未知'})")
