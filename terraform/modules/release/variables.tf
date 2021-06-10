variable "environment" {
  description = "The OpenHexa environment identifier"
  type        = string
}
variable "domain" {
  description = "The domain through with the app component will be accessed"
  type        = string
}
variable "image_tag" {
  description = "The tag of the OpenHexa app Docker image to use"
  type        = string
}
