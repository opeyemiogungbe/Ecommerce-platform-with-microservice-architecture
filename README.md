# Ecommerce Platform with Microservices Architecture

## Project Overview

This project is a fully containerized, cloud-native **Ecommerce Platform** built on a **Microservices Architecture**. Each service is independently developed, containerized with **Docker**, published to **Docker Hub**, and deployed to a **Kubernetes** cluster running on **Docker Desktop**.

The platform is managed entirely through **GitOps** using **Argo CD**, meaning the Kubernetes cluster continuously watches the GitHub repository and automatically applies any changes pushed to it — no manual deployments required.

Traffic from external clients enters the cluster through a single entry point — the **NGINX Ingress Controller** — which routes requests to the appropriate microservice based on the URL path.

The three core services are:

- **Product Service** — manages product listings and details
- **Cart Service** — handles shopping cart operations
- **Order Service** — processes and tracks customer orders

Each service runs independently, communicates internally via Kubernetes **ClusterIP** services, and can be updated, scaled, or redeployed without affecting the others. This architecture reflects real-world production patterns used in modern cloud-native application development.

---

## Project Architecture

```
                    +----------------------+
                    |      Client/User     |
                    +----------+-----------+
                               |
                               |
                        Ingress Controller
                      (NGINX Ingress Controller)
                               |
        -------------------------------------------------
        |                       |                       |
        |                       |                       |
+---------------+      +----------------+      +----------------+
| Product API   |      | Cart API       |      | Order API      |
| ClusterIP     |      | ClusterIP      |      | ClusterIP      |
+-------+-------+      +--------+-------+      +--------+-------+
        |                       |                       |
        |                       |                       |
     Docker Image          Docker Image           Docker Image
        |                       |                       |
        +-----------------------+-----------------------+
                                |
                           Docker Hub
                                |
                                |
                           Argo CD (GitOps)
                                |
                                |
                          GitHub Repository
```

---

## Project Structure

