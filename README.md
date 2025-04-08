# ✨ RadixHopper ✨

[![PyPI - Version](https://img.shields.io/pypi/v/radixhopper.svg)](https://pypi.org/project/radixhopper)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/radixhopper.svg)](https://pypi.org/project/radixhopper)

-----

🌟 Hop between number bases with ease! 🌟

RadixHopper is a Python library for efficient radix-based number system conversions, specializing in cyclic fractions handling, for arbitary bases with arbitary digits (defaults to `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ` digit-set).

## ✨ Features

- 🔢 Convert numbers between radices 2 to 36 out-of-the-box, and more with custom digits!
- 🧑‍🔬 Support for scientific notation 
- 🦅 Arbitary precision operations, by leveraging fractions
- 🖥️ Support for `0x`, `0o` and `0b` format 
- 🔄 Handle cyclic fractions with grace
- 🚀 Fast evaluations with conversion buffering
- 📓 Jupyter notebook support
- 🎨 Intuitive CLI interface
<!-- - 🌈 Streamlit web app included -->

## 🌠 Installation

Sprinkle some magic into your Python environment:

```console
pip install radixhopper
```

## 🎭 Usage

### As a library

```python
from radixhopper import RadixNumber

# Create a RadixNumber instance from a string in base 10
num = RadixNumber("3.14", base=10)

# Convert it to base 2
result = num.to(base=2)

# Print the representation in base 2
print(f"{result!r}") # or simply `>>> result` or print(repr(result))
# >>> RadixNumber(number=11.0[01000111101011100001], representation_base=2, digits=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ, case_sensitive=False, fraction=(157/50))

# Access the string representation directly
print(result) 
# >>> 11.0[01000111101011100001]

# Perform operations
num2 = RadixNumber("1.1", base=2) # Represents 1.5 in base 10
sum_result = num + num2 # Operations default to Fraction representation
print(sum_result) # >>> 100.[10100011110101110000]
print(sum_result.to(base=10)) # >>> 4.64
```

### CLI

```console
radixhopper --num 3.14 --base-from 10 --base-to 2
```

or simply

```console
radixhopper 3.14 10 2
```

<!-- ### Web App

Run the Streamlit app:

```console
streamlit run radixhopper/st.py
``` -->

## 🌟 Contributing

We welcome contributions! Please check our [Issues](https://github.com/aarmn/radixhopper/issues) page for open tasks or suggest new features.

## 📜 License

`radixhopper` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## 🌠 Star Gazing

```
   *  .  . *       *    .        .        .   *    ..
  .    *        .   ✨    .      .     *   .         *
    *.   *    .    .    *    .    *   .    .   *
  .   .     *     .   ✨     .        .       .     .
    .    *.      .     .    *    .    *   .    .  *
  *   .    .    .    .      .      .         .    .
    .        .    . ✨      *   .    .   *     *
  .    *     *     .     .    *    .    *   .    .
    .    .        .           .      .        .
  *     .    . *    .     *     .        .     *
```

Happy hopping! ✨🐰✨