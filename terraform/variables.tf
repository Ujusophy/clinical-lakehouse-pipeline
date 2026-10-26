variable "region" {
  description = "AWS region for the data lake"
  type        = string
  default     = "ca-central-1"
}

variable "project" {
  description = "Project name prefix"
  type        = string
  default     = "clinical-lakehouse"
}