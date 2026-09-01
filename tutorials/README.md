# Tutorials

Written walkthroughs for the patterns in the study route, plus the animated
assets that go with them.

```
tutorials/
  SlidingWindow.md      one Markdown tutorial per pattern
  TwoPointers.md
  assets/<pattern>/     generated GIFs, referenced from the tutorials
  anim/                 the generator that produces assets/ (see anim/README.md)
```

## Status

<!-- tutorials:status -->
2 of 21 patterns have a written tutorial. The rest are in progress and will be added one pattern at a time.

| Pattern | Status | Tutorial |
| --- | --- | --- |
| Arrays & Hashing | in progress | — |
| Two Pointers | ✓ written | [TwoPointers.md](TwoPointers.md) |
| Sliding Window | ✓ written | [SlidingWindow.md](SlidingWindow.md) |
| Stack & Monotonic Stack | in progress | — |
| Binary Search | in progress | — |
| Linked List | in progress | — |
| Trees & BSTs | in progress | — |
| Heap / Priority Queue | in progress | — |
| Backtracking | in progress | — |
| Tries | in progress | — |
| Graphs | in progress | — |
| Advanced Graphs | in progress | — |
| 1-D Dynamic Programming | in progress | — |
| 2-D Dynamic Programming | in progress | — |
| Greedy | in progress | — |
| Intervals | in progress | — |
| Math & Bit Manipulation | in progress | — |
| Insight & Case Analysis | in progress | — |
| String Algorithms | in progress | — |
| Number Theory & Combinatorics | in progress | — |
| Fenwick & Segment Tree | in progress | — |
<!-- /tutorials:status -->

## Using an animation in a tutorial

GIFs play inline on GitHub, in most Markdown renderers and in the tracker's
guide cards, so embedding is just:

```markdown
![Growing and shrinking a variable window](../assets/sliding-window/lc0003-longest-substring.gif)
```

Every animation loops forever and ends on a summary frame that sits on screen
for about two seconds, so a reader who scrolls past mid-loop still lands on the
takeaway.

## What exists today

| Pattern | Problem | File |
| --- | --- | --- |
| Sliding window, fixed size | LC 643 max sum of size k | `assets/sliding-window/lc0643-fixed-window.gif` |
| Sliding window, variable size | LC 3 longest substring without repeats | `assets/sliding-window/lc0003-longest-substring.gif` |
| Sliding window, shrink while valid | LC 76 minimum window substring | `assets/sliding-window/lc0076-min-window.gif` |
| Sliding window, shift not shrink | LC 424 longest repeating character replacement | `assets/sliding-window/lc0424-shift-dont-shrink.gif` |
| Sliding window, counting | LC 713 subarray product less than k | `assets/sliding-window/lc0713-count-subarrays.gif` |
| Monotonic deque | LC 239 sliding window maximum | `assets/sliding-window/lc0239-window-maximum.gif` |
| Two pointers, converging | LC 167 two sum on a sorted array | `assets/two-pointers/lc0167-two-pointers.gif` |
| Two pointers, elimination | LC 11 container with most water | `assets/two-pointers/lc0011-container-water.gif` |
| Two pointers, resolution | LC 42 trapping rain water | `assets/two-pointers/lc0042-trapping-water.gif` |
| Prefix and suffix maxima | LC 42 trapping rain water, two passes | `assets/two-pointers/lc0042-trapping-two-pass.gif` |
| Two pointers, read and write | LC 283 move zeroes | `assets/two-pointers/lc0283-read-write.gif` |
| Two pointers, three-way partition | LC 75 sort colors | `assets/two-pointers/lc0075-sort-colors.gif` |
| Two pointers, parallel | LC 88 merge sorted array | `assets/two-pointers/lc0088-merge-sorted.gif` |
| Slow and fast pointers | LC 142 Floyd's cycle detection | `assets/two-pointers/lc0142-floyd-cycle.gif` |
| Binary search | LC 704 binary search | `assets/binary-search/lc0704-binary-search.gif` |
| Monotonic stack | LC 739 daily temperatures | `assets/monotonic-stack/lc0739-monotonic-stack.gif` |
| Prefix sum + hash map | LC 560 subarray sum equals k | `assets/prefix-sum/lc0560-prefix-sum.gif` |

Every GIF is 2000 pixels wide, which is what keeps the text sharp on a HiDPI
screen once GitHub scales it into the content column. Files run 290 to 860 KB.

## Regenerating

```bash
cd tutorials/anim
pip install -r requirements.txt
python3 render_all.py
```

The GIFs are committed, so a reader never needs to run the generator. Rerun it
after editing a pattern module or the theme, and commit the result.

## Reading the animations

Every frame carries its own key row under the title, so an animation still
explains itself when someone meets it outside this repo.

The colours rest on one opposition, and it is the same in every animation:

- **blue** means this passes, is valid, is kept
- **red** means this fails, violates the rule, or is being thrown away

Red against blue is the pairing that survives the common forms of colour
blindness. Red against green is the pairing that does not, which is why green is
not used here at all.

The other three colours sit deliberately off that axis, so none of them can be
misread as a verdict:

- **slate**: in the current window, or still in the live search space, with no
  judgement passed yet
- **cyan**: a quantity the algorithm is accumulating, such as the water in LC 42
- **amber**: the element being examined right this step
- **purple**: part of the best answer found so far
- grey and white carry no meaning beyond "already done with" and "not reached yet"

The caption bar at the bottom says why the step happened, and the highlighted
line on the right is the line of code doing it.
