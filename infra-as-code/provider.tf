provider "aws" {
  region = "us-east-1"

  # Default tags to apply to all resources
  default_tags {
    tags = {
      Project   = "learn-mlops-with-sagemaker"
      SageMaker = true
    }
  }

}


  