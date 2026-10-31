"""Sorting algorithms for the /works/sorting page (from the Sorting Algorithms lesson).

1. The five plain algorithms: bubble, selection, insertion, merge and quick sort.
2. The same algorithms again as "tracers" that write down every step, so the page can
   show them one step at a time (like the lesson slides).
3. Info about each algorithm (definition, best used for, time and space complexity).
app.py only calls run() and compare_all() at the bottom of this file.
"""
import inspect
import math
import re


# =====================================================================
#  1. THE PLAIN ALGORITHMS (what you would hand in)
# =====================================================================
def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:                       # neighbours in the wrong order?
                arr[j], arr[j + 1] = arr[j + 1], arr[j]   # swap them
                swapped = True
        if not swapped:                                   # no swaps = already sorted
            break
    return arr


def selection_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        lowest = i
        for j in range(i + 1, n):                         # find the lowest value
            if arr[j] < arr[lowest]:                      # in the unsorted part
                lowest = j
        arr[i], arr[lowest] = arr[lowest], arr[i]         # swap it to the front
    return arr


def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]                                      # the value to place
        j = i - 1
        while j >= 0 and arr[j] > key:                    # shift bigger values right
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key                                  # insert the key in its spot
    return arr


def merge_sort(arr):
    if len(arr) <= 1:                                     # one value is already sorted
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])                          # sort each half
    right = merge_sort(arr[mid:])
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):               # merge: take the smaller front value
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])                               # copy what is left over
    merged.extend(right[j:])
    return merged


def partition(arr, low, high):
    pivot = arr[high]                                     # the pivot is the last value
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:                                # smaller values go to the left
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]         # put the pivot in the middle
    return i + 1


def quick_sort(arr, low=0, high=None):
    if high is None:
        high = len(arr) - 1
    if low < high:
        p = partition(arr, low, high)                     # the pivot is now in its final place
        quick_sort(arr, low, p - 1)                       # sort the left part
        quick_sort(arr, p + 1, high)                      # sort the right part
    return arr


# =====================================================================
#  2. THE TRACERS (the same algorithms, but they record every step)
# =====================================================================
class Trace:
    """Holds the list being sorted and writes down a snapshot (step) whenever something happens."""

    def __init__(self, values, descending=False):
        self.a = list(values)
        self.descending = descending
        self.steps = []
        self.comparisons = 0
        self.swaps = 0
        # words used in the explanations
        self.wrong = "smaller" if descending else "greater"
        self.small = "larger" if descending else "smaller"
        self.low = "highest" if descending else "lowest"

    def before(self, x, y):
        """True if x should come before y in the chosen order."""
        return x > y if self.descending else x < y

    def snap(self, note, compare=(), swap=(), done=(), pivot=None, low=None, rng=None):
        self.steps.append({
            "array": list(self.a), "note": note,
            "compare": list(compare), "swap": list(swap), "sorted": sorted(done),
            "pivot": pivot, "low": low, "range": rng,
            "comparisons": self.comparisons, "swaps": self.swaps,
        })

    def finish(self):
        self.snap("Sorted! Every value is in its final place.", done=range(len(self.a)))


def trace_bubble(t):
    a, n = t.a, len(t.a)
    done = set()
    t.snap("Start. Bubble sort compares neighbours and swaps them when they are in the wrong order.")
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            t.comparisons += 1
            x, y = a[j], a[j + 1]
            if t.before(y, x):
                t.snap(f"Compare {x} and {y}: {x} is {t.wrong} than {y}, so swap them.", compare=[j, j + 1], done=done)
                a[j], a[j + 1] = y, x
                t.swaps += 1
                swapped = True
                t.snap(f"Swapped. Now {y} comes before {x}.", swap=[j, j + 1], done=done)
            else:
                t.snap(f"Compare {x} and {y}: already in order, do nothing.", compare=[j, j + 1], done=done)
        done.add(n - 1 - i)
        if not swapped:
            t.snap(f"Pass {i + 1} had no swaps, so the list is already sorted. Stop early (this is why the best case is O(n)).", done=range(n))
            break
        t.snap(f"End of pass {i + 1}: {a[n - 1 - i]} has bubbled to its final place.", done=done)
    t.finish()


