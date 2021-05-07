# 1.0.15

-   Fix crash caused by YAML-tags in subproject config.

# 1.0.14

-   Support Foliant Core 1.0.12, write logs to the directory that is specified for the multiproject.

# 1.0.13

-   Keep temporary directories of built subprojects. It is needed when local includes that rewrite image paths are used.

# 1.0.12

-   Take into account the `quiet` flag. Require Foliant 1.0.11 for this reason.

# 1.0.11

-   Allow recursive processing of nested subprojects.
-   Allow to specify type (HTML/Markdown) and location for repo links.
-   Fix incompatibility with new Cliar: key names should not contain hyphens.

# 1.0.10

-   Allow the first heading to be located not in the beginning of a document.

# 1.0.9

-   Inherit the class `Cli` from `BaseCli`, not from `Cliar`.

# 1.0.8

-   Do not rewrite source Markdown file if an error occurs in RepoLink preprocessor.

# 1.0.7

-   Allow to override the `edit_uri` config option of RepoLink preprocessor with the `FOLIANT_REPOLINK_EDIT_URI` system environment variable.

# 1.0.6

-   Tidy up CLI arguments.

# 1.0.5

-   Provide Git submodules support.

# 1.0.4

-   Provide compatibility with Foliant 1.0.5. Allow to use multiple config files.

# 1.0.3

-   Fix config loading. Other small fixes.

# 1.0.2

-   Fix bugs with the project directory path and Git repos syncronizing.

# 1.0.1

-   Fix logging.
