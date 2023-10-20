# Keycloak

The CAB dedicated Keycloak instance is deployed in the `cab-auth` namespace using generic Helm chart templates.

> :warning: Applying directly Helm charts with values to the old 1.18 interne cluster does fail. Writing manifest is very pénible, so the solution is to use helm templating.

As usual, secrets are created before deploying, using the `/dev/urandom` command.

**URL**: https://cab-keycloak.irtsystemx.org/auth

## Helm Templating
- To install Helm and get the repositories, see this wiki [page](https://wiki.irt-systemx.fr/drt/ILI/first-aid-dev/work-with-helm).
- To configure you local **kubectl** (kubernetes CLI), see [here](https://wiki.irt-systemx.fr/drt/ILI/first-aid-dev/kubernetes_for_dev)


### Postgresql
```sh
helm show values bitnami/postgresql > postgres_values.yaml
# Modify postgres_values.yaml with needed values for Keycloak!
helm template cab-postgres bitnami/postgresql -f postgres_values.yaml
k login interne
kubens cab-auth
kubectl create secret generic cab-postgres --from-literal=postgres-password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '') --from-literal=password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '') --from-literal=replication-password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '')
# Careful !! Remove seccomp in spec container before applying.
k apply -f cab-postgres.yaml
```

### Keycloak
```sh
helm show values bitnami/keycloak > values.yaml
# Modify values.yaml
helm template cab-keycloak bitnami/keycloak -f values.yaml
k login interne
kubens cab-auth
kubectl create secret generic cab-keycloak-secret --from-literal=admin-password=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '')
# Careful !! Remove seccomp in spec container before applying.
# Adapt ingress to api v1beta1 (1.18 cluster...)
k apply -f cab-keycloak.yaml
```

## Realm and Client creation
The operator-fabric gives two json files that could have been used to import all data (realm, clients, roles, users) in Keycloak, but it would not work for the latest Keycloak versions.

- [dev-realm.json](of-config/cab-keycloak/export/dev-realm.json)
- [dev-users-0](of-config/cab-keycloak/export/dev-users-0.json)

The Keycloak server resources were added **manually** to mirror the previous embedded dev version. Check this configuration on the **admin console**: https://cab-keycloak.irtsystemx.org/auth/admin/.

- realm: `dev`
- client: `opfab-client`

> The admin Keycloak interface **password** can be found in the corresponding Kubernetes secret.
