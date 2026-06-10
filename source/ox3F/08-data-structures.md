# Data Structures — 0x3F list

> Curated from 灵茶山艾府 (0x3F)'s problem list: [https://leetcode.cn/discuss/post/mOr1u6/](https://leetcode.cn/discuss/post/mOr1u6/) (snapshot 2026-06-09). Section structure and problem order follow the original.
> Competition-only sections and leetcode.cn-exclusive problems are omitted (see the end of this file).
> **Rating** = LeetCode contest difficulty rating (~1000–3000+) from the [zerotrac project](https://zerotrac.github.io/leetcode_problem_rating/); 🔒 = premium.

## 0. Common Enumeration Techniques

### §0.1 Enumerate Right, Maintain Left

#### §0.1.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 1 | 1 | [Two Sum](https://leetcode.com/problems/two-sum/) | Easy |  |
| 2 | 1512 | [Number of Good Pairs](https://leetcode.com/problems/number-of-good-pairs/) | Easy | 1161 |
| 3 | 2441 | [Largest Positive Integer That Exists With Its Negative](https://leetcode.com/problems/largest-positive-integer-that-exists-with-its-negative/) | Easy | 1168 |
| 4 | 121 | [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy |  |
| 5 | 2016 | [Maximum Difference Between Increasing Elements](https://leetcode.com/problems/maximum-difference-between-increasing-elements/) | Easy | 1246 |
| 6 | 624 | [Maximum Distance in Arrays](https://leetcode.com/problems/maximum-distance-in-arrays/) | Medium |  |
| 7 | 3880 | [Minimum Absolute Difference Between Two Values](https://leetcode.com/problems/minimum-absolute-difference-between-two-values/) | Easy | 1257 |
| 8 | 2342 | [Max Sum of a Pair With Equal Sum of Digits](https://leetcode.com/problems/max-sum-of-a-pair-with-equal-sum-of-digits/) | Medium | 1309 |
| 9 | 1128 | [Number of Equivalent Domino Pairs](https://leetcode.com/problems/number-of-equivalent-domino-pairs/) | Easy | 1333 |
| 10 | 1679 | [Max Number of K-Sum Pairs](https://leetcode.com/problems/max-number-of-k-sum-pairs/) | Medium | 1346 |
| 11 | 219 | [Contains Duplicate II](https://leetcode.com/problems/contains-duplicate-ii/) | Easy |  |
| 12 | 2260 | [Minimum Consecutive Cards to Pick Up](https://leetcode.com/problems/minimum-consecutive-cards-to-pick-up/) | Medium | 1365 |
| 13 | 2001 | [Number of Pairs of Interchangeable Rectangles](https://leetcode.com/problems/number-of-pairs-of-interchangeable-rectangles/) | Medium | 1436 |
| 14 | 2815 | [Max Pair Sum in an Array](https://leetcode.com/problems/max-pair-sum-in-an-array/) | Easy | 1295 |
| 15 | 3623 | [Count Number of Trapezoids I](https://leetcode.com/problems/count-number-of-trapezoids-i/) | Medium | 1580 |
| 16 | 2364 | [Count Number of Bad Pairs](https://leetcode.com/problems/count-number-of-bad-pairs/) | Medium | 1622 |
| 17 | 3805 | [Count Caesar Cipher Pairs](https://leetcode.com/problems/count-caesar-cipher-pairs/) | Medium | 1624 |
| 18 | 3371 | [Identify the Largest Outlier in an Array](https://leetcode.com/problems/identify-the-largest-outlier-in-an-array/) | Medium | 1644 |
| 19 | 3761 | [Minimum Absolute Distance Between Mirror Pairs](https://leetcode.com/problems/minimum-absolute-distance-between-mirror-pairs/) | Medium | 1669 |
| 20 | 1014 | [Best Sightseeing Pair](https://leetcode.com/problems/best-sightseeing-pair/) | Medium | 1730 |
| 21 | 1814 | [Count Nice Pairs in an Array](https://leetcode.com/problems/count-nice-pairs-in-an-array/) | Medium | 1738 |
| 22 | 3584 | [Maximum Product of First and Last Elements of a Subsequence](https://leetcode.com/problems/maximum-product-of-first-and-last-elements-of-a-subsequence/) | Medium | 1763 |
| 23 | 2905 | [Find Indices With Index and Value Difference II](https://leetcode.com/problems/find-indices-with-index-and-value-difference-ii/) | Medium | 1764 |
| 24 | 3837 | [Delayed Count of Equal Elements](https://leetcode.com/problems/delayed-count-of-equal-elements/) 🔒 | Medium |  |
| 25 | 3907 | [Count Smaller Elements With Opposite Parity](https://leetcode.com/problems/count-smaller-elements-with-opposite-parity/) 🔒 | Medium |  |

#### §0.1.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 26 | 1010 | [Pairs of Songs With Total Durations Divisible by 60](https://leetcode.com/problems/pairs-of-songs-with-total-durations-divisible-by-60/) | Medium | 1377 |
| 27 | 3185 | [Count Pairs That Form a Complete Day II](https://leetcode.com/problems/count-pairs-that-form-a-complete-day-ii/) | Medium | 1385 |
| 28 | 2748 | [Number of Beautiful Pairs](https://leetcode.com/problems/number-of-beautiful-pairs/) | Easy | 1301 |
| 29 | 2506 | [Count Pairs Of Similar Strings](https://leetcode.com/problems/count-pairs-of-similar-strings/) | Easy | 1335 |
| 30 | 2874 | [Maximum Value of an Ordered Triplet II](https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/) | Medium | 1583 |
| 31 | 1497 | [Check If Array Pairs Are Divisible by k](https://leetcode.com/problems/check-if-array-pairs-are-divisible-by-k/) | Medium | 1787 |
| 32 | 1031 | [Maximum Sum of Two Non-Overlapping Subarrays](https://leetcode.com/problems/maximum-sum-of-two-non-overlapping-subarrays/) | Medium | 1680 |
| 33 | 2555 | [Maximize Win From Two Segments](https://leetcode.com/problems/maximize-win-from-two-segments/) | Medium | 2081 |
| 34 | 1995 | [Count Special Quadruplets](https://leetcode.com/problems/count-special-quadruplets/) | Easy | 1352 |
| 35 | 3404 | [Count Special Subsequences](https://leetcode.com/problems/count-special-subsequences/) | Medium | 2445 |
| 36 | 3267 | [Count Almost Equal Pairs II](https://leetcode.com/problems/count-almost-equal-pairs-ii/) | Hard | 2545 |
| 37 | 3480 | [Maximize Subarrays After Removing One Conflicting Pair](https://leetcode.com/problems/maximize-subarrays-after-removing-one-conflicting-pair/) | Hard | 2764 |
| 38 | 1214 | [Two Sum BSTs](https://leetcode.com/problems/two-sum-bsts/) 🔒 | Medium | 1389 |
| 39 | 2964 | [Number of Divisible Triplet Sums](https://leetcode.com/problems/number-of-divisible-triplet-sums/) 🔒 | Medium |  |
| 40 | 3917 | [Count Indices With Opposite Parity](https://leetcode.com/problems/count-indices-with-opposite-parity/) | Easy | 1199 |
| 41 | 2078 | [Two Furthest Houses With Different Colors](https://leetcode.com/problems/two-furthest-houses-with-different-colors/) | Easy | 1241 |
| 42 | 454 | [4Sum II](https://leetcode.com/problems/4sum-ii/) | Medium |  |
| 43 | 220 | [Contains Duplicate III](https://leetcode.com/problems/contains-duplicate-iii/) | Hard |  |
| 44 | 3027 | [Find the Number of Ways to Place People II](https://leetcode.com/problems/find-the-number-of-ways-to-place-people-ii/) | Hard | 2020 |
| 45 | 3548 | [Equal Sum Grid Partition II](https://leetcode.com/problems/equal-sum-grid-partition-ii/) | Hard | 2245 |
| 46 | 3713 | [Longest Balanced Substring I](https://leetcode.com/problems/longest-balanced-substring-i/) | Medium | 1490 |

### §0.2 Enumerate the Middle

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 47 | 2909 | [Minimum Sum of Mountain Triplets II](https://leetcode.com/problems/minimum-sum-of-mountain-triplets-ii/) | Medium | 1479 |
| 48 | 3583 | [Count Special Triplets](https://leetcode.com/problems/count-special-triplets/) | Medium | 1510 |
| 49 | 1930 | [Unique Length-3 Palindromic Subsequences](https://leetcode.com/problems/unique-length-3-palindromic-subsequences/) | Medium | 1533 |
| 50 | 3128 | [Right Triangles](https://leetcode.com/problems/right-triangles/) | Medium | 1541 |
| 51 | 2874 | [Maximum Value of an Ordered Triplet II](https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-ii/) | Medium | 1583 |
| 52 | 447 | [Number of Boomerangs](https://leetcode.com/problems/number-of-boomerangs/) | Medium |  |
| 53 | 456 | [132 Pattern](https://leetcode.com/problems/132-pattern/) | Medium |  |
| 54 | 3067 | [Count Pairs of Connectable Servers in a Weighted Tree Network](https://leetcode.com/problems/count-pairs-of-connectable-servers-in-a-weighted-tree-network/) | Medium | 1909 |
| 55 | 1534 | [Count Good Triplets](https://leetcode.com/problems/count-good-triplets/) | Easy | 1279 |
| 56 | 3455 | [Shortest Matching Substring](https://leetcode.com/problems/shortest-matching-substring/) | Hard | 2303 |
| 57 | 2242 | [Maximum Score of a Node Sequence](https://leetcode.com/problems/maximum-score-of-a-node-sequence/) | Hard | 2304 |
| 58 | 2867 | [Count Valid Paths in a Tree](https://leetcode.com/problems/count-valid-paths-in-a-tree/) | Hard | 2428 |
| 59 | 2552 | [Count Increasing Quadruplets](https://leetcode.com/problems/count-increasing-quadruplets/) | Hard | 2433 |
| 60 | 3257 | [Maximum Value Sum by Placing Three Rooks II](https://leetcode.com/problems/maximum-value-sum-by-placing-three-rooks-ii/) | Hard | 2553 |
| 61 | 3073 | [Maximum Increasing Triplet Value](https://leetcode.com/problems/maximum-increasing-triplet-value/) 🔒 | Medium |  |

### §0.3 Traversing Diagonals

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 62 | 3446 | [Sort Matrix by Diagonals](https://leetcode.com/problems/sort-matrix-by-diagonals/) | Medium | 1373 |
| 63 | 2711 | [Difference of Number of Distinct Values on Diagonals](https://leetcode.com/problems/difference-of-number-of-distinct-values-on-diagonals/) | Medium | 1429 |
| 64 | 1329 | [Sort the Matrix Diagonally](https://leetcode.com/problems/sort-the-matrix-diagonally/) | Medium | 1548 |
| 65 | 498 | [Diagonal Traverse](https://leetcode.com/problems/diagonal-traverse/) | Medium |  |
| 66 | 562 | [Longest Line of Consecutive One in Matrix](https://leetcode.com/problems/longest-line-of-consecutive-one-in-matrix/) 🔒 | Medium |  |

## 1. Prefix Sums

### §1.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 67 | 303 | [Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Easy |  |
| 68 | 3427 | [Sum of Variable Length Subarrays](https://leetcode.com/problems/sum-of-variable-length-subarrays/) | Easy | 1216 |
| 69 | 2559 | [Count Vowel Strings in Ranges](https://leetcode.com/problems/count-vowel-strings-in-ranges/) | Medium | 1435 |
| 70 | 1310 | [XOR Queries of a Subarray](https://leetcode.com/problems/xor-queries-of-a-subarray/) | Medium | 1460 |
| 71 | 3152 | [Special Array II](https://leetcode.com/problems/special-array-ii/) | Medium | 1523 |
| 72 | 1749 | [Maximum Absolute Sum of Any Subarray](https://leetcode.com/problems/maximum-absolute-sum-of-any-subarray/) | Medium | 1542 |
| 73 | 53 | [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | Medium |  |
| 74 | 3652 | [Best Time to Buy and Sell Stock using Strategy](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-using-strategy/) | Medium | 1557 |
| 75 | 3361 | [Shift Distance Between Two Strings](https://leetcode.com/problems/shift-distance-between-two-strings/) | Medium | 1553 |
| 76 | 3511 | [Make a Positive Array](https://leetcode.com/problems/make-a-positive-array/) 🔒 | Medium |  |
| 77 | 3540 | [Minimum Time to Visit All Houses](https://leetcode.com/problems/minimum-time-to-visit-all-houses/) 🔒 | Medium |  |
| 78 | 1523 | [Count Odd Numbers in an Interval Range](https://leetcode.com/problems/count-odd-numbers-in-an-interval-range/) | Easy | 1209 |
| 79 | 848 | [Shifting Letters](https://leetcode.com/problems/shifting-letters/) | Medium | 1353 |

### §1.2 Prefix Sums + Hash Map

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 80 | 560 | [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Medium |  |
| 81 | 930 | [Binary Subarrays With Sum](https://leetcode.com/problems/binary-subarrays-with-sum/) | Medium | 1592 |
| 82 | 1524 | [Number of Sub-arrays With Odd Sum](https://leetcode.com/problems/number-of-sub-arrays-with-odd-sum/) | Medium | 1611 |
| 83 | 974 | [Subarray Sums Divisible by K](https://leetcode.com/problems/subarray-sums-divisible-by-k/) | Medium | 1676 |
| 84 | 523 | [Continuous Subarray Sum](https://leetcode.com/problems/continuous-subarray-sum/) | Medium |  |
| 85 | 2588 | [Count the Number of Beautiful Subarrays](https://leetcode.com/problems/count-the-number-of-beautiful-subarrays/) | Medium | 1697 |
| 86 | 525 | [Contiguous Array](https://leetcode.com/problems/contiguous-array/) | Medium |  |
| 87 | 3755 | [Find Maximum Balanced XOR Subarray Length](https://leetcode.com/problems/find-maximum-balanced-xor-subarray-length/) | Medium | 1663 |
| 88 | 3026 | [Maximum Good Subarray Sum](https://leetcode.com/problems/maximum-good-subarray-sum/) | Medium | 1817 |
| 89 | 1477 | [Find Two Non-overlapping Sub-arrays Each With Target Sum](https://leetcode.com/problems/find-two-non-overlapping-sub-arrays-each-with-target-sum/) | Medium | 1851 |
| 90 | 1546 | [Maximum Number of Non-Overlapping Subarrays With Sum Equals Target](https://leetcode.com/problems/maximum-number-of-non-overlapping-subarrays-with-sum-equals-target/) | Medium | 1855 |
| 91 | 1124 | [Longest Well-Performing Interval](https://leetcode.com/problems/longest-well-performing-interval/) | Medium | 1908 |
| 92 | 3728 | [Stable Subarrays With Equal Boundary and Interior Sum](https://leetcode.com/problems/stable-subarrays-with-equal-boundary-and-interior-sum/) | Medium | 1909 |
| 93 | 3381 | [Maximum Subarray Sum With Length Divisible by K](https://leetcode.com/problems/maximum-subarray-sum-with-length-divisible-by-k/) | Medium | 1943 |
| 94 | 2488 | [Count Subarrays With Median K](https://leetcode.com/problems/count-subarrays-with-median-k/) | Hard | 1999 |
| 95 | 1590 | [Make Sum Divisible by P](https://leetcode.com/problems/make-sum-divisible-by-p/) | Medium | 2039 |
| 96 | 2845 | [Count of Interesting Subarrays](https://leetcode.com/problems/count-of-interesting-subarrays/) | Medium | 2073 |
| 97 | 3739 | [Count Subarrays With Majority Element II](https://leetcode.com/problems/count-subarrays-with-majority-element-ii/) | Hard | 2090 |
| 98 | 3900 | [Longest Balanced Substring After One Swap](https://leetcode.com/problems/longest-balanced-substring-after-one-swap/) | Medium | 2135 |
| 99 | 1074 | [Number of Submatrices That Sum to Target](https://leetcode.com/problems/number-of-submatrices-that-sum-to-target/) | Hard | 2189 |
| 100 | 1442 | [Count Triplets That Can Form Two Arrays of Equal XOR](https://leetcode.com/problems/count-triplets-that-can-form-two-arrays-of-equal-xor/) | Medium | 1525 |
| 101 | 3714 | [Longest Balanced Substring II](https://leetcode.com/problems/longest-balanced-substring-ii/) | Medium | 2202 |
| 102 | 2025 | [Maximum Number of Ways to Partition an Array](https://leetcode.com/problems/maximum-number-of-ways-to-partition-an-array/) | Hard | 2218 |
| 103 | 3729 | [Count Distinct Subarrays Divisible by K in Sorted Array](https://leetcode.com/problems/count-distinct-subarrays-divisible-by-k-in-sorted-array/) | Hard | 2248 |
| 104 | 2949 | [Count Beautiful Substrings II](https://leetcode.com/problems/count-beautiful-substrings-ii/) | Hard | 2445 |
| 105 | 325 | [Maximum Size Subarray Sum Equals k](https://leetcode.com/problems/maximum-size-subarray-sum-equals-k/) 🔒 | Medium |  |
| 106 | 548 | [Split Array with Equal Sum](https://leetcode.com/problems/split-array-with-equal-sum/) 🔒 | Hard |  |
| 107 | 1983 | [Widest Pair of Indices With Equal Range Sum](https://leetcode.com/problems/widest-pair-of-indices-with-equal-range-sum/) 🔒 | Medium |  |
| 108 | 2489 | [Number of Substrings With Fixed Ratio](https://leetcode.com/problems/number-of-substrings-with-fixed-ratio/) 🔒 | Medium |  |
| 109 | 2031 | [Count Subarrays With More Ones Than Zeros](https://leetcode.com/problems/count-subarrays-with-more-ones-than-zeros/) 🔒 | Medium |  |
| 110 | 2950 | [Number of Divisible Substrings](https://leetcode.com/problems/number-of-divisible-substrings/) 🔒 | Medium |  |
| 111 | 3364 | [Minimum Positive Sum Subarray ](https://leetcode.com/problems/minimum-positive-sum-subarray/) | Easy | 1301 |
| 112 | 363 | [Max Sum of Rectangle No Larger Than K](https://leetcode.com/problems/max-sum-of-rectangle-no-larger-than-k/) | Hard |  |
| 113 | 3739 | [Count Subarrays With Majority Element II](https://leetcode.com/problems/count-subarrays-with-majority-element-ii/) | Hard | 2090 |
| 114 | 2031 | [Count Subarrays With More Ones Than Zeros](https://leetcode.com/problems/count-subarrays-with-more-ones-than-zeros/) 🔒 | Medium |  |
| 115 | 437 | [Path Sum III](https://leetcode.com/problems/path-sum-iii/) | Medium |  |

### §1.3 Sum of Distances

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 116 | 1685 | [Sum of Absolute Differences in a Sorted Array](https://leetcode.com/problems/sum-of-absolute-differences-in-a-sorted-array/) | Medium | 1496 |
| 117 | 2615 | [Sum of Distances](https://leetcode.com/problems/sum-of-distances/) | Medium | 1793 |
| 118 | 2602 | [Minimum Operations to Make All Array Elements Equal](https://leetcode.com/problems/minimum-operations-to-make-all-array-elements-equal/) | Medium | 1903 |
| 119 | 3937 | [Minimum Operations to Make Array Modulo Alternating I](https://leetcode.com/problems/minimum-operations-to-make-array-modulo-alternating-i/) | Medium | 1626 |
| 120 | 2968 | [Apply Operations to Maximize Frequency Score](https://leetcode.com/problems/apply-operations-to-maximize-frequency-score/) | Hard | 2444 |
| 121 | 1703 | [Minimum Adjacent Swaps for K Consecutive Ones](https://leetcode.com/problems/minimum-adjacent-swaps-for-k-consecutive-ones/) | Hard | 2467 |
| 122 | 3086 | [Minimum Moves to Pick K Ones](https://leetcode.com/problems/minimum-moves-to-pick-k-ones/) | Hard | 2673 |
| 123 | 3422 | [Minimum Operations to Make Subarray Elements Equal](https://leetcode.com/problems/minimum-operations-to-make-subarray-elements-equal/) 🔒 | Medium |  |

### §1.4 Bitmask Prefix Sums

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 124 | 1177 | [Can Make Palindrome from Substring](https://leetcode.com/problems/can-make-palindrome-from-substring/) | Medium | 1848 |
| 125 | 1371 | [Find the Longest Substring Containing Vowels in Even Counts](https://leetcode.com/problems/find-the-longest-substring-containing-vowels-in-even-counts/) | Medium | 2041 |
| 126 | 1542 | [Find Longest Awesome Substring](https://leetcode.com/problems/find-longest-awesome-substring/) | Hard | 2222 |
| 127 | 1915 | [Number of Wonderful Substrings](https://leetcode.com/problems/number-of-wonderful-substrings/) | Medium | 2235 |
| 128 | 2791 | [Count Paths That Can Form a Palindrome in a Tree](https://leetcode.com/problems/count-paths-that-can-form-a-palindrome-in-a-tree/) | Hard | 2677 |

### §1.5 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 129 | 2389 | [Longest Subsequence With Limited Sum](https://leetcode.com/problems/longest-subsequence-with-limited-sum/) | Easy | 1388 |
| 130 | 3709 | [Design Exam Scores Tracker](https://leetcode.com/problems/design-exam-scores-tracker/) | Medium | 1648 |
| 131 | 3919 | [Minimum Cost to Move Between Indices](https://leetcode.com/problems/minimum-cost-to-move-between-indices/) | Medium | 1777 |
| 132 | 1895 | [Largest Magic Square](https://leetcode.com/problems/largest-magic-square/) | Medium | 1781 |
| 133 | 2055 | [Plates Between Candles](https://leetcode.com/problems/plates-between-candles/) | Medium | 1819 |
| 134 | 1744 | [Can You Eat Your Favorite Candy on Your Favorite Day?](https://leetcode.com/problems/can-you-eat-your-favorite-candy-on-your-favorite-day/) | Medium | 1859 |
| 135 | 1878 | [Get Biggest Three Rhombus Sums in a Grid](https://leetcode.com/problems/get-biggest-three-rhombus-sums-in-a-grid/) | Medium | 1898 |
| 136 | 3756 | [Concatenate Non-Zero Digits and Multiply by Sum II](https://leetcode.com/problems/concatenate-non-zero-digits-and-multiply-by-sum-ii/) | Medium | 1968 |
| 137 | 1031 | [Maximum Sum of Two Non-Overlapping Subarrays](https://leetcode.com/problems/maximum-sum-of-two-non-overlapping-subarrays/) | Medium | 1680 |
| 138 | 2245 | [Maximum Trailing Zeros in a Cornered Path](https://leetcode.com/problems/maximum-trailing-zeros-in-a-cornered-path/) | Medium | 2037 |
| 139 | 1712 | [Ways to Split Array Into Three Subarrays](https://leetcode.com/problems/ways-to-split-array-into-three-subarrays/) | Medium | 2079 |
| 140 | 1862 | [Sum of Floored Pairs](https://leetcode.com/problems/sum-of-floored-pairs/) | Hard | 2170 |
| 141 | 3748 | [Count Stable Subarrays](https://leetcode.com/problems/count-stable-subarrays/) | Hard | 2209 |
| 142 | 2281 | [Sum of Total Strength of Wizards](https://leetcode.com/problems/sum-of-total-strength-of-wizards/) | Hard | 2621 |
| 143 | 3445 | [Maximum Difference Between Even and Odd Frequency II](https://leetcode.com/problems/maximum-difference-between-even-and-odd-frequency-ii/) | Hard | 2694 |
| 144 | 2983 | [Palindrome Rearrangement Queries](https://leetcode.com/problems/palindrome-rearrangement-queries/) | Hard | 2780 |
| 145 | 2955 | [Number of Same-End Substrings](https://leetcode.com/problems/number-of-same-end-substrings/) 🔒 | Medium |  |
| 146 | 1788 | [Maximize the Beauty of the Garden](https://leetcode.com/problems/maximize-the-beauty-of-the-garden/) 🔒 | Hard |  |
| 147 | 2819 | [Minimum Relative Loss After Buying Chocolates](https://leetcode.com/problems/minimum-relative-loss-after-buying-chocolates/) 🔒 | Hard |  |
| 148 | 2300 | [Successful Pairs of Spells and Potions](https://leetcode.com/problems/successful-pairs-of-spells-and-potions/) | Medium | 1477 |
| 149 | 1534 | [Count Good Triplets](https://leetcode.com/problems/count-good-triplets/) | Easy | 1279 |

### §1.6 2D Prefix Sums

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 150 | 304 | [Range Sum Query 2D - Immutable](https://leetcode.com/problems/range-sum-query-2d-immutable/) | Medium |  |
| 151 | 1314 | [Matrix Block Sum](https://leetcode.com/problems/matrix-block-sum/) | Medium | 1484 |
| 152 | 3070 | [Count Submatrices with Top-Left Element and Sum Less Than k](https://leetcode.com/problems/count-submatrices-with-top-left-element-and-sum-less-than-k/) | Medium | 1499 |
| 153 | 1738 | [Find Kth Largest XOR Coordinate Value](https://leetcode.com/problems/find-kth-largest-xor-coordinate-value/) | Medium | 1671 |
| 154 | 3212 | [Count Submatrices With Equal Frequency of X and Y](https://leetcode.com/problems/count-submatrices-with-equal-frequency-of-x-and-y/) | Medium | 1673 |
| 155 | 1292 | [Maximum Side Length of a Square with Sum Less than or Equal to Threshold](https://leetcode.com/problems/maximum-side-length-of-a-square-with-sum-less-than-or-equal-to-threshold/) | Medium | 1735 |
| 156 | 3148 | [Maximum Difference Score in a Grid](https://leetcode.com/problems/maximum-difference-score-in-a-grid/) | Medium | 1820 |

## 2. Difference Arrays

### §2.1 1D Difference Arrays

#### §2.1.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 157 | 2848 | [Points That Intersect With Cars](https://leetcode.com/problems/points-that-intersect-with-cars/) | Easy | 1230 |
| 158 | 1893 | [Check if All the Integers in a Range Are Covered](https://leetcode.com/problems/check-if-all-the-integers-in-a-range-are-covered/) | Easy | 1307 |
| 159 | 1854 | [Maximum Population Year](https://leetcode.com/problems/maximum-population-year/) | Easy | 1370 |
| 160 | 2960 | [Count Tested Devices After Test Operations](https://leetcode.com/problems/count-tested-devices-after-test-operations/) | Easy | 1169 |
| 161 | 1094 | [Car Pooling](https://leetcode.com/problems/car-pooling/) | Medium | 1441 |
| 162 | 1109 | [Corporate Flight Bookings](https://leetcode.com/problems/corporate-flight-bookings/) | Medium | 1570 |
| 163 | 3355 | [Zero Array Transformation I](https://leetcode.com/problems/zero-array-transformation-i/) | Medium | 1591 |
| 164 | 370 | [Range Addition](https://leetcode.com/problems/range-addition/) 🔒 | Medium |  |

#### §2.1.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 165 | 3914 | [Minimum Operations to Make Array Non Decreasing](https://leetcode.com/problems/minimum-operations-to-make-array-non-decreasing/) | Medium | 1662 |
| 166 | 3453 | [Separate Squares I](https://leetcode.com/problems/separate-squares-i/) | Medium | 1735 |
| 167 | 2381 | [Shifting Letters II](https://leetcode.com/problems/shifting-letters-ii/) | Medium | 1793 |
| 168 | 995 | [Minimum Number of K Consecutive Bit Flips](https://leetcode.com/problems/minimum-number-of-k-consecutive-bit-flips/) | Hard | 1835 |
| 169 | 1589 | [Maximum Sum Obtained of Any Permutation](https://leetcode.com/problems/maximum-sum-obtained-of-any-permutation/) | Medium | 1871 |
| 170 | 1526 | [Minimum Number of Increments on Subarrays to Form a Target Array](https://leetcode.com/problems/minimum-number-of-increments-on-subarrays-to-form-a-target-array/) | Hard | 1872 |
| 171 | 1871 | [Jump Game VII](https://leetcode.com/problems/jump-game-vii/) | Medium | 1896 |
| 172 | 3356 | [Zero Array Transformation II](https://leetcode.com/problems/zero-array-transformation-ii/) | Medium | 1913 |
| 173 | 1943 | [Describe the Painting](https://leetcode.com/problems/describe-the-painting/) | Medium | 1969 |
| 174 | 3224 | [Minimum Array Changes to Make Differences Equal](https://leetcode.com/problems/minimum-array-changes-to-make-differences-equal/) | Medium | 1996 |
| 175 | 2327 | [Number of People Aware of a Secret](https://leetcode.com/problems/number-of-people-aware-of-a-secret/) | Medium | 1894 |
| 176 | 2251 | [Number of Flowers in Full Bloom](https://leetcode.com/problems/number-of-flowers-in-full-bloom/) | Hard | 2022 |
| 177 | 2772 | [Apply Operations to Make All Array Elements Equal to Zero](https://leetcode.com/problems/apply-operations-to-make-all-array-elements-equal-to-zero/) | Medium | 2029 |
| 178 | 3229 | [Minimum Operations to Make Array Equal to Target](https://leetcode.com/problems/minimum-operations-to-make-array-equal-to-target/) | Hard | 2067 |
| 179 | 3529 | [Count Cells in Overlapping Horizontal and Vertical Substrings](https://leetcode.com/problems/count-cells-in-overlapping-horizontal-and-vertical-substrings/) | Medium | 2105 |
| 180 | 798 | [Smallest Rotation with Highest Score](https://leetcode.com/problems/smallest-rotation-with-highest-score/) | Hard | 2130 |
| 181 | 3347 | [Maximum Frequency of an Element After Performing Operations II](https://leetcode.com/problems/maximum-frequency-of-an-element-after-performing-operations-ii/) | Hard | 2156 |
| 182 | 2528 | [Maximize the Minimum Powered City](https://leetcode.com/problems/maximize-the-minimum-powered-city/) | Hard | 2236 |
| 183 | 1674 | [Minimum Moves to Make Array Complementary](https://leetcode.com/problems/minimum-moves-to-make-array-complementary/) | Medium | 2333 |
| 184 | 3362 | [Zero Array Transformation III](https://leetcode.com/problems/zero-array-transformation-iii/) | Medium | 2424 |
| 185 | 3655 | [XOR After Range Multiplication Queries II](https://leetcode.com/problems/xor-after-range-multiplication-queries-ii/) | Hard | 2454 |
| 186 | 3017 | [Count the Number of Houses at a Certain Distance II](https://leetcode.com/problems/count-the-number-of-houses-at-a-certain-distance-ii/) | Hard | 2709 |
| 187 | 2021 | [Brightest Position on Street](https://leetcode.com/problems/brightest-position-on-street/) 🔒 | Medium |  |
| 188 | 2015 | [Average Height of Buildings in Each Segment](https://leetcode.com/problems/average-height-of-buildings-in-each-segment/) 🔒 | Medium |  |
| 189 | 2237 | [Count Positions on Street With Required Brightness](https://leetcode.com/problems/count-positions-on-street-with-required-brightness/) 🔒 | Medium |  |
| 190 | 3009 | [Maximum Number of Intersections on the Chart](https://leetcode.com/problems/maximum-number-of-intersections-on-the-chart/) 🔒 | Hard |  |
| 191 | 3279 | [Maximum Total Area Occupied by Pistons](https://leetcode.com/problems/maximum-total-area-occupied-by-pistons/) 🔒 | Hard |  |
| 192 | 56 | [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Medium |  |
| 193 | 57 | [Insert Interval](https://leetcode.com/problems/insert-interval/) | Medium |  |
| 194 | 732 | [My Calendar III](https://leetcode.com/problems/my-calendar-iii/) | Hard |  |
| 195 | 2406 | [Divide Intervals Into Minimum Number of Groups](https://leetcode.com/problems/divide-intervals-into-minimum-number-of-groups/) | Medium | 1713 |
| 196 | 253 | [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) 🔒 | Medium |  |
| 197 | 759 | [Employee Free Time](https://leetcode.com/problems/employee-free-time/) 🔒 | Hard | 1710 |

### §2.2 2D Difference Arrays

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 198 | 2536 | [Increment Submatrices by One](https://leetcode.com/problems/increment-submatrices-by-one/) | Medium | 1583 |
| 199 | 850 | [Rectangle Area II](https://leetcode.com/problems/rectangle-area-ii/) | Hard | 2236 |
| 200 | 2132 | [Stamping the Grid](https://leetcode.com/problems/stamping-the-grid/) | Hard | 2364 |
| 201 | 3888 | [Minimum Operations to Make All Grid Elements Equal](https://leetcode.com/problems/minimum-operations-to-make-all-grid-elements-equal/) 🔒 | Hard |  |

## 3. Stack

### §3.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 202 | 1441 | [Build an Array With Stack Operations](https://leetcode.com/problems/build-an-array-with-stack-operations/) | Medium | 1180 |
| 203 | 844 | [Backspace String Compare](https://leetcode.com/problems/backspace-string-compare/) | Easy | 1228 |
| 204 | 682 | [Baseball Game](https://leetcode.com/problems/baseball-game/) | Easy |  |
| 205 | 2390 | [Removing Stars From a String](https://leetcode.com/problems/removing-stars-from-a-string/) | Medium | 1348 |
| 206 | 1472 | [Design Browser History](https://leetcode.com/problems/design-browser-history/) | Medium | 1454 |
| 207 | 946 | [Validate Stack Sequences](https://leetcode.com/problems/validate-stack-sequences/) | Medium | 1462 |
| 208 | 3412 | [Find Mirror Score of a String](https://leetcode.com/problems/find-mirror-score-of-a-string/) | Medium | 1578 |
| 209 | 71 | [Simplify Path](https://leetcode.com/problems/simplify-path/) | Medium |  |

### §3.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 210 | 3170 | [Lexicographically Minimum String After Removing Stars](https://leetcode.com/problems/lexicographically-minimum-string-after-removing-stars/) | Medium | 1772 |
| 211 | 155 | [Min Stack](https://leetcode.com/problems/min-stack/) | Medium |  |
| 212 | 1381 | [Design a Stack With Increment Operation](https://leetcode.com/problems/design-a-stack-with-increment-operation/) | Medium | 1286 |
| 213 | 636 | [Exclusive Time of Functions](https://leetcode.com/problems/exclusive-time-of-functions/) | Medium |  |
| 214 | 2434 | [Using a Robot to Print the Lexicographically Smallest String](https://leetcode.com/problems/using-a-robot-to-print-the-lexicographically-smallest-string/) | Medium | 1953 |
| 215 | 895 | [Maximum Frequency Stack](https://leetcode.com/problems/maximum-frequency-stack/) | Hard | 2028 |
| 216 | 1172 | [Dinner Plate Stacks](https://leetcode.com/problems/dinner-plate-stacks/) | Hard | 2110 |
| 217 | 2589 | [Minimum Time to Complete All Tasks](https://leetcode.com/problems/minimum-time-to-complete-all-tasks/) | Hard | 2381 |
| 218 | 2524 | [Maximum Frequency Score of a Subarray](https://leetcode.com/problems/maximum-frequency-score-of-a-subarray/) 🔒 | Hard |  |
| 219 | 716 | [Max Stack](https://leetcode.com/problems/max-stack/) 🔒 | Hard |  |

### §3.3 Adjacent Pair Elimination

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 220 | 2696 | [Minimum String Length After Removing Substrings](https://leetcode.com/problems/minimum-string-length-after-removing-substrings/) | Easy | 1282 |
| 221 | 1047 | [Remove All Adjacent Duplicates In String](https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string/) | Easy | 1286 |
| 222 | 1544 | [Make The String Great](https://leetcode.com/problems/make-the-string-great/) | Easy | 1344 |
| 223 | 3561 | [Resulting String After Adjacent Removals](https://leetcode.com/problems/resulting-string-after-adjacent-removals/) | Medium | 1397 |
| 224 | 1003 | [Check If Word Is Valid After Substitutions](https://leetcode.com/problems/check-if-word-is-valid-after-substitutions/) | Medium | 1427 |
| 225 | 3834 | [Merge Adjacent Equal Elements](https://leetcode.com/problems/merge-adjacent-equal-elements/) | Medium | 1429 |
| 226 | 2216 | [Minimum Deletions to Make Array Beautiful](https://leetcode.com/problems/minimum-deletions-to-make-array-beautiful/) | Medium | 1510 |
| 227 | 1209 | [Remove All Adjacent Duplicates in String II](https://leetcode.com/problems/remove-all-adjacent-duplicates-in-string-ii/) | Medium | 1542 |
| 228 | 3703 | [Remove K-Balanced Substrings](https://leetcode.com/problems/remove-k-balanced-substrings/) | Medium | 1802 |
| 229 | 1717 | [Maximum Score From Removing Substrings](https://leetcode.com/problems/maximum-score-from-removing-substrings/) | Medium | 1868 |
| 230 | 2197 | [Replace Non-Coprime Numbers in Array](https://leetcode.com/problems/replace-non-coprime-numbers-in-array/) | Hard | 2057 |
| 231 | 735 | [Asteroid Collision](https://leetcode.com/problems/asteroid-collision/) | Medium |  |
| 232 | 2751 | [Robot Collisions](https://leetcode.com/problems/robot-collisions/) | Hard | 2092 |

### §3.4 Valid Parenthesis Strings

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 233 | 20 | [Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | Easy |  |
| 234 | 921 | [Minimum Add to Make Parentheses Valid](https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/) | Medium | 1242 |
| 235 | 1021 | [Remove Outermost Parentheses](https://leetcode.com/problems/remove-outermost-parentheses/) | Easy | 1311 |
| 236 | 1614 | [Maximum Nesting Depth of the Parentheses](https://leetcode.com/problems/maximum-nesting-depth-of-the-parentheses/) | Easy | 1323 |
| 237 | 1190 | [Reverse Substrings Between Each Pair of Parentheses](https://leetcode.com/problems/reverse-substrings-between-each-pair-of-parentheses/) | Medium | 1486 |
| 238 | 856 | [Score of Parentheses](https://leetcode.com/problems/score-of-parentheses/) | Medium | 1563 |
| 239 | 1249 | [Minimum Remove to Make Valid Parentheses](https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/) | Medium | 1657 |
| 240 | 1963 | [Minimum Number of Swaps to Make the String Balanced](https://leetcode.com/problems/minimum-number-of-swaps-to-make-the-string-balanced/) | Medium | 1689 |
| 241 | 678 | [Valid Parenthesis String](https://leetcode.com/problems/valid-parenthesis-string/) | Medium |  |
| 242 | 1111 | [Maximum Nesting Depth of Two Valid Parentheses Strings](https://leetcode.com/problems/maximum-nesting-depth-of-two-valid-parentheses-strings/) | Medium | 1749 |
| 243 | 1541 | [Minimum Insertions to Balance a Parentheses String](https://leetcode.com/problems/minimum-insertions-to-balance-a-parentheses-string/) | Medium | 1759 |
| 244 | 2116 | [Check if a Parentheses String Can Be Valid](https://leetcode.com/problems/check-if-a-parentheses-string-can-be-valid/) | Medium | 2038 |
| 245 | 32 | [Longest Valid Parentheses](https://leetcode.com/problems/longest-valid-parentheses/) | Hard |  |

### §3.5 Expression Parsing

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 246 | 1006 | [Clumsy Factorial](https://leetcode.com/problems/clumsy-factorial/) | Medium | 1408 |
| 247 | 150 | [Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | Medium |  |
| 248 | 394 | [Decode String](https://leetcode.com/problems/decode-string/) | Medium |  |
| 249 | 8 | [String to Integer (atoi)](https://leetcode.com/problems/string-to-integer-atoi/) | Medium |  |
| 250 | 224 | [Basic Calculator](https://leetcode.com/problems/basic-calculator/) | Hard |  |
| 251 | 227 | [Basic Calculator II](https://leetcode.com/problems/basic-calculator-ii/) | Medium |  |
| 252 | 726 | [Number of Atoms](https://leetcode.com/problems/number-of-atoms/) | Hard |  |
| 253 | 1106 | [Parsing A Boolean Expression](https://leetcode.com/problems/parsing-a-boolean-expression/) | Hard | 1880 |
| 254 | 591 | [Tag Validator](https://leetcode.com/problems/tag-validator/) | Hard |  |
| 255 | 736 | [Parse Lisp Expression](https://leetcode.com/problems/parse-lisp-expression/) | Hard |  |
| 256 | 1096 | [Brace Expansion II](https://leetcode.com/problems/brace-expansion-ii/) | Hard | 2349 |
| 257 | 1896 | [Minimum Cost to Change the Final Value of Expression](https://leetcode.com/problems/minimum-cost-to-change-the-final-value-of-expression/) | Hard | 2532 |
| 258 | 65 | [Valid Number](https://leetcode.com/problems/valid-number/) | Hard |  |
| 259 | 770 | [Basic Calculator IV](https://leetcode.com/problems/basic-calculator-iv/) | Hard | 2863 |
| 260 | 439 | [Ternary Expression Parser](https://leetcode.com/problems/ternary-expression-parser/) 🔒 | Medium |  |
| 261 | 3749 | [Evaluate Valid Expressions](https://leetcode.com/problems/evaluate-valid-expressions/) 🔒 | Hard |  |
| 262 | 772 | [Basic Calculator III](https://leetcode.com/problems/basic-calculator-iii/) 🔒 | Hard |  |
| 263 | 1087 | [Brace Expansion](https://leetcode.com/problems/brace-expansion/) 🔒 | Medium | 1480 |
| 264 | 1597 | [Build Binary Expression Tree From Infix Expression](https://leetcode.com/problems/build-binary-expression-tree-from-infix-expression/) 🔒 | Hard |  |
| 265 | 1628 | [Design an Expression Tree With Evaluate Function](https://leetcode.com/problems/design-an-expression-tree-with-evaluate-function/) 🔒 | Medium |  |

### §3.6 Two Opposing Stacks

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 266 | 2296 | [Design a Text Editor](https://leetcode.com/problems/design-a-text-editor/) | Hard | 1912 |

## 4. Queue

### §4.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 267 | 933 | [Number of Recent Calls](https://leetcode.com/problems/number-of-recent-calls/) | Easy | 1338 |
| 268 | 3829 | [Design Ride Sharing System](https://leetcode.com/problems/design-ride-sharing-system/) | Medium | 1594 |
| 269 | 950 | [Reveal Cards In Increasing Order](https://leetcode.com/problems/reveal-cards-in-increasing-order/) | Medium | 1686 |
| 270 | 649 | [Dota2 Senate](https://leetcode.com/problems/dota2-senate/) | Medium |  |
| 271 | 346 | [Moving Average from Data Stream](https://leetcode.com/problems/moving-average-from-data-stream/) 🔒 | Easy |  |
| 272 | 362 | [Design Hit Counter](https://leetcode.com/problems/design-hit-counter/) 🔒 | Medium |  |
| 273 | 3851 | [Maximum Requests Without Violating the Limit](https://leetcode.com/problems/maximum-requests-without-violating-the-limit/) 🔒 | Medium |  |
| 274 | 379 | [Design Phone Directory](https://leetcode.com/problems/design-phone-directory/) 🔒 | Medium |  |
| 275 | 1429 | [First Unique Number](https://leetcode.com/problems/first-unique-number/) 🔒 | Medium |  |
| 276 | 2534 | [Time Taken to Cross the Door](https://leetcode.com/problems/time-taken-to-cross-the-door/) 🔒 | Hard |  |

### §4.2 Design

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 277 | 1670 | [Design Front Middle Back Queue](https://leetcode.com/problems/design-front-middle-back-queue/) | Medium | 1610 |
| 278 | 3508 | [Implement Router](https://leetcode.com/problems/implement-router/) | Medium | 1851 |
| 279 | 225 | [Implement Stack using Queues](https://leetcode.com/problems/implement-stack-using-queues/) | Easy |  |
| 280 | 232 | [Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | Easy |  |
| 281 | 622 | [Design Circular Queue](https://leetcode.com/problems/design-circular-queue/) | Medium |  |
| 282 | 641 | [Design Circular Deque](https://leetcode.com/problems/design-circular-deque/) | Medium |  |

### §4.3 Deque

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 283 | 2810 | [Faulty Keyboard](https://leetcode.com/problems/faulty-keyboard/) | Easy | 1193 |
| 284 | 2071 | [Maximum Number of Tasks You Can Assign](https://leetcode.com/problems/maximum-number-of-tasks-you-can-assign/) | Hard | 2648 |

### §4.4 Monotonic Queue

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 285 | 239 | [Sliding Window Maximum](https://leetcode.com/problems/sliding-window-maximum/) | Hard |  |
| 286 | 1438 | [Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit](https://leetcode.com/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/) | Medium | 1672 |
| 287 | 2762 | [Continuous Subarrays](https://leetcode.com/problems/continuous-subarrays/) | Medium | 1940 |
| 288 | 3835 | [Count Subarrays With Cost Less Than or Equal to K](https://leetcode.com/problems/count-subarrays-with-cost-less-than-or-equal-to-k/) | Medium | 1759 |
| 289 | 2398 | [Maximum Number of Robots Within Budget](https://leetcode.com/problems/maximum-number-of-robots-within-budget/) | Hard | 1917 |
| 290 | 3589 | [Count Prime-Gap Balanced Subarrays](https://leetcode.com/problems/count-prime-gap-balanced-subarrays/) | Medium | 2235 |
| 291 | 862 | [Shortest Subarray with Sum at Least K](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) | Hard | 2307 |
| 292 | 1499 | [Max Value of Equation](https://leetcode.com/problems/max-value-of-equation/) | Hard | 2456 |

## 5. Heap (Priority Queue)

### §5.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 293 | 1046 | [Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) | Easy | 1173 |
| 294 | 3264 | [Final Array State After K Multiplication Operations I](https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-i/) | Easy | 1178 |
| 295 | 2558 | [Take Gifts From the Richest Pile](https://leetcode.com/problems/take-gifts-from-the-richest-pile/) | Easy | 1277 |
| 296 | 2336 | [Smallest Number in Infinite Set](https://leetcode.com/problems/smallest-number-in-infinite-set/) | Medium | 1375 |
| 297 | 2530 | [Maximal Score After Applying K Operations](https://leetcode.com/problems/maximal-score-after-applying-k-operations/) | Medium | 1386 |
| 298 | 3066 | [Minimum Operations to Exceed Threshold Value II](https://leetcode.com/problems/minimum-operations-to-exceed-threshold-value-ii/) | Medium | 1400 |
| 299 | 1962 | [Remove Stones to Minimize the Total](https://leetcode.com/problems/remove-stones-to-minimize-the-total/) | Medium | 1419 |
| 300 | 703 | [Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Easy |  |
| 301 | 3275 | [K-th Nearest Obstacle Queries](https://leetcode.com/problems/k-th-nearest-obstacle-queries/) | Medium | 1420 |
| 302 | 1845 | [Seat Reservation Manager](https://leetcode.com/problems/seat-reservation-manager/) | Medium | 1429 |
| 303 | 2208 | [Minimum Operations to Halve Array Sum](https://leetcode.com/problems/minimum-operations-to-halve-array-sum/) | Medium | 1550 |
| 304 | 2233 | [Maximum Product After K Increments](https://leetcode.com/problems/maximum-product-after-k-increments/) | Medium | 1686 |
| 305 | 3296 | [Minimum Number of Seconds to Make Mountain Height Zero](https://leetcode.com/problems/minimum-number-of-seconds-to-make-mountain-height-zero/) | Medium | 1695 |
| 306 | 1942 | [The Number of the Smallest Unoccupied Chair](https://leetcode.com/problems/the-number-of-the-smallest-unoccupied-chair/) | Medium | 1695 |
| 307 | 1801 | [Number of Orders in the Backlog](https://leetcode.com/problems/number-of-orders-in-the-backlog/) | Medium | 1711 |
| 308 | 2406 | [Divide Intervals Into Minimum Number of Groups](https://leetcode.com/problems/divide-intervals-into-minimum-number-of-groups/) | Medium | 1713 |
| 309 | 3478 | [Choose K Elements With Maximum Sum](https://leetcode.com/problems/choose-k-elements-with-maximum-sum/) | Medium | 1753 |
| 310 | 2462 | [Total Cost to Hire K Workers](https://leetcode.com/problems/total-cost-to-hire-k-workers/) | Medium | 1764 |
| 311 | 1834 | [Single-Threaded CPU](https://leetcode.com/problems/single-threaded-cpu/) | Medium | 1798 |
| 312 | 1792 | [Maximum Average Pass Ratio](https://leetcode.com/problems/maximum-average-pass-ratio/) | Medium | 1818 |
| 313 | 1167 | [Minimum Cost to Connect Sticks](https://leetcode.com/problems/minimum-cost-to-connect-sticks/) 🔒 | Medium | 1482 |
| 314 | 253 | [Meeting Rooms II](https://leetcode.com/problems/meeting-rooms-ii/) 🔒 | Medium |  |

### §5.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 315 | 23 | [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | Hard |  |
| 316 | 2931 | [Maximum Spending After Buying Items](https://leetcode.com/problems/maximum-spending-after-buying-items/) | Hard | 1822 |
| 317 | 3781 | [Maximum Score After Binary Swaps](https://leetcode.com/problems/maximum-score-after-binary-swaps/) | Medium | 1823 |
| 318 | 502 | [IPO](https://leetcode.com/problems/ipo/) | Hard |  |
| 319 | 1705 | [Maximum Number of Eaten Apples](https://leetcode.com/problems/maximum-number-of-eaten-apples/) | Medium | 1930 |
| 320 | 778 | [Swim in Rising Water](https://leetcode.com/problems/swim-in-rising-water/) | Hard | 2097 |
| 321 | 1631 | [Path With Minimum Effort](https://leetcode.com/problems/path-with-minimum-effort/) | Medium | 1948 |
| 322 | 1882 | [Process Tasks Using Servers](https://leetcode.com/problems/process-tasks-using-servers/) | Medium | 1979 |
| 323 | 1354 | [Construct Target Array With Multiple Sums](https://leetcode.com/problems/construct-target-array-with-multiple-sums/) | Hard | 2015 |
| 324 | 1353 | [Maximum Number of Events That Can Be Attended](https://leetcode.com/problems/maximum-number-of-events-that-can-be-attended/) | Medium | 2016 |
| 325 | 1235 | [Maximum Profit in Job Scheduling](https://leetcode.com/problems/maximum-profit-in-job-scheduling/) | Hard | 2023 |
| 326 | 632 | [Smallest Range Covering Elements from K Lists](https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/) | Hard |  |
| 327 | 2542 | [Maximum Subsequence Score](https://leetcode.com/problems/maximum-subsequence-score/) | Medium | 2056 |
| 328 | 1383 | [Maximum Performance of a Team](https://leetcode.com/problems/maximum-performance-of-a-team/) | Hard | 2091 |
| 329 | 2402 | [Meeting Rooms III](https://leetcode.com/problems/meeting-rooms-iii/) | Hard | 2093 |
| 330 | 2503 | [Maximum Number of Points From Grid Queries](https://leetcode.com/problems/maximum-number-of-points-from-grid-queries/) | Hard | 2196 |
| 331 | 2163 | [Minimum Difference in Sums After Removal of Elements](https://leetcode.com/problems/minimum-difference-in-sums-after-removal-of-elements/) | Hard | 2225 |
| 332 | 857 | [Minimum Cost to Hire K Workers](https://leetcode.com/problems/minimum-cost-to-hire-k-workers/) | Hard | 2260 |
| 333 | 1606 | [Find Servers That Handled Most Number of Requests](https://leetcode.com/problems/find-servers-that-handled-most-number-of-requests/) | Hard | 2276 |
| 334 | 1851 | [Minimum Interval to Include Each Query](https://leetcode.com/problems/minimum-interval-to-include-each-query/) | Hard | 2286 |
| 335 | 407 | [Trapping Rain Water II](https://leetcode.com/problems/trapping-rain-water-ii/) | Hard |  |
| 336 | 2940 | [Find Building Where Alice and Bob Can Meet](https://leetcode.com/problems/find-building-where-alice-and-bob-can-meet/) | Hard | 2327 |
| 337 | 3399 | [Smallest Substring With Identical Characters II](https://leetcode.com/problems/smallest-substring-with-identical-characters-ii/) | Hard | 2376 |
| 338 | 3266 | [Final Array State After K Multiplication Operations II](https://leetcode.com/problems/final-array-state-after-k-multiplication-operations-ii/) | Hard | 2509 |
| 339 | 1675 | [Minimize Deviation in Array](https://leetcode.com/problems/minimize-deviation-in-array/) | Hard | 2533 |
| 340 | 2617 | [Minimum Number of Visited Cells in a Grid](https://leetcode.com/problems/minimum-number-of-visited-cells-in-a-grid/) | Hard | 2582 |
| 341 | 2532 | [Time to Cross a Bridge](https://leetcode.com/problems/time-to-cross-a-bridge/) | Hard | 2589 |
| 342 | 1500 | [Design a File Sharing System](https://leetcode.com/problems/design-a-file-sharing-system/) 🔒 | Medium |  |
| 343 | 1199 | [Minimum Time to Build Blocks](https://leetcode.com/problems/minimum-time-to-build-blocks/) 🔒 | Hard | 2250 |
| 344 | 3506 | [Find Time Required to Eliminate Bacterial Strains](https://leetcode.com/problems/find-time-required-to-eliminate-bacterial-strains/) 🔒 | Hard |  |
| 345 | 1348 | [Tweet Counts Per Frequency](https://leetcode.com/problems/tweet-counts-per-frequency/) | Medium | 2037 |
| 346 | 855 | [Exam Room](https://leetcode.com/problems/exam-room/) | Medium | 2067 |
| 347 | 1912 | [Design Movie Rental System](https://leetcode.com/problems/design-movie-rental-system/) | Hard | 2182 |

### §5.3 K-th Smallest / Largest

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 348 | 264 | [Ugly Number II](https://leetcode.com/problems/ugly-number-ii/) | Medium |  |
| 349 | 378 | [Kth Smallest Element in a Sorted Matrix](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/) | Medium |  |
| 350 | 23 | [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | Hard |  |
| 351 | 373 | [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) | Medium |  |
| 352 | 1439 | [Find the Kth Smallest Sum of a Matrix With Sorted Rows](https://leetcode.com/problems/find-the-kth-smallest-sum-of-a-matrix-with-sorted-rows/) | Hard | 2134 |
| 353 | 786 | [K-th Smallest Prime Fraction](https://leetcode.com/problems/k-th-smallest-prime-fraction/) | Medium | 2169 |
| 354 | 3691 | [Maximum Total Subarray Value II](https://leetcode.com/problems/maximum-total-subarray-value-ii/) | Hard | 2469 |
| 355 | 2386 | [Find the K-Sum of an Array](https://leetcode.com/problems/find-the-k-sum-of-an-array/) | Hard | 2648 |

### §5.4 Rearranging Elements

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 356 | 984 | [String Without AAA or BBB](https://leetcode.com/problems/string-without-aaa-or-bbb/) | Medium | 1474 |
| 357 | 767 | [Reorganize String](https://leetcode.com/problems/reorganize-string/) | Medium | 1681 |
| 358 | 1054 | [Distant Barcodes](https://leetcode.com/problems/distant-barcodes/) | Medium | 1702 |
| 359 | 1405 | [Longest Happy String](https://leetcode.com/problems/longest-happy-string/) | Medium | 1821 |
| 360 | 3081 | [Replace Question Marks in String to Minimize Its Value](https://leetcode.com/problems/replace-question-marks-in-string-to-minimize-its-value/) | Medium | 1905 |
| 361 | 621 | [Task Scheduler](https://leetcode.com/problems/task-scheduler/) | Medium |  |
| 362 | 358 | [Rearrange String k Distance Apart](https://leetcode.com/problems/rearrange-string-k-distance-apart/) 🔒 | Hard |  |

### §5.5 Regret Heap (Greedy with Undo)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 363 | 1642 | [Furthest Building You Can Reach](https://leetcode.com/problems/furthest-building-you-can-reach/) | Medium | 1962 |
| 364 | 630 | [Course Schedule III](https://leetcode.com/problems/course-schedule-iii/) | Hard |  |
| 365 | 871 | [Minimum Number of Refueling Stops](https://leetcode.com/problems/minimum-number-of-refueling-stops/) | Hard | 2074 |
| 366 | 3362 | [Zero Array Transformation III](https://leetcode.com/problems/zero-array-transformation-iii/) | Medium | 2424 |
| 367 | 2813 | [Maximum Elegance of a K-Length Subsequence](https://leetcode.com/problems/maximum-elegance-of-a-k-length-subsequence/) | Hard | 2582 |
| 368 | 1388 | [Pizza With 3n Slices](https://leetcode.com/problems/pizza-with-3n-slices/) | Hard | 2410 |
| 369 | 3892 | [Minimum Operations to Achieve At Least K Peaks](https://leetcode.com/problems/minimum-operations-to-achieve-at-least-k-peaks/) | Hard | 2280 |
| 370 | 3049 | [Earliest Second to Mark Indices II](https://leetcode.com/problems/earliest-second-to-mark-indices-ii/) | Hard | 3111 |
| 371 | 3711 | [Maximum Transactions Without Negative Balance](https://leetcode.com/problems/maximum-transactions-without-negative-balance/) 🔒 | Medium |  |
| 372 | 2599 | [Make the Prefix Sum Non-negative](https://leetcode.com/problems/make-the-prefix-sum-non-negative/) 🔒 | Medium |  |

### §5.6 Lazy-Deletion Heap

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 373 | 2349 | [Design a Number Container System](https://leetcode.com/problems/design-a-number-container-system/) | Medium | 1540 |
| 374 | 3885 | [Design Event Manager](https://leetcode.com/problems/design-event-manager/) | Medium | 1548 |
| 375 | 3607 | [Power Grid Maintenance](https://leetcode.com/problems/power-grid-maintenance/) | Medium | 1700 |
| 376 | 2353 | [Design a Food Rating System](https://leetcode.com/problems/design-a-food-rating-system/) | Medium | 1782 |
| 377 | 3092 | [Most Frequent IDs](https://leetcode.com/problems/most-frequent-ids/) | Medium | 1793 |
| 378 | 3408 | [Design Task Manager](https://leetcode.com/problems/design-task-manager/) | Medium | 1807 |
| 379 | 2034 | [Stock Price Fluctuation ](https://leetcode.com/problems/stock-price-fluctuation/) | Medium | 1832 |
| 380 | 3815 | [Design Auction System](https://leetcode.com/problems/design-auction-system/) | Medium | 1854 |
| 381 | 1172 | [Dinner Plate Stacks](https://leetcode.com/problems/dinner-plate-stacks/) | Hard | 2110 |
| 382 | 218 | [The Skyline Problem](https://leetcode.com/problems/the-skyline-problem/) | Hard |  |
| 383 | 3510 | [Minimum Pair Removal to Sort Array II](https://leetcode.com/problems/minimum-pair-removal-to-sort-array-ii/) | Hard | 2608 |
| 384 | 3672 | [Sum of Weighted Modes in Subarrays](https://leetcode.com/problems/sum-of-weighted-modes-in-subarrays/) 🔒 | Medium |  |
| 385 | 3391 | [Design a 3D Binary Matrix with Efficient Layer Tracking](https://leetcode.com/problems/design-a-3d-binary-matrix-with-efficient-layer-tracking/) 🔒 | Medium |  |
| 386 | 716 | [Max Stack](https://leetcode.com/problems/max-stack/) 🔒 | Hard |  |

### §5.7 Two Heaps (Sliding-Window Median)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 387 | 2102 | [Sequentially Ordinal Rank Tracker](https://leetcode.com/problems/sequentially-ordinal-rank-tracker/) | Hard | 2159 |
| 388 | 295 | [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | Hard |  |
| 389 | 480 | [Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) | Hard |  |
| 390 | 2653 | [Sliding Subarray Beauty](https://leetcode.com/problems/sliding-subarray-beauty/) | Medium | 1786 |
| 391 | 1825 | [Finding MK Average](https://leetcode.com/problems/finding-mk-average/) | Hard | 2396 |
| 392 | 3505 | [Minimum Operations to Make Elements Within K Subarrays Equal](https://leetcode.com/problems/minimum-operations-to-make-elements-within-k-subarrays-equal/) | Hard | 2539 |
| 393 | 3013 | [Divide an Array Into Subarrays With Minimum Cost II](https://leetcode.com/problems/divide-an-array-into-subarrays-with-minimum-cost-ii/) | Hard | 2540 |
| 394 | 3321 | [Find X-Sum of All K-Long Subarrays II](https://leetcode.com/problems/find-x-sum-of-all-k-long-subarrays-ii/) | Hard | 2598 |
| 395 | 3369 | [Design an Array Statistics Tracker ](https://leetcode.com/problems/design-an-array-statistics-tracker/) 🔒 | Hard |  |
| 396 | 3422 | [Minimum Operations to Make Subarray Elements Equal](https://leetcode.com/problems/minimum-operations-to-make-subarray-elements-equal/) 🔒 | Medium |  |

## 6. Trie

### §6.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 397 | 208 | [Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | Medium |  |
| 398 | 3597 | [Partition String ](https://leetcode.com/problems/partition-string/) | Medium | 1347 |
| 399 | 3043 | [Find the Length of the Longest Common Prefix](https://leetcode.com/problems/find-the-length-of-the-longest-common-prefix/) | Medium | 1689 |
| 400 | 648 | [Replace Words](https://leetcode.com/problems/replace-words/) | Medium |  |
| 401 | 720 | [Longest Word in Dictionary](https://leetcode.com/problems/longest-word-in-dictionary/) | Medium |  |
| 402 | 2416 | [Sum of Prefix Scores of Strings](https://leetcode.com/problems/sum-of-prefix-scores-of-strings/) | Hard | 1725 |
| 403 | 677 | [Map Sum Pairs](https://leetcode.com/problems/map-sum-pairs/) | Medium |  |
| 404 | 1268 | [Search Suggestions System](https://leetcode.com/problems/search-suggestions-system/) | Medium | 1573 |
| 405 | 1233 | [Remove Sub-Folders from the Filesystem](https://leetcode.com/problems/remove-sub-folders-from-the-filesystem/) | Medium | 1545 |
| 406 | 820 | [Short Encoding of Words](https://leetcode.com/problems/short-encoding-of-words/) | Medium | 1632 |
| 407 | 2261 | [K Divisible Elements Subarrays](https://leetcode.com/problems/k-divisible-elements-subarrays/) | Medium | 1724 |
| 408 | 1804 | [Implement Trie II (Prefix Tree)](https://leetcode.com/problems/implement-trie-ii-prefix-tree/) 🔒 | Medium |  |
| 409 | 2168 | [Unique Substrings With Equal Digit Frequency](https://leetcode.com/problems/unique-substrings-with-equal-digit-frequency/) 🔒 | Medium |  |

### §6.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 410 | 211 | [Design Add and Search Words Data Structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | Medium |  |
| 411 | 676 | [Implement Magic Dictionary](https://leetcode.com/problems/implement-magic-dictionary/) | Medium |  |
| 412 | 212 | [Word Search II](https://leetcode.com/problems/word-search-ii/) | Hard |  |
| 413 | 3093 | [Longest Common Suffix Queries](https://leetcode.com/problems/longest-common-suffix-queries/) | Hard | 2118 |
| 414 | 745 | [Prefix and Suffix Search](https://leetcode.com/problems/prefix-and-suffix-search/) | Hard |  |
| 415 | 3045 | [Count Prefix and Suffix Pairs II](https://leetcode.com/problems/count-prefix-and-suffix-pairs-ii/) | Hard | 2328 |
| 416 | 336 | [Palindrome Pairs](https://leetcode.com/problems/palindrome-pairs/) | Hard |  |
| 417 | 1948 | [Delete Duplicate Folders in System](https://leetcode.com/problems/delete-duplicate-folders-in-system/) | Hard | 2534 |
| 418 | 425 | [Word Squares](https://leetcode.com/problems/word-squares/) 🔒 | Hard |  |
| 419 | 527 | [Word Abbreviation](https://leetcode.com/problems/word-abbreviation/) 🔒 | Hard |  |
| 420 | 588 | [Design In-Memory File System](https://leetcode.com/problems/design-in-memory-file-system/) 🔒 | Hard |  |
| 421 | 616 | [Add Bold Tag in String](https://leetcode.com/problems/add-bold-tag-in-string/) 🔒 | Medium |  |
| 422 | 758 | [Bold Words in String](https://leetcode.com/problems/bold-words-in-string/) 🔒 | Medium | 1547 |
| 423 | 642 | [Design Search Autocomplete System](https://leetcode.com/problems/design-search-autocomplete-system/) 🔒 | Hard |  |
| 424 | 1065 | [Index Pairs of a String](https://leetcode.com/problems/index-pairs-of-a-string/) 🔒 | Easy | 1389 |
| 425 | 1166 | [Design File System](https://leetcode.com/problems/design-file-system/) 🔒 | Medium | 1479 |
| 426 | 1858 | [Longest Word With All Prefixes](https://leetcode.com/problems/longest-word-with-all-prefixes/) 🔒 | Medium |  |
| 427 | 440 | [K-th Smallest in Lexicographical Order](https://leetcode.com/problems/k-th-smallest-in-lexicographical-order/) | Hard |  |

### §6.4 0-1 Trie (XOR Trie)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 428 | 421 | [Maximum XOR of Two Numbers in an Array](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/) | Medium |  |
| 429 | 2935 | [Maximum Strong Pair XOR II](https://leetcode.com/problems/maximum-strong-pair-xor-ii/) | Hard | 2349 |
| 430 | 3845 | [Maximum Subarray XOR with Bounded Range](https://leetcode.com/problems/maximum-subarray-xor-with-bounded-range/) | Hard | 2347 |
| 431 | 1707 | [Maximum XOR With an Element From Array](https://leetcode.com/problems/maximum-xor-with-an-element-from-array/) | Hard | 2359 |
| 432 | 1803 | [Count Pairs With XOR in a Range](https://leetcode.com/problems/count-pairs-with-xor-in-a-range/) | Hard | 2479 |
| 433 | 1938 | [Maximum Genetic Difference Query](https://leetcode.com/problems/maximum-genetic-difference-query/) | Hard | 2503 |
| 434 | 3632 | [Subarrays with XOR at Least K](https://leetcode.com/problems/subarrays-with-xor-at-least-k/) 🔒 | Hard |  |
| 435 | 2479 | [Maximum XOR of Two Non-Overlapping Subtrees](https://leetcode.com/problems/maximum-xor-of-two-non-overlapping-subtrees/) 🔒 | Hard |  |

## 7. Union-Find (DSU)

### §7.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 436 | 684 | [Redundant Connection](https://leetcode.com/problems/redundant-connection/) | Medium |  |
| 437 | 3493 | [Properties Graph](https://leetcode.com/problems/properties-graph/) | Medium | 1565 |
| 438 | 990 | [Satisfiability of Equality Equations](https://leetcode.com/problems/satisfiability-of-equality-equations/) | Medium | 1638 |
| 439 | 721 | [Accounts Merge](https://leetcode.com/problems/accounts-merge/) | Medium |  |
| 440 | 3532 | [Path Existence Queries in a Graph I](https://leetcode.com/problems/path-existence-queries-in-a-graph-i/) | Medium | 1659 |
| 441 | 737 | [Sentence Similarity II](https://leetcode.com/problems/sentence-similarity-ii/) 🔒 | Medium |  |
| 442 | 1101 | [The Earliest Moment When Everyone Become Friends](https://leetcode.com/problems/the-earliest-moment-when-everyone-become-friends/) 🔒 | Medium | 1558 |
| 443 | 1258 | [Synonymous Sentences](https://leetcode.com/problems/synonymous-sentences/) 🔒 | Medium | 1847 |

### §7.2 Advanced

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 444 | 3551 | [Minimum Swaps to Sort by Digit Sum](https://leetcode.com/problems/minimum-swaps-to-sort-by-digit-sum/) | Medium | 1507 |
| 445 | 2471 | [Minimum Number of Operations to Sort a Binary Tree by Level](https://leetcode.com/problems/minimum-number-of-operations-to-sort-a-binary-tree-by-level/) | Medium | 1635 |
| 446 | 1202 | [Smallest String With Swaps](https://leetcode.com/problems/smallest-string-with-swaps/) | Medium | 1855 |
| 447 | 1061 | [Lexicographically Smallest Equivalent String](https://leetcode.com/problems/lexicographically-smallest-equivalent-string/) | Medium |  |
| 448 | 1722 | [Minimize Hamming Distance After Swap Operations](https://leetcode.com/problems/minimize-hamming-distance-after-swap-operations/) | Medium | 1892 |
| 449 | 3608 | [Minimum Time for K Connected Components](https://leetcode.com/problems/minimum-time-for-k-connected-components/) | Medium | 1893 |
| 450 | 3613 | [Minimize Maximum Component Cost](https://leetcode.com/problems/minimize-maximum-component-cost/) | Medium | 1642 |
| 451 | 778 | [Swim in Rising Water](https://leetcode.com/problems/swim-in-rising-water/) | Hard | 2097 |
| 452 | 3695 | [Maximize Alternating Sum Using Swaps](https://leetcode.com/problems/maximize-alternating-sum-using-swaps/) | Hard | 1984 |
| 453 | 765 | [Couples Holding Hands](https://leetcode.com/problems/couples-holding-hands/) | Hard | 1999 |
| 454 | 2092 | [Find All People With Secret](https://leetcode.com/problems/find-all-people-with-secret/) | Hard | 2004 |
| 455 | 839 | [Similar String Groups](https://leetcode.com/problems/similar-string-groups/) | Hard | 2054 |
| 456 | 685 | [Redundant Connection II](https://leetcode.com/problems/redundant-connection-ii/) | Hard |  |
| 457 | 1970 | [Last Day Where You Can Still Cross](https://leetcode.com/problems/last-day-where-you-can-still-cross/) | Hard | 2124 |
| 458 | 2076 | [Process Restricted Friend Requests](https://leetcode.com/problems/process-restricted-friend-requests/) | Hard | 2131 |
| 459 | 1579 | [Remove Max Number of Edges to Keep Graph Fully Traversable](https://leetcode.com/problems/remove-max-number-of-edges-to-keep-graph-fully-traversable/) | Hard | 2132 |
| 460 | 959 | [Regions Cut By Slashes](https://leetcode.com/problems/regions-cut-by-slashes/) | Medium | 2136 |
| 461 | 2812 | [Find the Safest Path in a Grid](https://leetcode.com/problems/find-the-safest-path-in-a-grid/) | Medium | 2154 |
| 462 | 2503 | [Maximum Number of Points From Grid Queries](https://leetcode.com/problems/maximum-number-of-points-from-grid-queries/) | Hard | 2196 |
| 463 | 3600 | [Maximize Spanning Tree Stability with Upgrades](https://leetcode.com/problems/maximize-spanning-tree-stability-with-upgrades/) | Hard | 2301 |
| 464 | 2867 | [Count Valid Paths in a Tree](https://leetcode.com/problems/count-valid-paths-in-a-tree/) | Hard | 2428 |
| 465 | 2421 | [Number of Good Paths](https://leetcode.com/problems/number-of-good-paths/) | Hard | 2445 |
| 466 | 2157 | [Groups of Strings](https://leetcode.com/problems/groups-of-strings/) | Hard | 2499 |
| 467 | 803 | [Bricks Falling When Hit](https://leetcode.com/problems/bricks-falling-when-hit/) | Hard | 2765 |
| 468 | 3235 | [Check if the Rectangle Corner Is Reachable](https://leetcode.com/problems/check-if-the-rectangle-corner-is-reachable/) | Hard | 3774 |
| 469 | 2459 | [Sort Array by Moving Items to Empty Space](https://leetcode.com/problems/sort-array-by-moving-items-to-empty-space/) 🔒 | Hard |  |

## 8. Fenwick Tree (BIT) and Segment Tree

### §8.1 Fenwick Tree (BIT)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 470 | 307 | [Range Sum Query - Mutable](https://leetcode.com/problems/range-sum-query-mutable/) | Medium |  |
| 471 | 3072 | [Distribute Elements Into Two Arrays II](https://leetcode.com/problems/distribute-elements-into-two-arrays-ii/) | Hard | 2053 |
| 472 | 3624 | [Number of Integers With Popcount-Depth Equal to K II](https://leetcode.com/problems/number-of-integers-with-popcount-depth-equal-to-k-ii/) | Hard | 2086 |
| 473 | 3187 | [Peaks in Array](https://leetcode.com/problems/peaks-in-array/) | Hard | 2154 |
| 474 | 3777 | [Minimum Deletions to Make Alternating Substring](https://leetcode.com/problems/minimum-deletions-to-make-alternating-substring/) | Hard | 2202 |
| 475 | 1649 | [Create Sorted Array through Instructions](https://leetcode.com/problems/create-sorted-array-through-instructions/) | Hard | 2208 |
| 476 | 1626 | [Best Team With No Conflicts](https://leetcode.com/problems/best-team-with-no-conflicts/) | Medium | 2027 |
| 477 | 1409 | [Queries on a Permutation With Key](https://leetcode.com/problems/queries-on-a-permutation-with-key/) | Medium | 1335 |
| 478 | 2250 | [Count Number of Rectangles Containing Each Point](https://leetcode.com/problems/count-number-of-rectangles-containing-each-point/) | Medium | 1998 |
| 479 | 2179 | [Count Good Triplets in an Array](https://leetcode.com/problems/count-good-triplets-in-an-array/) | Hard | 2272 |
| 480 | 1395 | [Count Number of Teams](https://leetcode.com/problems/count-number-of-teams/) | Medium | 1344 |
| 481 | 2659 | [Make Array Empty](https://leetcode.com/problems/make-array-empty/) | Hard | 2282 |
| 482 | 3915 | [Maximum Sum of Alternating Subsequence With Distance at Least K](https://leetcode.com/problems/maximum-sum-of-alternating-subsequence-with-distance-at-least-k/) | Hard | 2288 |
| 483 | 2653 | [Sliding Subarray Beauty](https://leetcode.com/problems/sliding-subarray-beauty/) | Medium | 1786 |
| 484 | 3515 | [Shortest Path in a Weighted Tree](https://leetcode.com/problems/shortest-path-in-a-weighted-tree/) | Hard | 2312 |
| 485 | 1505 | [Minimum Possible Integer After at Most K Adjacent Swaps On Digits](https://leetcode.com/problems/minimum-possible-integer-after-at-most-k-adjacent-swaps-on-digits/) | Hard | 2337 |
| 486 | 3841 | [Palindromic Path Queries in a Tree](https://leetcode.com/problems/palindromic-path-queries-in-a-tree/) | Hard | 2384 |
| 487 | 2926 | [Maximum Balanced Subsequence Sum](https://leetcode.com/problems/maximum-balanced-subsequence-sum/) | Hard | 2448 |
| 488 | 2736 | [Maximum Sum Queries](https://leetcode.com/problems/maximum-sum-queries/) | Hard | 2533 |
| 489 | 3671 | [Sum of Beautiful Subsequences](https://leetcode.com/problems/sum-of-beautiful-subsequences/) | Hard | 2647 |
| 490 | 3382 | [Maximum Area Rectangle With Point Constraints II](https://leetcode.com/problems/maximum-area-rectangle-with-point-constraints-ii/) | Hard | 2723 |
| 491 | 3590 | [Kth Smallest Path XOR Sum](https://leetcode.com/problems/kth-smallest-path-xor-sum/) | Hard | 2646 |
| 492 | 3245 | [Alternating Groups III](https://leetcode.com/problems/alternating-groups-iii/) | Hard | 3112 |
| 493 | 3027 | [Find the Number of Ways to Place People II](https://leetcode.com/problems/find-the-number-of-ways-to-place-people-ii/) | Hard | 2020 |
| 494 | 1756 | [Design Most Recently Used Queue](https://leetcode.com/problems/design-most-recently-used-queue/) 🔒 | Medium |  |
| 495 | 60 | [Permutation Sequence](https://leetcode.com/problems/permutation-sequence/) | Hard |  |
| 496 | 3109 | [Find the Index of Permutation](https://leetcode.com/problems/find-the-index-of-permutation/) 🔒 | Medium |  |
| 497 | 2519 | [Count the Number of K-Big Indices](https://leetcode.com/problems/count-the-number-of-k-big-indices/) 🔒 | Hard |  |
| 498 | 2613 | [Beautiful Pairs](https://leetcode.com/problems/beautiful-pairs/) 🔒 | Hard |  |
| 499 | 2921 | [Maximum Profitable Triplets With Increasing Prices II](https://leetcode.com/problems/maximum-profitable-triplets-with-increasing-prices-ii/) 🔒 | Hard |  |
| 500 | 308 | [Range Sum Query 2D - Mutable](https://leetcode.com/problems/range-sum-query-2d-mutable/) 🔒 | Medium |  |

### §8.2 Counting Inversions

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 501 | 315 | [Count of Smaller Numbers After Self](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | Hard |  |
| 502 | 493 | [Reverse Pairs](https://leetcode.com/problems/reverse-pairs/) | Hard |  |
| 503 | 327 | [Count of Range Sum](https://leetcode.com/problems/count-of-range-sum/) | Hard |  |
| 504 | 2426 | [Number of Pairs Satisfying Inequality](https://leetcode.com/problems/number-of-pairs-satisfying-inequality/) | Hard | 2030 |
| 505 | 3768 | [Minimum Inversion Count in Subarrays of Fixed Length](https://leetcode.com/problems/minimum-inversion-count-in-subarrays-of-fixed-length/) | Hard | 2158 |
| 506 | 1850 | [Minimum Adjacent Swaps to Reach the Kth Smallest Number](https://leetcode.com/problems/minimum-adjacent-swaps-to-reach-the-kth-smallest-number/) | Medium | 2073 |
| 507 | 2193 | [Minimum Number of Moves to Make Palindrome](https://leetcode.com/problems/minimum-number-of-moves-to-make-palindrome/) | Hard | 2091 |
| 508 | 1885 | [Count Pairs in Two Arrays](https://leetcode.com/problems/count-pairs-in-two-arrays/) 🔒 | Medium |  |

### §8.3 Segment Tree (no range updates)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 509 | 3479 | [Fruits Into Baskets III](https://leetcode.com/problems/fruits-into-baskets-iii/) | Medium | 2178 |
| 510 | 2940 | [Find Building Where Alice and Bob Can Meet](https://leetcode.com/problems/find-building-where-alice-and-bob-can-meet/) | Hard | 2327 |
| 511 | 2286 | [Booking Concert Tickets in Groups](https://leetcode.com/problems/booking-concert-tickets-in-groups/) | Hard | 2470 |
| 512 | 3161 | [Block Placement Queries](https://leetcode.com/problems/block-placement-queries/) | Hard | 2513 |
| 513 | 3901 | [Good Subsequence Queries](https://leetcode.com/problems/good-subsequence-queries/) | Hard | 2545 |
| 514 | 2213 | [Longest Substring of One Repeating Character](https://leetcode.com/problems/longest-substring-of-one-repeating-character/) | Hard | 2629 |
| 515 | 3777 | [Minimum Deletions to Make Alternating Substring](https://leetcode.com/problems/minimum-deletions-to-make-alternating-substring/) | Hard | 2202 |
| 516 | 3525 | [Find X Value of Array II](https://leetcode.com/problems/find-x-value-of-array-ii/) | Hard | 2645 |
| 517 | 3165 | [Maximum Sum of Subsequence With Non-adjacent Elements](https://leetcode.com/problems/maximum-sum-of-subsequence-with-non-adjacent-elements/) | Hard | 2698 |
| 518 | 3410 | [Maximize Subarray Sum After Removing All Occurrences of One Element](https://leetcode.com/problems/maximize-subarray-sum-after-removing-all-occurrences-of-one-element/) | Hard | 2844 |
| 519 | 3501 | [Maximize Active Section with Trade II](https://leetcode.com/problems/maximize-active-section-with-trade-ii/) | Hard | 2941 |
| 520 | 1157 | [Online Majority Element In Subarray](https://leetcode.com/problems/online-majority-element-in-subarray/) | Hard | 2205 |
| 521 | 2407 | [Longest Increasing Subsequence II](https://leetcode.com/problems/longest-increasing-subsequence-ii/) | Hard | 2280 |
| 522 | 2770 | [Maximum Number of Jumps to Reach the Last Index](https://leetcode.com/problems/maximum-number-of-jumps-to-reach-the-last-index/) | Medium | 1533 |

## Programming Skills Practice

### Part A

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 523 | 12 | [Integer to Roman](https://leetcode.com/problems/integer-to-roman/) | Medium |  |
| 524 | 13 | [Roman to Integer](https://leetcode.com/problems/roman-to-integer/) | Easy |  |
| 525 | 273 | [Integer to English Words](https://leetcode.com/problems/integer-to-english-words/) | Hard |  |
| 526 | 68 | [Text Justification](https://leetcode.com/problems/text-justification/) | Hard |  |
| 527 | 420 | [Strong Password Checker](https://leetcode.com/problems/strong-password-checker/) | Hard |  |
| 528 | 8 | [String to Integer (atoi)](https://leetcode.com/problems/string-to-integer-atoi/) | Medium |  |
| 529 | 65 | [Valid Number](https://leetcode.com/problems/valid-number/) | Hard |  |

### Part B

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 530 | 146 | [LRU Cache](https://leetcode.com/problems/lru-cache/) | Medium |  |
| 531 | 460 | [LFU Cache](https://leetcode.com/problems/lfu-cache/) | Hard |  |
| 532 | 432 | [All O`one Data Structure](https://leetcode.com/problems/all-oone-data-structure/) | Hard |  |
| 533 | 1206 | [Design Skiplist](https://leetcode.com/problems/design-skiplist/) | Hard |  |

### Part C

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 534 | 3197 | [Find the Minimum Area to Cover All Ones II](https://leetcode.com/problems/find-the-minimum-area-to-cover-all-ones-ii/) | Hard | 2541 |
| 535 | 2532 | [Time to Cross a Bridge](https://leetcode.com/problems/time-to-cross-a-bridge/) | Hard | 2589 |
| 536 | 2056 | [Number of Valid Move Combinations On Chessboard](https://leetcode.com/problems/number-of-valid-move-combinations-on-chessboard/) | Hard | 2611 |

---

## Omitted from this list

Competition-oriented sections (see the original post or `source/data/ox3f.json` for their problems):

- §6.3 Trie-Optimized DP (5 problems)
- §7.3 Intermediary Union-Find (9 problems)
- §7.4 Union-Find on Arrays (7 problems)
- §7.5 Interval Union-Find (4 problems)
- §7.6 Weighted Union-Find (4 problems)
- §8.4 Lazy Segment Tree (range updates) (11 problems)
- §8.5 Dynamic Segment Tree (7 problems)
- §8.6 Persistent Segment Tree (1 problem)
- §8.7 Sparse Table (3 problems)
- 9. Splay Tree (2 problems)
- 10. Square-Root Algorithms (8 problems)
- Special Topic: Offline Algorithms (13 problems)

Also omitted: 20 problems exclusive to leetcode.cn (LCP / LCR / LCS / 面试题 series).
