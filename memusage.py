import re
import csv
from collections import defaultdict

mem_ptn = re.compile(r'.*\[\s*([0-9]+)\]\(PE([0-9])\).+Mem: type=([0-9])\s+now=([0-9]+)\s+max=([0-9]+)')
buf_ptn = re.compile(r'.+\(PE([0-9])\)\s+([A-Z]+\s+[a-zA-Z0-9]+):\s+uUsed=([0-9]+).+uMax=([0-9]+)')

NAME_SUM = 'sum'
NAME_COUNT = 'count'
NAME_MAX = 'max'
FILENAME_AVG_CSV = 'mem_avg_usage.csv'
FILENAME_ALL_CSV = 'mem_all_usage.csv'
STR_TIME = 'Time'
STR_PE = 'PE'
STR_TYPE = 'Type'
STR_NOW = 'Now'
STR_MAX = 'Max'
STR_NAME = 'Name'
STR_CTG = 'Category'

mem_usage = []
buf_usage = []


def analyze_log(file_path):
    # Step 1: 分组统计（直接计算总和和最大值）
    mem_stats = defaultdict(lambda: {NAME_SUM: 0, NAME_COUNT: 0, NAME_MAX: 0})
    buf_stats = defaultdict(lambda: {NAME_SUM: 0, NAME_COUNT: 0, NAME_MAX: 0})
    try:
        with open(file_path, 'r') as file:
            for line in file:
                memmatch = mem_ptn.match(line)
                if memmatch:
                    it = {STR_TIME: int(memmatch.group(1)),
                          STR_PE: int(memmatch.group(2)),
                          STR_TYPE: int(memmatch.group(3)),
                          STR_NOW: int(memmatch.group(4)),
                          STR_MAX: int(memmatch.group(5))}
                    mem_usage.append(it)
                    key = (it[STR_PE], it[STR_TYPE])
                    mem_stats[key][NAME_SUM] += it[STR_NOW]
                    mem_stats[key][NAME_COUNT] += 1
                    mem_stats[key][NAME_MAX] = max(mem_stats[key][NAME_MAX], it[STR_MAX])
                    continue
                bufmatch = buf_ptn.match(line)
                if bufmatch:
                    it = {STR_PE: int(bufmatch.group(1)),
                          STR_NAME: bufmatch.group(2),
                          STR_NOW: int(bufmatch.group(3)),
                          STR_MAX: int(bufmatch.group(4))}
                    buf_usage.append(it)
                    key = (it[STR_PE], it[STR_NAME])
                    buf_stats[key][NAME_SUM] += it[STR_NOW]
                    buf_stats[key][NAME_COUNT] += 1
                    buf_stats[key][NAME_MAX] = max(buf_stats[key][NAME_MAX], it[STR_MAX])
                    continue
    except FileNotFoundError:
        print(f"\n无法找到文件: {file_path}\n")
    except Exception as e:
        print(f"\n发生错误: {e}\n")
    return mem_stats, buf_stats


def saveto_avg_csv(mem_stats, buf_stats, csv_path):
    with open(csv_path, mode="w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[STR_CTG, STR_PE, STR_NAME, STR_NOW, STR_MAX])
        writer.writeheader()

        # 写入 mem_stats 部分
        for (pe, mem_type), val in mem_stats.items():
            writer.writerow({
                STR_CTG: "Mem",
                STR_PE: f'Core{pe}',
                STR_NAME: f'Mem{mem_type}',
                STR_NOW: val[NAME_SUM] / val[NAME_COUNT] if val[NAME_COUNT] else 0,
                STR_MAX: val[NAME_MAX]
            })

        # 写入 buf_stats 部分
        for (pe, name), val in buf_stats.items():
            writer.writerow({
                STR_CTG: "Buf",
                STR_PE: f'Core{pe}',
                STR_NAME: name,
                STR_NOW: val[NAME_SUM] / val[NAME_COUNT] if val[NAME_COUNT] else 0,
                STR_MAX: val[NAME_MAX]
            })
    return


def saveto_all_csv(csv_path):
    with open(csv_path, mode="w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[STR_TIME, STR_CTG, STR_PE, STR_NAME, STR_NOW, STR_MAX])
        writer.writeheader()
        for it in mem_usage:
            writer.writerow({
                STR_TIME: it[STR_TIME],
                STR_CTG: "Mem",
                STR_PE: f'Core{it[STR_PE]}',
                STR_NAME: f'Mem{it[STR_TYPE]}',
                STR_NOW: it[STR_NOW],
                STR_MAX: it[STR_MAX]
            })
    return


def main():
    while True:
        file_path = input("Please input log file(exit end): ")
        if file_path.lower() == 'exit':
            print("Program end")
            break
        mem_stats, buf_stats = analyze_log(file_path)
        saveto_avg_csv(mem_stats, buf_stats, FILENAME_AVG_CSV)
        saveto_all_csv(FILENAME_ALL_CSV)


if __name__ == "__main__":
    main()
