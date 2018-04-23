# MultiProject Extension

MultiProject is an extension for Foliant to generate the documentation from multiple sources. MultiProject consists of three parts:

* extension for `foliant.config` package to resolve the `!from` YAML tag;
* CLI extension for the `src` command;
* RepoLink preprocessor.

## Installation

```bash
$ pip install foliantcontrib.multiproject
```

## Config Extension to Resolve the `!from` Tag

This extension resolves the `!from` YAML tag in the project config and replaces the value of the tag with `chaptres` section of related subproject.

### Usage

The subproject location may be specified as a local path, or as a Git repository with optional revision (branch name, commit hash or another reference).

Example of `chapters` section in the project config:

```yaml
chapters:
    - index.md
    - !from local_dir
    - !from https://github.com/foliant-docs/docs.git
    - !from https://github.com/some_other_group/some_other_repo.git#develop
```

Before building the documentation superproject, Multiproject extension calls Foliant to build each subproject into `pre` target, and then moves the directories of built subprojects into the source directory of the superproject (usually called as `src`).

## CLI Extension for the `src` Command

This extension supports the command `src` to backup the source directory of Foliant project (usually called as `src`) and to restore it from prepared backup.

Backing up of the source directory is needed because MultiProject extension modifies this directory by moving the directories of built subprojects into it.

### Usage

To make a backup of the source directory, use the command:

```bash
$ foliant src backup
```

To restore the source directory from the backup, use the command:

```bash
$ foliant src restore
```

## RepoLink Preprocessor

This preprocessor allows to add into each Markdown source a hyperlink to the related file in Git repository. The hyperlink appears after the first heading of the document.

The preprocessor emulates MkDocs behavior and supports the same options `repo_url` and `edit_uri` as MkDocs. Applying of the preprocessor to subprojects allows to get links to separate repositories from different pages of a single site (or a single MkDocs project).

## Usage

To enable the preprocessor, add `repolink` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - repolink
```

The preprocessor has a number of options:

```yaml
preprocessors:
    - repolink:
        repo_url: https://github.com/foliant-docs/docs/
        edit_uri: /blob/master/src/
        link_text: "&#xE3C9;"
        link_title: View the source file
        link_html_attributes: "class=\"md-icon md-content__icon\" style=\"margin: -7.5rem 0\""
        targets:
            - pre
```

`repo_url`
:   URL of the related repository. Default value is an empty string; in this case the preprocessor does not apply. Trailing slashes do not affect.

`edit_uri`
:   Revision-dependent part of URL of each file in the repository. Default value is `/blob/master/src/`. Leading and trailing slashes do not affect.

`link_text`
:   Hyperlink text. Default value is `Edit this page`.

`link_title`
:   Hyperlink title (the value of `title` HTML attribute). Default value is also `Edit this page`.

`link_html_attributes`
:   Additional HTML attributes for the hyperlink. By using CSS in combination with `class` attribute, and/or `style` attribute, you may customize the presentation of your hyperlinks. Default value is an empty string.

`targets`
:   Allowed targets for the preprocessor. If not specified (by default), the preprocessor applies to all targets.
