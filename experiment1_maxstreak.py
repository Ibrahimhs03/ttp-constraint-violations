#Experiment 1: Effect of MaxStreak on constraint violations.
#Varies MaxStreak from 1 to 6 with NoRepeat fixed at 1.
#Run once per MaxStreak value by changing the max_streak variable.

import random
import time
import matplotlib.pyplot as plt

#ranndom scheduele generation
def random_round(n, rng):
    teams = list(range(n))
    rng.shuffle(teams)
    games = []
    for i in range(0, n, 2):
        a, b = teams[i], teams[i + 1]
        if rng.random() < 0.5:
            games.append((a, b))
        else:
            games.append((b, a))
    return games


def random_schedule(n):
    rng = random.Random()
    schedule = []
    for _ in range(2 * (n - 1)):
        schedule.append(random_round(n, rng))
    return schedule



def opponent_map(round_games):
    opp = {}
    for h, a in round_games:
        opp[h] = a
        opp[a] = h
    return opp

#Count violations where the same two teams face each other in consecutive rounds. (NoRepeat= 1 is the standard constraint.)
def count_no_repeat(schedule):
    violations = 0
    opp_per_round = [opponent_map(rnd) for rnd in schedule]
    for r in range(1, len(schedule)):
        prev = opp_per_round[r - 1]
        curr = opp_per_round[r]
        for team in curr:
            if curr[team] == prev[team]:
                violations += 1
    return violations

#Count violations where a team exceedes the maximum allowed consecutive home or away matches
def count_max_streak(schedule, n, max_streak):
    violations = 0
    home = [0] * n
    away = [0] * n
    for rnd in schedule:
        for h, a in rnd:
            home[h] += 1
            away[h] = 0
            if home[h] > max_streak:
                violations += 1
            away[a] += 1
            home[a] = 0
            if away[a] > max_streak:
                violations += 1
    return violations

#Count violations where a directed match (h,a) does not appear eactly once across the full schedule
def count_drr_violations(schedule, n):
    counts = {(h, a): 0 for h in range(n) for a in range(n) if h != a}
    for rnd in schedule:
        for h, a in rnd:
            counts[(h, a)] += 1
    violations = sum(abs(1 - c) for c in counts.values() if c != 1)
    return violations


#Analyze one schedule

def analyze_schedule(n, max_streak):
    sched = random_schedule(n)
    nr = count_no_repeat(sched)
    ms = count_max_streak(sched, n, max_streak)
    drr = count_drr_violations(sched, n)
    return nr, ms, drr

#Run many stimulations 
def run_experiment_stats(n, max_streak, repetitions):
    total_nr = total_ms = total_drr = 0
    min_nr = min_ms = min_drr = float("inf")
    max_nr = max_ms = max_drr = float("-inf")
    valid_schedules = 0

    for _ in range(repetitions):
        nr, ms, drr = analyze_schedule(n, max_streak)

        total_nr += nr
        total_ms += ms
        total_drr += drr

        min_nr = min(min_nr, nr)
        min_ms = min(min_ms, ms)
        min_drr = min(min_drr, drr)

        max_nr = max(max_nr, nr)
        max_ms = max(max_ms, ms)
        max_drr = max(max_drr, drr)

        if nr == 0 and ms == 0 and drr == 0:
            valid_schedules += 1

    return {
        "teams": n,
        "avg_no_repeat": total_nr / repetitions,
        "min_no_repeat": min_nr,
        "max_no_repeat": max_nr,
        "avg_max_streak": total_ms / repetitions,
        "min_max_streak": min_ms,
        "max_max_streak": max_ms,
        "avg_drr": total_drr / repetitions,
        "min_drr": min_drr,
        "max_drr": max_drr,
        "valid_count": valid_schedules,
        "valid_percentage": 100 * valid_schedules / repetitions,
    }




if __name__ == "__main__":

    #This value of max_streak is being changed every run (1,2,3,4,5,6)
    #The results are saved to a text file and plotted automatically
    max_streak = 3

    team_sizes = list(range(4, 52, 2))
    repetitions = 100_000

    results_all = []
    print(f"\nRunning experiments for MaxStreak = {max_streak}\n")

    result_filename = f"results_maxstreak_{max_streak}_100k.txt"
    with open(result_filename, "w") as f:
        f.write(f"Results for MaxStreak = {max_streak}, "
                f"repetitions = {repetitions}\n\n")

    for n in team_sizes:
        print(f"Running n = {n} ...")
        start = time.time()

        row = run_experiment_stats(n, max_streak, repetitions)
        results_all.append(row)

        elapsed = round(time.time() - start, 2)
        print(f"Time: {elapsed} sec")
        print(f"NoRepeat avg/min/max: {round(row['avg_no_repeat'], 4)} "
              f"{row['min_no_repeat']} {row['max_no_repeat']}")
        print(f"MaxStreak avg/min/max: {round(row['avg_max_streak'], 4)} "
              f"{row['min_max_streak']} {row['max_max_streak']}")
        print(f"DRR avg/min/max: {round(row['avg_drr'], 4)} "
              f"{row['min_drr']} {row['max_drr']}")
        print(f"Valid: {row['valid_count']} "
              f"({round(row['valid_percentage'], 6)}%)\n")

        with open(result_filename, "a") as f:
            f.write(str(row) + "\n")

    x   = [r["teams"] for r in results_all]
    drr = [r["avg_drr"] for r in results_all]
    ms  = [r["avg_max_streak"] for r in results_all]
    nr  = [r["avg_no_repeat"] for r in results_all]

    plt.figure(figsize=(8, 5))
    plt.plot(x, drr, marker="o", label="Double Round-Robin")
    plt.plot(x, ms,  marker="o", label="MaxStreak")
    plt.plot(x, nr,  marker="o", label="NoRepeat")
    plt.title(f"MaxStreak = {max_streak}, NoRepeat = 1 (standard)")
    plt.xlabel("Number of Teams")
    plt.ylabel("Average Violations")
    plt.xlim(2, 50)
    plt.ylim(0, 2500)
    plt.grid(True)
    plt.legend()
    plt.savefig(f"maxstreak_{max_streak}_100k.png", dpi=300, bbox_inches="tight")
    plt.show()
    print("Done.")
