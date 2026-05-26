# Experiment 3: Combined MaxStreak and NoRepeat analysis.
# Tests all 36 combinations of MaxStreak (1-6) and NoRepeat (1-6) for tournaments of 10, 20, and 50 teams.
# Results are visualized as heatmaps showing average MaxStreak violations.

import random
import os
import matplotlib.pyplot as plt

#Raandom schedule generation
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


# Count violations where the same two teams face each other more consecutively than the NoRepeat limit allows.
# A NoRepeat limit of 1 means 1 consecutive repeat is allowed before a violation is counted.
def count_no_repeat(schedule, n, no_repeat_limit):
    violations = 0
    opp_per_round = [opponent_map(rnd) for rnd in schedule]
    for team in range(n):
        streak = 1
        for r in range(1, len(schedule)):
            prev_opp = opp_per_round[r - 1][team]
            curr_opp = opp_per_round[r][team]
            if curr_opp == prev_opp:
                streak += 1
            else:
                streak = 1
            if streak > no_repeat_limit + 1:
                violations += 1
    return violations


# Count violations where a team exceeds the maximum allowed consecutive home or away matches.
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


# Count violations where a directed match (h, a) does not appear exactly once across the full schedule.
def count_drr_violations(schedule, n):
    counts = {(h, a): 0 for h in range(n) for a in range(n) if h != a}
    for rnd in schedule:
        for h, a in rnd:
            counts[(h, a)] += 1
    violations = sum(abs(1 - c) for c in counts.values() if c != 1)
    return violations


# Analyze one schedule

def analyze_schedule(n, max_streak, no_repeat_limit):
    sched = random_schedule(n)
    nr = count_no_repeat(sched, n, no_repeat_limit)
    ms = count_max_streak(sched, n, max_streak)
    drr = count_drr_violations(sched, n)
    return nr, ms, drr



#Run many simulations

def run_experiment_stats(n, max_streak, no_repeat_limit, repetitions):
    total_nr = total_ms = total_drr = 0
    min_nr = min_ms = min_drr = float("inf")
    max_nr = max_ms = max_drr = float("-inf")
    valid_schedules = 0

    for _ in range(repetitions):
        nr, ms, drr = analyze_schedule(n, max_streak, no_repeat_limit)

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
    max_streak_values = [1, 2, 3, 4, 5, 6]
    no_repeat_values  = [1, 2, 3, 4, 5, 6]
    team_sizes        = [10, 20, 50]
    repetitions       = 100_000

    # Results are saved as heatmap images in this folder
    save_dir = "heatmap_results"
    os.makedirs(save_dir, exist_ok=True)

    for team_size in team_sizes:
        print(f"\n=== Running for {team_size} teams ===\n")
        ms_grid = []

        for ms in max_streak_values:
            ms_row = []
            for nr in no_repeat_values:
                print(f"  MaxStreak={ms}, NoRepeat={nr}...")
                row = run_experiment_stats(
                    team_size, ms, nr, repetitions
                )
                # Only store average MaxStreak violations
                ms_row.append(row["avg_max_streak"])
            ms_grid.append(ms_row)

        fig, ax = plt.subplots(1, 1, figsize=(7, 5))

        # Lighter yellow = more violations, darker red = fewer violations
        im = ax.imshow(ms_grid, cmap="YlOrRd_r", aspect="auto")
        ax.set_xticks(range(len(no_repeat_values)))
        ax.set_xticklabels(no_repeat_values)
        ax.set_yticks(range(len(max_streak_values)))
        ax.set_yticklabels(max_streak_values)
        ax.set_xlabel("NoRepeat")
        ax.set_ylabel("MaxStreak")
        ax.set_title(f"Avg MaxStreak Violations - {team_size} teams")
        plt.colorbar(im, ax=ax)

        for i in range(len(max_streak_values)):
            for j in range(len(no_repeat_values)):
                ax.text(
                    j, i,
                    f"{ms_grid[i][j]:.0f}",
                    ha="center", va="center", fontsize=9
                )

        plt.tight_layout()
        plt.savefig(
            os.path.join(save_dir, f"heatmap_{team_size}_teams.png"),
            dpi=300,
            bbox_inches="tight"
        )
        plt.close()
        print(f"Done for {team_size} teams.")
