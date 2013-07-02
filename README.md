# alchemist
> A server architecture built on top of a solid foundation provided by flask, sqlalchemy, and various extensions.

**Alchemist** provides sane defaults, customizations, and various utilities to already powerful tools with the goal make it *easy* to accomplish common tasks, yet still be able to scale out to meet complex requirements (eg. routing to multiple databases).

## Management
The management layer utilizes [flask-script][] and provides a collection of built-in commatnds that make use of the configuration layer to provide immediate utility.

[flask-script]: http://flask-script.readthedocs.org/en/latest/

#### alchemist version [project|alchemist|sqlalchemy|flask]

Run this command to display the current version of the specified component; if unspecified, displays the version of all components.

### Database

Contains various commands to control and manage the database.

##### --sql

Use `--sql` on any database operation to not actually perform the operation but print all SQL that would be executed to `stdout`.

#### alchemist db init [package0, package1...] [options]

Creates the database tables for all packages registered in `PACKAGES` whose tables have not already been created.

A list of packages may be specified to initialize a specific package or set of packages.

#### alchemist db clear [package0, package1...] [options]

Drops the database tables for all packages registered in `PACKAGES` whose tables exist in the database.

A list of packages may be specified to drop a specific package or set of packages.

#### alchemist db flush [package0, package1...] [options]

Delete all data from the database tables all packages registered in `PACKAGES` whose tables exist in the database.

A list of packages may be specified to delete data for a specific package or set of packages.

## License
Unless otherwise noted, all files contained within this project are liensed under the MIT opensource license. See the included file LICENSE or visit [opensource.org][] for more information.

[opensource.org]: http://opensource.org/licenses/MIT