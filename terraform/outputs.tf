output "bucket_name" {
  value = aws_s3_bucket.lake.id
}

output "pipeline_user" {
  value = aws_iam_user.pipeline.name
}