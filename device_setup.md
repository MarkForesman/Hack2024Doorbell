# Device setup

```sh

# Install k3s

curl -sfL https://get.k3s.io | sh -

mkdir -p ~/.kube
sudo cat /etc/rancher/k3s/k3s.yaml > ~/.kube/config

sudo echo " cgroup_memory=1 cgroup_enable=memory" | sudo tee -a /boot/cmdline.txt
sudo cat /boot/cmdline.txt
sudo reboot

## Check everything works
sudo kubectl get pods -A

# Install Flux CLI

curl -s https://fluxcd.io/install.sh | sudo bash

flux check --pre

# Install Flux

flux install

# Configure flux with github repository

DEVICE_NAME="device-104"

flux create source git doorbell \
  --url=https://github.com/MarkForesman/Hack2024Doorbell.git \
  --branch=main \
  --interval=1m 
------------------------------------------------------------------------------------------------
flux create kustomization podinfo \
  --source=doorbell \
  --path="./gitops/clusters/$DEVICE_NAME" \
  --prune=true \
  --wait=true \
  --interval=1m \
  --retry-interval=2m \
  --health-check-timeout=3m 
------------------------------------------------------------------------------------------------
# Install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
DESIRED_VERSION=$HELM_VERSION ./get_helm.sh

# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
    helm install external-secrets \
    external-secrets/external-secrets \
    -n external-secrets \
    --create-namespace \
    --set installCRDs=true

export SP_CLIENT_ID="client_id"
export SP_CLIENT_SECRET="secret"


# Create Kubernetes Secrets for the ESO to access the Key Vault
sudo kubectl create secret -n external-secrets generic azkv-secret \
  --from-literal=ClientID="$SP_CLIENT_ID" \
  --from-literal=ClientSecret="$SP_CLIENT_SECRET"

```

Optional nice to have shell configuration

```sh
# Install K9s

curl -sS https://webi.sh/k9s | sh

# Add flux autocomplete to bash

. <(flux completion bash)
```
