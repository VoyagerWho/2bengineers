def extract_best_total(summary: str) -> float:
    return float(summary.splitlines()[2].split(":")[1])


def process_generation_block(block: str) -> []:
    crucial_lines = block.splitlines()[0:4]
    print(crucial_lines)
    gen_id = int(crucial_lines[0][27:-7])
    avg_fitness = float(crucial_lines[2][30:].split(" ")[0])
    best_fitness = float(crucial_lines[3][14:].split(" ")[0])
    return [gen_id, avg_fitness, best_fitness]


if __name__ == "__main__":
    file = "TrainLogFFN3.txt"
    data = "dataFFN3.csv"
    summary = ""
    errors = 0
    block = ""
    blockId = -1
    with open("logs/" + file, "r") as f:
        with open("logs/" + data, "w") as d:

            for line in f.readlines():

                if line.startswith("["):
                    errors += 1
                    continue

                if line.startswith(" ******") or line.startswith("Best genome:"):
                    blockId += 1
                    if blockId > 0:
                        [i, a, b] = process_generation_block(block)
                        print(f"Done {blockId}")
                        d.write(f"{i},{a},{b}\n")
                    block = ""

                block += line
            summary = block
    bestTotal = extract_best_total(summary)
    print([bestTotal, errors, blockId])


