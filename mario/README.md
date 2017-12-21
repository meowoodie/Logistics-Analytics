Mario
===

Mario is a set of python scripts that builds complex pipelines of batch jobs for analysing SF Express logistics raw data by (Spark)[https://spark.apache.org/docs/0.9.0/index.html]. It handles data preprocessing, workflow management, machine learning, visualization, command line integration, and much more. 

Background
---

The purpose of Mario is to address an unwieldy memory issue typically associated with long-running batch processes when dealing with massive data in SF Express project. By dint of much trying, I started thinking to decompose the analytical problem into tasks that can be executed in parallel & series, and make every component be memory-friendly. 

Basically, I rewrote all the feature service logic for Mario that requires high frequency R&W manipulations on the large raw dataset by (PySpark)[https://spark.apache.org/docs/0.9.0/python-programming-guide.html]. Clearly, by deploying computation on Spark, Mario makes the workflow easy to design without concern about insufficient memory, and it also greatly improves computational performance.

Ideally, you can assemble pretty much any pipelines of tasks you want, but mario still comes with some one-button pipeline templates that you can use. It includes support for running ... 

Change Log
---
***Dec 21, 2017*** Calculating specific computation task by running script directly.  


