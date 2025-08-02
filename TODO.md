# TODO

## Workflow
- [ ] Nix flake
- [ ] github actions for release
- [ ] github actions for code linting and stuff
- [ ] github actions for testing (after adding them lol)
- [ ] ⭐ Impl just or act for the project offline workflows (aside from the trusted publisher I guess, justfile reiterate or delete)
- [x] github actions for pypi publish
- [x] isort, flake8, black as ruff

## Documentation
- [ ] ⭐ improve pydocs (add example to them)
- [ ] improve comments
- [ ] Make a cool logo
- [ ] ⭐ Improve Readme.md (more examples, asciinema, some cool badges, proof read, make a cool logo)

## Bugs
- [x] chars should be limited to base bug for 0b17
- [ ] rich existence in installer check (assuming cli mode option is checked)

## Code Quality
- [ ] `__init__` of RadixNumber is hot mess
- [ ] flag handling of CLI is hot mess
- [ ] make a POSET of operations order in init code
- [ ] why I chose to set default base to 10? why not None? (to diff between explicit and non-explicit base 10)
- [ ] get rid of one of the duo of typeguard and typer if possible

## Features
- [ ] extend operations
- [ ] Improve errors (more helpful, like in check, what went wrong, what overlaps, ...)
- [ ] unary base easter egg
- [ ] research other bases (e.g.: negative, fractional, complex, ANS, RNS, etc.)
- [ ] handle none singular digit with list, maximal munch, and ambiguity check (should use a wrapper around the actual thing, instead of directly working with strings as digits)

## Tests
- [ ] ⭐ add unit test (octal, hex, 0x, and sci notation, zero, ...)
- [ ] tox, pytest, pytest-cov

## Deployment
- [ ] ⭐ Improved CLI (more flags like simple and ...)
- [ ] Deploy on streamlit cloud, vercel, github action, netlify or smth else, on my subdomain.

## CLI
- [ ] Never assume smth is flag, unless fully match the flag, has " to force number be a number (check for " not be in digits)
- [ ] Type check and beautify but dont use a 3rd party if it doesnt match the purpose of the project
