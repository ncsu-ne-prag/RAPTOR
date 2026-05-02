# table of contents
<!-- TOC -->
* [scram-profiling](#scram-profiling)
  * [1.introduction](#1introduction)
    * [1.1.scram](#11scram)
    * [1.2.vtune](#12vtune)
  * [2.methodology](#2methodology)
    * [2.1.preparing scram](#21preparing-scram)
    * [2.2.input file creation](#22input-file-creation)
    * [2.3.profiler set up](#23profiler-set-up)
      * [2.3.1.performance snap shot analysis](#231performance-snap-shot-analysis)
      * [2.3.2.hotspot analysis](#232hotspot-analysis)
      * [2.3.3.threading analysis](#233threading-analysis)
* [notebook](#notebook)
  * [1.25.23](#12523)
    * [Performance Snapshot Analysis](#performance-snapshot-analysis)
    * [Hotspot Analysis](#hotspot-analysis)
    * [Threading Analysis](#threading-analysis)
    * [Microarchitecture Exploration](#microarchitecture-exploration)
  * [1.24.23](#12423)
  * [1.14.23](#11423)
    * [Comparison of results for different configurations for ```BE_500_1_CCF```](#comparison-of-results-for-different-configurations-for-be5001ccf)
  * [1.13.23](#11323)
    * [Comparison of results for different configurations for ```BE_500_1_CCF```](#comparison-of-results-for-different-configurations-for-be5001ccf-1)
  * [1.5.23](#1523)
  * [1.4.23](#1423)
  * [12.19.22](#121922)
  * [12.1.22](#12122)
  * [11.17.22](#111722)
* [Note about Computer Used in This Study](#note-about-computer-used-in-this-study)
<!-- TOC -->

# scram-profiling

## 1.introduction
This readme file is under construction. I use this file as a roadmap how to profile [scram](https://gitlab.openpra.org/scram/scram) pra tool.

### 1.1.scram
[scram](https://gitlab.openpra.org/scram/scram) is an open-source pra tool. 
### 1.2.vtune
[vtune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html#gs.n2clij) is developed by Intel to find and fix performance bottlenecks.
## 2.methodology
Profiling of [scram](https://gitlab.openpra.org/scram/scram) will be done in three steps. First step is making scram ready to be profiled. [scram](https://gitlab.openpra.org/scram/scram) should be compiled in release mode with debug information. The second step is to create a fault tree that may take a quite time to quantify. After scram and input file are ready, it is time to configure [vtune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html#gs.n2clij). 
### 2.1.preparing scram
[scram](https://gitlab.openpra.org/scram/scram) should be compiled in release mode with debug information.
### 2.2.input file creation

### 2.3.profiler set up


#### 2.3.1.performance snap shot analysis

#### 2.3.2.hotspot analysis

#### 2.3.3.threading analysis


***
# notebook

This notebook is for tracking what I do step by step. It does not only include right steps that I did, but also includes mistakes.
## 1.25.23

### Performance Snapshot Analysis

| #   | Configuration                                                                                | Elapsed Time (sec) | Logical Core Utilization   | Microarchitecture Usage | Memory Bound (%)        | Vectorization (%)            |
|-----|----------------------------------------------------------------------------------------------|--------------------|----------------------------|-------------------------|-------------------------|------------------------------|
| 1.a | ```--probability --ccf --mocus --mcub --importance --uncertainty --num-trials 10000```       | 4,732.030          | **24.6% (0.985 out of 4)** | 75.3% of Pipeline Slots | 1.8% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 1.b | ```--probability --ccf --mocus --mcub --importance```                                        | 2,265.533          | **24.6% (0.984 out of 4)** | 73.3% of Pipeline Slots | 2.7% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 1.c | ```--probability --ccf --mocus --mcub```                                                     | 7.449              | **24.3% (0.972 out of 4)** | 52.9% of Pipeline Slots | 8.3% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 2.a | ```--probability --ccf --mocus --rare-event --importance --uncertainty --num-trials 10000``` | 4,828.218          | **24.4% (0.976 out of 4)** | 75.5% of Pipeline Slots | 1.8% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 2.b | ```--probability --ccf --mocus --rare-event --importance ```                                 | 2212.874           | **24.7% (0.989 out of 4)** | 75.7% of Pipeline Slots | 2.2% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 2.c | ```--probability --ccf --mocus --rare-event```                                               | 7.503              | **24.1% (0.962 out of 4)** | 52.9% of Pipeline Slots | 9.7% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 3.a | ```--probability --ccf --bdd --importance --uncertainty --num-trials 10000```                | 7.365              | **24.4% (0.976 out of 4)** | 50.6% of Pipeline Slots | 10.4% of Pipeline Slots | 0.0% of Packed FP Operations |
| 3.b | ```--probability --ccf --bdd --importance```                                                 | 14.755             | **12.6% (0.504 out of 4)** | 54.1% of Pipeline Slots | 9.3% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 3.c | ```--probability --ccf --bdd```                                                              | 6.585              | **24.1% (0.965 out of 4)** | 49.8% of Pipeline Slots | 10.0% of Pipeline Slots | 0.0% of Packed FP Operations |
| 4.a | ```--probability --ccf --zbdd --importance --uncertainty --num-trials 10000```               | 674.597            | **24.6% (0.983 out of 4)** | 74.3% of Pipeline Slots | 2.5% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 4.b | ```--probability --ccf --zbdd --importance```                                                | 330.400            | **24.4% (0.976 out of 4)** | 71.3% of Pipeline Slots | 3.4% of Pipeline Slots  | 0.0% of Packed FP Operations |
| 4.c | ```--probability --ccf --zbdd```                                                             | 6.570              | **24.0% (0.962 out of 4)** | **49.3% of Pipeline Slots** | 9.4% of Pipeline Slots  | 0.0% of Packed FP Operations |

* #### 1.a ```--probability --ccf --mocus --mcub --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/1.a_ps.png "Performance Snaphot of the Configuration 1.a")
***
* #### 1.b ```--probability --ccf --mocus --mcub --importance```
![](/home/egemen/Pictures/Screenshots/1.b_ps.png "Performance Snaphot of the Configuration 1.b")
***
* #### 1.c ```--probability --ccf --mocus --mcub```
![](/home/egemen/Pictures/Screenshots/1.c_ps.png "Performance Snaphot of the Configuration 1.c")
***
* #### 2.a ```--probability --ccf --mocus --rare-event --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/2.a_ps.png "Performance Snaphot of the Configuration 2.a")
***
* #### 2.b ```--probability --ccf --mocus --rare-event --importance ```
![](/home/egemen/Pictures/Screenshots/2.b_ps.png "Performance Snaphot of the Configuration 2.b")
***
* #### 2.c ```--probability --ccf --mocus --rare-event```
![](/home/egemen/Pictures/Screenshots/2.c_ps.png "Performance Snaphot of the Configuration 2.c")
***
* #### 3.a ```--probability --ccf --bdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/3.a_ps.png "Performance Snaphot of the Configuration 3.a")
***
* #### 3.b ```--probability --ccf --bdd --importance```
![](/home/egemen/Pictures/Screenshots/3.b_ps.png "Performance Snaphot of the Configuration 3.b")
***
* #### 3.c ```--probability --ccf --bdd```
![](/home/egemen/Pictures/Screenshots/3.c_ps.png "Performance Snaphot of the Configuration 3.c")
***
* #### 4.a ```--probability --ccf --zbdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/4.a_ps.png "Performance Snaphot of the Configuration 4.a")
***
* #### 4.b ```--probability --ccf --zbdd --importance```
![](/home/egemen/Pictures/Screenshots/4.b_ps.png "Performance Snaphot of the Configuration 4.b")
***
* #### 4.c ```--probability --ccf --zbdd```
![](/home/egemen/Pictures/Screenshots/4.c_ps.png "Performance Snaphot of the Configuration 4.c")
***
### Hotspot Analysis

* #### 1.a ```--probability --ccf --mocus --mcub --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/1.a_hs.png "Hotspot Analysis of the Configuration 1.a")
***
* #### 1.b ```--probability --ccf --mocus --mcub --importance```
![](/home/egemen/Pictures/Screenshots/1.b_hs.png "Hotspot Analysis of the Configuration 1.b")
***
* #### 1.c ```--probability --ccf --mocus --mcub```  
![](/home/egemen/Pictures/Screenshots/1.c_hs.png "Hotspot Analysis of the Configuration 1.c")
***
* #### 2.a ```--probability --ccf --mocus --rare-event --importance --uncertainty --num-trials 10000``` 
![](/home/egemen/Pictures/Screenshots/2.a_hs.png "Hotspot Analysis of the Configuration 2.a")
***
* #### 2.b ```--probability --ccf --mocus --rare-event --importance ``` 
![](/home/egemen/Pictures/Screenshots/2.b_hs.png "Hotspot Analysis of the Configuration 2.b")
***
* #### 2.c ```--probability --ccf --mocus --rare-event```
![](/home/egemen/Pictures/Screenshots/2.c_hs.png "Hotspot Analysis of the Configuration 2.c")
***
* #### 3.a ```--probability --ccf --bdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/3.a_hs.png "Hotspot Analysis of the Configuration 3.a")
***
* #### 3.b ```--probability --ccf --bdd --importance``` 
![](/home/egemen/Pictures/Screenshots/3.b_hs.png "Hotspot Analysis of the Configuration 3.b")
***
* #### 3.c ```--probability --ccf --bdd```
![](/home/egemen/Pictures/Screenshots/3.c_hs.png "Hotspot Analysis of the Configuration 3.c")
***
* #### 4.a ```--probability --ccf --zbdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/4.a_hs.png "Hotspot Analysis of the Configuration 4.a")
***
* #### 4.b ```--probability --ccf --zbdd --importance```
![](/home/egemen/Pictures/Screenshots/4.b_hs.png "Hotspot Analysis of the Configuration 4.b")
***
* #### 4.c ```--probability --ccf --zbdd```
![](/home/egemen/Pictures/Screenshots/4.c_hs.png "Hotspot Analysis of the Configuration 4.c")

### Threading Analysis

* #### 1.a ```--probability --ccf --mocus --mcub --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/1.a_th.png "Threading Analysis of the Configuration 1.a")
***
* #### 1.b ```--probability --ccf --mocus --mcub --importance```
![](/home/egemen/Pictures/Screenshots/1.b_th.png "Threading of the Configuration 1.b")
***
* #### 1.c ```--probability --ccf --mocus --mcub```  
![](/home/egemen/Pictures/Screenshots/1.c_th.png "Threading Analysis of the Configuration 1.c")
***
* #### 2.a ```--probability --ccf --mocus --rare-event --importance --uncertainty --num-trials 10000``` 
![](/home/egemen/Pictures/Screenshots/2.a_th.png "Threading Analysis of the Configuration 2.a")
***
* #### 2.b ```--probability --ccf --mocus --rare-event --importance ``` 
![](/home/egemen/Pictures/Screenshots/2.b_th.png "Threading Analysis of the Configuration 2.b")
***
* #### 2.c ```--probability --ccf --mocus --rare-event```
![](/home/egemen/Pictures/Screenshots/2.c_th.png "Threading Analysis of the Configuration 2.c")
***
* #### 3.a ```--probability --ccf --bdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/3.a_th.png "Threading Analysis of the Configuration 3.a")
***
* #### 3.b ```--probability --ccf --bdd --importance``` 
![](/home/egemen/Pictures/Screenshots/3.b_th.png "Threading Analysis of the Configuration 1.b")
***
* #### 3.c ```--probability --ccf --bdd```
![](/home/egemen/Pictures/Screenshots/3.c_th.png "Threading Analysis of the Configuration 3.c")
***
* #### 4.a ```--probability --ccf --zbdd --importance --uncertainty --num-trials 10000```
![](/home/egemen/Pictures/Screenshots/4.a_th.png "Threading Analysis of the Configuration 4.a")
***
* #### 4.b ```--probability --ccf --zbdd --importance```
![](/home/egemen/Pictures/Screenshots/4.b_th.png "Threading Analysis of the Configuration 4.b")
***
* #### 4.c ```--probability --ccf --zbdd```
![](/home/egemen/Pictures/Screenshots/4.c_th.png "Threading Analysis of the Configuration 4.c")

### Microarchitecture Exploration
* #### 3.c ```--probability --ccf --bdd```
![](/home/egemen/Pictures/Screenshots/3.c_ue.png "Microarchitecture Exploration of the Configuration 3.c")
***
* #### 4.c ```--probability --ccf --zbdd```
![](/home/egemen/Pictures/Screenshots/4.c_ue.png "Microarchitecture Exploration of the Configuration 4.c")

***
## 1.24.23
Starting with the command: ```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Log location: /tmp/vtune-tmp-egemen/self-checker-2023.01.24_11.55.12/log.txt

***
## 1.14.23
I am working on changing the running configuration of [scram](https://gitlab.openpra.org/scram/scram). At this time, I decided to go will ```full``` analysis meaning that [scram](https://gitlab.openpra.org/scram/scram) do all calculations, including uncertainy as well. 

For example, running [scram](https://gitlab.openpra.org/scram/scram) with the configuration ```--probability --ccf --importance --mocus --mcub --uncertainty --num-trials 10000 ``` took 4732.030 seconds for ```perfomance snaphot``` analysis in [vtune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html#gs.n2clij). The updated comparison table is below:

### Comparison of results for different configurations for ```BE_500_1_CCF```

| #   | Configuration                                                                          | probability | number of cutsets | performance snapshot time (sec) | output file                           | vtune project name           |
|-----|----------------------------------------------------------------------------------------|-------------|-------------------|---------------------------------|---------------------------------------|------------------------------|
| 1.a | --probability --ccf --importance --mocus --mcub --uncertainty --num-trials 10000       | 0           |                   | 4732.030                        | BE_500_1_CCF-output-full.txt          | scram_BE_1_CCF-full          |
| 1.b | --probability --ccf --importance --mocus --mcub                                        | 0           |                   | 2265.533                        | BE_500_1_CCF-output.txt               | scram_BE_1_CCF               |
| 1.c | --probability --ccf --mocus --mcub                                                     | 0           |                   | 7.449                           | BE_500_1_CCF-output-woimp.txt         | scram_BE_1_CCF-woimp         |
| 2.a | --probability --ccf --importance --mocus --rare-event --uncertainty --num-trials 10000 | 1.0661e-22  |                   | 4828.218                        | BE_500_1_CCF-config2-output-full.txt  | scram_BE_1_CCF-config2-full  |
| 2.b | --probability --ccf --importance --mocus --rare-event                                  | 1.0661e-22  |                   | 2212.874                        | BE_500_1_CCF-config2-output.txt       | scram_BE_1_CCF-config2       |
| 2.c | --probability --ccf --mocus --rare-event                                               | 1.0661e-22  |                   | 7.505                           | BE_500_1_CCF-config2-output-woimp.txt | scram_BE_1_CCF-config2-woimp |
| 3.a | --probability --ccf --importance --bdd --uncertainty --num-trials 10000                | 6.86304e-23 |                   | 7.365                           | BE_500_1_CCF-config3-output-full.txt  | scram_BE_1_CCF-config3-full  |
| 3.b | --probability --ccf --importance --bdd                                                 | 6.86304e-23 |                   | 14.755                          | BE_500_1_CCF-config3-output.txt       | scram_BE_1_CCF-config3       |
| 3.c | --probability --ccf --bdd                                                              | 6.86304e-23 |                   | 6.585                           | BE_500_1_CCF-config3-output-woimp.txt | scram_BE_1_CCF-config3-woimp |
| 4.a | --probability --ccf --importance --zbdd --uncertainty --num-trials 10000               | 1.0661e-22  |                   | 674.597                         | BE_500_1_CCF-config4-output-full.txt  | scram_BE_1_CCF-config4-full  |
| 4.b | --probability --ccf --importance --zbdd                                                | 1.0661e-22  |                   | 330.400                         | BE_500_1_CCF-config4-output.txt       | scram_BE_1_CCF-config4       |
| 4.c | --probability --ccf --zbdd                                                             | 1.0661e-22  |                   | 6.570                           | BE_500_1_CCF-config4-output-woimp.txt | scram_BE_1_CCF-config4-woimp |

>Questions: 

* Why is the quantification so quick?

* What is the difference between BDD and ZBDD algorithm that implemented in [scram](https://gitlab.openpra.org/scram/scram)?

* What is the best way to present/analysis profiling results?

* Why the ```--importance``` takes this much time?

* What is the best way to obtain number of ```MCS``` from output of [scram](https://gitlab.openpra.org/scram/scram) the run?

>Work on:

* BDD and ZBDD algorithms

* Dive into [scram](https://gitlab.openpra.org/scram/scram) source code

* Compare results with other engines

* Put all the results in a presentation to have a team meeting on those 
***
## 1.13.23
Starting with the command: ```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

The result of ```vtune-self-checker.sh``` is:
The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Log location: `````/tmp/vtune-tmp-egemen/self-checker-2023.01.12_22.45.08/log.txt`````

I noticed a very important detail. I've tried run scram without ```--importance```, the result is strange and valuable. Most of the calculation time belongs to ```--importance```.

So, I repeated the [vtune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html#gs.n2clij) evaluations for all scenarios, the results are below:

### Comparison of results for different configurations for ```BE_500_1_CCF```

| #   | Configuration                                         | probability  | number of cutsets | performance snapshot time (sec) | output file                           | vtune project name           |
|-----|-------------------------------------------------------|--------------|-------------------|---------------------------------|---------------------------------------|------------------------------|
| 1.a | --probability --ccf --importance --mocus --mcub       | 0            |                   | 2265.533                        | BE_500_1_CCF-output.txt               | scram_BE_1_CCF               |
| 1.b | --probability --ccf --mocus --mcub                    | 0            |                   | 7.449                           | BE_500_1_CCF-output-woimp.txt         | scram_BE_1_CCF-woimp         |
| 2.a | --probability --ccf --importance --mocus --rare-event | 1.0661e-22   |                   | 2212.874                        | BE_500_1_CCF-config2-output.txt       | scram_BE_1_CCF-config2       |
| 2.b | --probability --ccf --mocus --rare-event              | 1.0661e-22   |                   | 7.505                           | BE_500_1_CCF-config2-output-woimp.txt | scram_BE_1_CCF-config2-woimp |
| 3.a | --probability --ccf --importance --bdd                | 6.86304e-23  |                   | 14.755                          | BE_500_1_CCF-config3-output.txt       | scram_BE_1_CCF-config3       |
| 3.b | --probability --ccf --bdd                             | 6.86304e-23  |                   | 6.585                           | BE_500_1_CCF-config3-output-woimp.txt | scram_BE_1_CCF-config3-woimp |
| 4.a | --probability --ccf --importance --zbdd               | 1.0661e-22   |                   | 330.400                         | BE_500_1_CCF-config4-output.txt       | scram_BE_1_CCF-config4       |
| 4.b | --probability --ccf --zbdd                            | 1.0661e-22   |                   | 6.570                           | BE_500_1_CCF-config4-output-woimp.txt | scram_BE_1_CCF-config4-woimp |

>Questions: 

>>>>>What is the best way to present/analysis profiling results?

>>>>>Why the ```--importance``` takes this much time?

>>>>>What is the best way to obtain number of ```MCS``` from output of [scram](https://gitlab.openpra.org/scram/scram) the run?
***
## 1.5.23
Starting with the command: ```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

The result of ```vtune-self-checker.sh``` is:

The system is ready to be used for performance analysis with ```Intel VTune Profiler```.
Review warnings in the output above to find product limitations, if any.

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Log location: /tmp/vtune-tmp-egemen/self-checker-2023.01.05_12.56.53/log.txt

```vtune``` configurations with the fault tree ```BE_500_1_CCF``` is below. 

Firstly, ```performance snapshot``` is done, then ```hotspot analysis``` is performed. Third step is doing ```threading analysis```. All three steps are done for each configuration. No customization is done while doing these three analysis. 

1) --probability --ccf --importance --mocus --mcub	[done]	> 30 min
2) --probability --ccf --importance --mocus --rare-event	[done]	> 30 min
3) --probability --ccf --importance --bdd		[done]	~ 20 sec
4) --probability --ccf --importance --zbdd		[done]	~ 5 min
***
## 1.4.23
Starting with the command: ```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

The result of ```vtune-self-checker.sh``` is:

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Log location: /tmp/vtune-tmp-egemen/self-checker-2023.01.04_17.03.34/log.txt

- vtune command line

`````/opt/intel/oneapi/vtune/2022.4.1/bin64/vtune -collect performance-snapshot --app-working-dir=/home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin -- /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/scram /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/input-examples/BE_500_1_CCF.xml --probability --ccf --importance --mocus --mcub >/home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/input-examples/BE_500_1_CCF-output.txt`````
***
## 12.19.22
Starting with the command: ```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

The result of vtune-self-checker.sh is:
The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Log location: /tmp/vtune-tmp-egemen/self-checker-2022.12.19_15.06.15/log.txt

Today, I am starting to create various fault trees using [fault tree creator](https://gitlab.openpra.org/benchmarking/ft_solver/-/tree/develop/scripts) to use in profiling.

| #   | Argument                                         | [options]           | Default       | Option #1    | Option #2    | Option #3    | Option #4    | Option #5        | Option #6        | Option #7    | Option #8    |
|-----|--------------------------------------------------|---------------------|---------------|--------------|--------------|--------------|--------------|------------------|------------------|--------------|--------------|
| 1*  | name for the fault tree                          | [--ft-name]         | Autogenerated | BE_500_1     | BE_750_2     | BE_500_2     | BE_750_1     | BE_500_1_CCF**   | BE_750_1_CCF     | BE_550_1     | BE_600_1     |
| 2   | name for the root gate                           | [--root]            | root          | root         | root         | root         | root         | root             | root             | root         | root         |
| 3   | seed for the PRNG                                | [--seed]            | 123           | 123          | 123          | 123          | 123          | 123              | 123              | 123          | 123          |
| 4*  | # of basic events                                | [-b or --num-basic] | 100           | 500          | 750          | 500          | 750          | 500              | 750              | 550          | 600          |
| 5*  | avg. # of gate arguments                         | [-a or --num-args]  | 3.0           | 10           | 10           | 10           | 10           | 10               | 10               | 10           | 10           |
| 6*  | weights for [AND, OR, K/N, NOT, XOR] gates       | [--weights-g]       | [1,1,0,0,0]   | [1,1,1,0,0]  | [1,1,1,0,0]  | [1,1,1,0,0]  | [1,1,1,0,0]  | [1,1,1,0,0]      | [1,1,1,0,0]      | [1,1,1,0,0]  | [1,1,1,0,0]  |
| 7*  | avg. %% of common basic events per gate          | [--common-b]        | 0.3           | 0.5          | 0.7          | 0.7          | 0.5          | 0.5              | 0.5              | 0.5          | 0.5          |
| 8*  | avg. %% of common gates per gate                 | [--common-g]        | 0.1           | 0.3          | 0.5          | 0.5          | 0.3          | 0.3              | 0.3              | 0.3          | 0.3          |
| 9*  | avg. # of parents for common basic events        | [--parents-b]       | 2             | 5            | 5            | 5            | 5            | 5                | 5                | 5            | 5            |
| 10* | avg. # of parents for common gates               | [--parents-g]       | 2             | 5            | 5            | 5            | 5            | 5                | 5                | 5            | 5            |
| 11  | # of gates (discards parents-b/g and common-b/g) | [-g or --num-gate]  | 0             | 0            | 0            | 0            | 0            | 0                | 0                | 0            | 0            |
| 12  | maximum probability for basic events             | [--max-prob]        | 0.1           | 0.05         | 0.05         | 0.05         | 0.05         | 0.05             | 0.05             | 0.05         | 0.05         |
| 13* | minimum probability for basic events             | [--min-prob]        | 0.000001      | 0.01         | 0.01         | 0.01         | 0.01         | 0.01             | 0.01             | 0.01         | 0.01         |
| 14  | # of house events                                | [--num-house]       | 0             | 0            | 0            | 0            | 0            | 0                | 0                | 0            | 0            |
| 15  | # of ccf groups                                  | [--num-ccf]         | 0             | 0            | 0            | 0            | 0            | 2                | 2                | 0            | 0            |
| 16* | a file to write the fault tree                   | [-o or --out]       | -             | BE_500_1.xml | BE_750_2.xml | BE_500_2.xml | BE_750_1.xml | BE_500_1_CCF.xml | BE_750_1_CCF.xml | BE_550_1.xml | BE_600_1.xml |
| 17  | apply the Aralia format to the output            | [--aralia]          | -             | -            | -            | -            | -            | -                | -                | -            | -            |
| 18  | nest NOT connectives in Boolean formulae         | [--nest]            | -             | -            | -            | -            | -            | -                | -                | -            | -            |

*changed options for the analysis
**the fault tree used for the profiling

The fault tree used during SCRAM profiling is ```BE_500_1_CCF```. ```Default``` setting was used for this profiling.
* The performance snapshot took 2265.533 sec (~38 min). 
* Hotspots analysis took 2188.669 sec (~37 min)
* Threading analysis took 2270.057 sec (~38 min)
It is time to dive into analysis results, and look for the place to add parallelization.
***
## 12.1.22
This is the result of self-checker:

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* Hotspots and Threading with user-mode sampling
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

Failures:
- #1 

Instrumentation based analysis check   
Example of analysis types: Hotspots and Threading with user-mode sampling
    Collection: Fail
vtune: Error: Cannot start data collection because the scope of ptrace system call is limited. To enable profiling, please set /proc/sys/kernel/yama/ptrace_scope to 0. To make this change permanent, set kernel.yama.ptrace_scope to 0 in /etc/sysctl.d/10-ptrace.conf and reboot the machine.
- Solution #1:

Setting ``` /proc/sys/kernel/yama/ptrace_scope ``` to ```0``` can be done with this comment 

```sudo sh -c " echo 0 > /proc/sys/kernel/yama/ptrace_scope"```

After Solution #1, restarted self-checker, and the new results of self-checker is below:

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

For this profiling try, I decided to use ```CEA9601.xml``` input file. It was one of the input files under [scram](https://gitlab.openpra.org/scram/scram). The model data and model was stored in a different .xml file, I copied model data into model .xml file. 

Testing configuration is:
`````/opt/intel/oneapi/vtune/2022.4.1/bin64/vtune -collect performance-snapshot --app-working-dir=/home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin -- /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/scram /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin//input-examples/CEA9601.xml --mocus --probability --importance`````

It took 12 minutes, but could not get any result! 

Then, I did try to solve the same input file with BDD, it took a while and produced 41.95 GB file! In the mean time, I have tried to solve same fault tree on my MacBook Air, it could not give any result, gave same result with BDD.

Updated testing configuration is:
`````/opt/intel/oneapi/vtune/2022.4.1/bin64/vtune -collect performance-snapshot --app-working-dir=/home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin -- /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/scram /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin//input-examples/CEA9601.xml --bdd --probability --importance`````

It took 20 minutes, but could not get any result from vtune again!

Updated testing configuration is:
`````/opt/intel/oneapi/vtune/2022.4.1/bin64/vtune -collect performance-snapshot --app-working-dir=/home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin -- /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin/scram /home/egemen/Desktop/repo/gitlab/openpra/scram/build-release/install-release-w-debug/bin//input-examples/baobab1.xml --mocus --probability --importance`````

Now, it took 1.795 sec to complete, the configuration is called ```r005ps``` in [vtune](https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html#gs.n2clij)

***
## 11.17.22

After some corrections, vtune is ready on this machine by now [11/17/22]. Here is self-checker output:

The system is ready for the following analyses:
* Performance Snapshot
* Hotspots and Threading with user-mode sampling
* Hotspots with HW event-based sampling, HPC Performance Characterization, etc.
* Microarchitecture Exploration
* Memory Access
* Hotspots with HW event-based sampling and call stacks
* Threading with HW event-based sampling

The following analyses have failed on the system:
* GPU Compute/Media Hotspots (characterization mode)
* GPU Compute/Media Hotspots (source analysis mode)

self-checker may a take about 10 minutes. 

I also did first profiling step for SCRAM, got some results. 
Please see the screenshot of vtune, /home/Picture/Screenshots/Screenshot from 2022-11-17 12-56-09

***
# Note about Computer Used in This Study

* Device Name -- egemen-ubuntu22
* Hardware Model -- Dell Inc. Latitude E7470
* Memory -- 8.0GiB
* Processor -- Intel® Core™ i7-6600U CPU @ 2.60GHz × 4
* Graphics -- Mesa Intel® HD Graphics 520 (SKL GT2)
* Disk Capacity -- 256.1GB


* OS Name -- Ubuntu 22.04.1 LTS
* OS Type -- 64-bit
* GNOME Version -- 42.5
* Windowing System -- Wayland

***
***