def trace_selection(t):
    a, n = t.a, len(t.a)
    done = set()
    t.snap(f"Start. Selection sort finds the {t.low} value in the unsorted part and moves it to the front.")
    for i in range(n - 1):
        m = i
        t.snap(f"Pass {i + 1}: look for the {t.low} value. Start with {a[m]} as the {t.low} so far.", low=m, done=done)
        for j in range(i + 1, n):
            t.comparisons += 1
            if t.before(a[j], a[m]):
                t.snap(f"Compare {a[j]} with {a[m]}: {a[j]} is {t.small}, so it becomes the new {t.low}.", compare=[j], low=j, done=done)
                m = j
            else:
                t.snap(f"Compare {a[j]} with {a[m]}: the {t.low} stays {a[m]}.", compare=[j], low=m, done=done)
        if m != i:
            a[i], a[m] = a[m], a[i]
            t.swaps += 1
            t.snap(f"Swap the {t.low} value {a[i]} with the first unsorted element {a[m]}.", swap=[i, m], done=done)
        else:
            t.snap(f"{a[i]} is already the {t.low}, so it stays in place.", done=done)
        done.add(i)
    t.finish()


def trace_insertion(t):
    a, n = t.a, len(t.a)
    t.snap("Start. Insertion sort takes one value at a time and inserts it into the sorted part on the left. "
           "The first value is a sorted list of one.", done=[0])
    for i in range(1, n):
        key = a[i]
        t.snap(f"Take {key} and find where it belongs in the sorted part on the left.", compare=[i], done=range(i))
        j = i
        while j > 0:
            t.comparisons += 1
            left = a[j - 1]
            if t.before(key, left):
                a[j - 1], a[j] = a[j], a[j - 1]
                t.swaps += 1
                t.snap(f"Compare {key} with {left}: {key} belongs before it, so move {key} one step left.",
                       compare=[j - 1, j], swap=[j - 1, j], done=range(i + 1))
                j -= 1
            else:
                t.snap(f"Compare {key} with {left}: {key} is in the right spot, stop.", compare=[j - 1, j], done=range(i))
                break
        t.snap(f"{key} is inserted. The sorted part now has {i + 1} values.", done=range(i + 1))
    t.finish()


