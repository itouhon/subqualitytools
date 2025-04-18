import re
import csv
from collections import defaultdict

mem_ptn = re.compile(r'.+\(PE([0-9])\).+Mem: type=([0-9])\s+now=([0-9]+)\s+max=([0-9]+)')
buf_ptn = re.compile(r'.+\(PE([0-9])\)\s+([A-Z]+\s+[a-zA-Z0-9]+):\s+uUsed=([0-9]+).+uMax=([0-9]+)')

NAME_SUM = 'sum'
NAME_COUNT = 'count'
NAME_MAX = 'max'
FILENAME_CSV = 'memusage.csv'

mem_usage = []
buf_usage = []


def analyze_log(file_path):
    try:
        # Step 1: 分组统计（直接计算总和和最大值）
        mem_stats = defaultdict(lambda: {NAME_SUM: 0, NAME_COUNT: 0, NAME_MAX: 0})
        buf_stats = defaultdict(lambda: {NAME_SUM: 0, NAME_COUNT: 0, NAME_MAX: 0})

        with open(file_path, 'r') as file:
            for line in file:
                memmatch = mem_ptn.match(line)
                if memmatch:
                    mem_usage.append({"PE": int(memmatch.group(1)),
                                      "Type": int(memmatch.group(2)),
                                      "Now": int(memmatch.group(3)),
                                      "Max": int(memmatch.group(4))})
                    key = (int(memmatch.group(1)), int(memmatch.group(2)))
                    mem_stats[key][NAME_SUM] += int(memmatch.group(3))
                    mem_stats[key][NAME_COUNT] += 1
                    mem_stats[key][NAME_MAX] = max(mem_stats[key][NAME_MAX], int(memmatch.group(4)))
                    continue
                bufmatch = buf_ptn.match(line)
                if bufmatch:
                    buf_usage.append({"PE": int(bufmatch.group(1)),
                                      "Name": bufmatch.group(2),
                                      "Now": int(bufmatch.group(3)),
                                      "Max": int(bufmatch.group(4))})
                    key = (int(bufmatch.group(1)), bufmatch.group(2))
                    buf_stats[key][NAME_SUM] += int(bufmatch.group(3))
                    buf_stats[key][NAME_COUNT] += 1
                    buf_stats[key][NAME_MAX] = max(buf_stats[key][NAME_MAX], int(bufmatch.group(4)))
                    continue
    except FileNotFoundError:
        print(f"\n无法找到文件: {file_path}\n")
    except Exception as e:
        print(f"\n发生错误: {e}\n")
    return mem_stats, buf_stats


def saveto_csv(mem_stats, buf_stats, csv_path):
    with open(csv_path, mode="w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["Category", "PE", "T_or_N", "Avg_Now", "Max_Max"])
        writer.writeheader()

        # 写入 mem_stats 部分
        for (pe, mem_type), val in mem_stats.items():
            writer.writerow({
                "Category": "Mem",
                "PE": pe,
                "T_or_N": mem_type,
                "Avg_Now": val[NAME_SUM] / val[NAME_COUNT] if val[NAME_COUNT] else 0,
                "Max_Max": val[NAME_MAX]
            })

        # 写入 buf_stats 部分
        for (pe, name), val in buf_stats.items():
            writer.writerow({
                "Category": "Buf",
                "PE": pe,
                "T_or_N": name,
                "Avg_Now": val[NAME_SUM] / val[NAME_COUNT] if val[NAME_COUNT] else 0,
                "Max_Max": val[NAME_MAX]
            })

def main():
    while True:
        file_path = input("Please input log file(exit end): ")
        if file_path.lower() == 'exit':
            print("Program end")
            break
        mem_stats, buf_stats = analyze_log(file_path)
        saveto_csv(mem_stats, buf_stats, FILENAME_CSV)

if __name__ == "__main__":
    main()