```
Ecommerce-platform-with-microservice-architecture/
│
├── argocd/
│   └── application.yaml          # Argo CD Application manifests (platform + ingress-nginx)
│
├── cart-service/
│   ├── app.py                    # Cart service Flask application
│   ├── Dockerfile                # Container build instructions
│   └── requirements.txt          # Python dependencies
│
├── order-service/
│   ├── app.py                    # Order service Flask application
│   ├── Dockerfile
│   └── requirements.txt
│
├── product-service/
│   ├── app.py                    # Product service Flask application
│   ├── Dockerfile
│   └── requirements.txt
│
├── K8s/
│   ├── product-service.yaml      # Deployment + ClusterIP Service
│   ├── cart-service.yaml         # Deployment + ClusterIP Service
│   ├── order-service.yaml        # Deployment + ClusterIP Service
│   ├── ingress.yaml              # Ingress routing rules
│   │
│   └── ingress-controller/       # NGINX Ingress Controller manifests
│
└── README.md
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python / Flask | Microservice application framework |
| Docker | Containerization of each service |
| Docker Hub | Centralized container image registry |
| Kubernetes | Container orchestration |
| Docker Desktop Kubernetes | Local Kubernetes cluster |
| Argo CD | GitOps continuous delivery |
| GitHub | Source of truth for manifests and code |
| NGINX Ingress Controller | API gateway / external traffic routing |

---

## Microservices

The application is split into three independently deployable services, each with its own codebase, Docker image, and Kubernetes manifest.

!(https://i.postimg.cc/NGTFm4DT/Screenshot-2026-07-24-063243.png)

---

### Product Service

Responsible for managing product information.

**Responsibilities**
- List all available products
- Retrieve individual product details

**Endpoints**
```
GET  /products
GET  /products/{id}
GET  /health
```

---

### Cart Service

Responsible for customer shopping cart operations.

**Responsibilities**
- Add an item to a cart
- Remove an item from a cart
- View cart contents

**Endpoints**
```
GET    /carts/{cart_id}
POST   /carts/{cart_id}/items        body: {"product_id": "p-100", "quantity": 2}
DELETE /carts/{cart_id}/items/{product_id}
GET    /health
```

---

### Order Service

Responsible for order processing and tracking.

**Responsibilities**
- Create a new order
- List all orders
- Retrieve a specific order

**Endpoints**
```
POST /orders        body: {"customer_id": "customer-1", "items": [{"product_id": "p-100", "quantity": 2}]}
GET  /orders
GET  /orders/{id}
GET  /health
```

---

## Containerization with Docker

Each microservice is packaged independently using its own Dockerfile. The services are built on the official Python slim image and served with Gunicorn.

**Example Dockerfile**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

Each service has its own Docker image, meaning they can be built, versioned, and deployed completely independently of one another.

---

## Docker Hub

A Docker Hub repository was created for every microservice.

```
opeyf/product-service
opeyf/cart-service
opeyf/order-service
```

!(https://i.postimg.cc/MX2z3hYG/Screenshot-2026-07-24-063227.png)

Docker Hub acts as the centralized image registry. Kubernetes pulls images from here during deployment, which means no local image builds are needed on the cluster.

---

## Building and Pushing Docker Images

**Build each service**
```bash
docker build -t opeyf/product-service:1.0.0 ./product-service
docker build -t opeyf/cart-service:1.0.0 ./cart-service
docker build -t opeyf/order-service:1.0.0 ./order-service
```
!(https://i.postimg.cc/qMbPRfKB/Screenshot-2026-07-24-091715.png)

**Login and push to Docker Hub**
```bash
docker login
docker push opeyf/product-service:1.0.0
docker push opeyf/cart-service:1.0.0
docker push opeyf/order-service:1.0.0
```
!(https://i.postimg.cc/9FRpGsSJ/Screenshot-2026-07-24-091749.png)

---

## Kubernetes Deployment

Each microservice has its own Kubernetes manifest under `K8s/`. Every manifest contains a **Deployment** and a **ClusterIP Service**.

- The **Deployment** manages the Pod lifecycle, replicas, and rolling updates
- The **Service** provides a stable internal DNS name and load balances traffic across Pods

**Why ClusterIP?**

ClusterIP exposes each service only within the cluster. Services are not directly reachable from the internet, which improves security. All external traffic enters through a single controlled point — the Ingress Controller.

Traffic flow:
```
Client → NGINX Ingress → ClusterIP Service → Pod
```

---

## NGINX Ingress Controller

Since all services use ClusterIP, they are only reachable inside the cluster. The **NGINX Ingress Controller** acts as the API gateway — a single external entry point that inspects incoming HTTP requests and routes them to the correct service based on the URL path.

The controller is deployed and managed by Argo CD using the official **ingress-nginx Helm chart**, which automatically provisions all required resources including RBAC, admission webhooks, ConfigMaps, and the controller Deployment.

---

## Ingress Resource

The Ingress resource defines the routing rules:

| Path | Service | Port |
|---|---|---|
| `/products` | product-service | 5001 |
| `/carts` | cart-service | 5002 |
| `/orders` | order-service | 5003 |

Once the Ingress Controller is running and assigned an external IP, all three services are reachable through that single IP:

```
http://<EXTERNAL-IP>/products
http://<EXTERNAL-IP>/carts/{cart_id}
http://<EXTERNAL-IP>/orders
```

---

## Installing Argo CD

Argo CD is installed inside the Kubernetes cluster to implement GitOps.

```bash
kubectl create namespace argocd

kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```
!(https://i.postimg.cc/pdTYL7D5/Screenshot-2026-07-24-094518.png)

Verify all components are running:
```bash
kubectl get pods -n argocd
```
!(https://i.postimg.cc/xTZ9ZN6Q/Screenshot-2026-07-24-095231.png)

---

## Accessing Argo CD

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

!(https://i.postimg.cc/KzT9mw20/Screenshot-2026-07-31-063731.jpg)

Open `https://localhost:8080` in your browser.

