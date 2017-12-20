Mario
===

Mario is a set of python scripts that builds complex pipelines of batch jobs for analysing SF Express logistics raw data. It handles data preprocessing, workflow management, visualization, command line integration, and much more. 

Background
---

The purpose of Mario is to address an unwieldy memory issue typically associated with long-running batch processes when dealing with massive data in SF project. By dint of much trying, I started thinking to decompose the analytical problem into tasks that can be executed in parallel & series, and make every component be memory-friendly. 

Basically, I borrowed the idea of hadoop that divides anything into two parts (mapping and reducing), and concatenates them with sorting. Clearly, these scripts can also be easily deployed at any real hadoop environment with [hadoop streaming API](https://hadoop.apache.org/docs/r1.2.1/streaming.html). 

Ideally, you can assemble pretty much any pipelines of tasks you want, but mario still comes with some one-button pipeline templates that you can use. It includes support for running ... 

Raw Data
---

The raw data that Mario can handle is a kind of dataset that consists of bunches of link records in same format. Each link record contains 



Getting Started
---


