locals {
  local_folder_feature_engineering_dataset = "${path.module}/../applications/feature-engineering/dataset"
}
resource "random_pet" "random_name" {
  length    = 2 # Adjust the length for how many words you want
  separator = "-"
}

# Create S3 bucket
resource "aws_s3_bucket" "mlops_learner_bucket" {
  bucket = format("mlops-training-sagemaker-%s", random_pet.random_name.id)
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_object" "feature_engineering_uploaded_files" {
  for_each = fileset(local.local_folder_feature_engineering_dataset, "*")
  bucket   = aws_s3_bucket.mlops_learner_bucket.bucket
  key      = "feature-engineering/dataset/${each.value}"
  source   = "${local.local_folder_feature_engineering_dataset}/${each.value}"
  etag     = filemd5("${local.local_folder_feature_engineering_dataset}/${each.value}")
  lifecycle {
    prevent_destroy = false
  }
}


module "setup-sagemaker-for-mlops" {
  source = "./tf-modules/setup-sagemaker"
}


