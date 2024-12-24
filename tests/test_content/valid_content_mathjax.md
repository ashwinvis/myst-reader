---
title: "MathJax Content"
author: "My Author"
date: "2020-10-16"
---
<script type="text/javascript" id="MathJax-script" async
  src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
</script>

## Math role

Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`.

```{math}
:label: mymath
(a + b)^2 = a^2 + 2ab + b^2

(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
```

The equation {eq}`mymath` is a quadratic equation.

## With extension: `dollarmath`

$$
(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
$$ (mymath2)

The equation {eq}`mymath2` is also a quadratic equation.

Here is an inline equation $x + 3y = 5$.
Here is a some money $10 which should not be converted.

## With extension: amsmath

\begin{gather*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\end{gather*}

\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}
