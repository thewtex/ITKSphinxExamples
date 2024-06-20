---
name: ComputeLaplacian
---

# Compute Laplacian

```{index} single: LaplacianImageFilter
```

## Synopsis

This filter computes the Laplacian of a scalar-valued image.

## Results

:::{figure} cthead1.png
:alt: Input image
:scale: 50%

Input image
:::

:::{figure} OutputBaseline.png
:alt: Output image
:scale: 50%

Output image
:::

## Code

### Python

```{literalinclude} Code.py
:language: python
:lines: 1, 16-
```

### C++

```{literalinclude} Code.cxx
:lines: 18-
```

## Classes demonstrated

```{eval-rst}
.. breathelink:: itk::LaplacianImageFilter
```