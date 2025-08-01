# TODO

## Workflow
- [ ] 🔮 nix flake
- [ ] github actions (`.github` and test offline using `act`)
- [ ] ⭐ workflow move to just, tox, act
- [x] isort, flake8, black as ruff

## Documentation
- [ ] ⭐ improve pydocs (add example to em)
- [ ] improve comments
- [ ] ⭐ Improve Readme.md with examples and images and badges and re-read it

## Bugs
- [x] ⭐ chars should be limited to base bug for 0b17
- [ ] rich check
- [ ] one union of int and fraction might be extra

## Code Quality
- [ ] `__init__` of RadixNumber is hot mess
- [ ] flag handling of CLI is hot mess

## Features
- [ ] operations
- [ ] Improve errors (more helpful, like in check, what went wrong, what overlaps, ...)
- [ ] 🔮 unary base easter egg
- [ ] 🔮 handle none singular digit with list, maximal munch, and ambiguity check (should use a wrapper around the actual thing, instead of directly working with strings as digits)

## Tests
- [ ] ⭐ add unit test (octal, hex, 0x, and sci notation, zero, ...)
- [ ] tox, pytest, pytest-cov

## Deployment
- [ ] ⭐ Improved CLI (more flags like simple and ...)
- [ ] Deploy on streamlit cloud, vercel, github action, netlify or smth else, on my subdomain.

## CLI
- [ ] Never assume smth is flag, unless fully match the flag, has " to force number be a number (check for " not be in digits)
- [ ] Type check and beautify but dont use a 3rd party if it doesnt match the purpose of the project
