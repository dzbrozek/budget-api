# budget-api

The aim of this project is to build a simple budget API. Requirements:

* every user can create his own budget (no limit on number of budgets)
* budget's creator can add new members to the budget
* budget's members can transfer money into the budget. To transfer money they have to provide title and amount
* based on transfer's title every transfer is assigned to one of categories (every category has a list of keywords)
* budget's members can withdraw money from the budget
* every budget's member can check current budget balance
* every budget's member can check history of transactions (transfers & withdraws) for selected date range

[![codecov](https://codecov.io/gh/dzbrozek/budget-api/branch/master/graph/badge.svg?token=AEIuh4ihQO)](https://codecov.io/gh/dzbrozek/budget-api)


### Development

#### Requirements

This app is using Docker so make sure you have both: [Docker](https://docs.docker.com/install/)
and [Docker Compose](https://docs.docker.com/compose/install/)

#### Prepare env variables

Copy env variables from the template

```
cp .env.template .env
```

#### Build and bootstrap the app

```
make build
make bootstrap
```

Once it's done the app should be up app and running. You can verify that visiting [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

#### Running

Next time you want to start or stop the app use `up` or `down` command.

```
make up
```

```
make down
```

#### Users

Test users created during bootstrapping the project.

| Login    | Password |
|----------|----------|
| demo     | password |

### Tests

To run the tests use `make test` command

#### API spec

API spec is available under [http://127.0.0.1:8000/api/schema/redoc/](http://127.0.0.1:8000/api/schema/redoc/).
