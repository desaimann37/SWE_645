# SWE 645 – Static Website Deployment on AWS

**Name:** Mann Mihir Desai   
**Course:** SWE 645  
**Assignment:** Static Homepage and Student Survey Deployment  

---

## Overview

This assignment demonstrates the deployment of a static class homepage and a student survey form using Amazon Web Services. The class homepage is deployed using Amazon S3 static website hosting, while the student survey form built with HTML, CSS, and JavaScript is deployed on an Amazon EC2 instance using the Apache HTTP Server. Both deployments were tested to ensure accessibility and correct functionality before submission.

---

## Deployment of Static Home Page on Amazon S3

An Amazon S3 bucket was created to host the static class homepage. During bucket creation, the “Block all public access” option was unchecked to allow public access to the HTML, CSS, and JavaScript files. The static website files were uploaded directly from the local file system to the S3 bucket.

To allow public users to access the content, the bucket policy was updated to permit the `GetObject` action for all users. The following bucket policy was used for this deployment:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::swe-645-s3/*"
    }
  ]
}

After configuring permissions, static website hosting was enabled from the Properties section of the S3 bucket. The index document was set to `index.html` and the error document was set to `error.html`. Once static website hosting was enabled, the public website link was obtained from the Bucket Website Endpoint section.

The URL used for submission of the S3 static homepage is provided below:

http://swe-645-s3.s3-website-us-east-1.amazonaws.com/

---

## Deployment of Static Student Survey Form on Amazon EC2

An Amazon EC2 instance was created using the default configuration with Amazon Linux 2023 selected as the operating system. After the instance entered the running state, it was accessed using the terminal. Administrative privileges were obtained by switching to the root user.

A temporary directory named `temp` was created to store project files. The static survey website files, including HTML, CSS, and JavaScript, were retrieved by cloning a GitHub repository into this temporary directory. The public GitHub repository used for this deployment is:

https://github.com/desaimann37/SWE_645.git

Once the repository was cloned, the static website files were moved to the Apache web server’s document root directory located at `/var/www/html`. This directory is used by Apache to serve web content.

The Apache HTTP Server (`httpd`) was then installed, started, and enabled so that it runs automatically. The status of the Apache service was verified to ensure it was running successfully. After Apache was running, the website became accessible using the EC2 instance’s public IPv4 address through a web browser over the HTTP protocol on port 80.

The URL used for submission of the EC2-hosted survey application is provided below:

http://100.53.59.47/

---

## Notes

Amazon S3 static website hosting was used for deploying the class homepage. The student survey form was deployed on an Amazon EC2 instance using the Apache HTTP Server. All files were tested for accessibility and correctness prior to submission. The project satisfies all functional and deployment requirements specified in the assignment.
