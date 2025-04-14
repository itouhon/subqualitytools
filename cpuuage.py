import re
import csv

STR_COREDID = 'cid'
STR_TSKID = 'tid'
STR_TSKUSAGE = 'usage'
INT_INVTSKID = 64
core_ptn = re.compile(r'\[DBG\].+\[CORE([0-9])\]')
tsk_ptn = re.compile(r'\s+([0-9]+):\s*([0-9]+\.[0-9]+)')
cpu_ptn = re.compile(r'.+CORE([0-9]).+\s([0-9]+\.[0-9]+)%')

def analyze_log(file_path):
    cpu_usages = []
    coreid = 0
    try:
        with open(file_path, 'r') as file:
            for line in file:
                corematch = core_ptn.match(line)
                if corematch:
                    coreid = int(corematch.group(1))
                    continue
                tskmatch = tsk_ptn.match(line)
                if tskmatch and 0 != coreid:
                    usage = {STR_COREDID: coreid, STR_TSKID: int(tskmatch.group(1)), STR_TSKUSAGE: float(tskmatch.group(2))}
                    cpu_usages.append(usage)
                    continue
                cpumatch = cpu_ptn.match(line)
                if cpumatch:
                    usage = {STR_COREDID: int(cpumatch.group(1)), STR_TSKID: INT_INVTSKID, STR_TSKUSAGE: float(cpumatch.group(2))}
                    cpu_usages.append(usage)
                    continue
    except FileNotFoundError:
        print(f"\n无法找到文件: {file_path}\n")
    except Exception as e:
        print(f"\n发生错误: {e}\n")
    return cpu_usages


def calculate_average_usage(cpu_usages):
    # 用于存储每个TASKID的总USAGE和出现次数
    usage_summary = {}

    for entry in cpu_usages:
        core_id = entry[STR_COREDID]
        task_id = entry[STR_TSKID]
        usage = entry[STR_TSKUSAGE]

        # 如果当前核心ID还未在usage_summary中初始化，添加一个字典
        if core_id not in usage_summary:
            usage_summary[core_id] = {}

        # 如果当前任务ID还未在该核心ID下初始化，添加初始统计数据
        if task_id not in usage_summary[core_id]:
            usage_summary[core_id][task_id] = {"total_usage": 0, "count": 0}

        # 更新总使用率和出现次数
        usage_summary[core_id][task_id]["total_usage"] += usage
        usage_summary[core_id][task_id]["count"] += 1

    # 计算每个核心下的任务ID的平均使用率
    average_usage = {}
    for core_id, tasks in usage_summary.items():
        average_usage[core_id] = {}
        for task_id, data in tasks.items():
            avg_usage = data["total_usage"] / data["count"]
            average_usage[core_id][task_id] = avg_usage

    return average_usage


def save_tasks_csv(tasks, output_file):
    """
    将任务数据写入 CSV 文件
    :param tasks: 字典形式的任务数据 {task_id: avg_usage}
    :param output_file: 输出的 CSV 文件名
    """
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            # 写入标题行
            writer.writerow(["TaskID", "AverageUsage(%)"])

            # 写入任务数据
            for task_id, avg_usage in tasks.items():
                if task_id != INT_INVTSKID:
                    writer.writerow([task_id, f"{avg_usage:.3f}"])
                else:
                    writer.writerow(["CPU", f"{avg_usage:.3f}"])

        print(f"file: {output_file} done")
    except Exception as e:
        print(f"Err: {e}")

def main():
    while True:
        file_path = input("Please input log file(exit end): ")
        if file_path.lower() == 'exit':
            print("Program end")
            break
        cpu_usages = analyze_log(file_path)
        average_usage = calculate_average_usage(cpu_usages)
        for core_id, tasks in average_usage.items():
            print(f"CoreID[{core_id}]:")
            for task_id, avg_usage in tasks.items():
                if task_id != INT_INVTSKID:
                    print(f"  TaskID[{task_id}]: avg usage[{avg_usage:.3f}%]")
                else:
                    print(f"  CPU: avg usage[{avg_usage:.3f}%]")
            output_file = f"Core{core_id}_tasks.csv"  # 动态生成文件名
            save_tasks_csv(tasks, output_file)

if __name__ == "__main__":
    main()
