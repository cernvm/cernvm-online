# Changelog

The entries bellow are in reverse chronological order.

## v1.2.3 (14 September 2015)

* Fix santizizer for root ssh key

## v1.2.2 (20 May 2014)

* Cluster definitions can be encrypted
* CVMFS snapshot pinning for Long-Term Data Preservation
* Minor bugfixes


## v1.2.0 (x March 2014)

* Initial clean up of the code base. Former `cvmo` package is now split into:
    - `cvmo.core`: Core and common functionality
    - `cvmo.user`: User registration and profile edition UIs
    - `cvmo.dashboard`: Dashboard interface
    - `cvmo.context`: Context definition
    - `cvmo.vm`: VM deployment through WebAPI and pairing mechanism
    - `cvmo.market`: Marketplace
    - `cvmo.cluster`: Cluster definition
* Adds `cvmo.cluster` for cluster definition and deployment.
* Integration with [Twitter Bootstrap](http://getbootstrap.com/). Currently
    only affecting `cvmo.cluster`. Eventually should replace custom CSS and
    JavaScript for the template and the interactivity of CernVM Online.
* WebAPI integration is moved to `cvmo.vm` and drops need of `vmcp/sign.php`
    by implementing same functionality in the Django application.
* Integrates the project with [South](http://south.aeracode.org/) for schema
    management. Migration from v1.1.0 to v1.2.0 will required some manual
    fidling, but any other schema update should be automatic.
