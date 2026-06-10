# Sliding Window & Two Pointers — 0x3F list

> Curated from 灵茶山艾府 (0x3F)'s problem list: [https://leetcode.cn/discuss/post/0viNMK/](https://leetcode.cn/discuss/post/0viNMK/) (snapshot 2026-06-09). Section structure and problem order follow the original.
> Competition-only sections and leetcode.cn-exclusive problems are omitted (see the end of this file).
> **Rating** = LeetCode contest difficulty rating (~1000–3000+) from the [zerotrac project](https://zerotrac.github.io/leetcode_problem_rating/); 🔒 = premium.

## 1. Fixed-Length Sliding Window

### §1.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 1 | 1456 | [Maximum Number of Vowels in a Substring of Given Length](https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/) | Medium | 1263 |
| 2 | 643 | [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | Easy |  |
| 3 | 1343 | [Number of Sub-arrays of Size K and Average Greater than or Equal to Threshold](https://leetcode.com/problems/number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold/) | Medium | 1317 |
| 4 | 2090 | [K Radius Subarray Averages](https://leetcode.com/problems/k-radius-subarray-averages/) | Medium | 1358 |
| 5 | 2379 | [Minimum Recolors to Get K Consecutive Black Blocks](https://leetcode.com/problems/minimum-recolors-to-get-k-consecutive-black-blocks/) | Easy | 1360 |
| 6 | 2841 | [Maximum Sum of Almost Unique Subarray](https://leetcode.com/problems/maximum-sum-of-almost-unique-subarray/) | Medium | 1546 |
| 7 | 2461 | [Maximum Sum of Distinct Subarrays With Length K](https://leetcode.com/problems/maximum-sum-of-distinct-subarrays-with-length-k/) | Medium | 1553 |
| 8 | 1423 | [Maximum Points You Can Obtain from Cards](https://leetcode.com/problems/maximum-points-you-can-obtain-from-cards/) | Medium | 1574 |
| 9 | 1176 | [Diet Plan Performance](https://leetcode.com/problems/diet-plan-performance/) 🔒 | Easy | 1398 |
| 10 | 1100 | [Find K-Length Substrings With No Repeated Characters](https://leetcode.com/problems/find-k-length-substrings-with-no-repeated-characters/) 🔒 | Medium | 1349 |
| 11 | 1852 | [Distinct Numbers in Each Subarray](https://leetcode.com/problems/distinct-numbers-in-each-subarray/) 🔒 | Medium |  |
| 12 | 1151 | [Minimum Swaps to Group All 1's Together](https://leetcode.com/problems/minimum-swaps-to-group-all-1s-together/) 🔒 | Medium | 1508 |
| 13 | 2107 | [Number of Unique Flavors After Sharing K Candies](https://leetcode.com/problems/number-of-unique-flavors-after-sharing-k-candies/) 🔒 | Medium |  |

### §1.2 Advanced (optional)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 14 | 1052 | [Grumpy Bookstore Owner](https://leetcode.com/problems/grumpy-bookstore-owner/) | Medium | 1418 |
| 15 | 3679 | [ Minimum Discards to Balance Inventory](https://leetcode.com/problems/minimum-discards-to-balance-inventory/) | Medium | 1639 |
| 16 | 3439 | [Reschedule Meetings for Maximum Free Time I](https://leetcode.com/problems/reschedule-meetings-for-maximum-free-time-i/) | Medium | 1729 |
| 17 | 3694 | [Distinct Points Reachable After Substring Removal](https://leetcode.com/problems/distinct-points-reachable-after-substring-removal/) | Medium | 1739 |
| 18 | 2134 | [Minimum Swaps to Group All 1's Together II](https://leetcode.com/problems/minimum-swaps-to-group-all-1s-together-ii/) | Medium | 1748 |
| 19 | 1652 | [Defuse the Bomb](https://leetcode.com/problems/defuse-the-bomb/) | Easy | 1417 |
| 20 | 1297 | [Maximum Number of Occurrences of a Substring](https://leetcode.com/problems/maximum-number-of-occurrences-of-a-substring/) | Medium | 1748 |
| 21 | 3652 | [Best Time to Buy and Sell Stock using Strategy](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-using-strategy/) | Medium | 1557 |
| 22 | 567 | [Permutation in String](https://leetcode.com/problems/permutation-in-string/) | Medium |  |
| 23 | 438 | [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | Medium |  |
| 24 | 30 | [Substring with Concatenation of All Words](https://leetcode.com/problems/substring-with-concatenation-of-all-words/) | Hard |  |
| 25 | 1888 | [Minimum Number of Flips to Make the Binary String Alternating](https://leetcode.com/problems/minimum-number-of-flips-to-make-the-binary-string-alternating/) | Medium | 2006 |
| 26 | 2156 | [Find Substring With Given Hash Value](https://leetcode.com/problems/find-substring-with-given-hash-value/) | Hard | 2063 |
| 27 | 2953 | [Count Complete Substrings](https://leetcode.com/problems/count-complete-substrings/) | Hard | 2449 |
| 28 | 3672 | [Sum of Weighted Modes in Subarrays](https://leetcode.com/problems/sum-of-weighted-modes-in-subarrays/) 🔒 | Medium |  |
| 29 | 2067 | [Number of Equal Count Substrings](https://leetcode.com/problems/number-of-equal-count-substrings/) 🔒 | Medium |  |
| 30 | 2524 | [Maximum Frequency Score of a Subarray](https://leetcode.com/problems/maximum-frequency-score-of-a-subarray/) 🔒 | Hard |  |
| 31 | 2200 | [Find All K-Distant Indices in an Array](https://leetcode.com/problems/find-all-k-distant-indices-in-an-array/) | Easy | 1266 |
| 32 | 1461 | [Check If a String Contains All Binary Codes of Size K](https://leetcode.com/problems/check-if-a-string-contains-all-binary-codes-of-size-k/) | Medium | 1504 |
| 33 | 1016 | [Binary String With Substrings Representing 1 To N](https://leetcode.com/problems/binary-string-with-substrings-representing-1-to-n/) | Medium | 1779 |
| 34 | 2653 | [Sliding Subarray Beauty](https://leetcode.com/problems/sliding-subarray-beauty/) | Medium | 1786 |

## 2. Variable-Length Sliding Window

### §2.1 Shorter-is-valid / longest, maximum

#### §2.1.1 Basics

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 35 | 3 | [Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Medium |  |
| 36 | 3090 | [Maximum Length Substring With Two Occurrences](https://leetcode.com/problems/maximum-length-substring-with-two-occurrences/) | Easy | 1329 |
| 37 | 1493 | [Longest Subarray of 1's After Deleting One Element](https://leetcode.com/problems/longest-subarray-of-1s-after-deleting-one-element/) | Medium | 1423 |
| 38 | 3634 | [Minimum Removals to Balance Array](https://leetcode.com/problems/minimum-removals-to-balance-array/) | Medium | 1453 |
| 39 | 1208 | [Get Equal Substrings Within Budget](https://leetcode.com/problems/get-equal-substrings-within-budget/) | Medium | 1497 |
| 40 | 904 | [Fruit Into Baskets](https://leetcode.com/problems/fruit-into-baskets/) | Medium | 1516 |
| 41 | 1695 | [Maximum Erasure Value](https://leetcode.com/problems/maximum-erasure-value/) | Medium | 1529 |
| 42 | 2958 | [Length of Longest Subarray With at Most K Frequency](https://leetcode.com/problems/length-of-longest-subarray-with-at-most-k-frequency/) | Medium | 1535 |
| 43 | 2024 | [Maximize the Confusion of an Exam](https://leetcode.com/problems/maximize-the-confusion-of-an-exam/) | Medium | 1643 |
| 44 | 1004 | [Max Consecutive Ones III](https://leetcode.com/problems/max-consecutive-ones-iii/) | Medium | 1656 |
| 45 | 3641 | [Longest Semi-Repeating Subarray](https://leetcode.com/problems/longest-semi-repeating-subarray/) 🔒 | Medium |  |

#### §2.1.2 Advanced (optional)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 46 | 2730 | [Find the Longest Semi-Repetitive Substring](https://leetcode.com/problems/find-the-longest-semi-repetitive-substring/) | Medium | 1502 |
| 47 | 2779 | [Maximum Beauty of an Array After Applying Operation](https://leetcode.com/problems/maximum-beauty-of-an-array-after-applying-operation/) | Medium | 1638 |
| 48 | 1658 | [Minimum Operations to Reduce X to Zero](https://leetcode.com/problems/minimum-operations-to-reduce-x-to-zero/) | Medium | 1817 |
| 49 | 1838 | [Frequency of the Most Frequent Element](https://leetcode.com/problems/frequency-of-the-most-frequent-element/) | Medium | 1876 |
| 50 | 2516 | [Take K of Each Character From Left and Right](https://leetcode.com/problems/take-k-of-each-character-from-left-and-right/) | Medium | 1948 |
| 51 | 2831 | [Find the Longest Equal Subarray](https://leetcode.com/problems/find-the-longest-equal-subarray/) | Medium | 1976 |
| 52 | 2271 | [Maximum White Tiles Covered by a Carpet](https://leetcode.com/problems/maximum-white-tiles-covered-by-a-carpet/) | Medium | 2022 |
| 53 | 2106 | [Maximum Fruits Harvested After at Most K Steps](https://leetcode.com/problems/maximum-fruits-harvested-after-at-most-k-steps/) | Hard | 2062 |
| 54 | 2555 | [Maximize Win From Two Segments](https://leetcode.com/problems/maximize-win-from-two-segments/) | Medium | 2081 |
| 55 | 2009 | [Minimum Number of Operations to Make Array Continuous](https://leetcode.com/problems/minimum-number-of-operations-to-make-array-continuous/) | Hard | 2084 |
| 56 | 1610 | [Maximum Number of Visible Points](https://leetcode.com/problems/maximum-number-of-visible-points/) | Hard | 2147 |
| 57 | 2781 | [Length of the Longest Valid Substring](https://leetcode.com/problems/length-of-the-longest-valid-substring/) | Hard | 2204 |
| 58 | 3411 | [Maximum Subarray With Equal Products](https://leetcode.com/problems/maximum-subarray-with-equal-products/) | Easy | 1443 |
| 59 | 3413 | [Maximum Coins From K Consecutive Bags](https://leetcode.com/problems/maximum-coins-from-k-consecutive-bags/) | Medium | 2374 |
| 60 | 395 | [Longest Substring with At Least K Repeating Characters](https://leetcode.com/problems/longest-substring-with-at-least-k-repeating-characters/) | Medium |  |
| 61 | 1763 | [Longest Nice Substring](https://leetcode.com/problems/longest-nice-substring/) | Easy | 1522 |
| 62 | 2968 | [Apply Operations to Maximize Frequency Score](https://leetcode.com/problems/apply-operations-to-maximize-frequency-score/) | Hard | 2444 |
| 63 | 1040 | [Moving Stones Until Consecutive II](https://leetcode.com/problems/moving-stones-until-consecutive-ii/) | Medium | 2456 |
| 64 | 487 | [Max Consecutive Ones II](https://leetcode.com/problems/max-consecutive-ones-ii/) 🔒 | Medium |  |
| 65 | 159 | [Longest Substring with At Most Two Distinct Characters](https://leetcode.com/problems/longest-substring-with-at-most-two-distinct-characters/) 🔒 | Medium |  |
| 66 | 340 | [Longest Substring with At Most K Distinct Characters](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/) 🔒 | Medium |  |

### §2.2 Longer-is-valid / shortest, minimum

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 67 | 209 | [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) | Medium |  |
| 68 | 3795 | [Minimum Subarray Length With Distinct Sum At Least K](https://leetcode.com/problems/minimum-subarray-length-with-distinct-sum-at-least-k/) | Medium | 1505 |
| 69 | 2904 | [Shortest and Lexicographically Smallest Beautiful String](https://leetcode.com/problems/shortest-and-lexicographically-smallest-beautiful-string/) | Medium | 1483 |
| 70 | 1234 | [Replace the Substring for Balanced String](https://leetcode.com/problems/replace-the-substring-for-balanced-string/) | Medium | 1878 |
| 71 | 2875 | [Minimum Size Subarray in Infinite Array](https://leetcode.com/problems/minimum-size-subarray-in-infinite-array/) | Medium | 1914 |
| 72 | 76 | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | Hard |  |
| 73 | 632 | [Smallest Range Covering Elements from K Lists](https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/) | Hard |  |

### §2.3 Counting Subarrays

#### §2.3.1 Shorter-is-valid

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 74 | 713 | [Subarray Product Less Than K](https://leetcode.com/problems/subarray-product-less-than-k/) | Medium |  |
| 75 | 3258 | [Count Substrings That Satisfy K-Constraint I](https://leetcode.com/problems/count-substrings-that-satisfy-k-constraint-i/) | Easy | 1258 |
| 76 | 2302 | [Count Subarrays With Score Less Than K](https://leetcode.com/problems/count-subarrays-with-score-less-than-k/) | Hard | 1808 |
| 77 | 2762 | [Continuous Subarrays](https://leetcode.com/problems/continuous-subarrays/) | Medium | 1940 |
| 78 | 2743 | [Count Substrings Without Repeating Character](https://leetcode.com/problems/count-substrings-without-repeating-character/) 🔒 | Medium |  |
| 79 | 3134 | [Find the Median of the Uniqueness Array](https://leetcode.com/problems/find-the-median-of-the-uniqueness-array/) | Hard | 2451 |
| 80 | 3261 | [Count Substrings That Satisfy K-Constraint II](https://leetcode.com/problems/count-substrings-that-satisfy-k-constraint-ii/) | Hard | 2659 |

#### §2.3.2 Longer-is-valid

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 81 | 1358 | [Number of Substrings Containing All Three Characters](https://leetcode.com/problems/number-of-substrings-containing-all-three-characters/) | Medium | 1646 |
| 82 | 2962 | [Count Subarrays Where Max Element Appears at Least K Times](https://leetcode.com/problems/count-subarrays-where-max-element-appears-at-least-k-times/) | Medium | 1701 |
| 83 | 3325 | [Count Substrings With K-Frequency Characters I](https://leetcode.com/problems/count-substrings-with-k-frequency-characters-i/) | Medium | 1455 |
| 84 | 2062 | [Count Vowel Substrings of a String](https://leetcode.com/problems/count-vowel-substrings-of-a-string/) | Easy | 1458 |
| 85 | 2799 | [Count Complete Subarrays in an Array](https://leetcode.com/problems/count-complete-subarrays-in-an-array/) | Medium | 1398 |
| 86 | 2537 | [Count the Number of Good Subarrays](https://leetcode.com/problems/count-the-number-of-good-subarrays/) | Medium | 1892 |
| 87 | 3298 | [Count Substrings That Can Be Rearranged to Contain a String II](https://leetcode.com/problems/count-substrings-that-can-be-rearranged-to-contain-a-string-ii/) | Hard | 1909 |
| 88 | 2495 | [Number of Subarrays Having Even Product](https://leetcode.com/problems/number-of-subarrays-having-even-product/) 🔒 | Medium |  |

#### §2.3.3 Exactly-K Sliding Window

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 89 | 930 | [Binary Subarrays With Sum](https://leetcode.com/problems/binary-subarrays-with-sum/) | Medium | 1592 |
| 90 | 1248 | [Count Number of Nice Subarrays](https://leetcode.com/problems/count-number-of-nice-subarrays/) | Medium | 1624 |
| 91 | 3306 | [Count of Substrings Containing Every Vowel and K Consonants II](https://leetcode.com/problems/count-of-substrings-containing-every-vowel-and-k-consonants-ii/) | Medium | 2200 |
| 92 | 992 | [Subarrays with K Different Integers](https://leetcode.com/problems/subarrays-with-k-different-integers/) | Hard | 2210 |
| 93 | 3859 | [Count Subarrays With K Distinct Integers](https://leetcode.com/problems/count-subarrays-with-k-distinct-integers/) | Hard | 2302 |

### §2.4 Other (optional)

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 94 | 825 | [Friends Of Appropriate Ages](https://leetcode.com/problems/friends-of-appropriate-ages/) | Medium | 1697 |
| 95 | 2401 | [Longest Nice Subarray](https://leetcode.com/problems/longest-nice-subarray/) | Medium | 1750 |
| 96 | 1156 | [Swap For Longest Repeated Character Substring](https://leetcode.com/problems/swap-for-longest-repeated-character-substring/) | Medium | 1787 |
| 97 | 424 | [Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) | Medium |  |
| 98 | 438 | [Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | Medium |  |
| 99 | 1712 | [Ways to Split Array Into Three Subarrays](https://leetcode.com/problems/ways-to-split-array-into-three-subarrays/) | Medium | 2079 |
| 100 | 1918 | [Kth Smallest Subarray Sum](https://leetcode.com/problems/kth-smallest-subarray-sum/) 🔒 | Medium |  |

## 3. Two Pointers on One Sequence

### §3.1 Reversing Strings

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 101 | 344 | [Reverse String](https://leetcode.com/problems/reverse-string/) | Easy |  |
| 102 | 3794 | [Reverse String Prefix](https://leetcode.com/problems/reverse-string-prefix/) | Easy | 1230 |
| 103 | 2000 | [Reverse Prefix of Word](https://leetcode.com/problems/reverse-prefix-of-word/) | Easy | 1199 |
| 104 | 3643 | [Flip Square Submatrix Vertically](https://leetcode.com/problems/flip-square-submatrix-vertically/) | Easy | 1235 |
| 105 | 832 | [Flipping an Image](https://leetcode.com/problems/flipping-an-image/) | Easy | 1243 |
| 106 | 3823 | [Reverse Letters Then Special Characters in a String](https://leetcode.com/problems/reverse-letters-then-special-characters-in-a-string/) | Easy | 1250 |
| 107 | 541 | [Reverse String II](https://leetcode.com/problems/reverse-string-ii/) | Easy |  |
| 108 | 557 | [Reverse Words in a String III](https://leetcode.com/problems/reverse-words-in-a-string-iii/) | Easy |  |
| 109 | 151 | [Reverse Words in a String](https://leetcode.com/problems/reverse-words-in-a-string/) | Medium |  |
| 110 | 3775 | [Reverse Words With Same Vowel Count](https://leetcode.com/problems/reverse-words-with-same-vowel-count/) | Medium | 1392 |
| 111 | 917 | [Reverse Only Letters](https://leetcode.com/problems/reverse-only-letters/) | Easy | 1229 |
| 112 | 345 | [Reverse Vowels of a String](https://leetcode.com/problems/reverse-vowels-of-a-string/) | Easy |  |
| 113 | 3865 | [Reverse K Subarrays](https://leetcode.com/problems/reverse-k-subarrays/) 🔒 | Medium |  |
| 114 | 186 | [Reverse Words in a String II](https://leetcode.com/problems/reverse-words-in-a-string-ii/) 🔒 | Medium |  |

### §3.2 Opposite-Direction Two Pointers

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 115 | 2697 | [Lexicographically Smallest Palindrome](https://leetcode.com/problems/lexicographically-smallest-palindrome/) | Easy | 1304 |
| 116 | 125 | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | Easy |  |
| 117 | 1750 | [Minimum Length of String After Deleting Similar Ends](https://leetcode.com/problems/minimum-length-of-string-after-deleting-similar-ends/) | Medium | 1502 |
| 118 | 2105 | [Watering Plants II](https://leetcode.com/problems/watering-plants-ii/) | Medium | 1507 |
| 119 | 977 | [Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) | Easy | 1130 |
| 120 | 658 | [Find K Closest Elements](https://leetcode.com/problems/find-k-closest-elements/) | Medium |  |
| 121 | 1471 | [The k Strongest Values in an Array](https://leetcode.com/problems/the-k-strongest-values-in-an-array/) | Medium | 1332 |
| 122 | 167 | [Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Medium |  |
| 123 | 633 | [Sum of Square Numbers](https://leetcode.com/problems/sum-of-square-numbers/) | Medium |  |
| 124 | 2824 | [Count Pairs Whose Sum is Less than Target](https://leetcode.com/problems/count-pairs-whose-sum-is-less-than-target/) | Easy | 1166 |
| 125 | 16 | [3Sum Closest](https://leetcode.com/problems/3sum-closest/) | Medium |  |
| 126 | 15 | [3Sum](https://leetcode.com/problems/3sum/) | Medium |  |
| 127 | 18 | [4Sum](https://leetcode.com/problems/4sum/) | Medium |  |
| 128 | 1577 | [Number of Ways Where Square of Number Is Equal to Product of Two Numbers](https://leetcode.com/problems/number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers/) | Medium | 1594 |
| 129 | 3862 | [Find the Smallest Balanced Index](https://leetcode.com/problems/find-the-smallest-balanced-index/) | Medium | 1697 |
| 130 | 611 | [Valid Triangle Number](https://leetcode.com/problems/valid-triangle-number/) | Medium |  |
| 131 | 923 | [3Sum With Multiplicity](https://leetcode.com/problems/3sum-with-multiplicity/) | Medium | 1711 |
| 132 | 2563 | [Count the Number of Fair Pairs](https://leetcode.com/problems/count-the-number-of-fair-pairs/) | Medium | 1721 |
| 133 | 948 | [Bag of Tokens](https://leetcode.com/problems/bag-of-tokens/) | Medium | 1762 |
| 134 | 11 | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Medium |  |
| 135 | 42 | [Trapping Rain Water](https://leetcode.com/problems/trapping-rain-water/) | Hard |  |
| 136 | 1616 | [Split Two Strings to Make Palindrome](https://leetcode.com/problems/split-two-strings-to-make-palindrome/) | Medium | 1868 |
| 137 | 1498 | [Number of Subsequences That Satisfy the Given Sum Condition](https://leetcode.com/problems/number-of-subsequences-that-satisfy-the-given-sum-condition/) | Medium | 2276 |
| 138 | 1782 | [Count Pairs Of Nodes](https://leetcode.com/problems/count-pairs-of-nodes/) | Hard | 2457 |
| 139 | 1099 | [Two Sum Less Than K](https://leetcode.com/problems/two-sum-less-than-k/) 🔒 | Easy | 1245 |
| 140 | 360 | [Sort Transformed Array](https://leetcode.com/problems/sort-transformed-array/) 🔒 | Medium |  |
| 141 | 2422 | [Merge Operations to Turn Array Into a Palindrome](https://leetcode.com/problems/merge-operations-to-turn-array-into-a-palindrome/) 🔒 | Medium |  |
| 142 | 259 | [3Sum Smaller](https://leetcode.com/problems/3sum-smaller/) 🔒 | Medium |  |
| 143 | 3802 | [Number of Ways to Paint Sheets](https://leetcode.com/problems/number-of-ways-to-paint-sheets/) 🔒 | Hard |  |
| 144 | 1861 | [Rotating the Box](https://leetcode.com/problems/rotating-the-box/) | Medium | 1537 |
| 145 | 3814 | [Maximum Capacity Within Budget](https://leetcode.com/problems/maximum-capacity-within-budget/) | Medium | 1796 |

### §3.3 Same-Direction Two Pointers

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 146 | 2200 | [Find All K-Distant Indices in an Array](https://leetcode.com/problems/find-all-k-distant-indices-in-an-array/) | Easy | 1266 |
| 147 | 611 | [Valid Triangle Number](https://leetcode.com/problems/valid-triangle-number/) | Medium |  |
| 148 | 3649 | [Number of Perfect Pairs](https://leetcode.com/problems/number-of-perfect-pairs/) | Medium | 1716 |
| 149 | 1871 | [Jump Game VII](https://leetcode.com/problems/jump-game-vii/) | Medium | 1896 |
| 150 | 1574 | [Shortest Subarray to be Removed to Make Array Sorted](https://leetcode.com/problems/shortest-subarray-to-be-removed-to-make-array-sorted/) | Medium | 1932 |
| 151 | 2972 | [Count the Number of Incremovable Subarrays II](https://leetcode.com/problems/count-the-number-of-incremovable-subarrays-ii/) | Hard | 2153 |
| 152 | 2122 | [Recover the Original Array](https://leetcode.com/problems/recover-the-original-array/) | Hard | 2159 |
| 153 | 2234 | [Maximum Total Beauty of the Gardens](https://leetcode.com/problems/maximum-total-beauty-of-the-gardens/) | Hard | 2562 |
| 154 | 1989 | [Maximum Number of People That Can Be Caught in Tag](https://leetcode.com/problems/maximum-number-of-people-that-can-be-caught-in-tag/) 🔒 | Medium |  |
| 155 | 3323 | [Minimize Connected Groups by Inserting Interval](https://leetcode.com/problems/minimize-connected-groups-by-inserting-interval/) 🔒 | Medium |  |
| 156 | 581 | [Shortest Unsorted Continuous Subarray](https://leetcode.com/problems/shortest-unsorted-continuous-subarray/) | Medium |  |
| 157 | 3555 | [Smallest Subarray to Sort in Every Sliding Window](https://leetcode.com/problems/smallest-subarray-to-sort-in-every-sliding-window/) 🔒 | Medium |  |

### §3.4 Outward Two Pointers

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 158 | 1793 | [Maximum Score of a Good Subarray](https://leetcode.com/problems/maximum-score-of-a-good-subarray/) | Hard | 1946 |
| 159 | 976 | [Largest Perimeter Triangle](https://leetcode.com/problems/largest-perimeter-triangle/) | Easy | 1341 |

### §3.5 In-Place Modification

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 160 | 27 | [Remove Element](https://leetcode.com/problems/remove-element/) | Easy |  |
| 161 | 26 | [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Easy |  |
| 162 | 80 | [Remove Duplicates from Sorted Array II](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) | Medium |  |
| 163 | 2273 | [Find Resultant Array After Removing Anagrams](https://leetcode.com/problems/find-resultant-array-after-removing-anagrams/) | Easy | 1295 |
| 164 | 3684 | [Maximize Sum of At Most K Distinct Elements](https://leetcode.com/problems/maximize-sum-of-at-most-k-distinct-elements/) | Easy | 1299 |
| 165 | 283 | [Move Zeroes](https://leetcode.com/problems/move-zeroes/) | Easy |  |
| 166 | 905 | [Sort Array By Parity](https://leetcode.com/problems/sort-array-by-parity/) | Easy | 1178 |
| 167 | 922 | [Sort Array By Parity II](https://leetcode.com/problems/sort-array-by-parity-ii/) | Easy | 1174 |
| 168 | 3467 | [Transform Array by Parity](https://leetcode.com/problems/transform-array-by-parity/) | Easy | 1166 |
| 169 | 2460 | [Apply Operations to an Array](https://leetcode.com/problems/apply-operations-to-an-array/) | Easy | 1224 |
| 170 | 1089 | [Duplicate Zeros](https://leetcode.com/problems/duplicate-zeros/) | Easy | 1263 |
| 171 | 75 | [Sort Colors](https://leetcode.com/problems/sort-colors/) | Medium |  |
| 172 | 2784 | [Check if Array is Good](https://leetcode.com/problems/check-if-array-is-good/) | Easy | 1376 |
| 173 | 442 | [Find All Duplicates in an Array](https://leetcode.com/problems/find-all-duplicates-in-an-array/) | Medium |  |
| 174 | 448 | [Find All Numbers Disappeared in an Array](https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/) | Easy |  |
| 175 | 1920 | [Build Array from Permutation](https://leetcode.com/problems/build-array-from-permutation/) | Easy | 1160 |
| 176 | 41 | [First Missing Positive](https://leetcode.com/problems/first-missing-positive/) | Hard |  |

### §3.6 Two Pointers on a Matrix

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 177 | 240 | [Search a 2D Matrix II](https://leetcode.com/problems/search-a-2d-matrix-ii/) | Medium |  |
| 178 | 1351 | [Count Negative Numbers in a Sorted Matrix](https://leetcode.com/problems/count-negative-numbers-in-a-sorted-matrix/) | Easy | 1139 |

## 4. Two Pointers on Two Sequences

### §4.1 Two Pointers

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 179 | 2109 | [Adding Spaces to a String](https://leetcode.com/problems/adding-spaces-to-a-string/) | Medium | 1315 |
| 180 | 2540 | [Minimum Common Value](https://leetcode.com/problems/minimum-common-value/) | Easy | 1250 |
| 181 | 350 | [Intersection of Two Arrays II](https://leetcode.com/problems/intersection-of-two-arrays-ii/) | Easy |  |
| 182 | 88 | [Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | Easy |  |
| 183 | 2570 | [Merge Two 2D Arrays by Summing Values](https://leetcode.com/problems/merge-two-2d-arrays-by-summing-values/) | Easy | 1281 |
| 184 | 1855 | [Maximum Distance Between a Pair of Values](https://leetcode.com/problems/maximum-distance-between-a-pair-of-values/) | Medium | 1515 |
| 185 | 1385 | [Find the Distance Value Between Two Arrays](https://leetcode.com/problems/find-the-distance-value-between-two-arrays/) | Easy | 1235 |
| 186 | 925 | [Long Pressed Name](https://leetcode.com/problems/long-pressed-name/) | Easy | 1271 |
| 187 | 809 | [Expressive Words](https://leetcode.com/problems/expressive-words/) | Medium | 1605 |
| 188 | 2337 | [Move Pieces to Obtain a String](https://leetcode.com/problems/move-pieces-to-obtain-a-string/) | Medium | 1693 |
| 189 | 777 | [Swap Adjacent in LR String](https://leetcode.com/problems/swap-adjacent-in-lr-string/) | Medium | 1939 |
| 190 | 844 | [Backspace String Compare](https://leetcode.com/problems/backspace-string-compare/) | Easy | 1228 |
| 191 | 986 | [Interval List Intersections](https://leetcode.com/problems/interval-list-intersections/) | Medium | 1542 |
| 192 | 475 | [Heaters](https://leetcode.com/problems/heaters/) | Medium |  |
| 193 | 1537 | [Get the Maximum Score](https://leetcode.com/problems/get-the-maximum-score/) | Hard | 1961 |
| 194 | 244 | [Shortest Word Distance II](https://leetcode.com/problems/shortest-word-distance-ii/) 🔒 | Medium |  |
| 195 | 2838 | [Maximum Coins Heroes Can Collect](https://leetcode.com/problems/maximum-coins-heroes-can-collect/) 🔒 | Medium |  |
| 196 | 1229 | [Meeting Scheduler](https://leetcode.com/problems/meeting-scheduler/) 🔒 | Medium | 1541 |
| 197 | 1570 | [Dot Product of Two Sparse Vectors](https://leetcode.com/problems/dot-product-of-two-sparse-vectors/) 🔒 | Medium |  |
| 198 | 1868 | [Product of Two Run-Length Encoded Arrays](https://leetcode.com/problems/product-of-two-run-length-encoded-arrays/) 🔒 | Medium |  |

### §4.2 Subsequence Checking

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 199 | 392 | [Is Subsequence](https://leetcode.com/problems/is-subsequence/) | Easy |  |
| 200 | 524 | [Longest Word in Dictionary through Deleting](https://leetcode.com/problems/longest-word-in-dictionary-through-deleting/) | Medium |  |
| 201 | 2486 | [Append Characters to String to Make Subsequence](https://leetcode.com/problems/append-characters-to-string-to-make-subsequence/) | Medium | 1363 |
| 202 | 2825 | [Make String a Subsequence Using Cyclic Increments](https://leetcode.com/problems/make-string-a-subsequence-using-cyclic-increments/) | Medium | 1415 |
| 203 | 1023 | [Camelcase Matching](https://leetcode.com/problems/camelcase-matching/) | Medium | 1537 |
| 204 | 3132 | [Find the Integer Added to Array II](https://leetcode.com/problems/find-the-integer-added-to-array-ii/) | Medium | 1620 |
| 205 | 522 | [Longest Uncommon Subsequence II](https://leetcode.com/problems/longest-uncommon-subsequence-ii/) | Medium |  |
| 206 | 1826 | [Faulty Sensor](https://leetcode.com/problems/faulty-sensor/) 🔒 | Easy |  |
| 207 | 1898 | [Maximum Number of Removable Characters](https://leetcode.com/problems/maximum-number-of-removable-characters/) | Medium | 1913 |
| 208 | 2565 | [Subsequence With the Minimum Score](https://leetcode.com/problems/subsequence-with-the-minimum-score/) | Hard | 2432 |
| 209 | 3302 | [Find the Lexicographically Smallest Valid Sequence](https://leetcode.com/problems/find-the-lexicographically-smallest-valid-sequence/) | Medium | 2474 |

## 5. Three Pointers

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 210 | 2367 | [Number of Arithmetic Triplets](https://leetcode.com/problems/number-of-arithmetic-triplets/) | Easy | 1203 |
| 211 | 2563 | [Count the Number of Fair Pairs](https://leetcode.com/problems/count-the-number-of-fair-pairs/) | Medium | 1721 |
| 212 | 795 | [Number of Subarrays with Bounded Maximum](https://leetcode.com/problems/number-of-subarrays-with-bounded-maximum/) | Medium | 1817 |
| 213 | 2444 | [Count Subarrays With Fixed Bounds](https://leetcode.com/problems/count-subarrays-with-fixed-bounds/) | Hard | 2093 |
| 214 | 3347 | [Maximum Frequency of an Element After Performing Operations II](https://leetcode.com/problems/maximum-frequency-of-an-element-after-performing-operations-ii/) | Hard | 2156 |
| 215 | 1213 | [Intersection of Three Sorted Arrays](https://leetcode.com/problems/intersection-of-three-sorted-arrays/) 🔒 | Easy | 1259 |
| 216 | 3464 | [Maximize the Distance Between Points on a Square](https://leetcode.com/problems/maximize-the-distance-between-points-on-a-square/) | Hard | 2806 |

## 6. Group-by-Group Iteration

| # | ID | Problem | Difficulty | Rating |
|---|----|---------|------------|--------|
| 217 | 485 | [Max Consecutive Ones](https://leetcode.com/problems/max-consecutive-ones/) | Easy |  |
| 218 | 1446 | [Consecutive Characters](https://leetcode.com/problems/consecutive-characters/) | Easy | 1165 |
| 219 | 1869 | [Longer Contiguous Segments of Ones than Zeros](https://leetcode.com/problems/longer-contiguous-segments-of-ones-than-zeros/) | Easy | 1205 |
| 220 | 2414 | [Length of the Longest Alphabetical Continuous Substring](https://leetcode.com/problems/length-of-the-longest-alphabetical-continuous-substring/) | Medium | 1222 |
| 221 | 3456 | [Find Special Substring of Length K](https://leetcode.com/problems/find-special-substring-of-length-k/) | Easy | 1244 |
| 222 | 830 | [Positions of Large Groups](https://leetcode.com/problems/positions-of-large-groups/) | Easy | 1252 |
| 223 | 2273 | [Find Resultant Array After Removing Anagrams](https://leetcode.com/problems/find-resultant-array-after-removing-anagrams/) | Easy | 1295 |
| 224 | 2264 | [Largest 3-Same-Digit Number in String](https://leetcode.com/problems/largest-3-same-digit-number-in-string/) | Easy | 1309 |
| 225 | 2348 | [Number of Zero-Filled Subarrays](https://leetcode.com/problems/number-of-zero-filled-subarrays/) | Medium | 1316 |
| 226 | 1513 | [Number of Substrings With Only 1s](https://leetcode.com/problems/number-of-substrings-with-only-1s/) | Medium | 1351 |
| 227 | 1957 | [Delete Characters to Make Fancy String](https://leetcode.com/problems/delete-characters-to-make-fancy-string/) | Easy | 1358 |
| 228 | 674 | [Longest Continuous Increasing Subsequence](https://leetcode.com/problems/longest-continuous-increasing-subsequence/) | Easy |  |
| 229 | 3708 | [Longest Fibonacci Subarray](https://leetcode.com/problems/longest-fibonacci-subarray/) | Medium | 1381 |
| 230 | 696 | [Count Binary Substrings](https://leetcode.com/problems/count-binary-substrings/) | Easy |  |
| 231 | 978 | [Longest Turbulent Subarray](https://leetcode.com/problems/longest-turbulent-subarray/) | Medium | 1393 |
| 232 | 2110 | [Number of Smooth Descent Periods of a Stock](https://leetcode.com/problems/number-of-smooth-descent-periods-of-a-stock/) | Medium | 1408 |
| 233 | 228 | [Summary Ranges](https://leetcode.com/problems/summary-ranges/) | Easy |  |
| 234 | 2760 | [Longest Even Odd Subarray With Threshold](https://leetcode.com/problems/longest-even-odd-subarray-with-threshold/) | Easy | 1420 |
| 235 | 1887 | [Reduction Operations to Make the Array Elements Equal](https://leetcode.com/problems/reduction-operations-to-make-the-array-elements-equal/) | Medium | 1428 |
| 236 | 845 | [Longest Mountain in Array](https://leetcode.com/problems/longest-mountain-in-array/) | Medium | 1437 |
| 237 | 2038 | [Remove Colored Pieces if Both Neighbors are the Same Color](https://leetcode.com/problems/remove-colored-pieces-if-both-neighbors-are-the-same-color/) | Medium | 1468 |
| 238 | 2900 | [Longest Unequal Adjacent Groups Subsequence I](https://leetcode.com/problems/longest-unequal-adjacent-groups-subsequence-i/) | Easy | 1469 |
| 239 | 1759 | [Count Number of Homogenous Substrings](https://leetcode.com/problems/count-number-of-homogenous-substrings/) | Medium | 1491 |
| 240 | 3011 | [Find if Array Can Be Sorted](https://leetcode.com/problems/find-if-array-can-be-sorted/) | Medium | 1497 |
| 241 | 1861 | [Rotating the Box](https://leetcode.com/problems/rotating-the-box/) | Medium | 1537 |
| 242 | 1578 | [Minimum Time to Make Rope Colorful](https://leetcode.com/problems/minimum-time-to-make-rope-colorful/) | Medium | 1574 |
| 243 | 1839 | [Longest Substring Of All Vowels in Order](https://leetcode.com/problems/longest-substring-of-all-vowels-in-order/) | Medium | 1580 |
| 244 | 2765 | [Longest Alternating Subarray](https://leetcode.com/problems/longest-alternating-subarray/) | Easy | 1581 |
| 245 | 3255 | [Find the Power of K-Size Subarrays II](https://leetcode.com/problems/find-the-power-of-k-size-subarrays-ii/) | Medium | 1595 |
| 246 | 3350 | [Adjacent Increasing Subarrays Detection II](https://leetcode.com/problems/adjacent-increasing-subarrays-detection-ii/) | Medium | 1600 |
| 247 | 3105 | [Longest Strictly Increasing or Strictly Decreasing Subarray](https://leetcode.com/problems/longest-strictly-increasing-or-strictly-decreasing-subarray/) | Easy | 1217 |
| 248 | 3926 | [Count Valid Word Occurrences](https://leetcode.com/problems/count-valid-word-occurrences/) | Medium | 1608 |
| 249 | 838 | [Push Dominoes](https://leetcode.com/problems/push-dominoes/) | Medium | 1638 |
| 250 | 467 | [Unique Substrings in Wraparound String](https://leetcode.com/problems/unique-substrings-in-wraparound-string/) | Medium |  |
| 251 | 3499 | [Maximize Active Section with Trade I](https://leetcode.com/problems/maximize-active-section-with-trade-i/) | Medium | 1729 |
| 252 | 413 | [Arithmetic Slices](https://leetcode.com/problems/arithmetic-slices/) | Medium |  |
| 253 | 3738 | [Longest Non-Decreasing Subarray After Replacing at Most One Element](https://leetcode.com/problems/longest-non-decreasing-subarray-after-replacing-at-most-one-element/) | Medium | 1811 |
| 254 | 2147 | [Number of Ways to Divide a Long Corridor](https://leetcode.com/problems/number-of-ways-to-divide-a-long-corridor/) | Hard | 1915 |
| 255 | 2593 | [Find Score of an Array After Marking All Elements](https://leetcode.com/problems/find-score-of-an-array-after-marking-all-elements/) | Medium | 1665 |
| 256 | 68 | [Text Justification](https://leetcode.com/problems/text-justification/) | Hard |  |
| 257 | 135 | [Candy](https://leetcode.com/problems/candy/) | Hard |  |
| 258 | 3872 | [Longest Arithmetic Sequence After Changing At Most One Element](https://leetcode.com/problems/longest-arithmetic-sequence-after-changing-at-most-one-element/) | Medium | 2042 |
| 259 | 2948 | [Make Lexicographically Smallest Array by Swapping Elements](https://leetcode.com/problems/make-lexicographically-smallest-array-by-swapping-elements/) | Medium | 2047 |
| 260 | 3830 | [Longest Alternating Subarray After Removing At Most One Element](https://leetcode.com/problems/longest-alternating-subarray-after-removing-at-most-one-element/) | Hard | 2162 |
| 261 | 3640 | [Trionic Array II](https://leetcode.com/problems/trionic-array-ii/) | Hard | 2278 |
| 262 | 2393 | [Count Strictly Increasing Subarrays](https://leetcode.com/problems/count-strictly-increasing-subarrays/) 🔒 | Medium |  |
| 263 | 3773 | [Maximum Number of Equal Length Runs](https://leetcode.com/problems/maximum-number-of-equal-length-runs/) 🔒 | Medium |  |
| 264 | 2436 | [Minimum Split Into Subarrays With GCD Greater Than One](https://leetcode.com/problems/minimum-split-into-subarrays-with-gcd-greater-than-one/) 🔒 | Medium |  |
| 265 | 2495 | [Number of Subarrays Having Even Product](https://leetcode.com/problems/number-of-subarrays-having-even-product/) 🔒 | Medium |  |
| 266 | 3063 | [Linked List Frequency](https://leetcode.com/problems/linked-list-frequency/) 🔒 | Easy |  |

---

## Omitted from this list

Also omitted: 5 problems exclusive to leetcode.cn (LCP / LCR / LCS / 面试题 series).
