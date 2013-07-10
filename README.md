# alchemist
> A server architecture built on top of a solid foundation provided by flask, sqlalchemy, and various extensions.

**Alchemist** provides sane defaults, customizations, and various utilities to already powerful tools with the goal make it *easy* to accomplish common tasks, yet still be able to scale out to meet complex requirements.

## Management
The management layer utilizes [flask-script][] and provides a collection of built-in commatnds that make use of the configuration layer to provide immediate utility.

[flask-script]: http://flask-script.readthedocs.org/en/latest/

A benefit of a CLI over a `manage.py` proxy through flask-script is that **alchemist** will detect your flask application (just as `git` will detect your git repository) from any level inside your project structure.

```sh
$ pwd
/projects/example

$ alchemist show
<Flask example>

$ alchemist runserver
 * Running on http://localhost:8000/

$ cd some/path/deep/within
$ alchemist show
<Flask example>

$ alchemist runserver
 * Running on http://localhost:8000/
```

#### show

```sh
$ alchemist show
```

Prints the name of the application discovered by **alchemist**.

#### runserver

```sh
$ alchemist runserver <port> [options]
```

Runs the development server for the flask application.

> **Warning!** This *development* server is not intended for production use.

#### shell

```sh
$ alchemist shell
```

Starts a python shell with an established database session and all discovered models from each package in the `PACKAGES` setting imported into scope.

This will use IPython if it is installed, otherwise it defaults to the standard python shell.

### Database

Contains various commands to control and manage the database.

#### Default options

All database commands support the following options:

##### --sql

```sh
$ alchemist db <command> --sql
```

Use `--sql` on any database operation to not actually perform the operation but print all SQL that would be executed to stdout`.

#### db init

```sh
$ alchemist db init [package0, package1...] [options]
```

Creates the database tables for all packages registered in `PACKAGES` whose tables have not already been created.

A list of packages may be specified to initialize a specific package or set of packages.

#### db clear

```sh
$ alchemist db clear [package0, package1...] [options]
```

Drops the database tables for all packages registered in `PACKAGES` whose tables exist in the database.

A list of packages may be specified to drop a specific package or set of packages.

#### db flush

```sh
$ alchemist db flush [package0, package1...] [options]
```

Delete all data from the database tables all packages registered in `PACKAGES` whose tables exist in the database.

A list of packages may be specified to delete data for a specific package or set of packages.

## License
Unless otherwise noted, all files contained within this project are liensed under the MIT opensource license. See the included file LICENSE or visit [opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT
