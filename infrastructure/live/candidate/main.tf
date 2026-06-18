terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    key          = "candidate/terraform.tfstate"
    region       = "us-west-2"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project   = var.project_name
      Owner     = var.candidate_name
      ManagedBy = "terraform"
    }
  }
}

locals {
  name_prefix = "nmd-sa-${var.candidate_name}"
  tags = {
    Project   = var.project_name
    Owner     = var.candidate_name
    ManagedBy = "terraform"
  }
}

# =============================================================================
# Compute
# =============================================================================
module "ecs" {
  source = "../../modules/ecs"

  name_prefix           = local.name_prefix
  vpc_id                = var.vpc_id
  private_subnet_ids    = var.private_subnet_ids
  ecr_repository_url    = var.ecr_repository_url
  alb_target_group_arn  = module.alb.target_group_arn
  alb_security_group_id = module.alb.security_group_id
  aws_region            = var.aws_region
  database_url          = var.database_url
  tags                  = local.tags
}

# =============================================================================
# Load Balancer
# =============================================================================
module "alb" {
  source = "../../modules/alb"

  name_prefix       = local.name_prefix
  vpc_id            = var.vpc_id
  public_subnet_ids = var.public_subnet_ids
  tags              = local.tags
}