Retrieve the initial admin password:
```powershell
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }
```
!(https://i.postimg.cc/W3SdqbT2/Screenshot-2026-06-13-060426.png)

---

## Connecting GitHub to Argo CD

The `argocd/application.yaml` file defines two Argo CD Applications:

1. **ecommerce-platform** — watches the `K8s/` folder in this repository and deploys all microservice manifests and ingress rules
2. **ingress-nginx** — installs the NGINX Ingress Controller from the official Helm chart

Apply both with:
```bash
kubectl apply -f argocd/application.yaml
```
!(https://i.postimg.cc/vBmQj7FS/Screenshot-2026-07-31-082133.jpg)

From this point, any change pushed to the GitHub repository is automatically detected and applied to the cluster by Argo CD.

---

## GitOps Workflow

```
Developer pushes code
        ↓
GitHub Repository updated
        ↓
Argo CD detects the change
        ↓
Argo CD syncs the cluster
        ↓
Kubernetes applies the new state
```

No manual `kubectl apply` is needed after the initial Argo CD setup. The cluster always reflects what is in the repository.

---

## Deployment Flow

```
GitHub Repository
        ↓
Argo CD
        ↓
Kubernetes Deployment
        ↓
ClusterIP Service
        ↓
Pods
        ↓
NGINX Ingress Controller
        ↓
Client
```

---

## Challenges Encountered

### 1. Docker Desktop Networking Issues

**Problem:** Containers could not access external repositories. Symptoms included GitHub connection refused, Docker image pull failures, and Argo CD sync failures.

**Solution:** Added Google DNS (`8.8.8.8`, `8.8.4.4`) to the Docker Engine daemon config in Docker Desktop settings, then restarted Docker Desktop.

---

### 2. Argo CD Repository Authentication

**Problem:** Argo CD could not retrieve manifests from GitHub.

**Cause:** The repository URL was incorrectly configured.

**Solution:** Updated the repository URL in the Argo CD Application manifest and re-synchronized.

---

### 3. Docker Images Missing After Reset

**Problem:** Docker Desktop factory reset removed all locally stored images.

**Solution:** Images were pulled again directly from Docker Hub. Since Docker Hub is the source of truth for container images, no rebuilding was required.

---

### 4. Kubernetes Connectivity

**Problem:** `kubectl` could not connect to the Kubernetes API server after a factory reset.

**Cause:** Kubernetes had not been re-enabled in Docker Desktop after the reset.

**Solution:** Enabled Kubernetes in Docker Desktop settings and waited for the control plane to fully initialize.

---

### 5. NGINX Ingress RBAC Errors

**Problem:** A custom NGINX manifest caused repeated RBAC permission errors and controller crashes.

**Cause:** The manually written manifest was missing several required Kubernetes resources and permission bindings.

**Solution:** Replaced the custom manifest with the official `ingress-nginx` Helm chart deployed through Argo CD, which automatically provisions the complete set of required resources.

---

### 6. GitOps Synchronization Delays

**Problem:** Changes pushed to GitHub were not immediately reflected in the cluster.

**Solution:** Verified the Argo CD repository configuration, corrected the repository URL, and triggered a manual sync. Once correctly configured, automatic synchronization worked as expected.

---

## Lessons Learned

- Designing and building applications using a microservices architecture
- Containerizing Python/Flask applications with Docker
- Publishing and versioning container images on Docker Hub
- Writing Kubernetes Deployments, Services, and Ingress resources
- Using ClusterIP for secure internal service communication
- Implementing GitOps with Argo CD for automated, declarative deployments
- Deploying infrastructure components (NGINX) through Argo CD using Helm
- Exposing a multi-service application through a single Ingress entry point
- Troubleshooting Docker networking, Kubernetes RBAC, and Argo CD sync issues

---

## Future Improvements

- Deploy to **Amazon EKS** for a production-grade cloud environment
- Integrate **Kong API Gateway** for advanced traffic management, rate limiting, and authentication
- Implement **TLS termination** with cert-manager and Let's Encrypt
- Configure **Horizontal Pod Autoscaling (HPA)** based on CPU and memory metrics
- Add **Prometheus and Grafana** for metrics collection and dashboards
- Introduce **centralized logging** with the EFK or ELK stack
- Manage secrets securely using **External Secrets Operator** or **HashiCorp Vault**
- Build **CI/CD pipelines** with GitHub Actions to automate image builds and pushes on every commit

---

## Conclusion

This project demonstrates a complete, end-to-end GitOps-based deployment workflow for a microservices application. Each service is independently containerized, stored in Docker Hub, deployed to Kubernetes, and continuously synchronized from GitHub using Argo CD. By combining Docker, Kubernetes, Argo CD, and the NGINX Ingress Controller, the platform delivers a scalable, maintainable, and production-oriented architecture that reflects modern cloud-native application development practices.
