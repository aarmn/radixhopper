# ✨ RadixHopper ✨

[![PyPI - Version](https://img.shields.io/pypi/v/radixhopper.svg)](https://pypi.org/project/radixhopper)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/radixhopper.svg)](https://pypi.org/project/radixhopper)

-----

🌟 Hop between number bases with ease! 🌟

RadixHopper is a Python library for efficient radix-based number system conversions, specializing in cyclic fractions handling, for bases 2 through 36.

## ✨ Features

- 🔢 Convert numbers between bases 2 to 36
- 🔄 Handle cyclic fractions with grace
- 🚀 Lightning-fast conversions
- 🎨 Beautiful CLI interface
- 🌈 Streamlit web app included

## 🌠 Installation

Sprinkle some magic into your Python environment:

```console
pip install radixhopper
```

## 🎭 Usage

### As a library

```python
from radixhopper import BaseConverter, ConversionInput

input_data = ConversionInput(num="3.14", base_from=10, base_to=2)
result = BaseConverter.base_convert(input_data)
print(result)  # Output: 11.0[01000111101011100001]
```

### CLI

```console
radixhopper --num 3.14 --base-from 10 --base-to 2
```

### Web App

Run the Streamlit app:

```console
streamlit run radixhopper/st.py
```

## 🌟 Contributing

We welcome contributions! Please check our [Issues](https://github.com/aarmn/radixhopper/issues) page for open tasks or suggest new features.

## 📜 License

`radixhopper` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## ✅ TODO

- [x] Make it an actual pip package
- [x] CLI interface using fire
- [ ] Deploy on streamlit cloud, vercel, github action, netlify or smth else, on my subdomain.
- [ ] Add a better hint in web GUI for signs and stuff
- [ ] Improve Readme.md with examples and images and badges and re-read
- [ ] Typing and DX of library improve
- [ ] DevOps workflow setup
  - [ ] `.github` and test offline using `act`
  - [ ] mypy
  - [ ] tox
  - [ ] pytest
  - [ ] pytest-cov
  - [ ] black
  - [ ] isort
  - [ ] flake8
  - [ ] just file improve
- [ ] Improve data taking in and out structure

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