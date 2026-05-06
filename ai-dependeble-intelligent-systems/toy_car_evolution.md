# The Super-Toy-Car Contest 🏎️✨

Imagine you are a toy maker. You want to build the **best car ever**! To do that, you have two goals:
1.  **Be Super Strong!** (Reliability - it won't break when it hits a wall).
2.  **Be Super Cheap!** (Cost - it only costs a few gold coins to make).

### 📍 How to read the Map of Cars:
Each letter (**a, b, c...**) is the **Name** of a specific toy car design. Where they are on the map tells us how good they are:
*   **UP = STRONGER:** The higher the car is, the better it is at not breaking.
*   **LEFT = CHEAPER:** The further left the car is, the less it costs to make.

### 🗺️ The Map of Cars
Here is where each car sits. Remember: **Higher up is Stronger**, and **Further left is Cheaper**.

```text
Stronger ↑
         |          (g)---(k)
         |      (e)  |     |
         |  (d)      (h)---(l)
         |      (f)     (j)
         |  (b)    (i)
         |      (c)
         |(a)
         +------------------------->
          Cheaper             Costlier
```

**The Golden Rule:** A car is "The Boss" of another car if it is **Higher** (Stronger) AND **Further Left** (Cheaper) than the other one!

---

## 1. The "Big Boss" Cars (Choosing between g, h, k, l)

**Question:** If you have to pick the best car from the group **{g, h, k, l}**, which one would you pick?

**Answer:** We pick **g**! 🏆

**Why?**
*   **g vs h:** g is stronger than h for the same price. (g wins!)
*   **k vs l:** k is stronger than l for the same price. (k wins!)
*   **g vs k:** g and k are equally strong, but **g is cheaper**! 
Since g is just as strong as k but costs less, g is the absolute best of the four.

---

## 2. Why does Car 'f' have a score of 3? (D(f) = 3)

**Answer:** Because **2 other cars** are better than it! 
A car gets 1 point just for being there, plus 1 point for every car that beats it.
*   **Car 'd'** beats f (it's stronger AND cheaper!).
*   **Car 'e'** beats f (it's stronger AND cheaper!).
*   Since 2 cars beat it, we do 2 + 1 = **3**.

---

## 3. The "How Many Beat Me?" List (D-score)

Here is the score for every car. Remember: **1 is the best score!** It means no one is better than you in both ways.

*   **a**: 1 (The Cheapest!)
*   **b**: 1 (No one is cheaper AND stronger)
*   **c**: 2 (Car b beats it)
*   **d**: 1 (No one is cheaper AND stronger)
*   **e**: 1 (No one is cheaper AND stronger)
*   **f**: 3 (Cars d and e beat it)
*   **g**: 1 (The Strongest Boss!)
*   **h**: 2 (Car g beats it)
*   **i**: 3 (Cars b and d beat it)
*   **j**: 7 (Lots of cars like b, d, e, f, g, h beat it)
*   **k**: 2 (Car g beats it because g is cheaper!)
*   **l**: 3 (Cars g and k beat it)

**Vector Result:** `[1, 1, 2, 1, 1, 3, 1, 2, 3, 7, 2, 3]`

---

## 4. The "Super-Car" Team (Pareto Front)

**Question:** Which cars are on the Super-Car team?
**Answer:** The ones with a score of 1: **{a, b, d, e, g}** 🏅 
*(Note: k is not here because g is better!)*

---

## 5. Who gets to have babies? (Evolution)

**Question:** Which cars will the robot choose to make the next generation of cars?
**Answer:** The **Super-Cars** (a, b, d, e, g)!

**Why?**
Because they are the **leaders**. We don't want to copy a car like 'k' if we already have 'g' which is exactly the same but cheaper. We only keep the very best ideas! 🚀
