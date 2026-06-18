# Solutions Architect Technical Assessment

## Prerequisites

Make sure the following are installed on your machine before starting:

- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) — for `aws configure` and ECR login
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — for local development and building images
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.9 — for deploying infrastructure
- Python 3.12+ and [uv](https://docs.astral.sh/uv/getting-started/installation/) — for dependency management (`make init` handles the rest)

Make sure you have access to your favorite AI coding assistant. 

## Overview

Expected to take approximately **2 hours** to debug, deploy, and extend a document management API built with FastAPI, PostgreSQL (pgvector), and AWS Bedrock. The application runs on ECS Fargate behind an ALB, with infrastructure managed by Terraform.

The finished system is a document storage and retrieval service. Users upload documents, the system generates vector embeddings via Amazon Titan, stores them in PostgreSQL with pgvector, and exposes a semantic search endpoint. A separate extraction endpoint uses Claude via Bedrock to pull structured fields from document content.

This assessment evaluates your ability to work with a real-world codebase — reading existing code, identifying issues, completing infrastructure, and integrating AWS services.

## What's Already Deployed (via CloudFormation)

The following infrastructure has been pre-provisioned for you:

| Resource | Description |
|----------|-------------|
| VPC | 2 public subnets + 2 private subnets, Internet Gateway, NAT Gateway |
| RDS PostgreSQL 16 | pgvector-enabled, in private subnets, credentials in Secrets Manager |
| ECR Repository | For pushing your Docker images |
| S3 Bucket | Terraform state backend (versioning enabled) |
| IAM User | Scoped credentials you're using right now |

**You do NOT need to create these.** Your job is to deploy the application layer on top of them (ALB, ECS, security groups) using Terraform.

## Time Allocation

| Phase | Time | Focus |
|-------|------|-------|
| Debug & Fix | 30 min | Fix application bugs preventing local and deployed operation |
| Terraform | 45 min | Complete infrastructure modules and deploy to AWS |
| Bedrock Integration | 5 min | Wire the pre-built BedrockService into the API routes |
| Discussion | 15 min | Answer architecture questions in DISCUSSION.md |

## Deliverables

Complete as many as you can. Each builds on the previous:

1. **Application runs locally** — `make local-dev` starts without errors
   ```bash
   curl http://localhost:8080/health
   # Expected: {"status": "healthy"}
   ```

2. **POST /documents returns 201** — REST conventions followed
   ```bash
   curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8080/api/v1/documents \
     -H "Content-Type: application/json" \
     -d '{"title": "Test", "content": "Hello world"}'
   # Expected: 201
   ```

3. **Infrastructure deploys successfully** — `terraform apply` completes, ECS service stabilizes
   ```bash
   cd infrastructure/live/candidate
   terraform output alb_dns_name
   ```

4. **Application accessible via ALB** — health check passes on deployed service
   ```bash
   curl http://<alb-dns-name>/health
   # Expected: {"status": "healthy"}
   ```

5. **Bedrock integration works** — search and extract endpoints wired up and returning results (the `BedrockService` class is already implemented in `src/services/bedrock.py` — you just need to connect it to the routes in `src/app/routes/search.py`)
   ```bash
   curl -X POST http://<alb-dns-name>/api/v1/search \
     -H "Content-Type: application/json" \
     -d '{"query": "machine learning", "top_k": 3}'
   ```

6. **DISCUSSION.md completed** — architecture questions answered

## Getting Started

### 1. AWS Credentials

You have **CLI-only access** (no AWS Console login). All AWS interactions are through the `aws` CLI and Terraform.

Configure the AWS CLI with the credentials provided to you:

```bash
aws configure --profile sa-assessment
# AWS Access Key ID: <provided>
# AWS Secret Access Key: <provided>
# Default region: us-west-2
# Default output format: json
```

Verify access:

```bash
aws sts get-caller-identity --profile sa-assessment
```

### 2. Environment Setup

```bash
# Install dependencies
make init

# Copy environment template
cp env.example .env
# Edit .env with your database connection details
```

### 3. Local Development

```bash
# Start PostgreSQL (pgvector) + FastAPI locally
make local-dev

# In another terminal, verify it's running
curl http://localhost:8080/health
curl http://localhost:8080/docs  # OpenAPI documentation
```

### 4. Deployment Workflow

Once the application works locally:

```bash
# 1. Configure Terraform variables
cp infrastructure/live/candidate/terraform.tfvars.example infrastructure/live/candidate/terraform.tfvars
# Edit terraform.tfvars with your values (VPC ID, subnet IDs, etc.)

# 2. Initialize and apply Terraform
make tf-init
make tf-plan
make tf-apply

# 3. Build and push Docker image to ECR
make deploy-build

# 4. Deploy to ECS
make ecs-deploy
```

### 5. Retrieve ALB DNS

After Terraform applies successfully:

```bash
cd infrastructure/live/candidate
terraform output alb_dns_name
```

Use this DNS name to verify your deployed application.

## Project Structure

```
.
├── src/                    # Application source code
│   ├── app/               # FastAPI routes and dependencies
│   ├── common/            # Settings and logging
│   ├── db/                # Database engine and connection
│   ├── models/            # SQLAlchemy models and Pydantic schemas
│   └── services/          # Business logic (documents, bedrock)
├── docker/                # Dockerfile and docker-compose
├── infrastructure/        # Terraform modules
│   ├── live/candidate/    # Root module (backend, providers, module calls)
│   └── modules/           # ECR, ECS, ALB modules
├── tests/                 # Test suite
├── data/                  # Sample documents for testing
├── config/                # Logging configuration
├── pyproject.toml         # Python dependencies
├── Makefile               # Development commands
└── DISCUSSION.md          # Architecture discussion questions
```

## Prioritization Guidance

- **Partial completion is perfectly fine.** We value clear reasoning over finishing everything.
- If you get stuck on one phase, document what you tried and move on.
- Commit frequently with descriptive messages — we review your process, not just the end state.
- The DISCUSSION.md questions are independent of the coding tasks. Answer them even if you don't finish deploying.

## Useful Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available targets |
| `make local-dev` | Start local dev environment |
| `make local-stop` | Stop local services |
| `make test` | Run tests with coverage |
| `make check` | Run linting and type checks |
| `make tf-init` | Initialize Terraform |
| `make tf-plan` | Plan infrastructure changes |
| `make tf-apply` | Apply infrastructure changes |
| `make deploy-build` | Build and push Docker image |
| `make ecs-deploy` | Force new ECS deployment |

## Debugging (CLI-only — no Console access)

Since you have programmatic access only, use these commands to inspect your deployed resources:

```bash
# Check ECS service status and running tasks
aws ecs describe-services --cluster nmd-sa-<your-name>-cluster \
  --services nmd-sa-<your-name>-api --profile sa-assessment --region us-west-2

# List running tasks
aws ecs list-tasks --cluster nmd-sa-<your-name>-cluster \
  --profile sa-assessment --region us-west-2

# View ECS task logs (after getting task ID from above)
aws logs get-log-events --log-group-name /ecs/nmd-sa-<your-name> \
  --log-stream-name <stream-name> --profile sa-assessment --region us-west-2

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn <tg-arn> \
  --profile sa-assessment --region us-west-2

# Describe your security groups
aws ec2 describe-security-groups --profile sa-assessment --region us-west-2 \
  --filters "Name=vpc-id,Values=<your-vpc-id>"

# Get RDS password from Secrets Manager
aws secretsmanager get-secret-value --secret-id <rds-secret-arn> \
  --profile sa-assessment --region us-west-2 --query 'SecretString' --output text
```

## Submission

1. Push all changes to your repository (commit early and often)
2. Ensure `DISCUSSION.md` is filled out
3. Verify your deployed service is accessible (if you reached that phase)

Good luck!
