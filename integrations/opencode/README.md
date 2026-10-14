# RepoMap for OpenCode

A custom `/repomap` command that adds a filtered project tree to OpenCode's prompt.
It uses OpenCode's existing command-file and shell-output support; it is not a
built-in OpenCode feature or an installed JavaScript plugin.

## Setup

1. Clone RepoMap and install it into the Python environment available to OpenCode:

   ```sh
   git clone https://github.com/Palladiymateria/repomap.git
   cd repomap
   python -m pip install .
   ```

2. In the project you want to explore, create `.opencode/commands/` and copy
   [`repomap.md`](repomap.md) into it. Do not overwrite an existing command of the
   same name. For a global command, use `~/.config/opencode/commands/` instead.

3. Run `python -m repomap . --depth 4` in that project to verify the same Python
   environment can find RepoMap. If your interpreter is named `python3`, change
   `python` to `python3` in the command file as well.

4. Open OpenCode in that project and type:

   ```text
   /repomap where is authentication implemented?
   ```

OpenCode runs the fixed shell command in the project root and includes its stdout
in the prompt. Your question is inserted as prompt text, not as shell arguments.
The plan agent explains the tree and suggests relevant files to inspect.

## Scope

This command sends a tree of filenames to your configured model through OpenCode;
it does not automatically bundle source contents. Filename exclusions are not a
secret scanner. Filenames themselves can be sensitive. Normal OpenCode model
usage and charges still apply.

To supply selected source content, generate and review a bundle yourself:

```sh
python -m repomap . --bundle --include "*.py" --max-total-kb 256 -o context.md
```

Then reference `@context.md` in OpenCode. The limit covers source bytes, not model
tokens. Review the skipped-content section to understand what was omitted.

See [OpenCode custom commands](https://opencode.ai/docs/commands/) for command
configuration and permissions. The shell command is covered by RepoMap's tests;
an interactive OpenCode model session is not part of the automated test suite.
