Contributing
============

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/ashwinvis/myst-reader/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html


## Releasing

- Update [changelog](./CHANGELOG.md). Ensure the headings and the links match.
- Bump version in [pyproject.toml](./pyproject.toml)
- Switch to a new branch `git switch -c rel/<VERSION>`
- Make a commit `git commit -am "Prepare for <VERSION>"`
- Make an annotated tag `git tag <VERSION> -am <MESSAGE>`.
- Push the changes `git push --follow-tags` and GH actions should deploy the package to *Test PyPI*.
- Merge the branch
- Run the manual deploy workflow to copy the release to the main PyPI.