def trace_merge(t):
    a, n = t.a, len(t.a)
    done = set()
    t.snap("Start. Merge sort divides the list into halves, sorts each half, then merges them.")

    def sort(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        t.snap(f"Divide {a[lo:hi + 1]} into {a[lo:mid + 1]} and {a[mid + 1:hi + 1]}.", rng=[lo, hi], done=done)
        sort(lo, mid)
        sort(mid + 1, hi)
        left, right = a[lo:mid + 1], a[mid + 1:hi + 1]
        t.snap(f"Merge {left} and {right}: keep taking the smaller front value.", rng=[lo, hi], done=done)
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            t.comparisons += 1
            if t.before(right[j], left[i]):
                note = f"Compare {left[i]} and {right[j]}: take {right[j]}."
                a[k] = right[j]
                j += 1
            else:
                note = f"Compare {left[i]} and {right[j]}: take {left[i]}."
                a[k] = left[i]
                i += 1
            t.swaps += 1
            t.snap(note, swap=[k], rng=[lo, hi], done=done)
            k += 1
        while i < len(left):
            a[k] = left[i]
            t.swaps += 1
            t.snap(f"The right side is empty, so copy {left[i]}.", swap=[k], rng=[lo, hi], done=done)
            i += 1
            k += 1
        while j < len(right):
            a[k] = right[j]
            t.swaps += 1
            t.snap(f"The left side is empty, so copy {right[j]}.", swap=[k], rng=[lo, hi], done=done)
            j += 1
            k += 1
        done.update(range(lo, hi + 1))
        t.snap(f"Merged: {a[lo:hi + 1]}", rng=[lo, hi], done=done)

    sort(0, n - 1)
    t.finish()


def trace_quick(t):
    a = t.a
    done = set()
    t.snap("Start. Quick sort picks a pivot, puts smaller values on its left and the rest on its right, "
           "then sorts each side the same way.")

    def qs(lo, hi):
        if lo > hi:
            return
        if lo == hi:
            done.add(lo)
            t.snap(f"Only {a[lo]} is left in this part, so it is in its place.", rng=[lo, hi], done=done)
            return
        pivot = a[hi]
        t.snap(f"Choose the last value, {pivot}, as the pivot of {a[lo:hi + 1]}.", pivot=hi, rng=[lo, hi], done=done)
        i = lo - 1
        for j in range(lo, hi):
            t.comparisons += 1
            if t.before(a[j], pivot):
                i += 1
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    t.swaps += 1
                    t.snap(f"{a[i]} is {t.small} than the pivot {pivot}, so move it to the left part.",
                           compare=[j], swap=[i, j], pivot=hi, rng=[lo, hi], done=done)
                else:
                    t.snap(f"{a[j]} is {t.small} than the pivot {pivot} and is already in the left part.",
                           compare=[j], pivot=hi, rng=[lo, hi], done=done)
            else:
                t.snap(f"{a[j]} is not {t.small} than the pivot {pivot}, so it stays on the right.",
                       compare=[j], pivot=hi, rng=[lo, hi], done=done)
        p = i + 1
        if p != hi:
            a[p], a[hi] = a[hi], a[p]
            t.swaps += 1
        done.add(p)
        t.snap(f"Put the pivot {pivot} between the two parts. It is now in its final place.",
               swap=[p, hi] if p != hi else [], pivot=p, rng=[lo, hi], done=done)
        qs(lo, p - 1)
        qs(p + 1, hi)

    qs(0, len(a) - 1)
    t.finish()


TRACERS = {"bubble": trace_bubble, "selection": trace_selection, "insertion": trace_insertion,
           "merge": trace_merge, "quick": trace_quick}


# =====================================================================
#  3. INFO SHOWN ON THE PAGE
# =====================================================================
ALGORITHMS = {
    "bubble": {
        "name": "Bubble Sort",
        "definition": "A simple comparison-based algorithm. Each pair of neighbouring values is compared and swapped "
                      "if they are not in order. The passes repeat until no swaps are needed, which means the list is sorted.",
        "best_for": ["Small lists", "Teaching how sorting works"],
        "how": "Step through the list, compare neighbours and swap them if they are in the wrong order. Repeat the pass until the list is sorted.",
        "best": "O(n)", "avg": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "Yes",
        "functions": [bubble_sort],
    },
    "selection": {
        "name": "Selection Sort",
        "definition": "A comparison-based algorithm that splits the list into a sorted part on the left and an unsorted part "
                      "on the right. The smallest value of the unsorted part is swapped with the first unsorted element, "
                      "moving it into the sorted part.",
        "best_for": ["Not recommended for large lists", "When memory is limited (it needs almost no extra space)",
                     "When you want to keep the number of swaps low"],
        "how": "On each pass, pick the smallest (or largest) value from the unsorted part and move it to the end of the sorted part.",
        "best": "O(n²)", "avg": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "No",
        "functions": [selection_sort],
    },
    "insertion": {
        "name": "Insertion Sort",
        "definition": "A simple algorithm that builds the final sorted list one item at a time. It is much less efficient "
                      "on large lists than merge sort or quick sort.",
        "best_for": ["Lists that are mostly sorted", "Small lists", "When low memory use is a priority"],
        "how": "Take each value, find the spot where it belongs in the sorted part, and insert it there.",
        "best": "O(n)", "avg": "O(n²)", "worst": "O(n²)", "space": "O(1)", "stable": "Yes",
        "functions": [insertion_sort],
    },
    "merge": {
        "name": "Merge Sort",
        "definition": "A divide-and-conquer algorithm. It divides the list into two halves, sorts each half by calling "
                      "itself, and then merges the two sorted halves.",
        "best_for": ["Large lists", "When a stable sort is needed", "When there is enough memory (merging needs extra space)"],
        "how": "Divide the list into halves until each piece has one value (a single value is already sorted), then merge the pieces back together in order.",
        "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n log n)", "space": "O(n)", "stable": "Yes",
        "functions": [merge_sort],
    },
    "quick": {
        "name": "Quick Sort",
        "definition": "A divide-and-conquer algorithm (invented by C.A.R. Hoare in 1960). It picks a pivot value and "
                      "partitions the other values into two parts: the ones that go before the pivot and the ones that go "
                      "after it. Then each part is sorted the same way.",
        "best_for": ["When the average time of O(n log n) is expected",
                     "When space matters (it can sort in place with little extra memory)"],
        "how": "Pick a pivot, partition the list around it, then sort the two parts. The choice of pivot affects the speed.",
        "best": "O(n log n)", "avg": "O(n log n)", "worst": "O(n²)", "space": "O(log n)", "stable": "No",
        "functions": [quick_sort, partition],
    },
}
for _info in ALGORITHMS.values():       # show the real code on the page
    _info["code"] = "\n".join(inspect.getsource(fn).rstrip() + "\n" for fn in _info["functions"])
    del _info["functions"]

GUIDE = [
    ("Small lists", "Insertion sort or bubble sort is the simplest and a good choice."),
    ("Large lists", "Merge sort or quick sort are generally best because of their O(n log n) speed."),
    ("Memory concerns", "Quick sort is usually preferred over merge sort because it has a smaller memory footprint."),
    ("Stability", "If equal values must keep their original order, use merge sort (it is stable). The standard in-place quick sort is not."),
]

BIG_O_KEY = [
    ("O(1)", "constant time: the same time for any input size"),
    ("O(log N)", "logarithmic: grows with the logarithm of the input size"),
    ("O(N)", "linear: grows in step with the input size"),
    ("O(N log N)", "linearithmic: linear and logarithmic growth together"),
    ("O(N²)", "quadratic: grows with the square of the input size"),
]


# =====================================================================
#  Used by the web page (app.py calls these)
# =====================================================================
MAX_VALUES = 15


def parse_values(text):
    """Turn "4, 3, 7, 1, 5" into [4, 3, 7, 1, 5]. Raises ValueError with a friendly message."""
    parts = [p for p in re.split(r"[,\s]+", str(text).strip()) if p]
    if len(parts) < 2:
        raise ValueError("Please enter at least 2 numbers separated by commas, like 4, 3, 7, 1, 5.")
    if len(parts) > MAX_VALUES:
        raise ValueError(f"Please use {MAX_VALUES} numbers or fewer so the steps stay easy to follow.")
    out = []
    for p in parts:
        try:
            x = float(p)
        except ValueError:
            raise ValueError(f"'{p}' is not a number. Use numbers separated by commas, like 4, 3, 7, 1, 5.")
        if not math.isfinite(x) or abs(x) > 9999:
            raise ValueError("Please keep each number between -9999 and 9999.")
        out.append(int(x) if x == int(x) else x)
    return out


def run(algorithm, raw_values, order="asc"):
    """Sort the numbers with one algorithm and return every step for the page."""
    try:
        if algorithm not in ALGORITHMS:
            raise ValueError("Please choose a sorting algorithm.")
        values = parse_values(raw_values)
        t = Trace(values, descending=(order == "desc"))
        TRACERS[algorithm](t)
        return {"ok": True, "algorithm": algorithm, "name": ALGORITHMS[algorithm]["name"],
                "order": "desc" if order == "desc" else "asc", "values": values, "steps": t.steps,
                "comparisons": t.comparisons, "swaps": t.swaps, "result": t.a}
    except ValueError as e:
        return {"ok": False, "message": str(e)}


def compare_all(raw_values, order="asc"):
    """Run all five algorithms on the same numbers and return their counts."""
    try:
        values = parse_values(raw_values)
        rows = []
        for key, tracer in TRACERS.items():
            t = Trace(values, descending=(order == "desc"))
            tracer(t)
            rows.append({"name": ALGORITHMS[key]["name"], "comparisons": t.comparisons,
                         "swaps": t.swaps, "steps": len(t.steps), "result": t.a})
        return {"ok": True, "values": values, "rows": rows}
    except ValueError as e:
        return {"ok": False, "message": str(e)}
