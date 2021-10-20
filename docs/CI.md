Github Actions
============

We use [Github Actions](https://docs.github.com/en/actions) to test the app.
To test actions locally we use [act](https://github.com/nektos/act)


#### Running all actions locally

```
make testci
```

#### Running selected action locally

```
make testci arguments="-j lint"
```
