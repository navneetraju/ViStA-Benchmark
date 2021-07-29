## Helm chart to install production ready Redis cluster

```
kubectl create ns redis
sudo helm -n redis install my-release bitnami/redis-cluster --values values-production.yaml
```